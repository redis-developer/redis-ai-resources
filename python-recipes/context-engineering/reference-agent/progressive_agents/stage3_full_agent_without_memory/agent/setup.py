"""
Setup and initialization for the Course Q&A Agent.

Initializes CourseManager, Redis, and other dependencies.
Semantic cache initialization is commented out for now.
"""

import os
import logging
from typing import Optional

from redis_context_course import CourseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("course-qa-setup")


async def initialize_course_manager(redis_url: Optional[str] = None) -> CourseManager:
    """
    Initialize the CourseManager for course search.
    
    Args:
        redis_url: Redis connection URL (defaults to env var REDIS_URL)
        
    Returns:
        Initialized CourseManager instance
    """
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    logger.info(f"Initializing CourseManager with Redis URL: {redis_url}")
    
    try:
        # Create CourseManager instance
        course_manager = CourseManager()
        
        # Verify connection by getting course count
        all_courses = await course_manager.get_all_courses()
        logger.info(f"✅ CourseManager initialized successfully with {len(all_courses)} courses")
        
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


async def setup_agent():
    """
    Complete setup for the Course Q&A Agent.
    
    Returns:
        Tuple of (course_manager, semantic_cache)
        Note: semantic_cache is None for now
    """
    logger.info("=" * 80)
    logger.info("Setting up Course Q&A Agent")
    logger.info("=" * 80)
    
    # Initialize CourseManager
    course_manager = await initialize_course_manager()
    
    # NOTE: Semantic cache initialization commented out
    # semantic_cache = initialize_semantic_cache()
    semantic_cache = None
    
    logger.info("=" * 80)
    logger.info("✅ Course Q&A Agent setup complete")
    logger.info("=" * 80)
    
    return course_manager, semantic_cache

