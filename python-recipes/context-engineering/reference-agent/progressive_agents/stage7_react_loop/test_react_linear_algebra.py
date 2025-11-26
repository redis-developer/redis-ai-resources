"""
Test to see how the ReAct agent handles "linear algebra" queries.

Key question: Does it use vector search (semantic) or exact match?
Tests the agent's reasoning about search strategy selection.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from redis_context_course import CourseManager

from progressive_agents.stage7_react_loop.agent.workflow import (
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
        student_id="test_user_linear_algebra",
        enable_caching=False,
    )

    response = result.get("final_response", "No response")
    react_iterations = result.get("react_iterations", 0)
    reasoning_trace = result.get("reasoning_trace", [])

    print(f"\nResponse:\n{response}\n")
    print(f"ReAct Iterations: {react_iterations}")
    print(f"Reasoning Steps: {len(reasoning_trace)}")

    # Show reasoning trace
    if reasoning_trace:
        print("\nReasoning Trace:")
        print("-" * 80)
        for i, step in enumerate(reasoning_trace, 1):
            if step["type"] == "thought":
                print(f"{i}. 💭 Thought: {step['content'][:150]}...")
            elif step["type"] == "action":
                print(f"{i}. 🔧 Action: {step['action']}")
                print(f"      Input: {step['input']}")
                # Check search strategy
                if step["action"] == "search_courses" and "search_strategy" in step["input"]:
                    strategy = step["input"]["search_strategy"]
                    print(f"      ⭐ Search Strategy: {strategy}")
            elif step["type"] == "finish":
                print(f"{i}. ✅ FINISH")
        print("-" * 80)


async def main():
    """Run linear algebra tests."""
    print("Initializing Course Manager...")
    course_manager = CourseManager()

    print("Creating agent workflow...")
    agent = create_workflow(course_manager)

    print("\n" + "=" * 80)
    print("STAGE 7 REACT AGENT - LINEAR ALGEBRA TESTS")
    print("=" * 80)
    print("\nThese tests check if the agent correctly chooses search strategies")
    print("for 'linear algebra' (not a course code, requires semantic search)")
    print("=" * 80)

    # Test questions about "linear algebra" (not a course code)
    questions = [
        ("general_1", "I am interested in linear algebra"),
        ("prereq_1", "What are the prerequisites for linear algebra?"),
        ("topics_1", "What topics are covered in linear algebra?"),
        ("assignments_1", "What are the assignments for linear algebra course?"),
    ]

    for session_id, question in questions:
        await test_query(agent, question, session_id)

    print("\n" + "=" * 80)
    print("✅ LINEAR ALGEBRA TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

