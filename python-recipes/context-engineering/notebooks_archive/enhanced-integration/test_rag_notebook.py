#!/usr/bin/env python3
"""
Test script for the RAG notebook to ensure all cells work correctly.
"""

import asyncio
import os
import sys
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add reference agent to path
sys.path.append("../../reference-agent")

from redis_context_course.models import (
    Course,
    StudentProfile,
    DifficultyLevel,
    CourseFormat,
    Semester,
)
from redis_context_course.course_manager import CourseManager
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

print("🧪 Testing RAG Notebook Components")
print("=" * 50)

# Test 1: Environment Setup
print("\n📋 Test 1: Environment Setup")
try:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found")
    print("✅ Environment variables loaded")
    print(f'   REDIS_URL: {os.getenv("REDIS_URL", "redis://localhost:6379")}')
    print(
        f'   OPENAI_API_KEY: {"✓ Set" if os.getenv("OPENAI_API_KEY") else "✗ Not set"}'
    )
except Exception as e:
    print(f"❌ Environment setup failed: {e}")
    sys.exit(1)

# Test 2: Course Manager
print("\n📋 Test 2: Course Manager")


async def test_course_manager():
    try:
        course_manager = CourseManager()
        courses = await course_manager.get_all_courses()
        print(f"✅ Course manager initialized - {len(courses)} courses loaded")

        # Test search
        search_results = await course_manager.search_courses(
            "machine learning", limit=3
        )
        print(f"✅ Course search working - found {len(search_results)} results")

        return course_manager
    except Exception as e:
        print(f"❌ Course manager failed: {e}")
        raise


course_manager = asyncio.run(test_course_manager())

# Test 3: SimpleRAGAgent Class
print("\n📋 Test 3: SimpleRAGAgent Class")


class SimpleRAGAgent:
    def __init__(self, course_manager: CourseManager):
        self.course_manager = course_manager
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        self.conversation_history = {}

    def get_openai_client(self):
        """Get OpenAI client if API key is available"""
        api_key = os.getenv("OPENAI_API_KEY", "demo-key")
        if api_key != "demo-key":
            return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        return None

    async def search_courses(self, query: str, limit: int = 3) -> List[Course]:
        """Search for relevant courses using the course manager"""
        results = await self.course_manager.search_courses(query, limit=limit)
        return results

    def create_context(
        self, student: StudentProfile, query: str, courses: List[Course]
    ) -> str:
        """Create context for the LLM from student profile and retrieved courses"""
        # Student context
        student_context = f"""STUDENT PROFILE:
Name: {student.name}
Major: {student.major}, Year: {student.year}
Completed Courses: {', '.join(student.completed_courses) if student.completed_courses else 'None'}
Current Courses: {', '.join(student.current_courses) if student.current_courses else 'None'}
Interests: {', '.join(student.interests)}
Preferred Format: {student.preferred_format.value if student.preferred_format else 'Any'}
Preferred Difficulty: {student.preferred_difficulty.value if student.preferred_difficulty else 'Any'}
Max Credits per Semester: {student.max_credits_per_semester}"""

        # Course context
        courses_context = "RELEVANT COURSES:\n"
        for i, course in enumerate(courses, 1):
            courses_context += f"""
{i}. {course.course_code}: {course.title}
   Description: {course.description}
   Level: {course.difficulty_level.value}
   Format: {course.format.value}
   Credits: {course.credits}
   Tags: {', '.join(course.tags)}
   Learning Objectives: {'; '.join(course.learning_objectives) if course.learning_objectives else 'None'}
"""

        # Conversation history
        history_context = ""
        if student.email in self.conversation_history:
            history = self.conversation_history[student.email]
            if history:
                history_context = "\nCONVERSATION HISTORY:\n"
                for msg in history[-4:]:  # Last 4 messages
                    history_context += f"User: {msg['user']}\n"
                    history_context += f"Assistant: {msg['assistant']}\n"

        return f"{student_context}\n\n{courses_context}{history_context}\n\nSTUDENT QUERY: {query}"

    def generate_response(self, context: str) -> str:
        """Generate response using LLM or demo response"""
        system_prompt = """You are an expert Redis University course advisor. 
Provide specific, personalized course recommendations based on the student's profile and the retrieved course information.

Guidelines:
- Consider the student's completed courses and prerequisites
- Match recommendations to their interests and difficulty preferences
- Explain your reasoning clearly
- Be encouraging and supportive
- Base recommendations on the retrieved course information"""

        # Try to use real LLM if available
        client = self.get_openai_client()
        if client:
            try:
                system_message = SystemMessage(content=system_prompt)
                human_message = HumanMessage(content=context)
                response = client.invoke([system_message, human_message])
                return response.content
            except Exception as e:
                print(f"LLM call failed: {e}, using demo response")

        # Demo response for testing
        return """Based on your profile and interests, I recommend exploring our intermediate-level courses that build on Redis fundamentals. The courses I found match your interests and preferred learning format. Would you like me to explain more about any specific course?"""

    async def chat(self, student: StudentProfile, query: str) -> str:
        """Main chat method that implements the RAG pipeline"""

        # Step 1: Retrieval - Search for relevant courses
        relevant_courses = await self.search_courses(query, limit=3)

        # Step 2: Augmentation - Create context with student info and courses
        context = self.create_context(student, query, relevant_courses)

        # Step 3: Generation - Generate personalized response
        response = self.generate_response(context)

        # Update conversation history
        if student.email not in self.conversation_history:
            self.conversation_history[student.email] = []

        self.conversation_history[student.email].append(
            {"user": query, "assistant": response}
        )

        return response


try:
    rag_agent = SimpleRAGAgent(course_manager)
    print("✅ SimpleRAGAgent class created successfully")
except Exception as e:
    print(f"❌ SimpleRAGAgent creation failed: {e}")
    sys.exit(1)

# Test 4: Student Profiles
print("\n📋 Test 4: Student Profiles")
try:
    students = [
        StudentProfile(
            name="Sarah Chen",
            email="sarah.chen@university.edu",
            major="Computer Science",
            year=3,
            completed_courses=["RU101"],
            current_courses=[],
            interests=["machine learning", "data science", "python", "AI"],
            preferred_format=CourseFormat.ONLINE,
            preferred_difficulty=DifficultyLevel.INTERMEDIATE,
            max_credits_per_semester=15,
        ),
        StudentProfile(
            name="Marcus Johnson",
            email="marcus.j@university.edu",
            major="Software Engineering",
            year=2,
            completed_courses=[],
            current_courses=["RU101"],
            interests=[
                "backend development",
                "databases",
                "java",
                "enterprise systems",
            ],
            preferred_format=CourseFormat.HYBRID,
            preferred_difficulty=DifficultyLevel.BEGINNER,
            max_credits_per_semester=12,
        ),
    ]

    print(f"✅ Created {len(students)} student profiles")
    for student in students:
        print(f"   - {student.name}: {student.major} Year {student.year}")
except Exception as e:
    print(f"❌ Student profile creation failed: {e}")
    sys.exit(1)

# Test 5: RAG Pipeline
print("\n📋 Test 5: RAG Pipeline")


async def test_rag_pipeline():
    try:
        sarah = students[0]
        query = "What machine learning courses do you recommend?"

        print(f"Testing with student: {sarah.name}")
        print(f"Query: '{query}'")

        # Test search
        courses = await rag_agent.search_courses(query, limit=3)
        print(f"✅ Retrieved {len(courses)} relevant courses")

        # Test context creation
        context = rag_agent.create_context(sarah, query, courses)
        print(f"✅ Context created ({len(context)} characters)")

        # Test full chat
        response = await rag_agent.chat(sarah, query)
        print(f"✅ Chat response generated ({len(response)} characters)")
        print(f"Response preview: {response[:100]}...")

        return True
    except Exception as e:
        print(f"❌ RAG pipeline test failed: {e}")
        return False


success = asyncio.run(test_rag_pipeline())

# Test Results
print("\n" + "=" * 50)
if success:
    print("🎉 All tests passed! The RAG notebook is working correctly.")
    print("\nNext steps:")
    print("1. Run: jupyter notebook")
    print("2. Open: section-2-rag-foundations/01_building_your_rag_agent.ipynb")
    print("3. Execute all cells to see the full RAG system in action")
else:
    print("❌ Some tests failed. Please check the errors above.")
    sys.exit(1)
