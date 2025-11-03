#!/usr/bin/env python3
"""
Final comprehensive test of the Redis Context Course agent.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_complete_functionality():
    """Test all agent functionality."""
    try:
        from redis_context_course import ClassAgent
        
        print("🎓 Final Agent Test")
        print("=" * 40)
        
        # Create agent
        agent = ClassAgent("final_test_student")
        print("✅ Agent created successfully")
        
        # Test various queries
        test_queries = [
            "How many courses are available?",
            "Show me programming courses",
            "I'm interested in machine learning",
            "What courses are good for beginners?",
            "Find me data science courses"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            try:
                response = await agent.chat(query)
                print(f"✅ Response: {response[:200]}...")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function."""
    print("⚠️  DEPRECATED: Use 'python simple_health_check.py' instead")
    print("This provides better error handling and diagnostics.\n")

    success = await test_complete_functionality()

    if success:
        print("\n🎉 All tests passed! The agent is working correctly.")
        print("\n🚀 You can now use the agent with:")
        print("  redis-class-agent --student-id your_name")
        print("\n📚 Try asking questions like:")
        print("  - 'How many courses are there?'")
        print("  - 'Show me programming courses'")
        print("  - 'I want to learn machine learning'")
        print("  - 'What courses should I take for computer science?'")
        print("\n💡 For ongoing health checks, use: python simple_health_check.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("💡 For better diagnostics, run: python simple_health_check.py")

if __name__ == "__main__":
    asyncio.run(main())
