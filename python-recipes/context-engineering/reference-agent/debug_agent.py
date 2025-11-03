#!/usr/bin/env python3
"""
Debug the agent tools directly.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def debug_tools():
    """Debug the agent tools directly."""
    try:
        from redis_context_course import ClassAgent
        
        print("🔧 Testing agent tools directly...")
        
        # Create agent
        agent = ClassAgent("debug_student")
        
        # Test the search tool directly
        print("\n📚 Testing _search_courses_tool directly...")
        result = await agent._search_courses_tool.invoke({"query": "programming"})
        print(f"Result: {result}")

        # Test with a simple query
        print("\n🔍 Testing with empty query...")
        result = await agent._search_courses_tool.invoke({"query": ""})
        print(f"Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function."""
    print("🔧 Agent Tools Debug")
    print("=" * 30)
    print("⚠️  DEPRECATED: Use 'python simple_health_check.py' instead")
    print("This script provides better diagnostics and error handling.")
    print("=" * 30)

    success = await debug_tools()

    if success:
        print("\n✅ Debug completed!")
        print("💡 For comprehensive system check, run: python simple_health_check.py")
    else:
        print("\n❌ Debug failed!")
        print("💡 For better error diagnostics, run: python simple_health_check.py")

if __name__ == "__main__":
    asyncio.run(main())
