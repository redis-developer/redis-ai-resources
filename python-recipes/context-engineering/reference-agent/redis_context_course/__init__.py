"""
Redis Context Course - Context Engineering Reference Implementation

This package provides a complete reference implementation of a context-aware
AI agent for university course recommendations and academic planning.

The agent demonstrates key context engineering concepts:
- System context management
- Working memory and long-term memory (via Redis Agent Memory Server)
- Tool integration and usage
- Semantic search and retrieval
- Personalized recommendations

Main Components:
- agent: LangGraph-based agent implementation
- models: Data models for courses and students
- memory_client: Interface to Redis Agent Memory Server
- course_manager: Course storage and recommendation engine
- redis_config: Redis configuration and connections
- cli: Command-line interface

Installation:
    pip install redis-context-course agent-memory-server

Usage:
    from redis_context_course import ClassAgent, MemoryClient

    # Initialize agent (uses Agent Memory Server)
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
    Course, Major, StudentProfile,
    CourseRecommendation, AgentResponse, Prerequisite,
    CourseSchedule, DifficultyLevel, CourseFormat,
    Semester, DayOfWeek
)

# Import agent components
from .agent import ClassAgent, AgentState

# Import memory client
from .memory_client import MemoryClient
from .course_manager import CourseManager
from .redis_config import RedisConfig, redis_config

# Import tools (used in notebooks)
from .tools import (
    create_course_tools,
    create_memory_tools,
    select_tools_by_keywords
)

# Import optimization helpers (from Section 4)
from .optimization_helpers import (
    count_tokens,
    estimate_token_budget,
    hybrid_retrieval,
    create_summary_view,
    create_user_profile_view,
    filter_tools_by_intent,
    classify_intent_with_llm,
    extract_references,
    format_context_for_llm
)

__version__ = "1.0.0"
__author__ = "Redis AI Resources Team"
__email__ = "redis-ai@redis.com"
__license__ = "MIT"
__description__ = "Context Engineering with Redis - University Class Agent Reference Implementation"

__all__ = [
    # Core classes
    "ClassAgent",
    "AgentState",
    "MemoryClient",
    "CourseManager",
    "RedisConfig",
    "redis_config",

    # Data models
    "Course",
    "Major",
    "StudentProfile",
    "CourseRecommendation",
    "AgentResponse",
    "Prerequisite",
    "CourseSchedule",

    # Enums
    "DifficultyLevel",
    "CourseFormat",
    "Semester",
    "DayOfWeek",

    # Tools (for notebooks)
    "create_course_tools",
    "create_memory_tools",
    "select_tools_by_keywords",

    # Optimization helpers (Section 4)
    "count_tokens",
    "estimate_token_budget",
    "hybrid_retrieval",
    "create_summary_view",
    "create_user_profile_view",
    "filter_tools_by_intent",
    "classify_intent_with_llm",
    "extract_references",
    "format_context_for_llm",
]
