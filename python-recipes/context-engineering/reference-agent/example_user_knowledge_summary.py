#!/usr/bin/env python3
"""
Example demonstrating the new user knowledge summary tool.

This script shows how the _summarize_user_knowledge_tool works and provides
examples of the kind of output it generates.
"""

import asyncio
import os
from typing import List

# Mock classes to demonstrate the tool functionality
class MockMemory:
    def __init__(self, text: str, topics: List[str]):
        self.text = text
        self.topics = topics

class MockResults:
    def __init__(self, memories: List[MockMemory]):
        self.memories = memories

class MockMemoryClient:
    def __init__(self, memories: List[MockMemory]):
        self.memories = memories
    
    async def search_long_term_memory(self, text: str, user_id, limit: int):
        return MockResults(self.memories)

class MockAgent:
    def __init__(self, student_id: str, memories: List[MockMemory]):
        self.student_id = student_id
        self.memory_client = MockMemoryClient(memories)

async def demonstrate_user_knowledge_summary():
    """Demonstrate the user knowledge summary functionality."""
    
    print("🧠 User Knowledge Summary Tool Demonstration")
    print("=" * 60)
    
    # Create sample memories for different scenarios
    scenarios = [
        {
            "name": "Rich User Profile",
            "memories": [
                MockMemory("Student prefers online courses over in-person classes", ["preferences"]),
                MockMemory("Student is interested in machine learning and AI", ["interests", "technology"]),
                MockMemory("Student's goal is to become a data scientist", ["goals", "career"]),
                MockMemory("Student has completed CS101 and MATH201", ["courses", "academic_history"]),
                MockMemory("Student likes morning study sessions", ["preferences", "study_habits"]),
                MockMemory("Student wants to take advanced ML courses next semester", ["goals", "courses"]),
                MockMemory("Student prefers hands-on projects over theoretical work", ["preferences", "learning_style"]),
                MockMemory("Student is interested in Python programming", ["interests", "programming"]),
            ]
        },
        {
            "name": "New User (No Memories)",
            "memories": []
        },
        {
            "name": "Minimal User Profile",
            "memories": [
                MockMemory("Student mentioned interest in computer science", ["interests", "technology"]),
                MockMemory("Student prefers evening classes", ["preferences", "schedule"]),
            ]
        },
        {
            "name": "Topic-Rich Profile",
            "memories": [
                MockMemory("Student loves mathematics and statistics", ["interests", "mathematics", "statistics"]),
                MockMemory("Wants to work in fintech after graduation", ["goals", "career", "finance"]),
                MockMemory("Prefers small class sizes", ["preferences", "learning_environment"]),
                MockMemory("Has strong background in calculus", ["academic_history", "mathematics"]),
                MockMemory("Interested in quantitative analysis", ["interests", "analytics", "mathematics"]),
            ]
        }
    ]
    
    # Import the actual tool function
    from redis_context_course.agent import ClassAgent
    
    # Get the tool function
    tool_func = ClassAgent._summarize_user_knowledge_tool.func
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print("-" * 40)
        
        # Create mock agent with the scenario's memories
        mock_agent = MockAgent("demo_user", scenario['memories'])
        
        # Call the tool function
        try:
            result = await tool_func(mock_agent)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)

def show_docstring_examples():
    """Show examples of the updated Google-style docstrings."""
    
    print("\n📚 LLM-Powered User Knowledge Summary")
    print("=" * 60)

    print("\n🧠 New Approach: Pure LLM Summarization")
    print("✅ Benefits:")
    print("  • Natural, conversational summaries")
    print("  • Intelligent organization of information")
    print("  • Adapts to any type of stored information")
    print("  • No hardcoded categories or complex logic")
    print("  • Handles topics and context automatically")

    print("\n🔧 _summarize_user_knowledge_tool")
    print("   Description: Uses LLM to create intelligent summaries of user information")
    print("   Args: None")
    print("   Returns: str: Natural, well-organized summary created by LLM")
    print("   Example queries:")
    examples = [
        "What do you know about me?",
        "Tell me about my profile",
        "What are my interests and preferences?",
        "Show me my information"
    ]
    for query in examples:
        print(f"     - \"{query}\"")

    print("\n💡 How it works:")
    print("  1. Retrieves all stored memories for the user")
    print("  2. Includes topics information for context")
    print("  3. Sends to LLM with detailed prompt for organization")
    print("  4. LLM creates natural, well-structured summary")
    print("  5. Graceful fallback if LLM is unavailable")

def main():
    """Main function to run the demonstration."""
    print("User Knowledge Summary Tool - Example & Documentation")
    print("=" * 70)
    
    # Show the docstring examples first
    show_docstring_examples()
    
    # Then demonstrate the functionality
    try:
        asyncio.run(demonstrate_user_knowledge_summary())
    except Exception as e:
        print(f"\n❌ Error running demonstration: {e}")
        print("Note: This demo uses mock data and doesn't require a running memory server.")
    
    print("\n✅ Demonstration complete!")
    print("\nTo use the real tool:")
    print("1. Start the Redis Agent Memory Server: docker-compose up")
    print("2. Set OPENAI_API_KEY environment variable")
    print("3. Run the agent and ask: 'What do you know about me?'")

if __name__ == "__main__":
    main()
