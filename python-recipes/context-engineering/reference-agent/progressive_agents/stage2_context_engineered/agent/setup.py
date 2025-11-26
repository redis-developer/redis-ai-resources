"""
Setup and initialization for Stage 2 Context-Engineered Agent.

Handles:
- Course data loading
- Agent initialization
- Cleanup
"""

import logging
from typing import Optional

from redis_context_course import CourseManager
from redis_context_course.scripts.generate_courses import CourseGenerator
from redis_context_course.scripts.ingest_courses import CourseIngestionPipeline

logger = logging.getLogger("stage2-engineered")


async def load_courses_if_needed(
    course_manager: CourseManager, force_reload: bool = False
) -> int:
    """
    Load sample courses into Redis if not already present.

    Args:
        course_manager: CourseManager instance
        force_reload: If True, regenerate courses even if they exist

    Returns:
        Number of courses loaded
    """
    # Check if courses already exist
    existing_courses = await course_manager.get_all_courses()

    if existing_courses and not force_reload:
        logger.info(f"📚 Found {len(existing_courses)} existing courses in Redis")
        return len(existing_courses)

    logger.info("📚 Generating sample courses...")

    # Generate sample courses
    generator = CourseGenerator()
    courses = generator.generate_courses(courses_per_major=10)

    # Convert to format expected by ingestion pipeline
    courses_data = [course.model_dump(mode="json") for course in courses]

    logger.info(f"📥 Ingesting {len(courses_data)} courses into Redis...")

    # Ingest into Redis
    ingestion = CourseIngestionPipeline()

    # Clear existing data if force reload
    if force_reload:
        ingestion.clear_existing_data()

    ingested_count = await ingestion.ingest_courses(courses_data)

    logger.info(f"✅ Successfully loaded {ingested_count} courses")

    return ingested_count


async def cleanup_courses(course_manager: CourseManager):
    """
    Remove all courses from Redis.

    Args:
        course_manager: CourseManager instance
    """
    logger.info("🧹 Cleaning up courses from Redis...")

    # Get all courses
    courses = await course_manager.get_all_courses()

    if not courses:
        logger.info("No courses to clean up")
        return

    # Delete each course
    for course in courses:
        await course_manager.delete_course(course.course_code)

    logger.info(f"✅ Removed {len(courses)} courses from Redis")


def setup_agent(
    course_manager: Optional[CourseManager] = None, auto_load_courses: bool = True
) -> tuple:
    """
    Initialize the Stage 2 Context-Engineered Agent.

    Args:
        course_manager: Optional CourseManager instance (creates new if None)
        auto_load_courses: If True, automatically load courses if Redis is empty

    Returns:
        Tuple of (workflow, course_manager)
    """
    from .nodes import initialize_nodes
    from .workflow import create_workflow

    logger.info("🚀 Initializing Stage 2 Context-Engineered Agent...")

    # Create course manager if not provided
    if course_manager is None:
        course_manager = CourseManager()

    # Auto-load courses if needed
    if auto_load_courses:
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        courses_loaded = loop.run_until_complete(load_courses_if_needed(course_manager))
        logger.info(f"✅ {courses_loaded} courses available")

    # Initialize nodes with course manager
    initialize_nodes(course_manager)

    # Create workflow
    workflow = create_workflow()

    logger.info("✅ Stage 2 Context-Engineered Agent initialized")
    logger.info("✨ This agent uses Section 2 context engineering techniques!")

    return workflow, course_manager
