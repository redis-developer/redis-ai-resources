"""
Course Q&A Agent - Stage 3 (Full Agent without Memory)

A LangGraph-based agent for answering questions about courses using semantic search
and context engineering techniques. This is Stage 3 of the progressive learning path.

Adapted from the caching-agent architecture with CourseManager integration.
"""

from .state import WorkflowState, WorkflowMetrics, initialize_metrics
from .workflow import create_workflow, run_agent
from .setup import setup_agent, initialize_course_manager, cleanup_courses
from .tools import search_courses, transform_course_to_text, optimize_course_text

__all__ = [
    # State management
    "WorkflowState",
    "WorkflowMetrics",
    "initialize_metrics",

    # Workflow
    "create_workflow",
    "run_agent",

    # Setup
    "setup_agent",
    "initialize_course_manager",
    "cleanup_courses",

    # Tools
    "search_courses",
    "transform_course_to_text",
    "optimize_course_text",
]

__version__ = "0.1.0"

