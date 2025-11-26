"""
Data models for the Redis University Class Agent.

This module defines the core data structures used throughout the application,
including courses, majors, prerequisites, and student information.
"""

from datetime import datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from ulid import ULID


class DifficultyLevel(str, Enum):
    """Course difficulty levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    GRADUATE = "graduate"


class CourseFormat(str, Enum):
    """Course delivery formats."""

    IN_PERSON = "in_person"
    ONLINE = "online"
    HYBRID = "hybrid"


class Semester(str, Enum):
    """Academic semesters."""

    FALL = "fall"
    SPRING = "spring"
    SUMMER = "summer"
    WINTER = "winter"


class DayOfWeek(str, Enum):
    """Days of the week for scheduling."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class CourseSchedule(BaseModel):
    """Course schedule information."""

    days: List[DayOfWeek]
    start_time: time
    end_time: time
    location: Optional[str] = None

    model_config = ConfigDict(json_encoders={time: lambda v: v.strftime("%H:%M")})


class Prerequisite(BaseModel):
    """Course prerequisite information."""

    course_code: str
    course_title: str
    minimum_grade: Optional[str] = "C"
    can_be_concurrent: bool = False


class Course(BaseModel):
    """Complete course information."""

    id: str = Field(default_factory=lambda: str(ULID()))
    course_code: str  # e.g., "CS101"
    title: str
    description: str
    credits: int
    difficulty_level: DifficultyLevel
    format: CourseFormat
    department: str
    major: str
    prerequisites: List[Prerequisite] = Field(default_factory=list)
    schedule: Optional[CourseSchedule] = None
    semester: Semester
    year: int
    instructor: str
    max_enrollment: int
    current_enrollment: int = 0
    tags: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Major(BaseModel):
    """Academic major information."""

    id: str = Field(default_factory=lambda: str(ULID()))
    name: str
    code: str  # e.g., "CS", "MATH", "ENG"
    department: str
    description: str
    required_credits: int
    core_courses: List[str] = Field(default_factory=list)  # Course codes
    elective_courses: List[str] = Field(default_factory=list)  # Course codes
    career_paths: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class StudentProfile(BaseModel):
    """Student profile and preferences."""

    id: str = Field(default_factory=lambda: str(ULID()))
    name: str
    email: str
    major: Optional[str] = None
    year: int = 1  # 1-4 for undergraduate, 5+ for graduate
    completed_courses: List[str] = Field(default_factory=list)  # Course codes
    current_courses: List[str] = Field(default_factory=list)  # Course codes
    interests: List[str] = Field(default_factory=list)
    preferred_format: Optional[CourseFormat] = None
    preferred_difficulty: Optional[DifficultyLevel] = None
    max_credits_per_semester: int = 15
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CourseRecommendation(BaseModel):
    """Course recommendation with reasoning."""

    course: Course
    relevance_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    prerequisites_met: bool
    fits_schedule: bool = True
    fits_preferences: bool = True


class AgentResponse(BaseModel):
    """Structured response from the agent."""

    message: str
    recommendations: List[CourseRecommendation] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
