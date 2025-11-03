#!/usr/bin/env python3
"""
Quick script to verify course data is properly ingested in Redis.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_courses():
    """Check if courses are properly stored in Redis."""
    try:
        from redis_context_course.course_manager import CourseManager
        from redis_context_course.redis_config import redis_config

        print("🔍 Checking course data in Redis...")

        # Check Redis connection
        redis_client = redis_config.redis_client
        redis_client.ping()  # This is synchronous, not async
        print("✅ Redis connection successful")
        
        # Initialize course manager
        course_manager = CourseManager()
        
        # Try to search for courses
        print("\n📚 Searching for courses...")
        courses = await course_manager.search_courses("programming", limit=5)
        
        if courses:
            print(f"✅ Found {len(courses)} courses!")
            for i, course in enumerate(courses[:3], 1):
                print(f"  {i}. {course.course_code}: {course.title}")
        else:
            print("❌ No courses found. Course data may not be properly ingested.")
            
        # Check total course count
        print("\n🔢 Checking total course count...")
        try:
            # Try to get all courses by searching with a broad term
            all_courses = await course_manager.search_courses("", limit=100)
            print(f"✅ Total courses in database: {len(all_courses)}")
        except Exception as e:
            print(f"❌ Error getting course count: {e}")
            
        # Check majors
        print("\n🎓 Checking majors...")
        try:
            majors_key = "majors"
            majors_data = redis_client.get(majors_key)  # This is synchronous
            if majors_data:
                import json
                majors = json.loads(majors_data)
                print(f"✅ Found {len(majors)} majors:")
                for major in majors:
                    print(f"  - {major.get('name', 'Unknown')}")
            else:
                print("❌ No majors found in Redis")
        except Exception as e:
            print(f"❌ Error checking majors: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

async def main():
    """Main function."""
    print("🎓 Redis Context Course - Data Verification")
    print("=" * 50)
    print("⚠️  DEPRECATED: Use 'python simple_health_check.py' instead")
    print("This script provides more comprehensive validation.")
    print("=" * 50)

    success = await check_courses()

    if success:
        print("\n✅ Verification completed!")
        print("\nIf courses were found, your agent should work properly.")
        print("If no courses were found, run: ingest-courses --catalog course_catalog.json --clear")
        print("\n💡 For full system validation, run: python simple_health_check.py")
    else:
        print("\n❌ Verification failed!")
        print("Please check your Redis connection and course data.")
        print("💡 For detailed diagnostics, run: python simple_health_check.py")

if __name__ == "__main__":
    asyncio.run(main())
