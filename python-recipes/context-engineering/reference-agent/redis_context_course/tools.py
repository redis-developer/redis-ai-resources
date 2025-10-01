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


class StoreMemoryInput(BaseModel):
    """Input schema for storing memories."""
    text: str = Field(description="The information to remember")
    memory_type: str = Field(
        default="semantic",
        description="Type of memory: 'semantic' for facts, 'episodic' for events"
    )
    topics: List[str] = Field(
        default=[],
        description="Topics/tags for this memory (e.g., ['preferences', 'courses'])"
    )


class SearchMemoriesInput(BaseModel):
    """Input schema for searching memories."""
    query: str = Field(description="What to search for in memories")
    limit: int = Field(default=5, description="Maximum number of memories to retrieve")


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
def create_memory_tools(memory_client: MemoryAPIClient):
    """
    Create memory-related tools.

    These tools are demonstrated in Section 3, notebook 04_memory_tools.ipynb.
    They give the LLM explicit control over memory operations.
    """
    
    @tool(args_schema=StoreMemoryInput)
    async def store_memory(text: str, memory_type: str = "semantic", topics: List[str] = []) -> str:
        """
        Store important information in long-term memory.
        
        Use this tool when:
        - Student shares preferences (e.g., "I prefer online courses")
        - Student states goals (e.g., "I want to graduate in 2026")
        - Student provides important facts (e.g., "My major is Computer Science")
        - You learn something that should be remembered for future sessions
        
        Do NOT use for:
        - Temporary conversation context (working memory handles this)
        - Trivial details
        - Information that changes frequently
        
        Examples:
        - text="Student prefers morning classes", memory_type="semantic", topics=["preferences", "schedule"]
        - text="Student completed CS101 with grade A", memory_type="episodic", topics=["courses", "grades"]
        """
        try:
            from agent_memory_client import ClientMemoryRecord

            # Note: user_id should be passed from the calling context
            # For now, we'll let the client use its default namespace
            memory = ClientMemoryRecord(
                text=text,
                memory_type=memory_type,
                topics=topics if topics else ["general"]
            )

            await memory_client.create_long_term_memory([memory])
            return f"✅ Stored memory: {text}"
        except Exception as e:
            return f"❌ Failed to store memory: {str(e)}"
    
    @tool(args_schema=SearchMemoriesInput)
    async def search_memories(query: str, limit: int = 5) -> str:
        """
        Search for relevant memories using semantic search.
        
        Use this tool when:
        - You need to recall information about the student
        - Student asks "What do you know about me?"
        - You need context from previous sessions
        - Making personalized recommendations
        
        The search uses semantic matching, so natural language queries work well.
        
        Examples:
        - query="student preferences" → finds preference-related memories
        - query="completed courses" → finds course completion records
        - query="goals" → finds student's stated goals
        """
        try:
            results = await memory_client.search_long_term_memory(
                text=query,
                limit=limit
            )

            if not results.memories:
                return "No relevant memories found."

            result = f"Found {len(results.memories)} relevant memories:\n\n"
            for i, memory in enumerate(results.memories, 1):
                result += f"{i}. {memory.text}\n"
                result += f"   Type: {memory.memory_type} | Topics: {', '.join(memory.topics)}\n\n"
            
            return result
        except Exception as e:
            return f"❌ Failed to search memories: {str(e)}"
    
    return [store_memory, search_memories]


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

