"""
Simple test to verify the agent works with tool calling.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main():
    """Run a simple test."""
    print("Initializing Course Manager...")
    course_manager = CourseManager()

    print("Creating agent workflow...")
    agent = create_workflow(course_manager)

    # Test questions
    questions = [
        ("GENERAL", "What is CS004?"),
        ("PREREQUISITES", "What are the prerequisites for CS004?"),
        ("SYLLABUS", "What's the syllabus for CS004?"),
        ("ASSIGNMENTS", "What are the assignments for CS004?"),
    ]

    for intent_type, question in questions:
        print("\n" + "=" * 80)
        print(f"Testing: {intent_type}")
        print(f"Question: {question}")
        print("=" * 80)

        try:
            result = await run_agent_async(
                agent=agent,
                query=question,
                session_id=f"test_{intent_type.lower()}",
                student_id="test_user",
                enable_caching=False,
            )

            response = result.get("final_response", "No response")
            execution_path = " → ".join(result.get("execution_path", []))

            print(f"\nResponse:\n{response}\n")
            print(f"Execution Path: {execution_path}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

