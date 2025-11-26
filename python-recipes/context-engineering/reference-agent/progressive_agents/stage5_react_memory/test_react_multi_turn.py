"""
Multi-turn conversation tests for Stage 5 ReAct agent.

Tests the ReAct pattern with conversation history and context.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import List, Dict

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


async def run_conversation(queries: List[str], conversation_name: str):
    """Run a multi-turn conversation."""
    print("\n" + "=" * 80)
    print(f"CONVERSATION: {conversation_name}")
    print("=" * 80)
    
    # Initialize
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    course_manager = CourseManager()
    initialize_tools(course_manager)
    
    # Track conversation history
    conversation_history = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'─' * 80}")
        print(f"Turn {i}: {query}")
        print(f"{'─' * 80}")
        
        # Run agent
        result = await run_react_agent(
            query=query,
            llm=llm,
            conversation_history=conversation_history,
            max_iterations=10,
        )
        
        # Print reasoning trace
        print(f"\nREASONING STEPS:")
        for j, step in enumerate(result["reasoning_trace"], 1):
            print(f"\n  Step {j}:")
            print(f"    Thought: {step.thought}")
            print(f"    Action: {step.action}")
            if step.action != "FINISH":
                print(f"    Observation: {step.observation[:150]}...")
        
        # Print answer
        print(f"\n{'─' * 80}")
        print(f"ANSWER:")
        print(f"{'─' * 80}")
        print(result["answer"])
        print(f"\nIterations: {result['iterations']} | Success: {result['success']}")
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": result["answer"]})


async def test_pronoun_resolution():
    """Test pronoun resolution across turns."""
    queries = [
        "What is CS002?",
        "What are the prerequisites for it?",
        "Tell me more about the syllabus",
    ]
    await run_conversation(queries, "Pronoun Resolution Test")


async def test_follow_up_questions():
    """Test follow-up questions building on previous context."""
    queries = [
        "Tell me about machine learning courses",
        "Which one is best for beginners?",
        "What are the prerequisites for that course?",
    ]
    await run_conversation(queries, "Follow-up Questions Test")


async def test_comparison_across_turns():
    """Test comparing courses mentioned in different turns."""
    queries = [
        "What is CS001?",
        "What is CS002?",
        "Which one should I take first?",
    ]
    await run_conversation(queries, "Comparison Across Turns Test")


async def test_context_accumulation():
    """Test accumulating context across multiple turns."""
    queries = [
        "I'm interested in computer vision",
        "What courses cover that topic?",
        "What are the prerequisites for the advanced one?",
        "Are there any beginner courses I should take first?",
    ]
    await run_conversation(queries, "Context Accumulation Test")


async def main():
    """Run all multi-turn tests."""
    await test_pronoun_resolution()
    await test_follow_up_questions()
    await test_comparison_across_turns()
    await test_context_accumulation()
    
    print("\n" + "=" * 80)
    print("ALL MULTI-TURN TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

