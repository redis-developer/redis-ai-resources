"""
Stage 2: Context Engineering Utilities

This module provides context transformation and optimization functions
that demonstrate the techniques taught in Section 2 of the course.

Key Techniques:
1. Context Cleaning - Remove unnecessary fields
2. Context Transformation - Convert to natural text format
3. Context Compression - Optimize token usage
4. Token Counting - Measure improvements

Educational Purpose:
Students see how each technique reduces token usage while maintaining
or improving answer quality.
"""

from typing import List
import tiktoken
from redis_context_course import Course


def clean_course_data(course: Course) -> dict:
    """
    Clean course data by removing unnecessary fields.
    
    Removes:
    - Internal IDs (id, created_at, updated_at)
    - Enrollment data (current_enrollment, max_enrollment)
    - Other metadata not relevant for Q&A
    
    Keeps:
    - Course identification (course_code, title)
    - Academic info (department, credits, difficulty, format)
    - Content (description, learning_objectives)
    - Prerequisites
    - Instructor and schedule
    
    Args:
        course: Course object
        
    Returns:
        Cleaned dictionary with only relevant fields
    """
    return {
        "course_code": course.course_code,
        "title": course.title,
        "description": course.description,
        "department": course.department,
        "credits": course.credits,
        "difficulty_level": course.difficulty_level.value,
        "format": course.format.value,
        "instructor": course.instructor,
        "semester": course.semester.value,
        "year": course.year,
        "tags": course.tags,
        "learning_objectives": course.learning_objectives,
        "prerequisites": [
            {
                "course_code": p.course_code,
                "course_title": p.course_title,
                "minimum_grade": p.minimum_grade
            }
            for p in course.prerequisites
        ] if course.prerequisites else [],
    }


def transform_course_to_text(course: Course) -> str:
    """
    Transform course object to natural text format.
    
    This is the key optimization from Section 2:
    - Natural language instead of JSON
    - Structured but readable
    - ~30% fewer tokens than JSON
    - Easier for LLM to parse
    
    Args:
        course: Course object
        
    Returns:
        Natural text representation
    """
    # Build prerequisites text
    prereq_text = ""
    if course.prerequisites:
        prereq_codes = [p.course_code for p in course.prerequisites]
        prereq_text = f"\nPrerequisites: {', '.join(prereq_codes)}"
    
    # Build learning objectives text
    objectives_text = ""
    if course.learning_objectives:
        objectives_text = "\nLearning Objectives:\n" + "\n".join(
            f"  - {obj}" for obj in course.learning_objectives
        )
    
    # Build tags text
    tags_text = ""
    if course.tags:
        tags_text = f"\nTags: {', '.join(course.tags)}"
    
    # Assemble full text
    course_text = f"""{course.course_code}: {course.title}
Department: {course.department}
Credits: {course.credits}
Level: {course.difficulty_level.value}
Format: {course.format.value}
Instructor: {course.instructor}
Semester: {course.semester.value} {course.year}{prereq_text}

Description: {course.description}{objectives_text}{tags_text}
"""
    
    return course_text.strip()


def optimize_course_text(course: Course) -> str:
    """
    Create ultra-compact course description.
    
    This is the most aggressive optimization:
    - Only essential information
    - Minimal formatting
    - ~50% fewer tokens than natural text
    - Still maintains clarity
    
    Use when token budget is tight.
    
    Args:
        course: Course object
        
    Returns:
        Compact text representation
    """
    # Build compact prerequisites
    prereqs = ""
    if course.prerequisites:
        prereq_codes = [p.course_code for p in course.prerequisites]
        prereqs = f" (Prereq: {', '.join(prereq_codes)})"
    
    # Truncate description if too long
    description = course.description
    if len(description) > 150:
        description = description[:147] + "..."
    
    # Ultra-compact format
    return f"{course.course_code}: {course.title} - {description}{prereqs}"


def format_courses_as_text(courses: List[Course], optimization_level: str = "standard") -> str:
    """
    Format multiple courses as text with specified optimization level.
    
    Optimization Levels:
    - "none": Raw JSON (Stage 1 baseline)
    - "standard": Natural text format (recommended)
    - "aggressive": Ultra-compact format (maximum token savings)
    
    Args:
        courses: List of Course objects
        optimization_level: Level of optimization to apply
        
    Returns:
        Formatted text string
    """
    if optimization_level == "none":
        # This would be JSON format (Stage 1)
        import json
        return json.dumps([clean_course_data(c) for c in courses], indent=2)
    
    elif optimization_level == "aggressive":
        # Ultra-compact format
        course_texts = [optimize_course_text(c) for c in courses]
        return "\n\n".join(course_texts)
    
    else:  # "standard"
        # Natural text format (recommended)
        course_texts = [transform_course_to_text(c) for c in courses]
        return "\n\n---\n\n".join(course_texts)


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in text using tiktoken.
    
    Args:
        text: Text to count tokens for
        model: Model name for encoding
        
    Returns:
        Number of tokens
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def compare_formats(courses: List[Course]) -> dict:
    """
    Compare token usage across different formatting strategies.
    
    Educational tool to show the impact of each optimization.
    
    Args:
        courses: List of Course objects
        
    Returns:
        Dictionary with metrics for each format
    """
    import json
    
    # Stage 1: Raw JSON with ALL fields (baseline)
    raw_json = json.dumps([
        {
            "id": c.id,
            "course_code": c.course_code,
            "title": c.title,
            "description": c.description,
            "department": c.department,
            "credits": c.credits,
            "difficulty_level": c.difficulty_level.value,
            "format": c.format.value,
            "instructor": c.instructor,
            "semester": c.semester.value,
            "year": c.year,
            "max_enrollment": c.max_enrollment,
            "current_enrollment": c.current_enrollment,
            "tags": c.tags,
            "learning_objectives": c.learning_objectives,
            "prerequisites": [
                {"course_code": p.course_code, "course_title": p.course_title, "minimum_grade": p.minimum_grade}
                for p in c.prerequisites
            ] if c.prerequisites else [],
            "created_at": str(c.created_at),
            "updated_at": str(c.updated_at),
        }
        for c in courses
    ], indent=2)
    
    # Stage 2: Cleaned JSON
    cleaned_json = json.dumps([clean_course_data(c) for c in courses], indent=2)
    
    # Stage 2: Natural text (standard)
    natural_text = format_courses_as_text(courses, optimization_level="standard")
    
    # Stage 2: Compact text (aggressive)
    compact_text = format_courses_as_text(courses, optimization_level="aggressive")
    
    # Calculate metrics
    raw_tokens = count_tokens(raw_json)
    cleaned_tokens = count_tokens(cleaned_json)
    natural_tokens = count_tokens(natural_text)
    compact_tokens = count_tokens(compact_text)
    
    return {
        "raw_json": {
            "tokens": raw_tokens,
            "format": "JSON with all fields",
            "optimization": "none",
            "reduction_vs_baseline": "0%"
        },
        "cleaned_json": {
            "tokens": cleaned_tokens,
            "format": "JSON with cleaned fields",
            "optimization": "cleaning",
            "reduction_vs_baseline": f"{((raw_tokens - cleaned_tokens) / raw_tokens * 100):.1f}%"
        },
        "natural_text": {
            "tokens": natural_tokens,
            "format": "Natural text",
            "optimization": "cleaning + transformation",
            "reduction_vs_baseline": f"{((raw_tokens - natural_tokens) / raw_tokens * 100):.1f}%"
        },
        "compact_text": {
            "tokens": compact_tokens,
            "format": "Compact text",
            "optimization": "cleaning + transformation + compression",
            "reduction_vs_baseline": f"{((raw_tokens - compact_tokens) / raw_tokens * 100):.1f}%"
        }
    }


# Example usage
if __name__ == "__main__":
    import asyncio
    from redis_context_course import CourseManager
    
    async def demo():
        """Demonstrate context optimization techniques."""
        manager = CourseManager()
        courses = await manager.search_courses("machine learning", limit=5)
        
        print("=== Context Optimization Comparison ===\n")
        
        metrics = compare_formats(courses)
        
        for format_name, data in metrics.items():
            print(f"{format_name.upper()}:")
            print(f"  Tokens: {data['tokens']:,}")
            print(f"  Format: {data['format']}")
            print(f"  Reduction: {data['reduction_vs_baseline']}")
            print()
    
    asyncio.run(demo())

