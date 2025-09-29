"""
Redis Context Course - Context Engineering Reference Implementation

This package provides a complete reference implementation of a context-aware
AI agent for university course recommendations and academic planning.

The agent demonstrates key context engineering concepts:
- System context management
- Short-term and long-term memory
- Tool integration and usage
- Semantic search and retrieval
- Personalized recommendations

Main Components:
- agent: LangGraph-based agent implementation
- models: Data models for courses, students, and memory
- memory: Memory management system
- course_manager: Course storage and recommendation engine
- redis_config: Redis configuration and connections
- cli: Command-line interface

Installation:
    pip install redis-context-course

Usage:
    from redis_context_course import ClassAgent, MemoryManager

    # Initialize agent
    agent = ClassAgent("student_id")

    # Chat with agent
    response = await agent.chat("I'm interested in machine learning courses")

Command Line Tools:
    redis-class-agent --student-id your_name
    generate-courses --courses-per-major 15
    ingest-courses --catalog course_catalog.json
"""

# Import core models (these have minimal dependencies)
from .models import (
    Course, Major, StudentProfile, ConversationMemory,
    CourseRecommendation, AgentResponse, Prerequisite,
    CourseSchedule, DifficultyLevel, CourseFormat,
    Semester, DayOfWeek
)

# Import agent components
from .agent import ClassAgent, AgentState

# Import working memory components
from .working_memory import WorkingMemory, MessageCountStrategy, LongTermExtractionStrategy
from .working_memory_tools import WorkingMemoryToolProvider

try:
    from .memory import MemoryManager
except ImportError:
    MemoryManager = None

try:
    from .course_manager import CourseManager
except ImportError:
    CourseManager = None

try:
    from .redis_config import RedisConfig, redis_config
except ImportError:
    RedisConfig = None
    redis_config = None

__version__ = "1.0.0"
__author__ = "Redis AI Resources Team"
__email__ = "redis-ai@redis.com"
__license__ = "MIT"
__description__ = "Context Engineering with Redis - University Class Agent Reference Implementation"

__all__ = [
    # Core classes
    "ClassAgent",
    "AgentState",
    "MemoryManager",
    "CourseManager",
    "RedisConfig",
    "redis_config",

    # Data models
    "Course",
    "Major",
    "StudentProfile",
    "ConversationMemory",
    "CourseRecommendation",
    "AgentResponse",
    "Prerequisite",
    "CourseSchedule",

    # Enums
    "DifficultyLevel",
    "CourseFormat",
    "Semester",
    "DayOfWeek",
]
