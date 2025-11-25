"""
Tools for the Course Q&A Agent workflow.

Uses CourseManager for semantic course search and applies context engineering
techniques from Section 2 notebooks.
"""

import logging
from typing import Any, List, Dict, Optional
from redis_context_course import CourseManager
from redis_context_course.models import Course

# Configure logger
logger = logging.getLogger("course-qa-workflow")

# Global variables that will be set during initialization
course_manager: Optional[CourseManager] = None


def initialize_tools(manager: CourseManager):
    """
    Initialize tools with required dependencies.
    
    Args:
        manager: CourseManager instance for course search
    """
    global course_manager
    course_manager = manager


def transform_course_to_text(course: Course) -> str:
    """
    Transform course object to LLM-optimized text format.
    
    This is the context engineering technique from Section 2 Notebook 2.
    Converts structured course data into natural text format that's easier
    for LLMs to process.
    
    Args:
        course: Course object to transform
        
    Returns:
        LLM-friendly text representation
    """
    # Build prerequisites text
    prereq_text = ""
    if course.prerequisites:
        prereq_codes = [p.course_code for p in course.prerequisites]
        prereq_text = f"\nPrerequisites: {', '.join(prereq_codes)}"
    
    # Build learning objectives text
    objectives_text = ""
    if course.learning_objectives:
        objectives_text = f"\nLearning Objectives:\n" + "\n".join(
            f"  - {obj}" for obj in course.learning_objectives
        )
    
    # Build course text
    course_text = f"""{course.course_code}: {course.title}
Department: {course.department}
Credits: {course.credits}
Level: {course.difficulty_level.value}
Format: {course.format.value}
Instructor: {course.instructor}{prereq_text}
Description: {course.description}{objectives_text}"""
    
    return course_text


def optimize_course_text(course: Course) -> str:
    """
    Create ultra-compact course description.
    
    This is the optimization technique from Section 2 Notebook 2.
    Reduces token count while preserving essential information.
    
    Args:
        course: Course object to optimize
        
    Returns:
        Compact text representation
    """
    prereqs = (
        f" (Prereq: {', '.join([p.course_code for p in course.prerequisites])})"
        if course.prerequisites
        else ""
    )
    return (
        f"{course.course_code}: {course.title} - {course.description[:100]}...{prereqs}"
    )


async def search_courses(
    query: str, 
    top_k: int = 5,
    use_optimized_format: bool = False
) -> str:
    """
    Search for relevant courses using semantic search.
    
    This tool uses CourseManager.search_courses() for semantic retrieval
    and applies context engineering techniques to format results.
    
    Args:
        query: Search query
        top_k: Number of top results to return
        use_optimized_format: If True, use compact format; if False, use full format
        
    Returns:
        Formatted search results as string
    """
    if not course_manager:
        return "Course search not available - CourseManager not initialized"
    
    try:
        # Search for courses using semantic search
        results = await course_manager.search_courses(
            query=query,
            filters=None,
            limit=top_k,
            similarity_threshold=0.6
        )
        
        if not results:
            return "No relevant courses found"
        
        # Format results using context engineering techniques
        formatted_results = []
        
        for i, course in enumerate(results, 1):
            if use_optimized_format:
                # Use compact format (Stage 3 optimization)
                course_text = optimize_course_text(course)
            else:
                # Use full LLM-friendly format (Stage 2 transformation)
                course_text = transform_course_to_text(course)
            
            formatted_results.append(f"Course {i}:\n{course_text}")
        
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Course search failed: {e}")
        return f"Search failed: {str(e)}"


# NOTE: Original caching-agent used knowledge_base search with web content
# We've replaced this with CourseManager.search_courses() for course data
# The original implementation is preserved below for reference:

# ORIGINAL IMPLEMENTATION (COMMENTED OUT):
# """
# def search_knowledge_base(query: str, top_k: int = 3) -> str:
#     if not knowledge_base_index or not embeddings:
#         return "Knowledge base not available"
#     
#     try:
#         query_embedding = embeddings.embed(query)
#         vector_query = VectorQuery(
#             vector=query_embedding,
#             vector_field_name="embedding",
#             return_fields=["content", "source_id", "chunk_id"],
#             num_results=top_k
#         )
#         
#         results = knowledge_base_index.query(vector_query)
#         
#         if not results:
#             return "No relevant information found in knowledge base"
#         
#         formatted_results = []
#         for i, result in enumerate(results, 1):
#             content = result.get("content", "").strip()
#             if content:
#                 formatted_results.append(f"Result {i}:\n{content}")
#         
#         if not formatted_results:
#             return "No relevant content found"
#         
#         return "\n\n".join(formatted_results)
#         
#     except Exception as e:
#         logger.error(f"Knowledge base search failed: {e}")
#         return f"Search failed: {str(e)}"
# """

