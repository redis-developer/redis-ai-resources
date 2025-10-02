"""
Tools for the Redis University Class Agent.

This module defines the tools that the agent can use to interact with
the course catalog and student data. These tools are used in the notebooks
throughout the course.
"""

from typing import List, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .course_manager import CourseManager
from agent_memory_client import MemoryAPIClient


# Tool Input Schemas
class SearchCoursesInput(BaseModel):
    """Input schema for searching courses."""
    query: str = Field(
        description="Natural language search query. Can be topics (e.g., 'machine learning'), "
                    "characteristics (e.g., 'online courses'), or general questions "
                    "(e.g., 'beginner programming courses')"
    )
    limit: int = Field(
        default=5,
        description="Maximum number of results to return. Default is 5. "
                    "Use 3 for quick answers, 10 for comprehensive results."
    )


class GetCourseDetailsInput(BaseModel):
    """Input schema for getting course details."""
    course_code: str = Field(
        description="Specific course code like 'CS101' or 'MATH201'"
    )


class CheckPrerequisitesInput(BaseModel):
    """Input schema for checking prerequisites."""
    course_code: str = Field(
        description="Course code to check prerequisites for"
    )
    completed_courses: List[str] = Field(
        description="List of course codes the student has completed"
    )


# Course Tools
def create_course_tools(course_manager: CourseManager):
    """
    Create course-related tools.
    
    These tools are demonstrated in Section 2 notebooks.
    """
    
    @tool(args_schema=SearchCoursesInput)
    async def search_courses(query: str, limit: int = 5) -> str:
        """
        Search for courses using semantic search based on topics, descriptions, or characteristics.
        
        Use this tool when students ask about:
        - Topics or subjects: "machine learning courses", "database courses"
        - Course characteristics: "online courses", "beginner courses", "3-credit courses"
        - General exploration: "what courses are available in AI?"
        
        Do NOT use this tool when:
        - Student asks about a specific course code (use get_course_details instead)
        - Student wants all courses in a department (use a filter instead)
        
        The search uses semantic matching, so natural language queries work well.
        
        Examples:
        - "machine learning courses" → finds CS401, CS402, etc.
        - "beginner programming" → finds CS101, CS102, etc.
        - "online data science courses" → finds online courses about data science
        """
        results = await course_manager.search_courses(query, limit=limit)
        
        if not results:
            return "No courses found matching your query."
        
        output = []
        for course in results:
            output.append(
                f"{course.course_code}: {course.title}\n"
                f"  Credits: {course.credits} | {course.format.value} | {course.difficulty_level.value}\n"
                f"  {course.description[:150]}..."
            )
        
        return "\n\n".join(output)
    
    @tool(args_schema=GetCourseDetailsInput)
    async def get_course_details(course_code: str) -> str:
        """
        Get detailed information about a specific course by its course code.
        
        Use this tool when:
        - Student asks about a specific course (e.g., "Tell me about CS101")
        - You need prerequisites for a course
        - You need full course details (schedule, instructor, etc.)
        
        Returns complete course information including description, prerequisites,
        schedule, credits, and learning objectives.
        """
        course = await course_manager.get_course(course_code)
        
        if not course:
            return f"Course {course_code} not found."
        
        prereqs = "None" if not course.prerequisites else ", ".join(
            [f"{p.course_code} (min grade: {p.min_grade})" for p in course.prerequisites]
        )
        
        return f"""
{course.course_code}: {course.title}

Description: {course.description}

Details:
- Credits: {course.credits}
- Department: {course.department}
- Major: {course.major}
- Difficulty: {course.difficulty_level.value}
- Format: {course.format.value}
- Prerequisites: {prereqs}

Learning Objectives:
""" + "\n".join([f"- {obj}" for obj in course.learning_objectives])
    
    @tool(args_schema=CheckPrerequisitesInput)
    async def check_prerequisites(course_code: str, completed_courses: List[str]) -> str:
        """
        Check if a student meets the prerequisites for a specific course.
        
        Use this tool when:
        - Student asks "Can I take [course]?"
        - Student asks about prerequisites
        - You need to verify eligibility before recommending a course
        
        Returns whether the student is eligible and which prerequisites are missing (if any).
        """
        course = await course_manager.get_course(course_code)
        
        if not course:
            return f"Course {course_code} not found."
        
        if not course.prerequisites:
            return f"✅ {course_code} has no prerequisites. You can take this course!"
        
        missing = []
        for prereq in course.prerequisites:
            if prereq.course_code not in completed_courses:
                missing.append(f"{prereq.course_code} (min grade: {prereq.min_grade})")
        
        if not missing:
            return f"✅ You meet all prerequisites for {course_code}!"
        
        return f"""❌ You're missing prerequisites for {course_code}:

Missing:
""" + "\n".join([f"- {p}" for p in missing])
    
    return [search_courses, get_course_details, check_prerequisites]


# Memory Tools
def create_memory_tools(memory_client: MemoryAPIClient, session_id: str, user_id: str):
    """
    Create memory-related tools using the memory client's built-in LangChain integration.

    These tools are demonstrated in Section 3, notebook 04_memory_tools.ipynb.
    They give the LLM explicit control over memory operations.

    Args:
        memory_client: The memory client instance
        session_id: Session ID for the conversation
        user_id: User ID for the student

    Returns:
        List of LangChain StructuredTool objects for memory operations
    """
    from agent_memory_client.integrations.langchain import get_memory_tools

    return get_memory_tools(
        memory_client=memory_client,
        session_id=session_id,
        user_id=user_id
    )


# Tool Selection Helpers (from Section 4, notebook 04_tool_optimization.ipynb)
def select_tools_by_keywords(query: str, all_tools: dict) -> List:
    """
    Select relevant tools based on query keywords.
    
    This is a simple tool filtering strategy demonstrated in Section 4.
    For production, consider using intent classification or hierarchical tools.
    
    Args:
        query: User's query
        all_tools: Dictionary mapping categories to tool lists
        
    Returns:
        List of relevant tools
    """
    query_lower = query.lower()
    
    # Search-related keywords
    if any(word in query_lower for word in ['search', 'find', 'show', 'what', 'which', 'tell me about']):
        return all_tools.get("search", [])
    
    # Memory-related keywords
    elif any(word in query_lower for word in ['remember', 'recall', 'know about me', 'preferences']):
        return all_tools.get("memory", [])
    
    # Default: return search tools
    else:
        return all_tools.get("search", [])

