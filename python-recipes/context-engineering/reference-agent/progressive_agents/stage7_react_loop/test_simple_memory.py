"""
Simple test to verify Stage 6 memory tools work correctly.
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
    level=logging.WARNING,  # Reduce noise
    format="%(message)s",
)


async def main():
    """Run a simple memory test."""
    print("=" * 80)
    print("STAGE 6: SIMPLE MEMORY TEST")
    print("=" * 80)

    course_manager = CourseManager()
    agent = create_workflow(course_manager)

    student_id = f"demo_student_{uuid.uuid4().hex[:6]}"

    # Test 1: Store preferences
    print(f"\n👤 Student: {student_id}")
    print("\n📍 SESSION 1: Store Preferences")
    print("-" * 80)

    session_1 = f"session_1_{uuid.uuid4().hex[:6]}"
    query_1 = "I'm interested in machine learning and I prefer online courses."

    print(f"User: {query_1}")

    result_1 = await run_agent_async(
        agent=agent,
        query=query_1,
        session_id=session_1,
        student_id=student_id,
        enable_caching=False,
    )

    response_1 = result_1.get("final_response", "No response")
    print(f"\nAgent: {response_1}")

    # Test 2: Retrieve preferences in new session
    print("\n\n📍 SESSION 2: Retrieve Preferences (New Session)")
    print("-" * 80)

    session_2 = f"session_2_{uuid.uuid4().hex[:6]}"
    query_2 = "What courses would you recommend for me?"

    print(f"User: {query_2}")

    result_2 = await run_agent_async(
        agent=agent,
        query=query_2,
        session_id=session_2,
        student_id=student_id,
        enable_caching=False,
    )

    response_2 = result_2.get("final_response", "No response")
    print(f"\nAgent: {response_2}")

    # Check if personalization worked
    print("\n" + "=" * 80)
    if "machine learning" in response_2.lower() or "online" in response_2.lower():
        print("✅ SUCCESS: Agent used stored preferences for personalization!")
    else:
        print("⚠️  Note: Response may not have explicitly mentioned stored preferences")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

