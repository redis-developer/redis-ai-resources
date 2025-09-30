#!/usr/bin/env python3
"""
Demo script showing how to use the redis-context-course package.

This script demonstrates the basic usage of the package components
without requiring external dependencies like Redis or OpenAI.
"""

import asyncio
from datetime import time
from redis_context_course.models import (
    Course, StudentProfile, DifficultyLevel, CourseFormat, 
    Semester, DayOfWeek, CourseSchedule, Prerequisite
)


def demo_models():
    """Demonstrate the data models."""
    print("🎓 Redis Context Course - Demo")
    print("=" * 50)
    
    print("\n📚 Creating a sample course:")
    
    # Create a course schedule
    schedule = CourseSchedule(
        days=[DayOfWeek.MONDAY, DayOfWeek.WEDNESDAY, DayOfWeek.FRIDAY],
        start_time=time(10, 0),
        end_time=time(11, 30),
        location="Science Hall 101"
    )
    
    # Create prerequisites
    prereq = Prerequisite(
        course_code="CS101",
        course_title="Introduction to Programming",
        minimum_grade="C",
        can_be_concurrent=False
    )
    
    # Create a course
    course = Course(
        course_code="CS201",
        title="Data Structures and Algorithms",
        description="Study of fundamental data structures and algorithms including arrays, linked lists, trees, graphs, sorting, and searching.",
        credits=4,
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        format=CourseFormat.HYBRID,
        department="Computer Science",
        major="Computer Science",
        prerequisites=[prereq],
        schedule=schedule,
        semester=Semester.FALL,
        year=2024,
        instructor="Dr. Jane Smith",
        max_enrollment=50,
        current_enrollment=35,
        tags=["algorithms", "data structures", "programming"],
        learning_objectives=[
            "Implement common data structures",
            "Analyze algorithm complexity",
            "Solve problems using appropriate data structures",
            "Understand time and space complexity"
        ]
    )
    
    print(f"  Course: {course.course_code} - {course.title}")
    print(f"  Credits: {course.credits}")
    print(f"  Difficulty: {course.difficulty_level.value}")
    print(f"  Format: {course.format.value}")
    print(f"  Schedule: {', '.join([day.value for day in course.schedule.days])}")
    print(f"  Time: {course.schedule.start_time} - {course.schedule.end_time}")
    print(f"  Prerequisites: {len(course.prerequisites)} required")
    print(f"  Enrollment: {course.current_enrollment}/{course.max_enrollment}")
    
    print("\n👤 Creating a student profile:")
    
    student = StudentProfile(
        name="Alex Johnson",
        email="alex.johnson@university.edu",
        major="Computer Science",
        year=2,
        completed_courses=["CS101", "MATH101", "ENG101"],
        current_courses=["CS201", "MATH201"],
        interests=["machine learning", "web development", "data science"],
        preferred_format=CourseFormat.ONLINE,
        preferred_difficulty=DifficultyLevel.INTERMEDIATE,
        max_credits_per_semester=15
    )
    
    print(f"  Name: {student.name}")
    print(f"  Major: {student.major} (Year {student.year})")
    print(f"  Completed: {len(student.completed_courses)} courses")
    print(f"  Current: {len(student.current_courses)} courses")
    print(f"  Interests: {', '.join(student.interests)}")
    print(f"  Preferences: {student.preferred_format.value}, {student.preferred_difficulty.value}")
    
    return course, student


def demo_package_info():
    """Show package information."""
    print("\n📦 Package Information:")
    
    import redis_context_course
    
    print(f"  Version: {redis_context_course.__version__}")
    print(f"  Author: {redis_context_course.__author__}")
    print(f"  Description: {redis_context_course.__description__}")
    
    print("\n🔧 Available Components:")
    components = [
        ("Models", "Data structures for courses, students, and memory"),
        ("MemoryManager", "Handles long-term memory (cross-session knowledge)"),
        ("WorkingMemory", "Handles working memory (task-focused context)"),
        ("CourseManager", "Course storage and recommendation engine"),
        ("ClassAgent", "LangGraph-based conversational agent"),
        ("RedisConfig", "Redis connection and index management")
    ]
    
    for name, description in components:
        available = "✅" if getattr(redis_context_course, name, None) is not None else "❌"
        print(f"  {available} {name}: {description}")
    
    print("\n💡 Note: Some components require external dependencies (Redis, OpenAI)")
    print("   Install with: pip install redis-context-course")
    print("   Then set up Redis and OpenAI API key to use all features")


def demo_usage_examples():
    """Show usage examples."""
    print("\n💻 Usage Examples:")
    
    print("\n1. Basic Model Usage:")
    print("```python")
    print("from redis_context_course.models import Course, DifficultyLevel")
    print("")
    print("# Create a course")
    print("course = Course(")
    print("    course_code='CS101',")
    print("    title='Introduction to Programming',")
    print("    difficulty_level=DifficultyLevel.BEGINNER,")
    print("    # ... other fields")
    print(")")
    print("```")
    
    print("\n2. Agent Usage (requires dependencies):")
    print("```python")
    print("import asyncio")
    print("from redis_context_course import ClassAgent")
    print("")
    print("async def main():")
    print("    agent = ClassAgent('student_123')")
    print("    response = await agent.chat('I want to learn programming')")
    print("    print(response)")
    print("")
    print("asyncio.run(main())")
    print("```")
    
    print("\n3. Command Line Usage:")
    print("```bash")
    print("# Generate sample course data")
    print("generate-courses --courses-per-major 10")
    print("")
    print("# Ingest data into Redis")
    print("ingest-courses --catalog course_catalog.json")
    print("")
    print("# Start interactive agent")
    print("redis-class-agent --student-id your_name")
    print("```")


def main():
    """Run the demo."""
    try:
        # Demo the models
        course, student = demo_models()
        
        # Show package info
        demo_package_info()
        
        # Show usage examples
        demo_usage_examples()
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Install Redis 8: docker run -d --name redis -p 6379:6379 redis:8-alpine")
        print("2. Set OPENAI_API_KEY environment variable")
        print("3. Try the interactive agent: redis-class-agent --student-id demo")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
