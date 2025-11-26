#!/usr/bin/env python3
"""
Simple test for Stage 7 ReAct Loop Agent.

Tests basic ReAct functionality with explicit reasoning traces.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def test_react_simple():
    """Test simple ReAct loop with course search."""
    print("=" * 80)
    print("TEST: Simple ReAct Loop - Course Search")
    print("=" * 80)
    print()

    # Setup
    print("Initializing Course Manager...")
    course_manager = CourseManager()

    print("Creating agent workflow...")
    agent = create_workflow(course_manager)

    # Test query
    query = "What is CS004?"
    student_id = "test_student_react"
    session_id = "test_session_react_001"

    print(f"Query: {query}")
    print(f"Student: {student_id}")
    print()

    # Run agent
    result = await run_agent_async(
        agent, query, session_id=session_id, student_id=student_id, enable_caching=False
    )

    # Display results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    print(f"Final Response: {result['final_response']}")
    print()

    print(f"ReAct Iterations: {result.get('react_iterations', 0)}")
    print(f"Reasoning Steps: {len(result.get('reasoning_trace', []))}")
    print()

    # Show reasoning trace
    if result.get("reasoning_trace"):
        print("Reasoning Trace:")
        print("-" * 80)
        for i, step in enumerate(result["reasoning_trace"], 1):
            print(f"\nStep {i}:")
            if step["type"] == "thought":
                print(f"  💭 Thought: {step['content'][:100]}...")
            elif step["type"] == "action":
                print(f"  🔧 Action: {step['action']}")
                print(f"     Input: {step['input']}")
                print(f"  👁️  Observation: {step['observation'][:100]}...")
            elif step["type"] == "finish":
                print(f"  ✅ FINISH")
        print()

    print("=" * 80)
    print("✅ TEST PASSED")
    print("=" * 80)


async def test_react_memory():
    """Test ReAct loop with memory storage and retrieval."""
    print("\n\n")
    print("=" * 80)
    print("TEST: ReAct Loop - Memory Storage and Retrieval")
    print("=" * 80)
    print()

    # Setup
    print("Initializing Course Manager...")
    course_manager = CourseManager()

    print("Creating agent workflow...")
    agent = create_workflow(course_manager)

    student_id = "test_student_react_memory"
    session_id = "test_session_react_002"

    # Test 1: Store preferences
    query1 = "I'm interested in machine learning and prefer online courses."
    print(f"Query 1: {query1}")
    print()

    result1 = await run_agent_async(
        agent, query1, session_id=session_id, student_id=student_id, enable_caching=False
    )

    print(f"Response 1: {result1['final_response'][:100]}...")
    print(f"Iterations: {result1.get('react_iterations', 0)}")
    print(f"Reasoning Steps: {len(result1.get('reasoning_trace', []))}")
    print()

    # Test 2: Retrieve preferences
    query2 = "What courses would you recommend for me?"
    print(f"Query 2: {query2}")
    print()

    result2 = await run_agent_async(
        agent, query2, session_id=session_id, student_id=student_id, enable_caching=False
    )

    print(f"Response 2: {result2['final_response'][:100]}...")
    print(f"Iterations: {result2.get('react_iterations', 0)}")
    print(f"Reasoning Steps: {len(result2.get('reasoning_trace', []))}")
    print()

    # Show reasoning trace for query 2
    if result2.get("reasoning_trace"):
        print("Reasoning Trace (Query 2):")
        print("-" * 80)
        for i, step in enumerate(result2["reasoning_trace"], 1):
            print(f"\nStep {i}:")
            if step["type"] == "thought":
                print(f"  💭 Thought: {step['content'][:100]}...")
            elif step["type"] == "action":
                print(f"  🔧 Action: {step['action']}")
                print(f"     Input: {step['input']}")
                print(f"  👁️  Observation: {step['observation'][:100]}...")
            elif step["type"] == "finish":
                print(f"  ✅ FINISH")
        print()

    print("=" * 80)
    print("✅ TEST PASSED")
    print("=" * 80)


async def main():
    """Run all tests."""
    try:
        await test_react_simple()
        await test_react_memory()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

