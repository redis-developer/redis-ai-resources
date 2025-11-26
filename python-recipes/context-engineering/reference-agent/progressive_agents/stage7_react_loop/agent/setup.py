"""
Setup and initialization for the Memory-Augmented Course Q&A Agent.

Initializes CourseManager, Redis, Agent Memory Server client, and other dependencies.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional, Tuple

from agent_memory_client import MemoryAPIClient, MemoryClientConfig

from redis_context_course import CourseManager
from redis_context_course.scripts.generate_courses import CourseGenerator
from redis_context_course.scripts.ingest_courses import CourseIngestionPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("course-qa-setup")


def initialize_memory_client(
    base_url: Optional[str] = None, namespace: str = "course_qa_agent"
) -> MemoryAPIClient:
    """
    Initialize Agent Memory Server client.

    Args:
        base_url: Agent Memory Server URL (defaults to env var AGENT_MEMORY_URL)
        namespace: Namespace for memory storage

    Returns:
        Initialized MemoryAPIClient instance
    """
    if base_url is None:
        base_url = os.getenv("AGENT_MEMORY_URL", "http://localhost:8088")

    logger.info(f"Initializing Agent Memory Server client: {base_url}")

    try:
        config = MemoryClientConfig(
            base_url=base_url,
            default_namespace=namespace,
        )
        memory_client = MemoryAPIClient(config=config)

        logger.info(f"✅ Agent Memory Server client initialized")
        return memory_client

    except Exception as e:
        logger.error(f"Failed to initialize memory client: {e}")
        raise


async def load_courses_if_needed(
    course_manager: CourseManager, force_reload: bool = False
) -> int:
    """
    Load courses into Redis if they don't exist or if force_reload is True.

    Args:
        course_manager: CourseManager instance
        force_reload: If True, clear existing courses and reload

    Returns:
        Number of courses loaded
    """
    # Check if courses already exist
    existing_courses = await course_manager.get_all_courses()

    # If courses exist and we're not forcing reload, just return the count
    if existing_courses and not force_reload:
        logger.info(f"📚 Found {len(existing_courses)} existing courses in Redis")
        return len(existing_courses)

    # If we get here, either no courses exist OR force_reload is True
    if not existing_courses:
        logger.info(
            "📦 No courses found in Redis. Generating and loading sample courses..."
        )
    else:
        logger.info("🔄 Force reload requested. Regenerating courses...")

    try:
        # Generate sample courses
        generator = CourseGenerator()
        courses = generator.generate_courses(courses_per_major=10)

        logger.info(f"✅ Generated {len(courses)} sample courses")

        # Save to temporary JSON file
        temp_catalog_path = Path("/tmp/course_catalog_temp.json")
        catalog_data = {
            "majors": [],  # We don't need majors for basic functionality
            "courses": [course.model_dump(mode="json") for course in courses],
        }

        with open(temp_catalog_path, "w") as f:
            json.dump(catalog_data, f, indent=2, default=str)

        logger.info(f"💾 Saved catalog to {temp_catalog_path}")

        # Ingest courses into Redis
        ingestion = CourseIngestionPipeline()

        # Clear existing data if force_reload (or if empty, to be safe)
        if force_reload or not existing_courses:
            logger.info("🧹 Clearing existing course data...")
            ingestion.clear_existing_data()

        # Load and ingest courses
        catalog_data = ingestion.load_catalog_from_json(str(temp_catalog_path))
        courses_data = catalog_data.get("courses", [])

        ingested_count = await ingestion.ingest_courses(courses_data)

        logger.info(f"✅ Loaded {ingested_count} courses into Redis")

        # Clean up temp file
        temp_catalog_path.unlink()

        return ingested_count

    except Exception as e:
        logger.error(f"Failed to load courses: {e}")
        raise


async def initialize_course_manager(
    redis_url: Optional[str] = None, auto_load: bool = True
) -> CourseManager:
    """
    Initialize the CourseManager for course search.

    Args:
        redis_url: Redis connection URL (defaults to env var REDIS_URL)
        auto_load: If True, automatically load courses if they don't exist

    Returns:
        Initialized CourseManager instance
    """
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    logger.info(f"Initializing CourseManager with Redis URL: {redis_url}")

    try:
        # Create CourseManager instance
        course_manager = CourseManager()

        # Load courses if needed
        if auto_load:
            course_count = await load_courses_if_needed(course_manager)
            logger.info(f"✅ CourseManager initialized with {course_count} courses")
        else:
            # Just verify connection
            all_courses = await course_manager.get_all_courses()
            logger.info(f"✅ CourseManager initialized with {len(all_courses)} courses")

        return course_manager

    except Exception as e:
        logger.error(f"Failed to initialize CourseManager: {e}")
        raise


async def cleanup_courses(course_manager: CourseManager):
    """
    Clean up courses from Redis.

    Args:
        course_manager: CourseManager instance
    """
    logger.info("🧹 Cleaning up courses from Redis...")

    try:
        ingestion = CourseIngestionPipeline()
        ingestion.clear_existing_data()
        logger.info("✅ Courses cleaned up successfully")
    except Exception as e:
        logger.error(f"Failed to cleanup courses: {e}")


async def setup_agent(
    auto_load_courses: bool = True,
) -> Tuple[CourseManager, MemoryAPIClient]:
    """
    Complete setup for the Memory-Augmented Course Q&A Agent.

    Args:
        auto_load_courses: If True, automatically load courses if they don't exist

    Returns:
        Tuple of (course_manager, memory_client)
    """
    logger.info("=" * 80)
    logger.info("Setting up Memory-Augmented Course Q&A Agent")
    logger.info("=" * 80)

    # Initialize CourseManager (will auto-load courses if needed)
    course_manager = await initialize_course_manager(auto_load=auto_load_courses)

    # Initialize Agent Memory Server client
    memory_client = initialize_memory_client()

    logger.info("=" * 80)
    logger.info("✅ Memory-Augmented Course Q&A Agent setup complete")
    logger.info("=" * 80)

    return course_manager, memory_client
