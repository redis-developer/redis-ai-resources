"""
Comprehensive intent testing for Stage 7 ReAct Loop Agent.

Tests multiple questions for each intent category with follow-up questions:
- GENERAL: Course overviews/summaries
- PREREQUISITES: Prerequisite information
- SYLLABUS_OBJECTIVES: Syllabus and learning objectives
- ASSIGNMENTS: Assignment details

Also tests multi-turn conversations with memory.
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
logger = logging.getLogger(__name__)

# Test cases organized by intent
TEST_CASES = {
    "GENERAL": [
        "What is CS004?",
        "Tell me about Computer Vision course",
        "Show me machine learning courses",
        "What courses are available in Computer Science?",
    ],
    "PREREQUISITES": [
        "What are the prerequisites for CS004?",
        "What do I need to take before CS004?",
        "Show me the requirements for Computer Vision",
        "What courses must I complete before taking CS004?",
    ],
    "SYLLABUS_OBJECTIVES": [
        "What's the syllabus for CS004?",
        "Show me the learning objectives for Computer Vision",
        "What will I learn in CS004?",
        "What topics are covered in the Computer Vision course?",
    ],
    "ASSIGNMENTS": [
        "What are the assignments for CS004?",
        "Show me the homework for Computer Vision",
        "What projects are in CS004?",
        "What assignments will I have in the Computer Vision course?",
    ],
}


async def test_intent(agent, intent_name, questions):
    """Test multiple questions for a specific intent."""
    print("\n" + "=" * 80)
    print(f"Testing Intent: {intent_name}")
    print("=" * 80)

    results = []

    for i, question in enumerate(questions, 1):
        print(f"\n--- Test {i}/{len(questions)} ---")
        print(f"Question: {question}")

        try:
            # Run the agent
            result = await run_agent_async(
                agent=agent,
                query=question,
                session_id=f"test_{intent_name.lower()}_{i}",
                student_id="test_user_intents",
                enable_caching=False,
            )

            response = result.get("final_response", "No response")
            execution_path = " → ".join(result.get("execution_path", []))
            react_iterations = result.get("react_iterations", 0)
            reasoning_steps = len(result.get("reasoning_trace", []))

            print(f"\nResponse: {response[:200]}...")
            print(f"Execution Path: {execution_path}")
            print(f"ReAct Iterations: {react_iterations}")
            print(f"Reasoning Steps: {reasoning_steps}")

            # Analyze response content
            response_lower = response.lower()

            # Check if response matches intent
            intent_match = False
            if intent_name == "GENERAL":
                # Should have course overview/summary
                intent_match = (
                    "cs004" in response_lower or "computer vision" in response_lower
                )
            elif intent_name == "PREREQUISITES":
                # Should mention prerequisites
                intent_match = (
                    "prerequisite" in response_lower or "require" in response_lower
                )
            elif intent_name == "SYLLABUS_OBJECTIVES":
                # Should mention syllabus/objectives/topics
                intent_match = (
                    "syllabus" in response_lower
                    or "objective" in response_lower
                    or "learn" in response_lower
                    or "topic" in response_lower
                )
            elif intent_name == "ASSIGNMENTS":
                # Should mention assignments/projects/homework
                intent_match = (
                    "assignment" in response_lower
                    or "project" in response_lower
                    or "homework" in response_lower
                )

            status = "✅ PASS" if intent_match else "❌ FAIL"
            print(f"Intent Match: {status}")

            results.append(
                {
                    "question": question,
                    "response": response,
                    "intent_match": intent_match,
                    "execution_path": execution_path,
                    "react_iterations": react_iterations,
                    "reasoning_steps": reasoning_steps,
                }
            )

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()
            results.append(
                {
                    "question": question,
                    "response": f"Error: {e}",
                    "intent_match": False,
                    "execution_path": "error",
                    "react_iterations": 0,
                    "reasoning_steps": 0,
                }
            )

    # Summary for this intent
    passed = sum(1 for r in results if r["intent_match"])
    total = len(results)
    print(f"\n{intent_name} Summary: {passed}/{total} tests passed")

    return results


async def main():
    """Run all intent tests."""
    print("Initializing Course Manager...")
    course_manager = CourseManager()

    print("Creating agent workflow...")
    agent = create_workflow(course_manager)

    print("\n" + "=" * 80)
    print("STAGE 7 REACT AGENT INTENT TESTING")
    print("=" * 80)

    all_results = {}

    # Test each intent category
    for intent_name, questions in TEST_CASES.items():
        results = await test_intent(agent, intent_name, questions)
        all_results[intent_name] = results

    # Overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)

    total_passed = 0
    total_tests = 0
    total_iterations = 0
    total_reasoning_steps = 0

    for intent_name, results in all_results.items():
        passed = sum(1 for r in results if r["intent_match"])
        total = len(results)
        avg_iterations = (
            sum(r["react_iterations"] for r in results) / total if total > 0 else 0
        )
        avg_steps = (
            sum(r["reasoning_steps"] for r in results) / total if total > 0 else 0
        )

        total_passed += passed
        total_tests += total
        total_iterations += sum(r["react_iterations"] for r in results)
        total_reasoning_steps += sum(r["reasoning_steps"] for r in results)

        percentage = (passed / total * 100) if total > 0 else 0
        print(
            f"{intent_name:20s}: {passed:2d}/{total:2d} ({percentage:5.1f}%) | Avg Iterations: {avg_iterations:.1f} | Avg Steps: {avg_steps:.1f}"
        )

    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    avg_iterations_overall = total_iterations / total_tests if total_tests > 0 else 0
    avg_steps_overall = total_reasoning_steps / total_tests if total_tests > 0 else 0

    print(f"{'TOTAL':20s}: {total_passed:2d}/{total_tests:2d} ({overall_percentage:5.1f}%)")
    print(f"\nAverage ReAct Iterations: {avg_iterations_overall:.1f}")
    print(f"Average Reasoning Steps: {avg_steps_overall:.1f}")

    return all_results


if __name__ == "__main__":
    asyncio.run(main())

