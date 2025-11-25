"""
Setup and initialization for the Course Q&A Agent.

Initializes CourseManager, Redis, and other dependencies.
Semantic cache initialization is commented out for now.
"""

import os
import logging
import json
import asyncio
from pathlib import Path
from typing import Optional

from redis_context_course import CourseManager
from redis_context_course.scripts.generate_courses import CourseGenerator
from redis_context_course.scripts.ingest_courses import CourseIngestionPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("course-qa-setup")


async def load_courses_if_needed(course_manager: CourseManager, force_reload: bool = False) -> int:
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
        logger.info("📦 No courses found in Redis. Generating and loading sample courses...")
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
            "courses": [course.model_dump(mode='json') for course in courses]
        }

        with open(temp_catalog_path, 'w') as f:
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
        courses_data = catalog_data.get('courses', [])

        ingested_count = await ingestion.ingest_courses(courses_data)

        logger.info(f"✅ Loaded {ingested_count} courses into Redis")

        # Clean up temp file
        temp_catalog_path.unlink()

        return ingested_count

    except Exception as e:
        logger.error(f"Failed to load courses: {e}")
        raise


async def initialize_course_manager(redis_url: Optional[str] = None, auto_load: bool = True) -> CourseManager:
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


# NOTE: Semantic cache initialization is COMMENTED OUT for now
# Will be added in future stages
#
# ORIGINAL IMPLEMENTATION (from caching-agent):
# """
# from redisvl.extensions.llmcache import SemanticCache
# 
# def initialize_semantic_cache(
#     redis_url: str = "redis://localhost:6379",
#     cache_name: str = "course-qa-cache",
#     distance_threshold: float = 0.3,
#     ttl: int = 3600
# ) -> SemanticCache:
#     '''
#     Initialize semantic cache for caching course Q&A responses.
#     
#     Args:
#         redis_url: Redis connection URL
#         cache_name: Name for the cache instance
#         distance_threshold: Similarity threshold (0.0-1.0, lower = stricter)
#         ttl: Time-to-live for cache entries in seconds
#         
#     Returns:
#         Initialized SemanticCache instance
#     '''
#     logger.info(f"Initializing semantic cache: {cache_name}")
#     
#     try:
#         cache = SemanticCache(
#             name=cache_name,
#             redis_url=redis_url,
#             distance_threshold=distance_threshold,
#             ttl=ttl
#         )
#         
#         logger.info(f"✅ Semantic cache initialized: {cache_name}")
#         return cache
#         
#     except Exception as e:
#         logger.error(f"Failed to initialize semantic cache: {e}")
#         raise
# """


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


async def setup_agent(auto_load_courses: bool = True):
    """
    Complete setup for the Course Q&A Agent.

    Args:
        auto_load_courses: If True, automatically load courses if they don't exist

    Returns:
        Tuple of (course_manager, semantic_cache)
        Note: semantic_cache is None for now
    """
    logger.info("=" * 80)
    logger.info("Setting up Course Q&A Agent")
    logger.info("=" * 80)

    # Initialize CourseManager (will auto-load courses if needed)
    course_manager = await initialize_course_manager(auto_load=auto_load_courses)

    # NOTE: Semantic cache initialization commented out
    # semantic_cache = initialize_semantic_cache()
    semantic_cache = None

    logger.info("=" * 80)
    logger.info("✅ Course Q&A Agent setup complete")
    logger.info("=" * 80)

    return course_manager, semantic_cache

