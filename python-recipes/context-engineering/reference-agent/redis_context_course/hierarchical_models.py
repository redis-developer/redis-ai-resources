"""
Enhanced data models for hierarchical retrieval.

This module extends the base Course model with two-tier architecture:
1. CourseSummary - Lightweight overview for initial search
2. CourseDetails - Full details with syllabus, assignments, grading

This supports progressive disclosure and context budget management.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import (
    CourseFormat,
    DifficultyLevel,
    Prerequisite,
    Semester,
)


class AssignmentType(str, Enum):
    """Types of course assignments."""

    HOMEWORK = "homework"
    PROJECT = "project"
    QUIZ = "quiz"
    EXAM = "exam"
    LAB = "lab"
    READING = "reading"
    PRESENTATION = "presentation"


class WeekPlan(BaseModel):
    """Detailed plan for a single week of the course."""

    week_number: int
    topic: str
    subtopics: List[str] = Field(default_factory=list)
    readings: List[str] = Field(default_factory=list)
    assignments: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class Assignment(BaseModel):
    """Course assignment details."""

    title: str
    description: str
    type: AssignmentType
    due_week: int
    points: int
    estimated_hours: Optional[float] = None
    group_work: bool = False
    submission_format: Optional[str] = None  # e.g., "PDF", "Jupyter Notebook", "GitHub"


class CourseSyllabus(BaseModel):
    """Detailed week-by-week course syllabus."""

    weeks: List[WeekPlan]
    total_weeks: int

    def get_week(self, week_number: int) -> Optional[WeekPlan]:
        """Get plan for a specific week."""
        for week in self.weeks:
            if week.week_number == week_number:
                return week
        return None


class CourseSummary(BaseModel):
    """
    Lightweight course overview for initial search.

    This is the first tier in hierarchical retrieval.
    Contains just enough information for users to decide
    if they want more details.
    """

    # Core identification
    course_code: str
    title: str

    # Basic info
    department: str
    credits: int
    difficulty_level: DifficultyLevel
    format: CourseFormat
    instructor: str

    # Brief description (1-2 sentences)
    short_description: str

    # Prerequisites (just course codes for brevity)
    prerequisite_codes: List[str] = Field(default_factory=list)

    # Metadata for search
    tags: List[str] = Field(default_factory=list)

    # For vector search
    embedding_text: Optional[str] = None

    def generate_embedding_text(self) -> str:
        """Generate text for vector embedding."""
        parts = [
            f"{self.course_code}: {self.title}",
            f"Department: {self.department}",
            f"Level: {self.difficulty_level.value}",
            self.short_description,
        ]
        if self.tags:
            parts.append(f"Topics: {', '.join(self.tags)}")

        self.embedding_text = " | ".join(parts)
        return self.embedding_text


class CourseDetails(BaseModel):
    """
    Full course details with syllabus and assignments.

    This is the second tier in hierarchical retrieval.
    Retrieved only for the most relevant courses after
    initial summary search.
    """

    # All fields from CourseSummary
    course_code: str
    title: str
    department: str
    credits: int
    difficulty_level: DifficultyLevel
    format: CourseFormat
    instructor: str

    # Full description (multiple paragraphs)
    full_description: str

    # Prerequisites (full details)
    prerequisites: List[Prerequisite] = Field(default_factory=list)

    # Learning outcomes
    learning_objectives: List[str] = Field(default_factory=list)

    # Detailed syllabus
    syllabus: CourseSyllabus

    # Assignments
    assignments: List[Assignment] = Field(default_factory=list)

    # Additional metadata
    semester: Semester
    year: int
    max_enrollment: int
    tags: List[str] = Field(default_factory=list)

    def to_summary(self) -> CourseSummary:
        """Convert full details to summary view."""
        # Create short description from first 2 sentences of full description
        sentences = self.full_description.split(". ")
        short_desc = ". ".join(sentences[:2])
        if not short_desc.endswith("."):
            short_desc += "."

        return CourseSummary(
            course_code=self.course_code,
            title=self.title,
            department=self.department,
            credits=self.credits,
            difficulty_level=self.difficulty_level,
            format=self.format,
            instructor=self.instructor,
            short_description=short_desc,
            prerequisite_codes=[p.course_code for p in self.prerequisites],
            tags=self.tags,
        )

    def get_total_assignments(self) -> int:
        """Count total assignments."""
        return len(self.assignments)

    def get_assignments_by_type(
        self, assignment_type: AssignmentType
    ) -> List[Assignment]:
        """Get all assignments of a specific type."""
        return [a for a in self.assignments if a.type == assignment_type]

    def get_total_points(self) -> int:
        """Calculate total points available."""
        return sum(a.points for a in self.assignments)


class HierarchicalCourse(BaseModel):
    """
    Container for both summary and details.

    Used during data generation and storage to keep
    both representations together.
    """

    summary: CourseSummary
    details: CourseDetails

    # Storage metadata
    id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def validate_consistency(self) -> bool:
        """Ensure summary and details are consistent."""
        return (
            self.summary.course_code == self.details.course_code
            and self.summary.title == self.details.title
            and self.summary.department == self.details.department
        )
