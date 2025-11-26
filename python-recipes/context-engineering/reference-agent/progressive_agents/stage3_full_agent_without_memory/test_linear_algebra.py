"""
Test script for Stage 3 with topic-based queries (linear algebra).

Tests how the agent handles:
1. Topic-based queries (should use semantic_only strategy)
2. Different intents with the same topic
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from redis_context_course import CourseManager

from progressive_agents.stage3_full_agent_without_memory.agent.workflow import (
    create_workflow,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Suppress verbose logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


async def test_linear_algebra():
    """Test the agent with linear algebra queries."""
    
    print("\n" + "=" * 80)
    print("STAGE 3 LINEAR ALGEBRA TEST")
    print("=" * 80)
    
    # Initialize course manager
    print("\n📚 Initializing CourseManager...")
    course_manager = CourseManager()
    
    # Create workflow
    print("🔧 Creating workflow...")
    workflow = create_workflow(course_manager)
    
    # Test questions about linear algebra
    test_questions = [
        "I am interested in linear algebra",
        "What are the prerequisites for linear algebra?",
        "What's the topics for linear algebra?",
        "What are the assignments for linear algebra course?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}/{len(test_questions)}")
        print(f"{'=' * 80}")
        print(f"Query: {question}")
        
        # Run workflow
        initial_state = {
            "original_query": question,
            "execution_path": [],
            "llm_calls": {},
            "metrics": {},
        }
        
        result = await workflow.ainvoke(initial_state)
        
        # Extract response
        response = result.get("final_response", "No response")
        
        print(f"\nResponse:\n{response}")
        print(f"\n{'-' * 80}")


if __name__ == "__main__":
    asyncio.run(test_linear_algebra())

