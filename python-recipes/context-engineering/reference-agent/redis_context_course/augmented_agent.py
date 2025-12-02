"""
AugmentedClassAgent builds on the reference ClassAgent by adding specialized tools
while preserving the original memory architecture and graph orchestration.

This demonstrates the recommended extension pattern: inherit from ClassAgent,
override _get_tools() to append domain tools, and optionally extend the system prompt.
"""
from typing import List, Optional, Dict, Any

from langchain_core.tools import tool

from .agent import ClassAgent
from .models import StudentProfile


class AugmentedClassAgent(ClassAgent):
    """Extended agent that reuses the reference ClassAgent and adds tools.

    Additions:
    - get_course_details_tool: fetch structured details for a course by code
    - check_prerequisites_tool: verify a student's readiness for a course

    Notes:
    - We keep the original graph; only the toolset and prompt are extended.
    - Tools use the same CourseManager and MemoryAPIClient as the base class.
    """

    # --------------------------- New tools ---------------------------------
    @tool
    async def get_course_details_tool(self, course_code: str) -> str:
        """Get detailed course information by course code.

        Use this when the user asks for details like description, credits,
        prerequisites, schedule, or instructor for a specific course code
        (e.g., "Tell me more about CS101").
        """
        course = await self.course_manager.get_course_by_code(course_code)
        if not course:
            return f"No course found with code '{course_code}'."

        prereqs = ", ".join(p.course_code for p in course.prerequisites) or "None"
        objectives = ", ".join(course.learning_objectives[:3]) or "-"
        tags = ", ".join(course.tags[:5]) or "-"
        schedule = (
            f"{course.schedule.days} {course.schedule.start_time}-{course.schedule.end_time}"
            if course.schedule else "TBD"
        )

        return (
            f"{course.course_code}: {course.title}\n"
            f"Department: {course.department} | Major: {course.major} | Credits: {course.credits}\n"
            f"Difficulty: {course.difficulty_level.value} | Format: {course.format.value}\n"
            f"Instructor: {course.instructor} | Schedule: {schedule}\n\n"
            f"Description: {course.description}\n\n"
            f"Prerequisites: {prereqs}\n"
            f"Objectives: {objectives}\n"
            f"Tags: {tags}\n"
        )

    @tool
    async def check_prerequisites_tool(
        self,
        course_code: str,
        completed: Optional[List[str]] = None,
        current: Optional[List[str]] = None,
    ) -> str:
        """Check whether the student meets prerequisites for a course.

        Args:
            course_code: Target course code (e.g., "CS301").
            completed: List of completed course codes (optional).
            current: List of currently enrolled course codes (optional).

        Behavior:
            - If completed/current are omitted, assumes none and reports missing prereqs.
            - Returns a concise status plus any missing prerequisites.
        """
        course = await self.course_manager.get_course_by_code(course_code)
        if not course:
            return f"No course found with code '{course_code}'."

        completed = completed or []
        current = current or []
        # Build a minimal profile for prerequisite checks
        profile = StudentProfile(
            name=self.student_id,
            email=f"{self.student_id}@university.edu",
            interests=[],
            completed_courses=completed,
            current_courses=current,
        )

        # Determine missing prerequisites (do not rely on private method)
        missing: List[str] = []
        for prereq in course.prerequisites:
            if prereq.course_code not in completed:
                if not prereq.can_be_concurrent or prereq.course_code not in current:
                    missing.append(prereq.course_code)

        if not course.prerequisites:
            return f"{course.course_code} has no prerequisites. You can enroll."
        if not missing:
            return f"Prerequisites for {course.course_code} are satisfied."
        return (
            f"Missing prerequisites for {course.course_code}: "
            + ", ".join(missing)
            + ". If some of these are in progress, include them in 'current'."
        )

    # ---------------------- Extension points -------------------------------
    def _get_tools(self):
        """Extend the base toolset with our augmented tools."""
        base = super()._get_tools()
        # Append new tools; order can influence model choice; keep base first
        return base + [self.get_course_details_tool, self.check_prerequisites_tool]

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Extend the base prompt with guidance for new tools."""
        prompt = super()._build_system_prompt(context)
        extra = """

Additional tools available:
- get_course_details_tool: Use when the user asks for details about a specific course (description, credits, schedule, prerequisites, instructor).
- check_prerequisites_tool: Use to verify whether the student meets prerequisites for a course. If the student's completed/current courses are unknown, you may call get_course_details_tool first, then ask the user to share their completed/current courses in your final response.
        """
        return prompt + extra

