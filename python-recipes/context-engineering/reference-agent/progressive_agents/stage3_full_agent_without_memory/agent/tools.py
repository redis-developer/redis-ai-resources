"""
Tools for the Course Q&A Agent workflow.

Stage 3: Agentic workflow with LLM-controlled search tool!

This demonstrates the transition from scripted to agentic workflows:
- LLM decides when to search and what parameters to use
- Complex tool with multiple parameters (intent, strategy, entities)
- Replaces hardcoded nodes with tool-based decision making
- Hierarchical retrieval with progressive disclosure
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from redis_context_course import CourseManager
from redis_context_course.hierarchical_context import HierarchicalContextAssembler
from redis_context_course.hierarchical_models import (
    CourseSummary,
    HierarchicalCourse,
)
from redis_context_course.models import Course

# Configure logger
logger = logging.getLogger("course-qa-workflow")

# Global variables that will be set during initialization
course_manager: Optional[CourseManager] = None
hierarchical_courses = []
context_assembler = HierarchicalContextAssembler()


def initialize_tools(manager: CourseManager):
    """
    Initialize tools with required dependencies.

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
                f"Loaded {len(hierarchical_courses)} hierarchical courses for progressive disclosure"
            )
        else:
            logger.warning(f"Hierarchical courses not found at {data_path}")
    except Exception as e:
        logger.error(f"Failed to load hierarchical courses: {e}")


def transform_course_to_text(course: Course) -> str:
    """
    Transform course object to LLM-optimized text format.

    This is the context engineering technique from Section 2 Notebook 2.
    Converts structured course data into natural text format that's easier
    for LLMs to process.

    Args:
        course: Course object to transform

    Returns:
        LLM-friendly text representation
    """
    # Build prerequisites text
    prereq_text = ""
    if course.prerequisites:
        prereq_codes = [p.course_code for p in course.prerequisites]
        prereq_text = f"\nPrerequisites: {', '.join(prereq_codes)}"

    # Build learning objectives text
    objectives_text = ""
    if course.learning_objectives:
        objectives_text = f"\nLearning Objectives:\n" + "\n".join(
            f"  - {obj}" for obj in course.learning_objectives
        )

    # Build course text
    course_text = f"""{course.course_code}: {course.title}
Department: {course.department}
Credits: {course.credits}
Level: {course.difficulty_level.value}
Format: {course.format.value}
Instructor: {course.instructor}{prereq_text}
Description: {course.description}{objectives_text}"""

    return course_text


def optimize_course_text(course: Course) -> str:
    """
    Create ultra-compact course description.

    This is the optimization technique from Section 2 Notebook 2.
    Reduces token count while preserving essential information.

    Args:
        course: Course object to optimize

    Returns:
        Compact text representation
    """
    prereqs = (
        f" (Prereq: {', '.join([p.course_code for p in course.prerequisites])})"
        if course.prerequisites
        else ""
    )
    return (
        f"{course.course_code}: {course.title} - {course.description[:100]}...{prereqs}"
    )


def search_courses_sync(
    query: str,
    top_k: int = 5,
    use_optimized_format: bool = False,
    intent: str = "GENERAL",
) -> str:
    """
    Search for relevant courses using HIERARCHICAL RETRIEVAL (synchronous version).

    Stage 3: Progressive disclosure with two-tier retrieval!

    Strategy (based on intent):
    - "GREETING": No search needed
    - "GENERAL": Return ONLY summaries for ALL matches (~300 tokens)
    - "SYLLABUS_OBJECTIVES": Summaries + full details with syllabus & learning objectives
    - "ASSIGNMENTS": Summaries + full details with assignments
    - "PREREQUISITES": Summaries + full details with prerequisites

    This provides:
    - Broad awareness of all options (summaries)
    - Deep understanding with targeted information based on what user asked for
    - Adaptive context based on query intent

    Args:
        query: Search query
        top_k: Number of summaries to return
        use_optimized_format: Ignored (always uses hierarchical format)
        intent: Intent category (GREETING, GENERAL, SYLLABUS_OBJECTIVES, ASSIGNMENTS, PREREQUISITES)

    Returns:
        Hierarchically formatted search results
    """
    if not course_manager:
        return "Course search not available - CourseManager not initialized"

    try:
        # Use asyncio to run the async search in a sync context
        import asyncio

        import nest_asyncio

        # Allow nested event loops (needed when LangGraph is already running async)
        nest_asyncio.apply()

        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # TIER 1: Search for courses using semantic search (basic courses)
        basic_results = loop.run_until_complete(
            course_manager.search_courses(
                query=query, filters=None, limit=top_k, similarity_threshold=0.5
            )
        )

        if not basic_results:
            return "No relevant courses found"

        # TIER 2: Match to hierarchical courses and extract summaries + details
        summaries = []
        all_details = []

        for basic_course in basic_results:
            # Find matching hierarchical course
            for h_course in hierarchical_courses:
                if h_course.summary.course_code == basic_course.course_code:
                    summaries.append(h_course.summary)
                    all_details.append(h_course.details)
                    break
            else:
                # Fallback: create summary from basic course
                logger.warning(
                    f"No hierarchical data for {basic_course.course_code}, using basic data"
                )
                summary = CourseSummary(
                    course_code=basic_course.course_code,
                    title=basic_course.title,
                    department=basic_course.department,
                    credits=basic_course.credits,
                    difficulty_level=basic_course.difficulty_level,
                    format=basic_course.format,
                    instructor=basic_course.instructor,
                    short_description=basic_course.description[:200],
                    prerequisite_codes=[
                        p.course_code for p in basic_course.prerequisites
                    ]
                    if basic_course.prerequisites
                    else [],
                    tags=[],
                )
                summaries.append(summary)

        # PROGRESSIVE DISCLOSURE: Adapt based on intent
        if intent == "GENERAL":
            # SUMMARY ONLY: Just return summaries, no details
            hierarchical_context = context_assembler.assemble_summary_only_context(
                summaries=summaries, query=query
            )
            token_estimate = len(hierarchical_context) // 4
            logger.info(f"📊 Summary-only context: ~{token_estimate} tokens")
            logger.info(f"   - Summaries for {len(summaries)} courses")
            logger.info("✅ Summary mode: overview only")
        else:
            # DETAILED: Return summaries for ALL, details for top 2-3
            # Intent determines what details are included (syllabus, assignments, prerequisites)
            detail_limit = min(3, len(all_details))
            top_details = all_details[:detail_limit]

            hierarchical_context = context_assembler.assemble_hierarchical_context(
                summaries=summaries, details=top_details, query=query
            )
            token_estimate = len(hierarchical_context) // 4
            logger.info(f"📊 Hierarchical context: ~{token_estimate} tokens")
            logger.info(f"   - Summaries for {len(summaries)} courses")
            logger.info(
                f"   - Full details for top {len(top_details)} courses (intent: {intent})"
            )
            logger.info(
                "✅ Progressive disclosure: targeted information based on intent!"
            )

        return hierarchical_context

    except Exception as e:
        logger.error(f"Course search failed: {e}")
        import traceback

        traceback.print_exc()
        return f"Search failed: {str(e)}"


async def search_courses(
    query: str, top_k: int = 5, use_optimized_format: bool = False
) -> str:
    """
    Search for relevant courses using HIERARCHICAL RETRIEVAL (async version).

    Stage 3: Progressive disclosure with two-tier retrieval!

    See search_courses_sync() for full documentation.

    Args:
        query: Search query
        top_k: Number of summaries to return
        use_optimized_format: Ignored (always uses hierarchical format)

    Returns:
        Hierarchically formatted search results
    """
    if not course_manager:
        return "Course search not available - CourseManager not initialized"

    try:
        # TIER 1: Search for courses using semantic search
        basic_results = await course_manager.search_courses(
            query=query, filters=None, limit=top_k, similarity_threshold=0.5
        )

        if not basic_results:
            return "No relevant courses found"

        # TIER 2: Match to hierarchical courses
        summaries = []
        all_details = []

        for basic_course in basic_results:
            for h_course in hierarchical_courses:
                if h_course.summary.course_code == basic_course.course_code:
                    summaries.append(h_course.summary)
                    all_details.append(h_course.details)
                    break
            else:
                # Fallback: create summary from basic course
                logger.warning(f"No hierarchical data for {basic_course.course_code}")
                summary = CourseSummary(
                    course_code=basic_course.course_code,
                    title=basic_course.title,
                    department=basic_course.department,
                    credits=basic_course.credits,
                    difficulty_level=basic_course.difficulty_level,
                    format=basic_course.format,
                    instructor=basic_course.instructor,
                    short_description=basic_course.description[:200],
                    prerequisite_codes=[
                        p.course_code for p in basic_course.prerequisites
                    ]
                    if basic_course.prerequisites
                    else [],
                    tags=[],
                )
                summaries.append(summary)

        # PROGRESSIVE DISCLOSURE: Summaries for ALL, details for top 2-3
        detail_limit = min(3, len(all_details))
        top_details = all_details[:detail_limit]

        # Assemble hierarchical context
        hierarchical_context = context_assembler.assemble_hierarchical_context(
            summaries=summaries, details=top_details, query=query
        )

        # Log token efficiency
        token_estimate = len(hierarchical_context) // 4
        logger.info(f"📊 Hierarchical context: ~{token_estimate} tokens")
        logger.info(f"   - Summaries for {len(summaries)} courses")
        logger.info(
            f"   - Full details (with syllabi) for top {len(top_details)} courses"
        )

        return hierarchical_context

    except Exception as e:
        logger.error(f"Course search failed: {e}")
        return f"Search failed: {str(e)}"


# ============================================================================
# NEW: LangChain Tool for Agentic Workflow
# ============================================================================


class SearchCoursesInput(BaseModel):
    """Input schema for search_courses tool."""

    query: str = Field(description="The search query for finding courses")
    intent: str = Field(
        default="GENERAL",
        description="Intent category: GENERAL (summaries only), PREREQUISITES (prerequisite details), SYLLABUS_OBJECTIVES (syllabus and learning objectives), ASSIGNMENTS (assignment details)",
    )
    search_strategy: str = Field(
        default="semantic_only",
        description="Search strategy: exact_match (for course codes), hybrid (exact + semantic + filters), semantic_only (traditional vector search)",
    )
    course_codes: List[str] = Field(
        default_factory=list,
        description="Specific course codes to search for (e.g., ['CS004', 'MATH301'])",
    )
    information_type: List[str] = Field(
        default_factory=list,
        description="Types of information needed: prerequisites, syllabus, assignments, objectives, description",
    )
    departments: List[str] = Field(
        default_factory=list,
        description="Filter by departments (e.g., ['Computer Science', 'Mathematics'])",
    )
    difficulty_level: Optional[str] = Field(
        default=None,
        description="Filter by difficulty: beginner, intermediate, advanced",
    )


@tool("search_courses", args_schema=SearchCoursesInput)
async def search_courses_tool(
    query: str,
    intent: str = "GENERAL",
    search_strategy: str = "semantic_only",
    course_codes: List[str] = [],
    information_type: List[str] = [],
    departments: List[str] = [],
    difficulty_level: Optional[str] = None,
) -> str:
    """
    Search for courses with flexible parameters controlled by the LLM.

    This tool replaces the scripted research_node, allowing the LLM to decide:
    - WHEN to search (instead of always searching)
    - WHAT intent to use (GENERAL, PREREQUISITES, SYLLABUS_OBJECTIVES, ASSIGNMENTS)

    Stage 3 uses simple hierarchical retrieval (semantic search only).
    The search_strategy, course_codes, and other advanced parameters are accepted
    but not used - Stage 3 always uses semantic search with hierarchical disclosure.

    Use this tool when you need to find course information to answer the user's question.

    Args:
        query: The search query
        intent: What type of information to return (GENERAL, PREREQUISITES, SYLLABUS_OBJECTIVES, ASSIGNMENTS)
        search_strategy: Ignored in Stage 3 (always uses semantic search)
        course_codes: Ignored in Stage 3 (query is used directly)
        information_type: Ignored in Stage 3 (intent determines what's included)
        departments: Ignored in Stage 3
        difficulty_level: Ignored in Stage 3

    Returns:
        Formatted course information based on intent using hierarchical retrieval
    """
    if not course_manager:
        return "Course search not available - CourseManager not initialized"

    logger.info(f"🔧 Tool called: search_courses")
    logger.info(f"   Query: {query}")
    logger.info(f"   Intent: {intent}")
    logger.info(f"   (Stage 3: Using simple hierarchical retrieval)")

    # Call the existing search_courses_sync function (Stage 3 version)
    # This only takes: query, top_k, use_optimized_format, intent
    try:
        result = search_courses_sync(
            query=query,
            top_k=5,
            use_optimized_format=False,
            intent=intent,
        )
        logger.info(f"   ✅ Search completed: {len(result)} chars returned")
        return result
    except Exception as e:
        logger.error(f"   ❌ Search failed: {e}")
        return f"Search failed: {str(e)}"
