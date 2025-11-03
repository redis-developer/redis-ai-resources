#!/usr/bin/env python3
"""
Test the agent functionality directly.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_agent():
    """Test the agent functionality."""
    try:
        from redis_context_course import ClassAgent
        from redis_context_course.course_manager import CourseManager
        
        print("🤖 Testing agent functionality...")
        
        # Test course manager first
        print("\n📚 Testing CourseManager...")
        course_manager = CourseManager()
        
        # Test search
        courses = await course_manager.search_courses("programming", limit=3)
        print(f"Found {len(courses)} programming courses:")
        for course in courses:
            print(f"  - {course.course_code}: {course.title}")
        
        # Test agent
        print("\n🤖 Testing ClassAgent...")
        agent = ClassAgent("test_student")
        
        # Test a simple query
        print("Asking: 'How many courses are available?'")
        response = await agent.chat("How many courses are available?")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function."""
    print("🎓 Agent Functionality Test")
    print("=" * 40)
    print("⚠️  DEPRECATED: Use 'python simple_health_check.py' instead")
    print("This script provides more comprehensive testing.")
    print("=" * 40)

    success = await test_agent()

    if success:
        print("\n✅ Agent test completed!")
        print("💡 For full system validation, run: python simple_health_check.py")
    else:
        print("\n❌ Agent test failed!")
        print("💡 For detailed diagnostics, run: python simple_health_check.py")

if __name__ == "__main__":
    asyncio.run(main())
