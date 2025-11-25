"""
Workflow nodes for Stage 2 Context-Engineered Agent.

This demonstrates CONTEXT ENGINEERING - applying Section 2 techniques!
Students will see the improvements over Stage 1's raw context.
"""

import logging
import time
import asyncio
import nest_asyncio
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from redis_context_course import CourseManager

from .state import AgentState
from .context_engineering import format_courses_for_llm

# Configure logger
logger = logging.getLogger("stage2-engineered")

# Global course manager (set during initialization)
course_manager: Optional[CourseManager] = None


def initialize_nodes(manager: CourseManager):
    """
    Initialize nodes with required dependencies.
    
    Args:
        manager: CourseManager instance for course search
    """
    global course_manager
    course_manager = manager


def research_node(state: AgentState) -> AgentState:
    """
    Research node - performs semantic search and returns ENGINEERED context.
    
    THIS IS THE SOLUTION: Context engineering!
    - Applies Section 2 techniques (clean, transform, optimize)
    - Removes noise fields
    - Converts to natural text format
    - Efficient token usage
    - LLM-friendly formatting
    
    Students will see these improvements compared to Stage 1.
    """
    start_time = time.perf_counter()
    query = state["query"]
    
    logger.info(f"🔍 Searching for courses: '{query[:50]}...'")
    
    try:
        # Allow nested event loops
        nest_asyncio.apply()
        
        # Get event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Semantic search (same as Stage 1)
        courses = loop.run_until_complete(
            course_manager.search_courses(
                query=query,
                limit=5,
                similarity_threshold=0.5
            )
        )
        
        logger.info(f"✅ Found {len(courses)} courses")
        
        if not courses:
            state["engineered_context"] = "No courses found."
            state["courses_found"] = 0
            return state
        
        # CONTEXT ENGINEERING - Apply Section 2 techniques!
        # This is the KEY difference from Stage 1
        
        engineered_context = format_courses_for_llm(
            courses,
            use_optimized=False  # Use full format for better quality
        )
        
        # Calculate approximate token count (rough estimate: 1 token ≈ 4 chars)
        token_estimate = len(engineered_context) // 4
        
        logger.info(f"📊 Engineered context: {len(engineered_context)} chars (~{token_estimate} tokens)")
        logger.info("✅ Context engineering applied:")
        logger.info("   - Cleaned: Removed noise fields (id, timestamps, enrollment)")
        logger.info("   - Transformed: JSON → natural text format")
        logger.info("   - Structured: Consistent, LLM-friendly formatting")
        
        state["engineered_context"] = engineered_context
        state["courses_found"] = len(courses)
        state["total_tokens"] = token_estimate
        
        research_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"🔬 Research complete in {research_time:.2f}ms")
        
        return state
        
    except Exception as e:
        logger.error(f"Research failed: {e}")
        import traceback
        traceback.print_exc()
        state["engineered_context"] = f"Search failed: {str(e)}"
        state["courses_found"] = 0
        return state


def synthesize_node(state: AgentState) -> AgentState:
    """
    Synthesis node - uses LLM to answer the question based on engineered context.
    
    The LLM receives clean, well-formatted context that's easy to parse.
    Students will see better answers with fewer tokens compared to Stage 1.
    """
    start_time = time.perf_counter()
    query = state["query"]
    context = state["engineered_context"]
    
    logger.info("🔗 Synthesizing answer from engineered context...")
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Create prompt with engineered context
        prompt = f"""You are a helpful course advisor assistant. Answer the student's question based on the course information provided.

Course Information (context-engineered):
{context}

Student Question: {query}

Please provide a clear, helpful answer based on the course information above."""

        # Get LLM response
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content
        
        synthesis_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"🔗 Synthesis complete in {synthesis_time:.2f}ms")
        logger.info(f"📝 Answer: {answer[:100]}...")
        
        state["final_answer"] = answer
        
        return state
        
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        import traceback
        traceback.print_exc()
        state["final_answer"] = f"Failed to generate answer: {str(e)}"
        return state

