"""
Test to see how the agent handles "linear algebra" queries.

Key question: Does it use vector search (semantic) or exact match?
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from redis_context_course import CourseManager

from progressive_agents.stage5_memory_augmented.agent.workflow import (
    create_workflow,
    run_agent_async,
)

# Configure logging to show tool calls
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def test_query(agent, query, session_id):
    """Test a single query and show what strategy was used."""
    print("\n" + "=" * 80)
    print(f"Query: {query}")
    print("=" * 80)

    result = await run_agent_async(
        agent=agent,
        query=query,
        session_id=session_id,
        student_id="test_user",
        enable_caching=False,
    )

    response = result.get("final_response", "No response")
    print(f"\nResponse:\n{response}\n")


async def main():
    """Run linear algebra tests."""
    print("Initializing Course Manager...")
    course_manager = CourseManager()

    print("Creating agent workflow...")
    agent = create_workflow(course_manager)

    # Test questions about "linear algebra" (not a course code)
    questions = [
        ("general_1", "I am interested in linear algebra"),
        ("prereq_1", "What are the prerequisites for linear algebra?"),
        ("topics_1", "What's the topics for linear algebra?"),
        ("assignments_1", "What are the assignments for linear algebra course?"),
    ]

    for session_id, question in questions:
        await test_query(agent, question, session_id)


if __name__ == "__main__":
    asyncio.run(main())

