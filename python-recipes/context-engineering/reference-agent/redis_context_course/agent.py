"""
LangGraph agent implementation for the Redis University Class Agent.

This module implements the main agent logic using LangGraph for workflow orchestration,
with Redis Agent Memory Server for memory management.

Memory Architecture:
- LangGraph Checkpointer (Redis): Low-level graph state persistence for resuming execution
- Working Memory (Agent Memory Server): Session-scoped conversation and task context
  * Automatically extracts important facts to long-term storage
  * Loaded at start of conversation turn, saved at end
- Long-term Memory (Agent Memory Server): Cross-session knowledge (preferences, facts)
  * Searchable via semantic vector search
  * Accessible via tools
"""

import json
from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from .models import StudentProfile, CourseRecommendation, AgentResponse
from agent_memory_client import MemoryAPIClient, MemoryClientConfig
from .course_manager import CourseManager
from .redis_config import redis_config


class AgentState(BaseModel):
    """State for the LangGraph agent."""
    messages: Annotated[List[BaseMessage], add_messages]
    student_id: str
    student_profile: Optional[StudentProfile] = None
    current_query: str = ""
    recommendations: List[CourseRecommendation] = []
    context: Dict[str, Any] = {}
    next_action: str = "respond"


class ClassAgent:
    """Redis University Class Agent using LangGraph and Agent Memory Server."""

    def __init__(self, student_id: str, session_id: Optional[str] = None):
        self.student_id = student_id
        self.session_id = session_id or f"session_{student_id}"

        # Initialize memory client with proper config
        config = MemoryClientConfig(
            base_url=os.getenv("AGENT_MEMORY_URL", "http://localhost:8000"),
            default_namespace="redis_university"
        )
        self.memory_client = MemoryAPIClient(config=config)
        self.course_manager = CourseManager()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

        # Build the agent graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        The graph uses:
        1. Redis checkpointer for low-level graph state persistence (resuming nodes)
        2. Agent Memory Server for high-level memory management (working + long-term)
        """
        # Define tools
        tools = [
            self._search_courses_tool,
            self._get_recommendations_tool,
            self._store_memory_tool,
            self._search_memories_tool
        ]

        # Create tool node
        tool_node = ToolNode(tools)

        # Define the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("load_working_memory", self._load_working_memory)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", tool_node)
        workflow.add_node("respond", self._respond_node)
        workflow.add_node("save_working_memory", self._save_working_memory)

        # Define edges
        workflow.set_entry_point("load_working_memory")
        workflow.add_edge("load_working_memory", "retrieve_context")
        workflow.add_edge("retrieve_context", "agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_use_tools,
            {
                "tools": "tools",
                "respond": "respond"
            }
        )
        workflow.add_edge("tools", "agent")
        workflow.add_edge("respond", "save_working_memory")
        workflow.add_edge("save_working_memory", END)

        # Compile with Redis checkpointer for graph state persistence
        # Note: This is separate from Agent Memory Server's working memory
        return workflow.compile(checkpointer=redis_config.checkpointer)
    
    async def _load_working_memory(self, state: AgentState) -> AgentState:
        """
        Load working memory from Agent Memory Server.

        Working memory contains:
        - Conversation messages from this session
        - Structured memories awaiting promotion to long-term storage
        - Session-specific data

        This is the first node in the graph, loading context for the current turn.
        """
        # Get or create working memory for this session
        _, working_memory = await self.memory_client.get_or_create_working_memory(
            session_id=self.session_id,
            user_id=self.student_id,
            model_name="gpt-4o"
        )

        # If we have working memory, add previous messages to state
        if working_memory and working_memory.messages:
            # Convert MemoryMessage objects to LangChain messages
            for msg in working_memory.messages:
                if msg.role == "user":
                    state.messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    state.messages.append(AIMessage(content=msg.content))

        return state

    async def _retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve relevant context for the current conversation."""
        # Get the latest human message
        human_messages = [msg for msg in state.messages if isinstance(msg, HumanMessage)]
        if human_messages:
            state.current_query = human_messages[-1].content

        # Search long-term memories for relevant context
        if state.current_query:
            memories = await self.memory_client.search_memories(
                query=state.current_query,
                limit=5
            )

            # Build context from memories
            context = {
                "preferences": [],
                "goals": [],
                "recent_facts": []
            }

            for memory in memories:
                if memory.memory_type == "semantic":
                    if "preference" in memory.topics:
                        context["preferences"].append(memory.text)
                    elif "goal" in memory.topics:
                        context["goals"].append(memory.text)
                    else:
                        context["recent_facts"].append(memory.text)

            state.context = context

        return state
    
    async def _agent_node(self, state: AgentState) -> AgentState:
        """Main agent reasoning node."""
        # Build system message with context
        system_prompt = self._build_system_prompt(state.context)

        # Prepare messages for the LLM
        messages = [SystemMessage(content=system_prompt)] + state.messages

        # Get LLM response with tools
        response = await self.llm.bind_tools(self._get_tools()).ainvoke(messages)
        state.messages.append(response)

        return state
    
    def _should_use_tools(self, state: AgentState) -> str:
        """Determine if tools should be used or if we should respond."""
        last_message = state.messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "respond"
    
    async def _respond_node(self, state: AgentState) -> AgentState:
        """Generate final response."""
        # The response is already in the last message
        return state

    async def _save_working_memory(self, state: AgentState) -> AgentState:
        """
        Save working memory to Agent Memory Server.

        This is the final node in the graph. It saves the conversation to working memory,
        and the Agent Memory Server automatically:
        1. Stores the conversation messages
        2. Extracts important facts to long-term storage
        3. Manages memory deduplication and compaction

        This demonstrates the key concept of working memory: it's persistent storage
        for task-focused context that automatically promotes important information
        to long-term memory.
        """
        # Convert LangChain messages to simple dict format
        messages = []
        for msg in state.messages:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content})

        # Save to working memory
        # The Agent Memory Server will automatically extract important memories
        # to long-term storage based on its configured extraction strategy
        from agent_memory_client import WorkingMemory, MemoryMessage

        # Convert messages to MemoryMessage format
        memory_messages = [MemoryMessage(**msg) for msg in messages]

        # Create WorkingMemory object
        working_memory = WorkingMemory(
            session_id=self.session_id,
            user_id=self.student_id,
            messages=memory_messages,
            memories=[],
            data={}
        )

        await self.memory_client.put_working_memory(
            session_id=self.session_id,
            memory=working_memory,
            user_id=self.student_id,
            model_name="gpt-4o"
        )

        return state
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with current context."""
        prompt = """You are a helpful Redis University Class Agent powered by Redis Agent Memory Server.
        Your role is to help students find courses, plan their academic journey, and provide personalized
        recommendations based on their interests and goals.

        Memory Architecture:

        1. LangGraph Checkpointer (Redis):
           - Low-level graph state persistence for resuming execution
           - You don't interact with this directly

        2. Working Memory (Agent Memory Server):
           - Session-scoped, task-focused context
           - Contains conversation messages and task-related data
           - Automatically loaded at the start of each turn
           - Automatically saved at the end of each turn
           - Agent Memory Server automatically extracts important facts to long-term storage

        3. Long-term Memory (Agent Memory Server):
           - Cross-session, persistent knowledge (preferences, goals, facts)
           - Searchable via semantic vector search
           - You can store memories directly using the store_memory tool
           - You can search memories using the search_memories tool

        You have access to tools to:
        - search_courses: Search for courses in the catalog
        - get_recommendations: Get personalized course recommendations
        - store_memory: Store important facts in long-term memory (preferences, goals, etc.)
        - search_memories: Search existing long-term memories

        Current student context (from long-term memory):"""

        if context.get("preferences"):
            prompt += f"\n\nPreferences:\n" + "\n".join(f"- {p}" for p in context['preferences'])

        if context.get("goals"):
            prompt += f"\n\nGoals:\n" + "\n".join(f"- {g}" for g in context['goals'])

        if context.get("recent_facts"):
            prompt += f"\n\nRecent Facts:\n" + "\n".join(f"- {f}" for f in context['recent_facts'])

        prompt += """

        Guidelines:
        - Be helpful, friendly, and encouraging
        - Ask clarifying questions when needed
        - Provide specific course recommendations when appropriate
        - When you learn important preferences or goals, use store_memory to save them
        - Reference previous context from long-term memory when relevant
        - Explain course prerequisites and requirements clearly
        - The conversation is automatically saved to working memory
        """

        return prompt

    @tool
    async def _search_courses_tool(self, query: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """Search for courses based on a query and optional filters."""
        courses = await self.course_manager.search_courses(query, filters or {})

        if not courses:
            return "No courses found matching your criteria."

        result = f"Found {len(courses)} courses:\n\n"
        for course in courses[:5]:  # Limit to top 5 results
            result += f"**{course.course_code}: {course.title}**\n"
            result += f"Department: {course.department} | Credits: {course.credits} | Difficulty: {course.difficulty_level.value}\n"
            result += f"Description: {course.description[:200]}...\n\n"

        return result

    @tool
    async def _get_recommendations_tool(self, query: str = "", limit: int = 3) -> str:
        """Get personalized course recommendations for the student."""
        # For now, create a basic student profile
        # In a real implementation, this would be retrieved from storage
        student_profile = StudentProfile(
            name="Student",
            email="student@example.com",
            interests=["programming", "data science", "web development"]
        )

        recommendations = await self.course_manager.recommend_courses(
            student_profile, query, limit
        )

        if not recommendations:
            return "No recommendations available at this time."

        result = f"Here are {len(recommendations)} personalized course recommendations:\n\n"
        for i, rec in enumerate(recommendations, 1):
            result += f"{i}. **{rec.course.course_code}: {rec.course.title}**\n"
            result += f"   Relevance: {rec.relevance_score:.2f} | Credits: {rec.course.credits}\n"
            result += f"   Reasoning: {rec.reasoning}\n"
            result += f"   Prerequisites met: {'Yes' if rec.prerequisites_met else 'No'}\n\n"

        return result

    @tool
    async def _store_memory_tool(
        self,
        text: str,
        memory_type: str = "semantic",
        topics: Optional[List[str]] = None
    ) -> str:
        """
        Store important information in long-term memory.

        Args:
            text: The information to store (e.g., "Student prefers online courses")
            memory_type: Type of memory - "semantic" for facts/preferences, "episodic" for events
            topics: Related topics for filtering (e.g., ["preferences", "courses"])
        """
        from agent_memory_client import ClientMemoryRecord

        memory = ClientMemoryRecord(
            text=text,
            user_id=self.student_id,
            memory_type=memory_type,
            topics=topics or []
        )

        await self.memory_client.create_long_term_memory([memory])
        return f"Stored in long-term memory: {text}"

    @tool
    async def _search_memories_tool(
        self,
        query: str,
        limit: int = 5
    ) -> str:
        """
        Search long-term memories using semantic search.

        Args:
            query: Search query (e.g., "student preferences")
            limit: Maximum number of results to return
        """
        from agent_memory_client import UserId

        results = await self.memory_client.search_long_term_memory(
            text=query,
            user_id=UserId(eq=self.student_id),
            limit=limit
        )

        if not results.memories:
            return "No relevant memories found."

        result = f"Found {len(results.memories)} relevant memories:\n\n"
        for i, memory in enumerate(results.memories, 1):
            result += f"{i}. {memory.text}\n"
            if memory.topics:
                result += f"   Topics: {', '.join(memory.topics)}\n"
            result += "\n"

        return result

    def _get_tools(self):
        """Get list of tools for the agent."""
        return [
            self._search_courses_tool,
            self._get_recommendations_tool,
            self._store_memory_tool,
            self._search_memories_tool
        ]

    async def chat(self, message: str, thread_id: str = "default") -> str:
        """Main chat interface for the agent."""
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            student_id=self.student_id
        )

        # Run the graph
        config = {"configurable": {"thread_id": thread_id}}
        result = await self.graph.ainvoke(initial_state, config)

        # Return the last AI message
        ai_messages = [msg for msg in result.messages if isinstance(msg, AIMessage)]
        if ai_messages:
            return ai_messages[-1].content

        return "I'm sorry, I couldn't process your request."
