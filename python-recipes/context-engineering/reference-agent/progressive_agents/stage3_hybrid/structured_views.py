"""
Stage 3: Structured Views and Hybrid Retrieval

This module provides advanced context engineering patterns:
1. Structured catalog views (hierarchical organization)
2. Hybrid context assembly (overview + details)
3. Multi-strategy retrieval (semantic + metadata filtering)

Educational Purpose:
Students learn production-ready patterns that combine multiple
context engineering techniques for optimal results.
"""

from typing import List, Dict, Optional
from collections import defaultdict
from redis_context_course import Course


def create_catalog_view(courses: List[Course], max_per_department: int = 10) -> str:
    """
    Create a structured catalog overview organized by department.
    
    This provides a high-level view of available courses without
    overwhelming the LLM with full details. Useful for:
    - "What courses are available?" queries
    - Browsing and exploration
    - Getting oriented before diving into specifics
    
    Args:
        courses: List of Course objects
        max_per_department: Maximum courses to show per department
        
    Returns:
        Structured catalog text
    """
    # Group courses by department
    by_department = defaultdict(list)
    for course in courses:
        by_department[course.department].append(course)
    
    # Build catalog sections
    catalog_sections = []
    for dept_name in sorted(by_department.keys()):
        dept_courses = by_department[dept_name]
        
        # Department header
        dept_section = f"\n## {dept_name} ({len(dept_courses)} courses)\n"
        
        # Course summaries (compact format)
        course_summaries = []
        for course in dept_courses[:max_per_department]:
            summary = f"- {course.course_code}: {course.title} ({course.difficulty_level.value})"
            course_summaries.append(summary)
        
        if len(dept_courses) > max_per_department:
            course_summaries.append(f"- ... and {len(dept_courses) - max_per_department} more")
        
        dept_section += "\n".join(course_summaries)
        catalog_sections.append(dept_section)
    
    # Assemble full catalog
    catalog_view = "# Redis University Course Catalog\n" + "\n".join(catalog_sections)
    
    return catalog_view


def create_course_details(courses: List[Course]) -> str:
    """
    Create detailed course information in natural text format.
    
    This provides full details for specific courses. Use when:
    - User asks about specific courses
    - Need prerequisite information
    - Need learning objectives
    
    Args:
        courses: List of Course objects
        
    Returns:
        Detailed course text
    """
    from progressive_agents.stage2_optimized.context_utils import transform_course_to_text
    
    course_texts = [transform_course_to_text(c) for c in courses]
    return "\n\n---\n\n".join(course_texts)


def create_prerequisite_map(courses: List[Course]) -> str:
    """
    Create a prerequisite dependency map.
    
    Shows which courses require which prerequisites, useful for:
    - Planning learning paths
    - Understanding course sequences
    - Identifying foundational courses
    
    Args:
        courses: List of Course objects
        
    Returns:
        Prerequisite map text
    """
    lines = ["# Course Prerequisites\n"]
    
    for course in courses:
        if course.prerequisites:
            prereq_codes = [p.course_code for p in course.prerequisites]
            lines.append(f"- {course.course_code}: Requires {', '.join(prereq_codes)}")
        else:
            lines.append(f"- {course.course_code}: No prerequisites (foundational)")
    
    return "\n".join(lines)


def create_difficulty_progression(courses: List[Course]) -> str:
    """
    Create a difficulty-based progression view.
    
    Groups courses by difficulty level to help students plan
    their learning journey from beginner to advanced.
    
    Args:
        courses: List of Course objects
        
    Returns:
        Difficulty progression text
    """
    by_difficulty = defaultdict(list)
    for course in courses:
        by_difficulty[course.difficulty_level.value].append(course)
    
    # Order: beginner → intermediate → advanced
    difficulty_order = ["beginner", "intermediate", "advanced"]
    
    lines = ["# Course Difficulty Progression\n"]
    
    for level in difficulty_order:
        if level in by_difficulty:
            level_courses = by_difficulty[level]
            lines.append(f"\n## {level.title()} ({len(level_courses)} courses)")
            for course in level_courses:
                lines.append(f"- {course.course_code}: {course.title}")
    
    return "\n".join(lines)


def hybrid_context_assembly(
    query: str,
    all_courses: List[Course],
    relevant_courses: List[Course],
    include_catalog: bool = True,
    include_prerequisites: bool = False,
    include_difficulty: bool = False
) -> str:
    """
    Assemble hybrid context combining multiple views.
    
    This is the KEY PATTERN for Stage 3:
    - Structured overview (catalog view) for context
    - Detailed information (natural text) for specific courses
    - Optional supplementary views (prerequisites, difficulty)
    
    Result: Best of both worlds - overview + details
    
    Args:
        query: User's query (for context)
        all_courses: All available courses (for catalog view)
        relevant_courses: Semantically relevant courses (for details)
        include_catalog: Include catalog overview
        include_prerequisites: Include prerequisite map
        include_difficulty: Include difficulty progression
        
    Returns:
        Assembled hybrid context
    """
    sections = []
    
    # Section 1: Catalog overview (if requested)
    if include_catalog and all_courses:
        catalog = create_catalog_view(all_courses, max_per_department=5)
        sections.append(catalog)
    
    # Section 2: Detailed relevant courses
    if relevant_courses:
        details = create_course_details(relevant_courses)
        sections.append("\n# Relevant Courses (Detailed)\n\n" + details)
    
    # Section 3: Prerequisite map (if requested)
    if include_prerequisites and relevant_courses:
        prereq_map = create_prerequisite_map(relevant_courses)
        sections.append("\n" + prereq_map)
    
    # Section 4: Difficulty progression (if requested)
    if include_difficulty and relevant_courses:
        difficulty = create_difficulty_progression(relevant_courses)
        sections.append("\n" + difficulty)
    
    return "\n\n".join(sections)


def smart_context_selection(query: str, courses: List[Course]) -> Dict[str, bool]:
    """
    Intelligently decide which context views to include based on query.
    
    This demonstrates query-aware context engineering:
    - "What courses are available?" → Include catalog
    - "Prerequisites for X?" → Include prerequisite map
    - "Beginner courses?" → Include difficulty progression
    
    Args:
        query: User's query
        courses: Available courses
        
    Returns:
        Dictionary of view flags
    """
    query_lower = query.lower()
    
    # Default: just show relevant courses
    views = {
        "include_catalog": False,
        "include_prerequisites": False,
        "include_difficulty": False
    }
    
    # Catalog view triggers
    catalog_keywords = ["available", "what courses", "list", "catalog", "browse", "all courses"]
    if any(keyword in query_lower for keyword in catalog_keywords):
        views["include_catalog"] = True
    
    # Prerequisite view triggers
    prereq_keywords = ["prerequisite", "prereq", "required", "before", "sequence", "path"]
    if any(keyword in query_lower for keyword in prereq_keywords):
        views["include_prerequisites"] = True
    
    # Difficulty view triggers
    difficulty_keywords = ["beginner", "intermediate", "advanced", "easy", "hard", "difficulty", "level"]
    if any(keyword in query_lower for keyword in difficulty_keywords):
        views["include_difficulty"] = True
    
    return views


def estimate_token_savings(
    num_courses: int,
    use_catalog: bool = True,
    use_hybrid: bool = True
) -> Dict[str, int]:
    """
    Estimate token savings from hybrid approach.
    
    Educational tool to show the impact of structured views.
    
    Args:
        num_courses: Number of courses in catalog
        use_catalog: Whether to use catalog view
        use_hybrid: Whether to use hybrid assembly
        
    Returns:
        Token estimates for different approaches
    """
    # Rough estimates based on typical course data
    tokens_per_course_full = 500  # Full details (Stage 2)
    tokens_per_course_summary = 20  # Catalog summary
    tokens_per_course_detailed = 400  # Detailed view
    
    # Stage 2: All courses with full details
    stage2_tokens = num_courses * tokens_per_course_full
    
    # Stage 3: Catalog (all) + Details (top 5)
    if use_hybrid:
        catalog_tokens = num_courses * tokens_per_course_summary
        detail_tokens = min(5, num_courses) * tokens_per_course_detailed
        stage3_tokens = catalog_tokens + detail_tokens
    else:
        stage3_tokens = min(5, num_courses) * tokens_per_course_detailed
    
    return {
        "stage2_all_details": stage2_tokens,
        "stage3_hybrid": stage3_tokens,
        "savings": stage2_tokens - stage3_tokens,
        "reduction_percentage": round((stage2_tokens - stage3_tokens) / stage2_tokens * 100, 1)
    }


# Example usage
if __name__ == "__main__":
    import asyncio
    from redis_context_course import CourseManager
    
    async def demo():
        """Demonstrate structured views and hybrid assembly."""
        manager = CourseManager()
        
        # Get all courses
        all_courses = await manager.search_courses("", limit=50)
        
        # Get relevant courses for a query
        query = "What machine learning courses are available?"
        relevant_courses = await manager.search_courses("machine learning", limit=5)
        
        print("=== Catalog View ===")
        catalog = create_catalog_view(all_courses[:20])
        print(catalog[:500] + "...\n")
        
        print("=== Hybrid Context ===")
        views = smart_context_selection(query, relevant_courses)
        hybrid = hybrid_context_assembly(
            query=query,
            all_courses=all_courses[:20],
            relevant_courses=relevant_courses,
            **views
        )
        print(hybrid[:500] + "...\n")
        
        print("=== Token Savings ===")
        savings = estimate_token_savings(num_courses=50, use_hybrid=True)
        print(f"Stage 2 (all details): {savings['stage2_all_details']:,} tokens")
        print(f"Stage 3 (hybrid): {savings['stage3_hybrid']:,} tokens")
        print(f"Savings: {savings['savings']:,} tokens ({savings['reduction_percentage']}%)")
    
    asyncio.run(demo())

