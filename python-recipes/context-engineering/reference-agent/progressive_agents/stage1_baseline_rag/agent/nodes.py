"""
Workflow nodes for Stage 1 Baseline RAG Agent.

This demonstrates the BASELINE approach - INFORMATION OVERLOAD!
Students will see the problems with returning EVERYTHING:
- Full course details including syllabi for ALL 5 courses
- Massive token waste (~6,000+ tokens)
- LLM struggles with too much information
- No progressive disclosure, no context engineering
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional

import nest_asyncio
from langchain_openai import ChatOpenAI

# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)
from langchain_core.messages import HumanMessage

from redis_context_course import CourseManager
from redis_context_course.hierarchical_context import RawContextAssembler
from redis_context_course.hierarchical_models import HierarchicalCourse

from .state import AgentState

# Configure logger
logger = logging.getLogger("stage1-baseline")

# Global course manager and hierarchical courses
course_manager: Optional[CourseManager] = None
hierarchical_courses = []


def initialize_nodes(manager: CourseManager):
    """
    Initialize nodes with required dependencies.

    Args:
        manager: CourseManager instance for course search
    """
    global course_manager, hierarchical_courses
    course_manager = manager

    # Load hierarchical courses with full syllabi
    try:
        data_path = (
            Path(__file__).parent.parent.parent.parent
            / "redis_context_course"
            / "data"
            / "hierarchical"
            / "hierarchical_courses.json"
        )
        if data_path.exists():
            with open(data_path) as f:
                data = json.load(f)
                hierarchical_courses = [
                    HierarchicalCourse(**course_data) for course_data in data["courses"]
                ]
            logger.info(
                f"Loaded {len(hierarchical_courses)} hierarchical courses with full syllabi"
            )
        else:
            logger.warning(f"Hierarchical courses not found at {data_path}")
    except Exception as e:
        logger.error(f"Failed to load hierarchical courses: {e}")


def research_node(state: AgentState) -> AgentState:
    """
    Research node - performs semantic search and returns EVERYTHING.

    THIS IS THE PROBLEM: INFORMATION OVERLOAD!
    - Returns FULL course details including syllabi for ALL 5 courses
    - Massive token waste (~6,000+ tokens vs ~700 with hierarchical)
    - LLM gets overwhelmed with too much information
    - No progressive disclosure - everything all at once
    - Includes details for courses user doesn't even care about

    Students will see why hierarchical retrieval and progressive disclosure matter.
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

        # Semantic search using basic course manager
        basic_courses = loop.run_until_complete(
            course_manager.search_courses(
                query=query, limit=5, similarity_threshold=0.5
            )
        )

        logger.info(f"✅ Found {len(basic_courses)} courses")

        if not basic_courses:
            state["raw_context"] = "No courses found."
            state["courses_found"] = 0
            return state

        # INFORMATION OVERLOAD - Return FULL details for ALL courses!
        # Match basic courses to hierarchical courses with full syllabi
        detailed_courses = []
        for basic_course in basic_courses:
            # Find matching hierarchical course
            for h_course in hierarchical_courses:
                if h_course.summary.course_code == basic_course.course_code:
                    detailed_courses.append(h_course.details)
                    break
            else:
                # Fallback: create CourseDetails from basic course (without syllabus)
                logger.warning(f"No hierarchical data for {basic_course.course_code}")

        if not detailed_courses:
            # Fallback to basic courses if no hierarchical data
            logger.warning("No hierarchical courses found, using basic courses")
            course_dicts = [course.model_dump(mode="json") for course in basic_courses]
            raw_context = json.dumps(course_dicts, indent=2, default=str)
        else:
            # Use RawContextAssembler to show EVERYTHING
            assembler = RawContextAssembler()
            raw_context = assembler.assemble_raw_context(detailed_courses, query)

        # Calculate approximate token count (rough estimate: 1 token ≈ 4 chars)
        token_estimate = len(raw_context) // 4

        logger.info(
            f"📊 INFORMATION OVERLOAD: {len(raw_context)} chars (~{token_estimate} tokens)"
        )
        logger.warning(
            "⚠️  Returning FULL details (including syllabi) for ALL 5 courses!"
        )
        logger.warning("⚠️  This wastes tokens on courses the user doesn't care about!")
        logger.warning("⚠️  No progressive disclosure, no context engineering!")

        state["raw_context"] = raw_context
        state["courses_found"] = (
            len(detailed_courses) if detailed_courses else len(basic_courses)
        )
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
