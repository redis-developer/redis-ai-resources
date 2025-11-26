"""
Simple test script for Stage 4 agentic workflow.

Tests basic functionality with one question per intent type.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from redis_context_course import CourseManager

from progressive_agents.stage4_hybrid_search_with_ner.agent.workflow import (
    create_workflow,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Suppress verbose logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


async def test_agent():
    """Test the agent with simple questions."""
    
    print("\n" + "=" * 80)
    print("STAGE 4 AGENTIC WORKFLOW TEST")
    print("=" * 80)
    
    # Initialize course manager
    print("\n📚 Initializing CourseManager...")
    course_manager = CourseManager()
    
    # Create workflow
    print("🔧 Creating workflow...")
    workflow = create_workflow(course_manager)
    
    # Test questions (one per intent)
    test_questions = [
        ("GENERAL", "What is CS004?"),
        ("PREREQUISITES", "What are the prerequisites for CS004?"),
        ("SYLLABUS", "What's the syllabus for CS004?"),
        ("ASSIGNMENTS", "What are the assignments for CS004?"),
    ]
    
    results = []
    
    for intent_type, question in test_questions:
        print(f"\n{'=' * 80}")
        print(f"Testing Intent: {intent_type}")
        print(f"{'=' * 80}")
        print(f"Question: {question}")
        
        # Run workflow
        initial_state = {
            "original_query": question,
            "execution_path": [],
            "llm_calls": {},
            "metrics": {},
        }
        
        result = await workflow.ainvoke(initial_state)
        
        # Extract response
        response = result.get("final_response", "No response")
        
        print(f"\nResponse: {response[:200]}...")
        
        # Check if intent matches
        intent_match = "✅" if any(
            keyword in response.lower()
            for keyword in {
                "GENERAL": ["computer vision", "cs004"],
                "PREREQUISITES": ["prerequisite", "required"],
                "SYLLABUS": ["syllabus", "topics", "week"],
                "ASSIGNMENTS": ["assignment", "project"],
            }[intent_type]
        ) else "❌"
        
        print(f"Intent Match: {intent_match}")
        
        results.append({
            "intent": intent_type,
            "question": question,
            "response": response,
            "match": intent_match,
        })
    
    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    
    passed = sum(1 for r in results if r["match"] == "✅")
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    for r in results:
        print(f"\n{r['match']} {r['intent']}: {r['question']}")
    
    print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    asyncio.run(test_agent())

