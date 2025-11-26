"""
Context Engineering Functions for Stage 2.

These functions are from Section 2 Notebook 2 and demonstrate
the core context engineering techniques:
1. Context Cleaning - Remove noise fields
2. Context Transformation - JSON → natural text
3. Context Optimization - Token compression

Students will see how these techniques improve upon Stage 1's raw context.
"""

from redis_context_course.models import Course


def transform_course_to_text(course: Course) -> str:
    """
    Transform course object to LLM-optimized text format.

    This is the context engineering technique from Section 2 Notebook 2.
    Converts structured course data into natural text format that's easier
    for LLMs to process.

    Context Engineering Steps Applied:
    1. CLEAN: Only include relevant fields (no id, timestamps, enrollment)
    2. TRANSFORM: Convert JSON → natural text format
    3. STRUCTURE: Use consistent, readable formatting

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

    # Build course text (CLEANED and TRANSFORMED)
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

    Use this when you need maximum token efficiency (e.g., many courses).
    Use transform_course_to_text() when you need full details.

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


def format_courses_for_llm(courses: list[Course], use_optimized: bool = False) -> str:
    """
    Format a list of courses for LLM consumption.

    Applies context engineering to all courses and combines them
    into a single, well-structured context string.

    Args:
        courses: List of Course objects
        use_optimized: If True, use compact format; if False, use full format

    Returns:
        Formatted context string ready for LLM
    """
    if not courses:
        return "No courses found."

    formatted_courses = []

    for i, course in enumerate(courses, 1):
        if use_optimized:
            course_text = optimize_course_text(course)
        else:
            course_text = transform_course_to_text(course)

        formatted_courses.append(f"Course {i}:\n{course_text}")

    return "\n\n".join(formatted_courses)
