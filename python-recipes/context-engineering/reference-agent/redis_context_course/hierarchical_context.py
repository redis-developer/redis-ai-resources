"""
Hierarchical context assembler for progressive disclosure.

This module demonstrates advanced Section 2 techniques:
- Structured views (summary vs detailed representations)
- Hybrid assembly (combining multiple retrieval strategies)
- Progressive disclosure (overview first, details on-demand)
- Context budget management (strategic token allocation)
"""

from typing import List, Tuple

from .hierarchical_models import CourseDetails, CourseSummary


class HierarchicalContextAssembler:
    """
    Assembles context using progressive disclosure pattern.

    Strategy:
    1. Show summaries for ALL matches (lightweight overview)
    2. Show full details for TOP N matches (deep information)

    This provides:
    - Broad awareness of all options
    - Deep understanding of best matches
    - Efficient token usage
    """

    def assemble_summary_only_context(
        self,
        summaries: List[CourseSummary],
        query: str,
    ) -> str:
        """
        Assemble context with ONLY summaries (no details).

        Use this for course overview queries where user just wants to know
        what courses exist, not full syllabi.

        Args:
            summaries: All course summaries (e.g., top 5)
            query: Original search query

        Returns:
            Assembled context string with summaries only
        """
        sections = []

        # Header
        sections.append(f"# Course Search Results for: {query}\n")

        # Summary Overview (ALL matches)
        sections.append(f"Found {len(summaries)} relevant courses:\n")

        for i, summary in enumerate(summaries, 1):
            sections.append(self._format_summary(summary, i))

        return "\n".join(sections)

    def assemble_hierarchical_context(
        self,
        summaries: List[CourseSummary],
        details: List[CourseDetails],
        query: str,
    ) -> str:
        """
        Assemble context with progressive disclosure.

        Args:
            summaries: All course summaries (e.g., top 5)
            details: Detailed courses (e.g., top 2-3)
            query: Original search query

        Returns:
            Assembled context string
        """
        sections = []

        # Header
        sections.append(f"# Course Search Results for: {query}\n")

        # Section 1: Summary Overview (ALL matches)
        sections.append("## Overview of All Matches\n")
        sections.append(f"Found {len(summaries)} relevant courses:\n")

        for i, summary in enumerate(summaries, 1):
            sections.append(self._format_summary(summary, i))

        # Section 2: Detailed Information (TOP matches)
        if details:
            sections.append(f"\n## Detailed Information (Top {len(details)} Courses)\n")
            sections.append(
                "Full syllabi and assignments for the most relevant courses:\n"
            )

            for detail in details:
                sections.append(self._format_details(detail))

        return "\n".join(sections)

    def _format_summary(self, summary: CourseSummary, index: int) -> str:
        """Format a course summary (lightweight)."""
        parts = [
            f"\n### {index}. {summary.course_code}: {summary.title}",
            f"**Department**: {summary.department}",
            f"**Instructor**: {summary.instructor}",
            f"**Credits**: {summary.credits} | **Level**: {summary.difficulty_level.value}",
            f"**Format**: {summary.format.value}",
            f"\n{summary.short_description}",
        ]

        if summary.prerequisite_codes:
            parts.append(
                f"\n**Prerequisites**: {', '.join(summary.prerequisite_codes)}"
            )

        if summary.tags:
            parts.append(f"**Tags**: {', '.join(summary.tags)}")

        return "\n".join(parts) + "\n"

    def _format_details(self, details: CourseDetails) -> str:
        """Format full course details (comprehensive)."""
        sections = [
            f"\n---\n## {details.course_code}: {details.title}",
            f"\n**Instructor**: {details.instructor}",
        ]

        # Description
        sections.append(f"\n### Description\n{details.full_description}")

        # Learning Objectives
        if details.learning_objectives:
            sections.append("\n### Learning Objectives")
            for obj in details.learning_objectives:
                sections.append(f"- {obj}")

        # Prerequisites
        if details.prerequisites:
            sections.append("\n### Prerequisites")
            for prereq in details.prerequisites:
                sections.append(f"- {prereq.course_code}: {prereq.course_title}")

        # Assignments Summary
        if details.assignments:
            sections.append(
                f"\n### Assignments ({details.get_total_assignments()} total, {details.get_total_points()} points)"
            )

            # Group by type
            by_type = {}
            for assignment in details.assignments:
                if assignment.type not in by_type:
                    by_type[assignment.type] = []
                by_type[assignment.type].append(assignment)

            for assign_type, assignments in sorted(
                by_type.items(), key=lambda x: x[0].value
            ):
                sections.append(
                    f"\n**{assign_type.value.title()}s** ({len(assignments)}):"
                )
                for assignment in sorted(assignments, key=lambda a: a.due_week):
                    sections.append(
                        f"- Week {assignment.due_week}: {assignment.title} "
                        f"({assignment.points} points)"
                    )

        # Syllabus
        sections.append(f"\n### Course Syllabus ({details.syllabus.total_weeks} weeks)")

        for week in details.syllabus.weeks:
            sections.append(f"\n**Week {week.week_number}: {week.topic}**")

            if week.subtopics:
                sections.append("Topics: " + ", ".join(week.subtopics))

            if week.readings:
                sections.append("Readings: " + ", ".join(week.readings))

            if week.assignments:
                sections.append("Due: " + ", ".join(week.assignments))

        return "\n".join(sections) + "\n"

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4

    def assemble_with_budget(
        self,
        summaries: List[CourseSummary],
        details: List[CourseDetails],
        query: str,
        max_tokens: int = 2000,
    ) -> Tuple[str, int]:
        """
        Assemble context within token budget.

        Args:
            summaries: All course summaries
            details: Detailed courses
            query: Search query
            max_tokens: Maximum token budget

        Returns:
            Tuple of (context, estimated_tokens)
        """
        # Start with full context
        context = self.assemble_hierarchical_context(summaries, details, query)
        estimated = self.estimate_tokens(context)

        # If over budget, reduce details
        if estimated > max_tokens and len(details) > 1:
            # Try with fewer details
            reduced_details = details[: len(details) - 1]
            context = self.assemble_hierarchical_context(
                summaries, reduced_details, query
            )
            estimated = self.estimate_tokens(context)

        return context, estimated


class FlatContextAssembler:
    """
    Traditional flat context assembly (for comparison).

    This is the Stage 2 approach: returns ALL courses with full details.
    No progressive disclosure, no hierarchy.
    """

    def assemble_flat_context(
        self,
        courses: List[CourseDetails],
        query: str,
    ) -> str:
        """
        Assemble flat context with all course details.

        Args:
            courses: All courses to include
            query: Search query

        Returns:
            Assembled context string
        """
        sections = [f"# Course Search Results for: {query}\n"]

        for i, course in enumerate(courses, 1):
            sections.append(f"\n## {i}. {course.course_code}: {course.title}")
            sections.append(f"Instructor: {course.instructor}")
            sections.append(
                f"Credits: {course.credits} | Level: {course.difficulty_level.value}"
            )
            sections.append(f"\n{course.full_description}")

            # Include everything for every course
            if course.prerequisites:
                sections.append("\nPrerequisites:")
                for prereq in course.prerequisites:
                    sections.append(f"- {prereq.course_code}")

            sections.append("\nLearning Objectives:")
            for obj in course.learning_objectives:
                sections.append(f"- {obj}")

            # Full syllabus for EVERY course
            sections.append(f"\nSyllabus ({course.syllabus.total_weeks} weeks):")
            for week in course.syllabus.weeks:
                sections.append(f"Week {week.week_number}: {week.topic}")

            # All assignments for EVERY course
            sections.append(f"\nAssignments ({course.get_total_assignments()}):")
            for assignment in course.assignments:
                sections.append(f"- {assignment.title} (Week {assignment.due_week})")

        return "\n".join(sections)


class RawContextAssembler:
    """
    Raw JSON context assembly (for Stage 1 baseline).

    This shows the problem: unstructured, noisy, inefficient.
    """

    def assemble_raw_context(
        self,
        courses: List[CourseDetails],
        query: str,
    ) -> str:
        """
        Assemble raw JSON context (baseline approach).

        Args:
            courses: All courses
            query: Search query

        Returns:
            Raw JSON string
        """
        import json

        data = {"query": query, "results": [course.model_dump() for course in courses]}

        return json.dumps(data, indent=2, default=str)
