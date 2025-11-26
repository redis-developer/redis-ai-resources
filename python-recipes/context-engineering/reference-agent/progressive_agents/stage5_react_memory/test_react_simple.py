"""
Simple tests for Stage 5 ReAct agent (single-turn conversations).

Tests the ReAct pattern with working memory and search_courses tool.
"""

import asyncio
import logging
import os
from pathlib import Path

from langchain_openai import ChatOpenAI
from redis_context_course import CourseManager

from progressive_agents.stage5_react_memory.agent.react_agent import run_react_agent
from progressive_agents.stage5_react_memory.agent.tools import initialize_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("course-qa-workflow")


async def test_simple_query():
    """Test a simple course lookup."""
    print("\n" + "=" * 80)
    print("TEST 1: Simple Course Lookup")
    print("=" * 80)
    
    # Initialize
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Initialize course manager
    course_manager = CourseManager()

    # Initialize tools
    initialize_tools(course_manager)
    
    # Run query
    query = "What is CS004?"
    print(f"\nQuery: {query}")
    
    result = await run_react_agent(
        query=query,
        llm=llm,
        max_iterations=10,
    )
    
    # Print results
    print(f"\n{'─' * 80}")
    print("REASONING TRACE:")
    print(f"{'─' * 80}")
    for i, step in enumerate(result["reasoning_trace"], 1):
        print(f"\nStep {i}:")
        print(f"  Thought: {step.thought}")
        print(f"  Action: {step.action}")
        if step.action != "FINISH":
            print(f"  Action Input: {step.action_input}")
            print(f"  Observation: {step.observation[:200]}...")
        else:
            print(f"  Final Answer: {step.action_input}")
    
    print(f"\n{'─' * 80}")
    print(f"FINAL ANSWER:")
    print(f"{'─' * 80}")
    print(result["answer"])
    print(f"\nIterations: {result['iterations']}")
    print(f"Success: {result['success']}")


async def test_semantic_search():
    """Test semantic search for courses."""
    print("\n" + "=" * 80)
    print("TEST 2: Semantic Search")
    print("=" * 80)
    
    # Initialize
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Initialize course manager
    course_manager = CourseManager()

    # Initialize tools
    initialize_tools(course_manager)
    
    # Run query
    query = "I want to learn about machine learning"
    print(f"\nQuery: {query}")
    
    result = await run_react_agent(
        query=query,
        llm=llm,
        max_iterations=10,
    )
    
    # Print results
    print(f"\n{'─' * 80}")
    print("REASONING TRACE:")
    print(f"{'─' * 80}")
    for i, step in enumerate(result["reasoning_trace"], 1):
        print(f"\nStep {i}:")
        print(f"  Thought: {step.thought}")
        print(f"  Action: {step.action}")
        if step.action != "FINISH":
            print(f"  Action Input: {step.action_input}")
            print(f"  Observation: {step.observation[:200]}...")
        else:
            print(f"  Final Answer: {step.action_input[:200]}...")
    
    print(f"\n{'─' * 80}")
    print(f"FINAL ANSWER:")
    print(f"{'─' * 80}")
    print(result["answer"])
    print(f"\nIterations: {result['iterations']}")
    print(f"Success: {result['success']}")


async def test_prerequisites():
    """Test prerequisite lookup."""
    print("\n" + "=" * 80)
    print("TEST 3: Prerequisites Lookup")
    print("=" * 80)
    
    # Initialize
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Initialize course manager
    course_manager = CourseManager()

    # Initialize tools
    initialize_tools(course_manager)
    
    # Run query
    query = "What are the prerequisites for CS004?"
    print(f"\nQuery: {query}")
    
    result = await run_react_agent(
        query=query,
        llm=llm,
        max_iterations=10,
    )
    
    # Print results
    print(f"\n{'─' * 80}")
    print("REASONING TRACE:")
    print(f"{'─' * 80}")
    for i, step in enumerate(result["reasoning_trace"], 1):
        print(f"\nStep {i}:")
        print(f"  Thought: {step.thought}")
        print(f"  Action: {step.action}")
        if step.action != "FINISH":
            print(f"  Action Input: {step.action_input}")
            print(f"  Observation: {step.observation[:200]}...")
        else:
            print(f"  Final Answer: {step.action_input}")
    
    print(f"\n{'─' * 80}")
    print(f"FINAL ANSWER:")
    print(f"{'─' * 80}")
    print(result["answer"])
    print(f"\nIterations: {result['iterations']}")
    print(f"Success: {result['success']}")


async def main():
    """Run all tests."""
    await test_simple_query()
    await test_semantic_search()
    await test_prerequisites()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

