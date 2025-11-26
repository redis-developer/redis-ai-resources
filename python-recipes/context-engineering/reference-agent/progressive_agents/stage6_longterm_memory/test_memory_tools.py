"""
Test script for Stage 6: Long-term Memory Tools

This script tests:
1. Storing student preferences
2. Retrieving memories
3. Cross-session persistence
4. Multi-tool decision-making
"""

import asyncio
import logging
import sys
import uuid
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from redis_context_course import CourseManager

from progressive_agents.stage6_longterm_memory.agent.workflow import (
    create_workflow,
    run_agent_async,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def test_store_preferences():
    """Test 1: Store student preferences."""
    print("\n" + "=" * 80)
    print("TEST 1: Store Student Preferences")
    print("=" * 80)

    course_manager = CourseManager()
    agent = create_workflow(course_manager)

    student_id = "test_student_memory"
    session_id = f"session_1_{uuid.uuid4().hex[:8]}"

    query = "Hi! I'm interested in machine learning and I prefer online courses."

    print(f"\n👤 Student ID: {student_id}")
    print(f"🔗 Session ID: {session_id}")
    print(f"❓ Query: {query}")
    print()

    result = await run_agent_async(
        agent=agent,
        query=query,
        session_id=session_id,
        student_id=student_id,
        enable_caching=False,
    )

    response = result.get("final_response", "No response")
    print(f"\n✅ Response:\n{response}\n")

    # Check if agent stored memories
    execution_path = " → ".join(result.get("execution_path", []))
    print(f"📊 Execution Path: {execution_path}")

    return student_id


async def test_retrieve_memories(student_id: str):
    """Test 2: Retrieve memories in a new session."""
    print("\n" + "=" * 80)
    print("TEST 2: Retrieve Memories (New Session)")
    print("=" * 80)

    course_manager = CourseManager()
    agent = create_workflow(course_manager)

    # NEW SESSION (different session_id, same student_id)
    session_id = f"session_2_{uuid.uuid4().hex[:8]}"

    query = "What courses would you recommend for me?"

    print(f"\n👤 Student ID: {student_id} (same student)")
    print(f"🔗 Session ID: {session_id} (NEW SESSION)")
    print(f"❓ Query: {query}")
    print()

    result = await run_agent_async(
        agent=agent,
        query=query,
        session_id=session_id,
        student_id=student_id,
        enable_caching=False,
    )

    response = result.get("final_response", "No response")
    print(f"\n✅ Response:\n{response}\n")

    # Check if agent searched memories
    execution_path = " → ".join(result.get("execution_path", []))
    print(f"📊 Execution Path: {execution_path}")

    # Check if response mentions stored preferences
    if "machine learning" in response.lower() or "online" in response.lower():
        print("\n✅ SUCCESS: Response includes stored preferences!")
    else:
        print("\n⚠️  WARNING: Response may not have used stored preferences")


async def test_multi_tool_usage():
    """Test 3: Multi-tool decision-making."""
    print("\n" + "=" * 80)
    print("TEST 3: Multi-Tool Decision Making")
    print("=" * 80)

    course_manager = CourseManager()
    agent = create_workflow(course_manager)

    student_id = f"test_student_multitool_{uuid.uuid4().hex[:8]}"
    session_id = f"session_3_{uuid.uuid4().hex[:8]}"

    query = "I want to prepare for a career in AI research. Show me relevant courses."

    print(f"\n👤 Student ID: {student_id}")
    print(f"🔗 Session ID: {session_id}")
    print(f"❓ Query: {query}")
    print()

    result = await run_agent_async(
        agent=agent,
        query=query,
        session_id=session_id,
        student_id=student_id,
        enable_caching=False,
    )

    response = result.get("final_response", "No response")
    print(f"\n✅ Response:\n{response}\n")

    execution_path = " → ".join(result.get("execution_path", []))
    print(f"📊 Execution Path: {execution_path}")

    print("\n💡 Expected: Agent should store_memory (career goal) AND search_courses")


async def test_cross_session_persistence():
    """Test 4: Cross-session persistence."""
    print("\n" + "=" * 80)
    print("TEST 4: Cross-Session Persistence")
    print("=" * 80)

    course_manager = CourseManager()
    agent = create_workflow(course_manager)

    student_id = f"test_student_persistence_{uuid.uuid4().hex[:8]}"

    # Session 1: Store preference
    session_1 = f"session_4a_{uuid.uuid4().hex[:8]}"
    query_1 = "I prefer evening classes because I work during the day."

    print(f"\n📍 SESSION 1")
    print(f"👤 Student ID: {student_id}")
    print(f"🔗 Session ID: {session_1}")
    print(f"❓ Query: {query_1}")
    print()

    result_1 = await run_agent_async(
        agent=agent,
        query=query_1,
        session_id=session_1,
        student_id=student_id,
        enable_caching=False,
    )

    response_1 = result_1.get("final_response", "No response")
    print(f"✅ Response: {response_1}\n")

    # Session 2: Retrieve preference (days later)
    session_2 = f"session_4b_{uuid.uuid4().hex[:8]}"
    query_2 = "What are my scheduling preferences?"

    print(f"\n📍 SESSION 2 (Days Later)")
    print(f"👤 Student ID: {student_id} (same student)")
    print(f"🔗 Session ID: {session_2} (NEW SESSION)")
    print(f"❓ Query: {query_2}")
    print()

    result_2 = await run_agent_async(
        agent=agent,
        query=query_2,
        session_id=session_2,
        student_id=student_id,
        enable_caching=False,
    )

    response_2 = result_2.get("final_response", "No response")
    print(f"✅ Response: {response_2}\n")

    if "evening" in response_2.lower() or "work" in response_2.lower():
        print("✅ SUCCESS: Cross-session persistence working!")
    else:
        print("⚠️  WARNING: May not have retrieved stored preference")


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("STAGE 6: LONG-TERM MEMORY TOOLS - TEST SUITE")
    print("=" * 80)

    try:
        # Test 1: Store preferences
        student_id = await test_store_preferences()

        # Test 2: Retrieve memories (same student, new session)
        await test_retrieve_memories(student_id)

        # Test 3: Multi-tool usage
        await test_multi_tool_usage()

        # Test 4: Cross-session persistence
        await test_cross_session_persistence()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

