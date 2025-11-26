"""
Comprehensive multi-turn conversation tests for Stage 7 ReAct Agent.

Tests:
1. Memory storage and retrieval across sessions
2. Follow-up questions with context
3. Preference-based recommendations
4. Complex multi-step reasoning
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


async def run_conversation(agent, student_id, session_id, conversation):
    """Run a multi-turn conversation and track results."""
    print("\n" + "=" * 80)
    print(f"CONVERSATION: {conversation['name']}")
    print("=" * 80)
    print(f"Student: {student_id}")
    print(f"Session: {session_id}")
    print("=" * 80)

    results = []

    for i, turn in enumerate(conversation["turns"], 1):
        print(f"\n--- Turn {i}/{len(conversation['turns'])} ---")
        print(f"User: {turn['query']}")
        print()

        try:
            result = await run_agent_async(
                agent=agent,
                query=turn["query"],
                session_id=session_id,
                student_id=student_id,
                enable_caching=False,
            )

            response = result.get("final_response", "No response")
            react_iterations = result.get("react_iterations", 0)
            reasoning_trace = result.get("reasoning_trace", [])

            print(f"Agent: {response[:200]}...")
            print()
            print(f"ReAct Iterations: {react_iterations}")
            print(f"Reasoning Steps: {len(reasoning_trace)}")

            # Show key actions taken
            actions = [
                step["action"]
                for step in reasoning_trace
                if step["type"] == "action"
            ]
            print(f"Actions: {' → '.join(actions)}")

            # Check expected behavior
            expected = turn.get("expected_actions", [])
            if expected:
                matched = all(action in actions for action in expected)
                status = "✅ PASS" if matched else "❌ FAIL"
                print(f"Expected Actions: {expected} - {status}")

            results.append(
                {
                    "turn": i,
                    "query": turn["query"],
                    "response": response,
                    "react_iterations": react_iterations,
                    "reasoning_steps": len(reasoning_trace),
                    "actions": actions,
                    "expected_match": matched if expected else None,
                }
            )

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()
            results.append(
                {
                    "turn": i,
                    "query": turn["query"],
                    "response": f"Error: {e}",
                    "react_iterations": 0,
                    "reasoning_steps": 0,
                    "actions": [],
                    "expected_match": False,
                }
            )

    # Summary
    print("\n" + "=" * 80)
    print(f"CONVERSATION SUMMARY: {conversation['name']}")
    print("=" * 80)
    total_iterations = sum(r["react_iterations"] for r in results)
    total_steps = sum(r["reasoning_steps"] for r in results)
    print(f"Total Turns: {len(results)}")
    print(f"Total ReAct Iterations: {total_iterations}")
    print(f"Total Reasoning Steps: {total_steps}")
    print(f"Avg Iterations/Turn: {total_iterations / len(results):.1f}")
    print(f"Avg Steps/Turn: {total_steps / len(results):.1f}")

    return results


# Define test conversations
CONVERSATIONS = [
    {
        "name": "Preference Storage and Retrieval",
        "student_id": "student_prefs_001",
        "session_id": "session_prefs_001",
        "turns": [
            {
                "query": "I'm interested in machine learning and prefer online courses.",
                "expected_actions": ["store_memory", "store_memory"],
            },
            {
                "query": "What courses would you recommend for me?",
                "expected_actions": ["search_memories", "search_courses"],
            },
            {
                "query": "Tell me more about the first course you mentioned.",
                "expected_actions": ["search_courses"],
            },
        ],
    },
    {
        "name": "Career Goal with Follow-ups",
        "student_id": "student_career_001",
        "session_id": "session_career_001",
        "turns": [
            {
                "query": "I want to prepare for a career in AI research.",
                "expected_actions": ["store_memory", "search_courses"],
            },
            {
                "query": "What are the prerequisites for the courses you mentioned?",
                "expected_actions": ["search_courses"],
            },
            {
                "query": "Can you remind me what my career goal is?",
                "expected_actions": ["search_memories"],
            },
        ],
    },
    {
        "name": "Course Exploration with Constraints",
        "student_id": "student_constraints_001",
        "session_id": "session_constraints_001",
        "turns": [
            {
                "query": "I can only take 2 courses per semester and prefer evening classes.",
                "expected_actions": ["store_memory", "store_memory"],
            },
            {
                "query": "Show me data science courses.",
                "expected_actions": ["search_courses"],
            },
            {
                "query": "What did I say about my schedule preferences?",
                "expected_actions": ["search_memories"],
            },
        ],
    },
    {
        "name": "Specific Course Deep Dive",
        "student_id": "student_deepdive_001",
        "session_id": "session_deepdive_001",
        "turns": [
            {
                "query": "What is CS004?",
                "expected_actions": ["search_courses"],
            },
            {
                "query": "What are the prerequisites?",
                "expected_actions": ["search_courses"],
            },
            {
                "query": "What's the syllabus?",
                "expected_actions": ["search_courses"],
            },
            {
                "query": "What are the assignments?",
                "expected_actions": ["search_courses"],
            },
        ],
    },
    {
        "name": "Cross-Session Memory Persistence",
        "student_id": "student_persistence_001",
        "session_id": "session_persistence_001",
        "turns": [
            {
                "query": "I'm interested in cybersecurity and network security.",
                "expected_actions": ["store_memory"],
            },
        ],
    },
    {
        "name": "Cross-Session Memory Retrieval (New Session)",
        "student_id": "student_persistence_001",  # Same student
        "session_id": "session_persistence_002",  # Different session
        "turns": [
            {
                "query": "What courses would you recommend based on my interests?",
                "expected_actions": ["search_memories", "search_courses"],
            },
        ],
    },
]


async def main():
    """Run all multi-turn conversation tests."""
    print("Initializing Course Manager...")
    course_manager = CourseManager()

    print("Creating agent workflow...")
    agent = create_workflow(course_manager)

    print("\n" + "=" * 80)
    print("STAGE 7 REACT AGENT - MULTI-TURN CONVERSATION TESTS")
    print("=" * 80)

    all_results = {}

    # Run each conversation
    for conversation in CONVERSATIONS:
        results = await run_conversation(
            agent,
            conversation["student_id"],
            conversation["session_id"],
            conversation,
        )
        all_results[conversation["name"]] = results

    # Overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)

    total_turns = 0
    total_iterations = 0
    total_steps = 0
    total_expected_matches = 0
    total_expected_tests = 0

    for conv_name, results in all_results.items():
        turns = len(results)
        iterations = sum(r["react_iterations"] for r in results)
        steps = sum(r["reasoning_steps"] for r in results)
        expected_matches = sum(
            1 for r in results if r["expected_match"] is True
        )
        expected_tests = sum(
            1 for r in results if r["expected_match"] is not None
        )

        total_turns += turns
        total_iterations += iterations
        total_steps += steps
        total_expected_matches += expected_matches
        total_expected_tests += expected_tests

        match_rate = (
            f"{expected_matches}/{expected_tests}"
            if expected_tests > 0
            else "N/A"
        )
        print(
            f"{conv_name:40s}: {turns} turns | {iterations} iterations | {steps} steps | Match: {match_rate}"
        )

    print(f"\n{'TOTAL':40s}: {total_turns} turns | {total_iterations} iterations | {total_steps} steps")
    print(f"Average Iterations/Turn: {total_iterations / total_turns:.1f}")
    print(f"Average Steps/Turn: {total_steps / total_turns:.1f}")

    if total_expected_tests > 0:
        match_percentage = (total_expected_matches / total_expected_tests * 100)
        print(
            f"Expected Action Match Rate: {total_expected_matches}/{total_expected_tests} ({match_percentage:.1f}%)"
        )

    print("\n✅ ALL MULTI-TURN TESTS COMPLETE")

    return all_results


if __name__ == "__main__":
    asyncio.run(main())

