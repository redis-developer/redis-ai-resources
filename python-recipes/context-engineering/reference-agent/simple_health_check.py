#!/usr/bin/env python3
"""
Simple Redis Context Course System Health Check

Quick validation of core system functionality.
"""

import asyncio
import os
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_redis():
    """Test Redis connection."""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping()
        return True
    except:
        return False


def count_courses():
    """Count course records in Redis."""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url, decode_responses=True)
        course_keys = r.keys("course_catalog:*")
        return len(course_keys)
    except:
        return 0


def count_majors():
    """Count major records in Redis."""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url, decode_responses=True)
        major_keys = r.keys("major:*")
        return len(major_keys)
    except:
        return 0


async def test_course_search():
    """Test course search functionality."""
    try:
        from redis_context_course.course_manager import CourseManager
        course_manager = CourseManager()
        courses = await course_manager.search_courses("programming", limit=1)
        return len(courses) > 0
    except:
        return False


async def test_agent():
    """Test basic agent functionality."""
    try:
        from redis_context_course import ClassAgent
        agent = ClassAgent("test_student")
        response = await agent.chat("How many courses are available?")
        return response and len(response) > 10
    except:
        return False


def check_env_vars():
    """Check required environment variables."""
    required_vars = ['OPENAI_API_KEY', 'REDIS_URL', 'AGENT_MEMORY_URL']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == 'your_openai_api_key_here':
            missing.append(var)
    
    return missing


async def main():
    """Run all health checks."""
    print("""Redis Context Course - Health Check
=====================================""")
    
    # Environment check
    missing_vars = check_env_vars()
    if missing_vars:
        print(f"❌ Environment: Missing {', '.join(missing_vars)}")
        print("   Fix: Update .env file with correct values")
        return False
    else:
        print("✅ Environment: All variables set")
    
    # Redis check
    if test_redis():
        print("✅ Redis: Connected")
    else:
        print("❌ Redis: Connection failed")
        print("   Fix: Start Redis with 'docker run -d -p 6379:6379 redis:8-alpine'")
        return False
    
    # Data checks
    course_count = count_courses()
    major_count = count_majors()
    
    if course_count > 0:
        print(f"✅ Courses: {course_count} found")
    else:
        print("❌ Courses: None found")
        print("   Fix: Run 'ingest-courses --catalog course_catalog.json --clear'")
        return False
    
    if major_count > 0:
        print(f"✅ Majors: {major_count} found")
    else:
        print("❌ Majors: None found")
        print("   Fix: Run 'ingest-courses --catalog course_catalog.json --clear'")
    
    # Functionality checks
    if await test_course_search():
        print("✅ Course Search: Working")
    else:
        print("❌ Course Search: Failed")
        print("   Fix: Check if courses have embeddings")
        return False
    
    if await test_agent():
        print("✅ Agent: Working")
    else:
        print("❌ Agent: Failed")
        print("   Fix: Check OpenAI API key and course data")
        return False
    
    # Success
    print("""
🎯 Status: READY
📊 All checks passed!

🚀 Try: redis-class-agent --student-id your_name""")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nHealth check interrupted")
        exit(1)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        exit(1)
