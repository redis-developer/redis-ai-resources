"""
LangGraph agent implementation for the Redis University Class Agent.

This module implements the main agent logic using LangGraph for workflow orchestration,
with Redis for memory management and state persistence.
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
from .memory import MemoryManager
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
    """Redis University Class Agent using LangGraph."""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.memory_manager = MemoryManager(student_id)
        self.course_manager = CourseManager()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        
        # Build the agent graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Define tools
        tools = [
            self._search_courses_tool,
            self._get_recommendations_tool,
            self._store_preference_tool,
            self._store_goal_tool,
            self._get_student_context_tool
        ]
        
        # Create tool node
        tool_node = ToolNode(tools)
        
        # Define the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", tool_node)
        workflow.add_node("respond", self._respond_node)
        workflow.add_node("store_memory", self._store_memory_node)
        
        # Define edges
        workflow.set_entry_point("retrieve_context")
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
        workflow.add_edge("respond", "store_memory")
        workflow.add_edge("store_memory", END)
        
        return workflow.compile(checkpointer=redis_config.checkpointer)
    
    async def _retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve relevant context for the current conversation."""
        # Get the latest human message
        human_messages = [msg for msg in state.messages if isinstance(msg, HumanMessage)]
        if human_messages:
            state.current_query = human_messages[-1].content
        
        # Retrieve student context
        context = await self.memory_manager.get_student_context(state.current_query)
        state.context = context
        
        return state
    
    async def _agent_node(self, state: AgentState) -> AgentState:
        """Main agent reasoning node."""
        # Build system message with context
        system_prompt = self._build_system_prompt(state.context)
        
        # Prepare messages for the LLM
        messages = [SystemMessage(content=system_prompt)] + state.messages
        
        # Get LLM response
        response = await self.llm.ainvoke(messages)
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
    
    async def _store_memory_node(self, state: AgentState) -> AgentState:
        """Store important information from the conversation."""
        # Store conversation summary if conversation is getting long
        if len(state.messages) > 20:
            await self.memory_manager.store_conversation_summary(state.messages)
        
        return state
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with current context."""
        prompt = """You are a helpful Redis University Class Agent. Your role is to help students find courses, 
        plan their academic journey, and provide personalized recommendations based on their interests and goals.

        You have access to tools to:
        - Search for courses in the catalog
        - Get personalized course recommendations
        - Store student preferences and goals
        - Retrieve student context and history

        Current student context:"""
        
        if context.get("preferences"):
            prompt += f"\nStudent preferences: {', '.join(context['preferences'])}"
        
        if context.get("goals"):
            prompt += f"\nStudent goals: {', '.join(context['goals'])}"
        
        if context.get("recent_conversations"):
            prompt += f"\nRecent conversation context: {', '.join(context['recent_conversations'])}"
        
        prompt += """

        Guidelines:
        - Be helpful, friendly, and encouraging
        - Ask clarifying questions when needed
        - Provide specific course recommendations when appropriate
        - Remember and reference previous conversations
        - Store important preferences and goals for future reference
        - Explain course prerequisites and requirements clearly
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
    async def _store_preference_tool(self, preference: str, context: str = "") -> str:
        """Store a student preference for future reference."""
        memory_id = await self.memory_manager.store_preference(preference, context)
        return f"Stored preference: {preference}"

    @tool
    async def _store_goal_tool(self, goal: str, context: str = "") -> str:
        """Store a student goal or objective."""
        memory_id = await self.memory_manager.store_goal(goal, context)
        return f"Stored goal: {goal}"

    @tool
    async def _get_student_context_tool(self, query: str = "") -> str:
        """Retrieve student context and history."""
        context = await self.memory_manager.get_student_context(query)

        result = "Student Context:\n"
        if context.get("preferences"):
            result += f"Preferences: {', '.join(context['preferences'])}\n"
        if context.get("goals"):
            result += f"Goals: {', '.join(context['goals'])}\n"
        if context.get("recent_conversations"):
            result += f"Recent conversations: {', '.join(context['recent_conversations'])}\n"

        return result if len(result) > 20 else "No significant context found."

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
