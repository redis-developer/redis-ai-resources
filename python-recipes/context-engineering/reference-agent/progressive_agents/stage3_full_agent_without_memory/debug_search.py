#!/usr/bin/env python3
"""
Debug script to test course search functionality.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from reference-agent directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Add agent module to path
sys.path.insert(0, str(Path(__file__).parent))

from redis_context_course import CourseManager
from agent.setup import setup_agent
from agent.tools import search_courses, transform_course_to_text


async def test_course_search():
    """Test course search functionality."""
    print("=" * 80)
    print("Course Search Debug Tool")
    print("=" * 80)
    print()
    
    # Initialize CourseManager
    print("🔧 Initializing CourseManager...")
    course_manager, _ = await setup_agent(auto_load_courses=True)
    print()
    
    # Test 1: Get all courses
    print("=" * 80)
    print("Test 1: Get All Courses")
    print("=" * 80)
    all_courses = await course_manager.get_all_courses()
    print(f"✅ Found {len(all_courses)} courses in Redis")
    
    if all_courses:
        print("\nFirst 3 courses:")
        for i, course in enumerate(all_courses[:3], 1):
            print(f"\n{i}. {course.course_code}: {course.title}")
            print(f"   Department: {course.department}")
            print(f"   Description: {course.description[:100]}...")
    print()
    
    # Test 2: Direct CourseManager search
    print("=" * 80)
    print("Test 2: Direct CourseManager Search")
    print("=" * 80)
    test_queries = [
        "machine learning",
        "database",
        "web development",
        "python programming",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = await course_manager.search_courses(
            query=query,
            limit=3,
            similarity_threshold=0.6
        )
        print(f"   Results: {len(results)} courses found")
        
        if results:
            for i, course in enumerate(results, 1):
                print(f"   {i}. {course.course_code}: {course.title}")
        else:
            print("   ⚠️  No courses found!")
    print()
    
    # Test 3: Lower similarity threshold
    print("=" * 80)
    print("Test 3: Search with Lower Threshold (0.3)")
    print("=" * 80)
    query = "machine learning"
    print(f"🔍 Query: '{query}'")
    results = await course_manager.search_courses(
        query=query,
        limit=5,
        similarity_threshold=0.3  # Lower threshold
    )
    print(f"   Results: {len(results)} courses found")
    
    if results:
        for i, course in enumerate(results, 1):
            print(f"   {i}. {course.course_code}: {course.title}")
            print(f"      Department: {course.department}")
    print()
    
    # Test 4: Test the search_courses tool
    print("=" * 80)
    print("Test 4: Agent Tool Search (search_courses)")
    print("=" * 80)
    
    # Initialize the tool with course_manager
    from agent.tools import initialize_tools
    initialize_tools(course_manager)
    
    query = "machine learning courses"
    print(f"🔍 Query: '{query}'")
    result = await search_courses(query, top_k=3)
    print("\nTool Result:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    print()
    
    # Test 5: Check course content for embeddings
    print("=" * 80)
    print("Test 5: Sample Course Content")
    print("=" * 80)
    if all_courses:
        sample = all_courses[0]
        print(f"Course: {sample.course_code}: {sample.title}")
        print(f"Department: {sample.department}")
        print(f"Major: {sample.major}")
        print(f"Tags: {', '.join(sample.tags)}")
        print(f"Description: {sample.description}")
        print(f"Learning Objectives: {', '.join(sample.learning_objectives[:2])}...")
        
        # Show what gets embedded
        content = f"{sample.title} {sample.description} {sample.department} {sample.major} {' '.join(sample.tags)} {' '.join(sample.learning_objectives)}"
        print(f"\nEmbedded content length: {len(content)} chars")
        print(f"Embedded content preview: {content[:200]}...")
    print()
    
    # Test 6: Try different query formats
    print("=" * 80)
    print("Test 6: Different Query Formats")
    print("=" * 80)
    
    query_variations = [
        "What machine learning courses are available?",
        "machine learning",
        "ML courses",
        "artificial intelligence",
        "data science",
    ]
    
    for query in query_variations:
        print(f"\n🔍 Query: '{query}'")
        results = await course_manager.search_courses(
            query=query,
            limit=2,
            similarity_threshold=0.5
        )
        print(f"   Results: {len(results)} courses")
        if results:
            print(f"   Top: {results[0].course_code}: {results[0].title}")
    
    print()
    print("=" * 80)
    print("✅ Debug Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_course_search())

