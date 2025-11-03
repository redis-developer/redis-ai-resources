#!/usr/bin/env python3
"""
Test script for the new user knowledge summary tool.

This script tests the _summarize_user_knowledge_tool to ensure it works correctly
and provides meaningful summaries of user information.
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from redis_context_course.agent import ClassAgent
from agent_memory_client import MemoryAPIClient, MemoryClientConfig
from agent_memory_client.models import ClientMemoryRecord


async def setup_test_data(memory_client: MemoryAPIClient, user_id: str) -> None:
    """Set up test data for the user knowledge summary tool."""
    print("Setting up test data...")
    
    # Create sample memories for testing
    test_memories = [
        ClientMemoryRecord(
            text="Student prefers online courses over in-person classes",
            user_id=user_id,
            memory_type="semantic",
            topics=["preferences", "learning_style"]
        ),
        ClientMemoryRecord(
            text="Student expressed interest in machine learning and data science",
            user_id=user_id,
            memory_type="semantic",
            topics=["interests", "subjects"]
        ),
        ClientMemoryRecord(
            text="Student's goal is to become a data scientist within 2 years",
            user_id=user_id,
            memory_type="semantic",
            topics=["goals", "career"]
        ),
        ClientMemoryRecord(
            text="Student has completed CS101 and MATH201 courses",
            user_id=user_id,
            memory_type="semantic",
            topics=["academic_history", "courses"]
        ),
        ClientMemoryRecord(
            text="Student likes to study in the morning and prefers visual learning materials",
            user_id=user_id,
            memory_type="semantic",
            topics=["preferences", "study_habits"]
        ),
        ClientMemoryRecord(
            text="Student is interested in Python programming and statistical analysis",
            user_id=user_id,
            memory_type="semantic",
            topics=["interests", "programming"]
        ),
        ClientMemoryRecord(
            text="Student wants to take advanced machine learning courses next semester",
            user_id=user_id,
            memory_type="semantic",
            topics=["goals", "courses"]
        ),
        ClientMemoryRecord(
            text="Student prefers courses with practical projects over theoretical ones",
            user_id=user_id,
            memory_type="semantic",
            topics=["preferences", "learning_style"]
        )
    ]
    
    # Store the test memories
    await memory_client.create_long_term_memory(test_memories)
    print(f"Created {len(test_memories)} test memories for user {user_id}")


async def test_user_knowledge_tool():
    """Test the user knowledge summary tool."""
    print("Starting user knowledge tool test...")
    
    # Test configuration
    test_user_id = "test_user_knowledge_123"
    test_session_id = "test_session_knowledge_456"
    
    try:
        # Initialize the agent
        print("Initializing ClassAgent...")
        agent = ClassAgent(student_id=test_user_id, session_id=test_session_id)
        
        # Set up test data
        await setup_test_data(agent.memory_client, test_user_id)
        
        # Test the tool directly
        print("\n" + "="*60)
        print("TESTING USER KNOWLEDGE SUMMARY TOOL")
        print("="*60)
        
        # Call the summarize user knowledge tool
        summary = await agent._summarize_user_knowledge_tool()
        
        print("\nUser Knowledge Summary:")
        print("-" * 40)
        print(summary)
        print("-" * 40)
        
        # Test through the chat interface
        print("\n" + "="*60)
        print("TESTING THROUGH CHAT INTERFACE")
        print("="*60)
        
        test_queries = [
            "What do you know about me?",
            "Tell me about my profile",
            "What are my interests and preferences?",
            "What do you remember about me?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            print("-" * 40)
            response = await agent.chat(query)
            print(f"Response: {response}")
            print("-" * 40)
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def cleanup_test_data(user_id: str):
    """Clean up test data after testing."""
    print(f"\nCleaning up test data for user {user_id}...")
    
    try:
        # Initialize memory client
        config = MemoryClientConfig(
            base_url=os.getenv("AGENT_MEMORY_URL", "http://localhost:8088"),
            default_namespace="redis_university"
        )
        memory_client = MemoryAPIClient(config=config)
        
        # Search for test memories and delete them
        from agent_memory_client.filters import UserId
        results = await memory_client.search_long_term_memory(
            text="",
            user_id=UserId(eq=user_id),
            limit=100
        )
        
        if results.memories:
            print(f"Found {len(results.memories)} memories to clean up")
            # Note: The actual deletion would depend on the memory client API
            # For now, we'll just report what we found
        else:
            print("No memories found to clean up")
            
    except Exception as e:
        print(f"Warning: Could not clean up test data: {e}")


def main():
    """Main function to run the test."""
    print("User Knowledge Summary Tool Test")
    print("=" * 50)
    
    # Check if required environment variables are set
    required_env_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running the test.")
        return 1
    
    # Check if the memory server is running
    memory_url = os.getenv("AGENT_MEMORY_URL", "http://localhost:8088")
    print(f"Using memory server at: {memory_url}")
    print("Make sure the Redis Agent Memory Server is running!")
    print("You can start it with: docker-compose up")
    print()
    
    # Run the test
    try:
        success = asyncio.run(test_user_knowledge_tool())
        if success:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print("\n💥 Some tests failed!")
            return 1
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test failed with unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
