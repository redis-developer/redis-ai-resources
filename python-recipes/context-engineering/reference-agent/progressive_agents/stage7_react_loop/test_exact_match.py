"""
Test exact match with Stage 7 ReAct agent for CS002.
"""

import asyncio
import logging

from langchain_openai import ChatOpenAI
from redis_context_course import CourseManager

from progressive_agents.stage7_react_loop.agent.react_agent import run_react_agent
from progressive_agents.stage7_react_loop.agent.tools import initialize_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("course-qa-workflow")


async def test_cs002():
    """Test exact match for CS002."""
    print("\n" + "=" * 80)
    print("STAGE 7 TEST: Exact Match for CS002")
    print("=" * 80)
    
    # Initialize
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    course_manager = CourseManager()
    initialize_tools(course_manager, user_id="test_user")
    
    # Test CS002
    query = "What is CS002?"
    print(f"\nQuery: {query}")
    
    result = await run_react_agent(
        query=query,
        llm=llm,
        user_id="test_user",
        max_iterations=10,
    )
    
    # Print results
    print(f"\n{'─' * 80}")
    print(f"FINAL ANSWER:")
    print(f"{'─' * 80}")
    print(result["answer"])
    print(f"\nIterations: {result['iterations']}")
    print(f"Success: {result['success']}")
    
    # Verify it's the right course
    if "Machine Learning" in result["answer"]:
        print("\n✅ CORRECT: Found CS002 - Machine Learning Fundamentals")
    else:
        print("\n❌ WRONG: Did not find the correct course")


async def test_cs001():
    """Test exact match for CS001."""
    print("\n" + "=" * 80)
    print("STAGE 7 TEST: Exact Match for CS001")
    print("=" * 80)
    
    # Initialize
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    course_manager = CourseManager()
    initialize_tools(course_manager, user_id="test_user")
    
    # Test CS001
    query = "What is CS001?"
    print(f"\nQuery: {query}")
    
    result = await run_react_agent(
        query=query,
        llm=llm,
        user_id="test_user",
        max_iterations=10,
    )
    
    # Print answer
    print(f"\n{'─' * 80}")
    print(f"FINAL ANSWER:")
    print(f"{'─' * 80}")
    print(result["answer"])
    print(f"\nIterations: {result['iterations']}")
    
    # Verify it's the right course
    if "Database" in result["answer"]:
        print("\n✅ CORRECT: Found CS001 - Database Systems")
    else:
        print("\n❌ WRONG: Did not find the correct course")


async def main():
    """Run tests."""
    await test_cs002()
    await test_cs001()
    
    print("\n" + "=" * 80)
    print("STAGE 7 EXACT MATCH TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

