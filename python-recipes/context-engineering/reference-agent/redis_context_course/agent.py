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

import os

import json

from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
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
            base_url=os.getenv("AGENT_MEMORY_URL", "http://localhost:8088"),
            default_namespace="redis_university"
        )
        self.memory_client = MemoryAPIClient(config=config)
        self.course_manager = CourseManager()
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.0)


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

            self._create_search_courses_tool(),
            self._create_list_majors_tool(),
            self._create_recommendations_tool(),
            self._store_memory_tool,
            self._search_memories_tool,
            self._create_summarize_user_knowledge_tool(),
            self._create_clear_user_memories_tool()
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

        # Compile graph without Redis checkpointer
        # TODO(CE-Checkpointer): Re-enable Redis checkpointer once langgraph's async
        # checkpointer interface is compatible in our environment. Current versions
        # raise NotImplementedError on aget_tuple via AsyncPregelLoop. Track and
        # fix by upgrading langgraph (and/or using the correct async RedisSaver)
        # and then switch to: workflow.compile(checkpointer=redis_config.checkpointer)
        return workflow.compile()

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
            model_name=self.model_name
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
            from agent_memory_client.filters import UserId
            results = await self.memory_client.search_long_term_memory(
                text=state.current_query,
                user_id=UserId(eq=self.student_id),
                limit=5
            )

            # Build context from memories
            context = {
                "preferences": [],
                "goals": [],
                "recent_facts": []
            }

            for memory in results.memories:
                if memory.memory_type == "semantic":
                    if "preference" in memory.topics:
                        context["preferences"].append(memory.text)
                    elif "goal" in memory.topics:
                        context["goals"].append(memory.text)
                    else:
                        context["recent_facts"].append(memory.text)

            state.context = context



    async def _agent_node(self, state: AgentState) -> AgentState:
        """Main agent reasoning node."""
        # Build system message with context
        system_prompt = self._build_system_prompt(state.context)

        # Prepare messages for the LLM
        messages = [SystemMessage(content=system_prompt)] + state.messages

        # Get LLM response with tools
        # Always require the model to choose a tool (no code heuristics)
        tools = self._get_tools()
        # If we don't yet have a tool result this turn, require a tool call; otherwise allow a normal reply
        has_tool_result = any(isinstance(m, ToolMessage) for m in state.messages)
        try:
            if not has_tool_result:
                model = self.llm.bind_tools(tools, tool_choice="required", parallel_tool_calls=False)
            else:
                model = self.llm.bind_tools(tools, tool_choice="none", parallel_tool_calls=False)
        except TypeError:
            # Fallback for older/mocked LLMs that don't accept tool_choice
            model = self.llm.bind_tools(tools)
        response = await model.ainvoke(messages)
        # Optional debug: log chosen tool
        if os.getenv("AGENT_DEBUG_TOOLCALLS"):
            try:
                tool_calls = getattr(response, "tool_calls", None)
                if tool_calls:
                    # LangChain ToolCall objects have .name and .args
                    chosen = ", ".join([f"{tc.get('name') or getattr(tc, 'name', '')}" for tc in tool_calls])
                    print(f"[DEBUG] tool_choice={chosen}")
                else:
                    # OpenAI raw additional_kwargs path
                    aw = getattr(response, "additional_kwargs", {})
                    tc_raw = aw.get("tool_calls")
                    if tc_raw:
                        names = []
                        for t in tc_raw:
                            fn = (t.get("function") or {}).get("name")
                            if fn:
                                names.append(fn)
                        if names:
                            print(f"[DEBUG] tool_choice={', '.join(names)}")
            except Exception as _:
                pass

        state.messages.append(response)

        return state

    def _should_use_tools(self, state: AgentState) -> str:
        """Determine if we should run tools or generate a final response.



        Logic per turn:
        - If a tool has already been executed after the latest user message, respond now.
        - Else, if the last LLM message includes a tool call, run tools.
        - Otherwise, respond.
        """
        # Find index of the latest user message (this turn's query)
        last_user_idx = -1
        for i, m in enumerate(state.messages):
            if isinstance(m, HumanMessage):
                last_user_idx = i
        # If there's any ToolMessage after the latest user message, we've already executed a tool this turn
        if last_user_idx != -1:
            for m in state.messages[last_user_idx + 1:]:
                if isinstance(m, ToolMessage):
                    return "respond"
        # Otherwise, decide based on the last AI message having tool calls
        last_message = state.messages[-1]
        if hasattr(last_message, 'tool_calls') and getattr(last_message, 'tool_calls'):
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
            content = getattr(msg, "content", None)
            if not content:
                continue
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": content})

        # Save to working memory
        # The Agent Memory Server will automatically extract important memories
        # to long-term storage based on its configured extraction strategy
        from agent_memory_client.models import WorkingMemory, MemoryMessage

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
            model_name=self.model_name
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

        - search_courses_tool: Search for specific courses by topic or department
        - list_majors_tool: List all available majors and programs
        - get_recommendations_tool: Get personalized course recommendations based on interests
        - _store_memory_tool: Store important facts in long-term memory (preferences, goals, etc.)
        - _search_memories_tool: Search existing long-term memories
        - summarize_user_knowledge_tool: Provide comprehensive summary of what you know about the user
        - clear_user_memories_tool: Clear, delete, remove, or reset stored user information when explicitly requested

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


        - Always call exactly one tool per user message. Never reply without using a tool.
        After you call a tool and receive its output, produce a clear final answer to the user without calling more tools in the same turn.


        For ALL OTHER requests, use the appropriate tools as described below.

        IMPORTANT: Use the correct tools for different user requests:

        For user profile/memory questions:
        - Use summarize_user_knowledge_tool when users ask "what do you know about me", "show me my profile", "what do you remember about me"
        - Use clear_user_memories_tool when users say "ignore all that", "clear my profile", "reset what you know"
            - Never call clear_user_memories_tool unless the user's latest message explicitly requests clearing/resetting/deleting/erasing/forgetting their data.
            - Regular requests like "recommend", "find", "list", "show" must NOT call clear_user_memories_tool.

        - Use _search_memories_tool for specific memory searches

        For academic requests:
        - Use get_recommendations_tool when users express interests ("I like math") or ask for suggestions ("suggest courses", "recommend courses")
        - Use search_courses_tool when users want specific courses by name or topic ("show me CS courses", "find programming classes")
        - Use list_majors_tool only when users ask about available majors/programs ("what majors are available")

        For storing information:
        - Use _store_memory_tool when you learn important preferences, goals, or facts about the user
        - Never use _store_memory_tool to answer questions like "what do you know about me", "my history", or "show my profile". Use summarize_user_knowledge_tool instead.

        Hard constraints:
        - For any query about "history", "profile", or "what do you know": you MUST call summarize_user_knowledge_tool. Do NOT call get_recommendations_tool, search_courses_tool, or list_majors_tool for these.
        - Only call list_majors_tool when the user's latest message explicitly contains one of: "major", "majors", "program", "programs", "degree", "degrees".
        - When the user says "more" after you recommended courses, call get_recommendations_tool again for more courses. Never switch to list_majors_tool for "more".


        DO NOT default to search_courses_tool for everything. Choose the most appropriate tool based on the user's actual request.

        Tool selection examples (exact mappings):
        - User: "what do you know about me?" -> Call summarize_user_knowledge_tool
        - User: "show me my profile" -> Call summarize_user_knowledge_tool
        - User: "what's my history" -> Call summarize_user_knowledge_tool
            - User: "show my history" -> Call summarize_user_knowledge_tool
            - User: "see my history" -> Call summarize_user_knowledge_tool
            - User: "my history" -> Call summarize_user_knowledge_tool
            - User: "my profile" -> Call summarize_user_knowledge_tool

        - User: "learn about my profile" -> Call summarize_user_knowledge_tool
        - User: "clear my history" -> Call clear_user_memories_tool
        - User: "clear my profile" -> Call clear_user_memories_tool
        - User: "ignore my preferences" -> Call clear_user_memories_tool
        - User: "reset what you know" -> Call clear_user_memories_tool
        - User: "what majors are available" -> Call list_majors_tool
        - User: "list majors" -> Call list_majors_tool
        - User: "find me courses" -> Call get_recommendations_tool
        - User: "help me find courses" -> Call get_recommendations_tool
        - User: "suggest math courses" -> Call get_recommendations_tool
        - User: "show me cs courses" -> Call search_courses_tool
        - User: "find programming classes" -> Call search_courses_tool
        - User: "what math courses are available" -> Call search_courses_tool

        Always prefer get_recommendations_tool when the user expresses interests ("I like X", "I'm into Y") or asks for suggestions ("suggest", "recommend").


            Recommendation count handling:
            - If a user specifies a number (e.g., "recommend 5 math courses" or "top 10 AI courses"), call get_recommendations_tool with limit set to that number (1–10).
            - If a user says "more" after receiving recommendations and does not provide a number, call get_recommendations_tool with limit=5 by default.
            - Keep the query/topic from the conversation context when possible (e.g., if the user previously asked for "math" then says "more", continue with math).


        """

        return prompt



    def _create_search_courses_tool(self):
        """Create the search courses tool."""
        @tool
        async def search_courses_tool(query: str, filters: Optional[Dict[str, Any]] = None) -> str:
            """Search course catalog by topic, department, or difficulty.

            Use this tool when users ask for specific courses or subjects, or when
            filtering by department, difficulty, or topic. Returns matching courses
            with detailed information.

            Args:
                query (str): Search terms like "programming", "CS", "beginner math".
                filters (Dict[str, Any], optional): Additional filters for department,
                    difficulty, or other course attributes. Defaults to None.

            Returns:
                str: Formatted list of courses with codes, titles, descriptions,
                    credits, and difficulty levels. Returns "No courses found" if
                    no matches.

            Examples:
                Use for queries like:
                - "Show me CS courses"
                - "Find beginner programming classes"
                - "What math courses are available"

            Note:
                For listing all majors, use list_majors_tool instead.
            """
            # Hybrid approach: Handle problematic abbreviations explicitly, let LLM handle the rest
            if not filters:
                filters = {}

            # Only handle the most problematic/ambiguous cases explicitly
            problematic_mappings = {
                ' ds ': 'Data Science',  # Space-bounded to avoid false matches
                'ds classes': 'Data Science',
                'ds courses': 'Data Science',
            }

            query_lower = query.lower()
            for pattern, dept in problematic_mappings.items():
                if pattern in query_lower:
                    filters['department'] = dept
                    break

            courses = await self.course_manager.search_courses(query, filters=filters)

            if not courses:
                return "No courses found matching your criteria."

            result = f"Found {len(courses)} courses:\n\n"
            for course in courses[:10]:  # Show more results for department searches
                result += f"**{course.course_code}: {course.title}**\n"
                result += f"Department: {course.department} | Credits: {course.credits} | Difficulty: {course.difficulty_level.value}\n"
                result += f"Description: {course.description[:150]}...\n\n"

            return result

        return search_courses_tool

    def _create_list_majors_tool(self):
        """Create the list majors tool."""
        @tool
        async def list_majors_tool() -> str:
            """List all university majors and degree programs.

            Use this tool when users ask about available majors, programs, or degrees,
            or for general inquiries about fields of study. Returns a comprehensive
            list of all academic programs offered.

            Returns:
                str: Formatted list of majors with codes, departments, descriptions,
                    and required credits. Returns error message if majors cannot
                    be retrieved.

            Examples:
                Use for queries like:
                - "What majors are available?"
                - "List all programs"
                - "What can I study here?"

            Note:
                For specific course searches, use search_courses_tool instead.
            """
            try:
                # Get all major keys from Redis
                major_keys = self.course_manager.redis_client.keys("major:*")

                if not major_keys:
                    return "No majors found in the system."

                majors = []
                for key in major_keys:
                    major_data = self.course_manager.redis_client.hgetall(key)
                    if major_data:
                        major_info = {
                            'name': major_data.get('name', 'Unknown'),
                            'code': major_data.get('code', 'N/A'),
                            'department': major_data.get('department', 'N/A'),
                            'description': major_data.get('description', 'No description available'),
                            'required_credits': major_data.get('required_credits', 'N/A')
                        }
                        majors.append(major_info)

                if not majors:
                    return "No major information could be retrieved."

                # Format the response
                result = f"Available majors at Redis University ({len(majors)} total):\n\n"
                for major in majors:
                    result += f"**{major['name']} ({major['code']})**\n"
                    result += f"Department: {major['department']}\n"
                    result += f"Required Credits: {major['required_credits']}\n"
                    result += f"Description: {major['description']}\n\n"

                return result

            except Exception as e:
                return f"Error retrieving majors: {str(e)}"

        return list_majors_tool

    def _create_recommendations_tool(self):
        """Create the recommendations tool."""
        @tool
        async def get_recommendations_tool(query: str = "", limit: int = 3) -> str:
            """Generate personalized course recommendations based on user interests.

            Use this tool when users express interests or ask for course suggestions.
            Creates personalized recommendations with reasoning and automatically
            stores user interests in long-term memory for future reference.

            Args:
                query (str, optional): User interests like "math and engineering"
                    or "programming". Defaults to "".
                limit (int, optional): Maximum number of recommendations to return.
                    Defaults to 3.

            Returns:
                str: Personalized course recommendations with details, relevance
                    scores, reasoning, and prerequisite information. Returns
                    "No recommendations available" if none found.

            Examples:
                Use for queries like:
                - "I'm interested in math and engineering"
                - "Recommend courses for me"
                - "What should I take for data science?"


                Handling counts:
                - If the user specifies a number (e.g., "recommend 5" or "top 10"), set limit to that number (1–10).
                - If the user says "more" without a number, use limit=5 by default.

            Note:
                Automatically stores expressed interests in long-term memory.
                For general course searches, use search_courses_tool instead.
            """
            # Extract interests from the query and store them
            interests = []
            if query:
                # Store the user's expressed interests
                from agent_memory_client.models import ClientMemoryRecord
                memory = ClientMemoryRecord(
                    text=f"Student expressed interest in: {query}",
                    user_id=self.student_id,
                    memory_type="semantic",
                    topics=["interests", "preferences"]
                )
                await self.memory_client.create_long_term_memory([memory])
                interests = [interest.strip() for interest in query.split(" and ")]

            # Create student profile with current interests
            student_profile = StudentProfile(
                name=self.student_id,
                email=f"{self.student_id}@university.edu",
                interests=interests if interests else ["general"]
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

        return get_recommendations_tool

    @tool
    async def _store_memory_tool(
        self,
        text: str,
        memory_type: str = "semantic",
        topics: Optional[List[str]] = None
    ) -> str:
        """Store important student information in persistent long-term memory.

        Use this tool when the user shares preferences, goals, or important facts that
        should be remembered for future sessions. Avoid storing temporary conversation
        details that don't need persistence.

        Args:
            text (str): Information to store in memory.
            memory_type (str, optional): Type of memory - "semantic" for facts,
                "episodic" for events. Defaults to "semantic".
            topics (List[str], optional): Tags to categorize the memory, such as
                ["preferences", "courses"]. Defaults to None.

        Returns:
            str: Confirmation message indicating the information was stored.

        Examples:
            Store when user says:
            - "I prefer online courses"
            - "My goal is to become a data scientist"
            - "I've completed CS101"

        Note:
            This writes to persistent storage and will be available across sessions.
        """
        from agent_memory_client.models import ClientMemoryRecord

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
        """Search stored memories using semantic search.

        Use this tool to recall previous preferences, context, or specific information
        about the user. Performs semantic search across long-term memory to find
        relevant stored information.

        Args:
            query (str): Search terms for finding relevant memories.
            limit (int, optional): Maximum number of results to return. Defaults to 5.

        Returns:
            str: Formatted list of relevant memories with topics and context.
                Returns "No relevant memories found" if no matches.

        Examples:
            Use for queries like:
            - "What are my preferences?"
            - "What courses have I mentioned?"
            - "Remind me of my goals"

        Note:
            For comprehensive user summaries, use _summarize_user_knowledge_tool instead.
        """
        from agent_memory_client.models import UserId

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

    def _create_summarize_user_knowledge_tool(self):
        """Create the user knowledge summary tool."""

        @tool
        async def summarize_user_knowledge_tool() -> str:
            """Summarize what the agent knows about the user.

            Searches through long-term memory to gather all stored information about the user
            and organizes it into logical categories for easy review. Use this when the user
            asks about their profile, history, interests, or what you remember about them.

            Returns:
                str: Comprehensive summary of user information organized by categories
                    (preferences, goals, interests, academic history, facts). Returns
                    a helpful message if no information is stored.


            Examples:
                Use when user asks:
                - "What do you know about me?"
                - "Tell me about my profile"
                - "What are my interests and preferences?"
                - "What do you remember about me?"
                - "Show my history"
                - "See my history"
                - "Show my profile"
                - "My history"
            """
            try:
                from agent_memory_client.filters import UserId


                # Search long-term memories for all user information
                results = await self.memory_client.search_long_term_memory(
                    text="",  # Empty query to get all memories for this user
                    user_id=UserId(eq=self.student_id),
                    limit=50  # Get more results for comprehensive summary
                )
            except Exception as e:
                return f"I'm having trouble accessing your stored information right now. Error: {str(e)}"

            if not results.memories:
                return "I don't have any stored information about you yet. As we interact more, I'll learn about your preferences, interests, and goals."

            # Check if user has requested a reset
            reset_memories = [m for m in results.memories if m.topics and "reset" in [t.lower() for t in m.topics]]
            if reset_memories:
                return ("You previously requested to start fresh with your information. I don't have any current "
                       "stored information about your preferences or interests. Please share what you'd like me "
                       "to know about your academic interests and goals!")

            # Use LLM to create a comprehensive summary
            return await self._create_llm_summary(results.memories)

        return summarize_user_knowledge_tool

    async def _create_llm_summary(self, memories):
        """Create an LLM-based summary of user information."""
        if not memories:
            return "I don't have any stored information about you yet. As we interact more, I'll learn about your preferences, interests, and goals."

        # Prepare memory texts and topics for LLM
        memory_info = []
        for memory in memories:
            topics_str = f" (Topics: {', '.join(memory.topics)})" if memory.topics else ""
            memory_info.append(f"- {memory.text}{topics_str}")

        memories_str = "\n".join(memory_info)

        prompt = f"""Based on the following stored information about a student, create a well-organized, friendly summary of what I know about them:

{memories_str}

Please create a comprehensive summary that:
1. Groups related information together logically
2. Uses clear headings like "Your Interests", "Your Preferences", "Your Goals", etc.
3. Is conversational and helpful
4. Highlights the most important information
5. Uses bullet points for easy reading

Start with "Here's what I know about you based on our interactions:" and organize the information in a way that would be most useful to the student."""

        try:
            # Use the LLM to create a summary
            from langchain_core.messages import HumanMessage

            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content

        except Exception as e:
            # Fallback to simple organized list if LLM fails
            fallback = "Here's what I know about you:\n\n"
            fallback += "\n".join([f"• {memory.text}" for memory in memories])
            fallback += f"\n\n(Note: I encountered an issue creating a detailed summary, but here's the basic information I have stored.)"
            return fallback

    def _create_clear_user_memories_tool(self):
        """Create the clear user memories tool."""

        @tool
        async def clear_user_memories_tool(
            confirmation: str = "yes"
        ) -> str:
            """Clear or reset stored user information.

            Use this tool when users explicitly request to clear, reset, or "ignore" their
            previously stored information. This is useful when users want to start fresh
            or correct outdated information.

            If supported by the Agent Memory Server, this will:
            - Delete ALL long-term memories for this user_id
            - Delete ALL working-memory sessions for this user_id

            Args:
                confirmation (str, optional): Confirmation that user wants to clear memories.
                    Must be "yes" to proceed. Defaults to "yes".

            Returns:
                str: Confirmation message about the memory clearing operation.

            Examples:
                Use when user says:
                - "Ignore all that previous information"
                - "Clear my profile"
                - "Reset what you know about me"
                - "Start fresh"

            Note:

                Strict usage guard:
                - Only use this tool if the user's latest message explicitly includes clear/reset/erase/delete/forget/remove (e.g., "clear my history", "reset what you know").
                - Never use this tool for recommendations, search, listing majors, or any normal Q&A.

                This operation cannot be undone. Use with caution and only when
                explicitly requested by the user.
            """
            if confirmation.lower() != "yes":
                return "Memory clearing cancelled. If you want to clear your stored information, please confirm."

            try:
                # 1) Delete all long-term memories for this user
                from agent_memory_client.filters import UserId
                memory_ids = []
                async for mem in self.memory_client.search_all_long_term_memories(
                    text="",
                    user_id=UserId(eq=self.student_id),
                    batch_size=100,
                ):
                    if getattr(mem, "memory_id", None):
                        memory_ids.append(mem.memory_id)

                deleted_lt = 0
                if memory_ids:
                    # Delete in batches to avoid huge query params
                    BATCH = 100
                    for i in range(0, len(memory_ids), BATCH):
                        batch = memory_ids[i:i+BATCH]
                        try:
                            await self.memory_client.delete_long_term_memories(batch)
                            deleted_lt += len(batch)
                        except Exception:
                            # Continue best-effort deletion
                            pass

                # 2) Delete all working-memory sessions for this user
                deleted_wm = 0
                try:
                    offset = 0
                    page = await self.memory_client.list_sessions(limit=100, offset=offset, user_id=self.student_id)
                    while page.sessions:

                        for s in page.sessions:
                            sid = getattr(s, "session_id", None) or s
                            try:
                                await self.memory_client.delete_working_memory(session_id=sid, user_id=self.student_id)
                                deleted_wm += 1
                            except Exception:
                                pass
                        offset += len(page.sessions)
                        if len(page.sessions) < 100:
                            break
                        page = await self.memory_client.list_sessions(limit=100, offset=offset, user_id=self.student_id)
                except Exception:
                    # Best-effort: if list_sessions isn't supported, try current session only
                    try:
                        await self.memory_client.delete_working_memory(session_id=self.session_id, user_id=self.student_id)
                        deleted_wm += 1
                    except Exception:
                        pass

                if deleted_lt == 0 and deleted_wm == 0:
                    # Fall back: mark reset if deletion didn't occur
                    from agent_memory_client.models import ClientMemoryRecord
                    reset_memory = ClientMemoryRecord(
                        text="User requested to clear/reset all previous information and start fresh",
                        user_id=self.student_id,
                        memory_type="semantic",
                        topics=["reset", "clear", "fresh_start"]
                    )
                    await self.memory_client.create_long_term_memory([reset_memory])
                    return (
                        "I couldn't remove existing data, but I marked your profile as reset. "
                        "I'll ignore prior information and start fresh."
                    )

                # Success message summarizing deletions
                parts = []
                if deleted_lt:
                    parts.append(f"deleted {deleted_lt} long-term memories")
                if deleted_wm:
                    parts.append(f"cleared {deleted_wm} working-memory sessions")
                summary = ", ".join(parts)
                return f"Done: {summary}. We're starting fresh. What would you like me to know about your current interests and goals?"

            except Exception as e:
                return f"I encountered an error while trying to clear your information: {str(e)}"

        return clear_user_memories_tool

    def _get_tools(self):
        """Get list of tools for the agent."""
        return [

            self._create_search_courses_tool(),
            self._create_list_majors_tool(),
            self._create_recommendations_tool(),
            self._store_memory_tool,
            self._search_memories_tool,
            self._create_summarize_user_knowledge_tool(),
            self._create_clear_user_memories_tool()
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

        # Handle result structure (dict-like or object)
        result_messages = []
        if isinstance(result, dict) or hasattr(result, "get"):
            result_messages = result.get("messages", [])
        else:
            result_messages = getattr(result, "messages", [])

        # Return the last AI message
        ai_messages = [msg for msg in result_messages if isinstance(msg, AIMessage)]
        if ai_messages:
            return ai_messages[-1].content

        return "I'm sorry, I couldn't process your request."
