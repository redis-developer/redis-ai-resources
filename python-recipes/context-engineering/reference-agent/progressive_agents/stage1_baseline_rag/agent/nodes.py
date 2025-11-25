"""
Workflow nodes for Stage 1 Baseline RAG Agent.

This demonstrates the BASELINE approach - no context engineering!
Students will see the problems with raw, unoptimized context.
"""

import json
import logging
import time
import asyncio
import nest_asyncio
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from redis_context_course import CourseManager

from .state import AgentState

# Configure logger
logger = logging.getLogger("stage1-baseline")

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
    Research node - performs semantic search and returns RAW context.
    
    THIS IS THE PROBLEM: No context engineering!
    - Returns raw JSON dump of course objects
    - Includes ALL fields (noise, timestamps, IDs, etc.)
    - Inefficient token usage
    - Hard for LLM to parse
    
    Students will see these problems and learn why context engineering matters.
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
        
        # Semantic search (same as Stage 3)
        courses = loop.run_until_complete(
            course_manager.search_courses(
                query=query,
                limit=5,
                similarity_threshold=0.5
            )
        )
        
        logger.info(f"✅ Found {len(courses)} courses")
        
        if not courses:
            state["raw_context"] = "No courses found."
            state["courses_found"] = 0
            return state
        
        # RAW CONTEXT - NO ENGINEERING!
        # This is intentionally bad to show students the problem
        
        # Convert courses to dictionaries (includes ALL fields)
        course_dicts = [course.model_dump(mode='json') for course in courses]
        
        # Option 1: JSON dump (most verbose, hardest to parse)
        raw_context = json.dumps(course_dicts, indent=2, default=str)
        
        # Calculate approximate token count (rough estimate: 1 token ≈ 4 chars)
        token_estimate = len(raw_context) // 4
        
        logger.info(f"📊 Raw context: {len(raw_context)} chars (~{token_estimate} tokens)")
        logger.warning("⚠️  Using RAW context - no cleaning, no optimization!")
        
        state["raw_context"] = raw_context
        state["courses_found"] = len(courses)
        state["total_tokens"] = token_estimate
        
        research_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"🔬 Research complete in {research_time:.2f}ms")
        
        return state
        
    except Exception as e:
        logger.error(f"Research failed: {e}")
        import traceback
        traceback.print_exc()
        state["raw_context"] = f"Search failed: {str(e)}"
        state["courses_found"] = 0
        return state


def synthesize_node(state: AgentState) -> AgentState:
    """
    Synthesis node - uses LLM to answer the question based on raw context.
    
    The LLM receives the raw, unoptimized context and must parse it.
    Students will see that LLMs can handle this, but it's inefficient.
    """
    start_time = time.perf_counter()
    query = state["query"]
    context = state["raw_context"]
    
    logger.info("🔗 Synthesizing answer from raw context...")
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Create prompt with raw context
        prompt = f"""You are a helpful course advisor assistant. Answer the student's question based on the course information provided.

Course Information (raw data):
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

