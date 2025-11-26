"""
Test exact match search to debug the CS002 issue.
"""

import asyncio
import logging
from redis_context_course import CourseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_exact_search():
    """Test exact course code search."""
    course_manager = CourseManager()
    
    # Test searching for CS002
    print("\n" + "=" * 80)
    print("Testing exact search for CS002")
    print("=" * 80)
    
    results = await course_manager.search_courses(
        query="CS002",
        filters=None,
        limit=5,
        similarity_threshold=0.0,  # Get all results to see what's happening
    )
    
    print(f"\nFound {len(results)} results:")
    for i, course in enumerate(results, 1):
        print(f"{i}. {course.course_code}: {course.title}")
        print(f"   Department: {course.department}")
        print(f"   Description: {course.description[:100]}...")
        print()
    
    # Test searching for CS004
    print("\n" + "=" * 80)
    print("Testing exact search for CS004")
    print("=" * 80)
    
    results = await course_manager.search_courses(
        query="CS004",
        filters=None,
        limit=5,
        similarity_threshold=0.0,
    )
    
    print(f"\nFound {len(results)} results:")
    for i, course in enumerate(results, 1):
        print(f"{i}. {course.course_code}: {course.title}")
        print(f"   Department: {course.department}")
        print(f"   Description: {course.description[:100]}...")
        print()
    
    # Get all courses to see what's available
    print("\n" + "=" * 80)
    print("Getting all CS courses")
    print("=" * 80)
    
    all_courses = await course_manager.get_all_courses()
    cs_courses = [c for c in all_courses if c.course_code.startswith("CS")]
    cs_courses.sort(key=lambda x: x.course_code)
    
    print(f"\nFound {len(cs_courses)} CS courses:")
    for course in cs_courses:
        print(f"  {course.course_code}: {course.title}")
    
    # Try get_course_by_code
    print("\n" + "=" * 80)
    print("Testing get_course_by_code for CS002")
    print("=" * 80)
    
    course = await course_manager.get_course_by_code("CS002")
    if course:
        print(f"Found: {course.course_code}: {course.title}")
        print(f"Description: {course.description}")
    else:
        print("Course not found!")


if __name__ == "__main__":
    asyncio.run(test_exact_search())

