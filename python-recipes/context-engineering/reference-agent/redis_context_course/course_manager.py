"""
Course management system for the Class Agent.

This module handles course storage, retrieval, and recommendation logic
using Redis vector search for semantic course discovery.
"""

import json
from typing import List, Optional, Dict, Any
import numpy as np

from redisvl.query import VectorQuery, FilterQuery
from redisvl.query.filter import Tag, Num

from .models import Course, CourseRecommendation, StudentProfile, DifficultyLevel, CourseFormat
from .redis_config import redis_config


class CourseManager:
    """Manages course data and provides recommendation functionality."""

    def __init__(self):
        self.redis_client = redis_config.redis_client
        self.vector_index = redis_config.vector_index
        self.embeddings = redis_config.embeddings

    def _build_filters(self, filters: Dict[str, Any]) -> str:
        """Build filter expressions for Redis queries using RedisVL filter classes."""
        if not filters:
            return ""

        filter_conditions = []

        if "department" in filters:
            filter_conditions.append(Tag("department") == filters["department"])
        if "major" in filters:
            filter_conditions.append(Tag("major") == filters["major"])
        if "difficulty_level" in filters:
            filter_conditions.append(Tag("difficulty_level") == filters["difficulty_level"])
        if "format" in filters:
            filter_conditions.append(Tag("format") == filters["format"])
        if "semester" in filters:
            filter_conditions.append(Tag("semester") == filters["semester"])
        if "year" in filters:
            filter_conditions.append(Num("year") == filters["year"])
        if "credits_min" in filters:
            min_credits = filters["credits_min"]
            max_credits = filters.get("credits_max", 10)
            filter_conditions.append(Num("credits") >= min_credits)
            if max_credits != min_credits:
                filter_conditions.append(Num("credits") <= max_credits)

        # Combine filters with AND logic
        if filter_conditions:
            combined_filter = filter_conditions[0]
            for condition in filter_conditions[1:]:
                combined_filter = combined_filter & condition
            return combined_filter

        return ""
    
    async def store_course(self, course: Course) -> str:
        """Store a course in Redis with vector embedding."""
        # Create searchable content for embedding
        content = f"{course.title} {course.description} {course.department} {course.major} {' '.join(course.tags)} {' '.join(course.learning_objectives)}"
        
        # Generate embedding
        embedding = await self.embeddings.aembed_query(content)
        
        # Prepare course data for storage
        course_data = {
            "id": course.id,
            "course_code": course.course_code,
            "title": course.title,
            "description": course.description,
            "department": course.department,
            "major": course.major,
            "difficulty_level": course.difficulty_level.value,
            "format": course.format.value,
            "semester": course.semester.value,
            "year": course.year,
            "credits": course.credits,
            "tags": "|".join(course.tags),
            "instructor": course.instructor,
            "max_enrollment": course.max_enrollment,
            "current_enrollment": course.current_enrollment,
            "learning_objectives": json.dumps(course.learning_objectives),
            "prerequisites": json.dumps([p.dict() for p in course.prerequisites]),
            "schedule": json.dumps(course.schedule.dict()) if course.schedule else "",
            "created_at": course.created_at.timestamp(),
            "updated_at": course.updated_at.timestamp(),
            "content_vector": np.array(embedding, dtype=np.float32).tobytes()
        }
        
        # Store in Redis
        key = f"{redis_config.vector_index_name}:{course.id}"
        self.redis_client.hset(key, mapping=course_data)
        
        return course.id
    
    async def get_course(self, course_id: str) -> Optional[Course]:
        """Retrieve a course by ID."""
        key = f"{redis_config.vector_index_name}:{course_id}"
        course_data = self.redis_client.hgetall(key)
        
        if not course_data:
            return None
        
        return self._dict_to_course(course_data)
    
    async def get_course_by_code(self, course_code: str) -> Optional[Course]:
        """Retrieve a course by course code."""
        query = FilterQuery(
            filter_expression=Tag("course_code") == course_code,
            return_fields=["id", "course_code", "title", "description", "department", "major",
                          "difficulty_level", "format", "semester", "year", "credits", "tags",
                          "instructor", "max_enrollment", "current_enrollment", "learning_objectives",
                          "prerequisites", "schedule", "created_at", "updated_at"]
        )
        results = self.vector_index.query(query)

        if results.docs:
            return self._dict_to_course(results.docs[0].__dict__)
        return None

    async def get_all_courses(self) -> List[Course]:
        """Retrieve all courses from the catalog."""
        # Use search with empty query to get all courses
        return await self.search_courses(query="", limit=1000, similarity_threshold=0.0)
    
    async def search_courses(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.6
    ) -> List[Course]:
        """Search courses using semantic similarity."""
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Build vector query
        vector_query = VectorQuery(
            vector=query_embedding,
            vector_field_name="content_vector",
            return_fields=["id", "course_code", "title", "description", "department", "major", 
                          "difficulty_level", "format", "semester", "year", "credits", "tags",
                          "instructor", "max_enrollment", "current_enrollment", "learning_objectives",
                          "prerequisites", "schedule", "created_at", "updated_at"],
            num_results=limit
        )
        
        # Apply filters using the helper method
        filter_expression = self._build_filters(filters or {})
        if filter_expression:
            vector_query.set_filter(filter_expression)
        
        # Execute search
        results = self.vector_index.query(vector_query)

        # Convert results to Course objects
        courses = []
        # Handle both list and object with .docs attribute
        result_list = results if isinstance(results, list) else results.docs
        for result in result_list:
            if result.vector_score >= similarity_threshold:
                course = self._dict_to_course(result.__dict__)
                if course:
                    courses.append(course)
        
        return courses
    
    async def recommend_courses(
        self,
        student_profile: StudentProfile,
        query: str = "",
        limit: int = 5
    ) -> List[CourseRecommendation]:
        """Generate personalized course recommendations."""
        # Build search query based on student profile and interests
        search_terms = []
        
        if query:
            search_terms.append(query)
        
        if student_profile.interests:
            search_terms.extend(student_profile.interests)
        
        if student_profile.major:
            search_terms.append(student_profile.major)
        
        search_query = " ".join(search_terms) if search_terms else "courses"
        
        # Build filters based on student preferences
        filters = {}
        if student_profile.preferred_format:
            filters["format"] = student_profile.preferred_format.value
        if student_profile.preferred_difficulty:
            filters["difficulty_level"] = student_profile.preferred_difficulty.value
        
        # Search for relevant courses
        courses = await self.search_courses(
            query=search_query,
            filters=filters,
            limit=limit * 2  # Get more to filter out completed courses
        )
        
        # Generate recommendations with scoring
        recommendations = []
        for course in courses:
            # Skip if already completed or currently enrolled
            if (course.course_code in student_profile.completed_courses or 
                course.course_code in student_profile.current_courses):
                continue
            
            # Check prerequisites
            prerequisites_met = self._check_prerequisites(course, student_profile)
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(course, student_profile, query)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(course, student_profile, relevance_score)
            
            recommendation = CourseRecommendation(
                course=course,
                relevance_score=relevance_score,
                reasoning=reasoning,
                prerequisites_met=prerequisites_met,
                fits_schedule=True,  # Simplified for now
                fits_preferences=self._fits_preferences(course, student_profile)
            )
            
            recommendations.append(recommendation)
            
            if len(recommendations) >= limit:
                break
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:limit]
    
    def _dict_to_course(self, data: Dict[str, Any]) -> Optional[Course]:
        """Convert Redis hash data to Course object."""
        try:
            from .models import Prerequisite, CourseSchedule
            
            # Parse prerequisites
            prerequisites = []
            if data.get("prerequisites"):
                prereq_data = json.loads(data["prerequisites"])
                prerequisites = [Prerequisite(**p) for p in prereq_data]
            
            # Parse schedule
            schedule = None
            if data.get("schedule"):
                schedule_data = json.loads(data["schedule"])
                if schedule_data:
                    schedule = CourseSchedule(**schedule_data)
            
            # Parse learning objectives
            learning_objectives = []
            if data.get("learning_objectives"):
                learning_objectives = json.loads(data["learning_objectives"])
            
            course = Course(
                id=data["id"],
                course_code=data["course_code"],
                title=data["title"],
                description=data["description"],
                department=data["department"],
                major=data["major"],
                difficulty_level=DifficultyLevel(data["difficulty_level"]),
                format=CourseFormat(data["format"]),
                semester=data["semester"],
                year=int(data["year"]),
                credits=int(data["credits"]),
                tags=data["tags"].split("|") if data.get("tags") else [],
                instructor=data["instructor"],
                max_enrollment=int(data["max_enrollment"]),
                current_enrollment=int(data["current_enrollment"]),
                learning_objectives=learning_objectives,
                prerequisites=prerequisites,
                schedule=schedule
            )
            
            return course
        except Exception as e:
            print(f"Error converting data to Course: {e}")
            return None
    
    def _check_prerequisites(self, course: Course, student: StudentProfile) -> bool:
        """Check if student meets course prerequisites."""
        for prereq in course.prerequisites:
            if prereq.course_code not in student.completed_courses:
                if not prereq.can_be_concurrent or prereq.course_code not in student.current_courses:
                    return False
        return True
    
    def _calculate_relevance_score(self, course: Course, student: StudentProfile, query: str) -> float:
        """Calculate relevance score for a course recommendation."""
        score = 0.5  # Base score
        
        # Major match
        if student.major and course.major.lower() == student.major.lower():
            score += 0.3
        
        # Interest match
        for interest in student.interests:
            if (interest.lower() in course.title.lower() or 
                interest.lower() in course.description.lower() or
                interest.lower() in " ".join(course.tags).lower()):
                score += 0.1
        
        # Difficulty preference
        if student.preferred_difficulty and course.difficulty_level == student.preferred_difficulty:
            score += 0.1
        
        # Format preference
        if student.preferred_format and course.format == student.preferred_format:
            score += 0.1
        
        # Ensure score is between 0 and 1
        return min(1.0, max(0.0, score))
    
    def _fits_preferences(self, course: Course, student: StudentProfile) -> bool:
        """Check if course fits student preferences."""
        if student.preferred_format and course.format != student.preferred_format:
            return False
        if student.preferred_difficulty and course.difficulty_level != student.preferred_difficulty:
            return False
        return True
    
    def _generate_reasoning(self, course: Course, student: StudentProfile, score: float) -> str:
        """Generate human-readable reasoning for the recommendation."""
        reasons = []
        
        if student.major and course.major.lower() == student.major.lower():
            reasons.append(f"matches your {student.major} major")
        
        matching_interests = [
            interest for interest in student.interests
            if (interest.lower() in course.title.lower() or 
                interest.lower() in course.description.lower())
        ]
        if matching_interests:
            reasons.append(f"aligns with your interests in {', '.join(matching_interests)}")
        
        if student.preferred_difficulty and course.difficulty_level == student.preferred_difficulty:
            reasons.append(f"matches your preferred {course.difficulty_level.value} difficulty level")
        
        if not reasons:
            reasons.append("is relevant to your academic goals")
        
        return f"This course {', '.join(reasons)}."
