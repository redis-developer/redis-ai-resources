"""
Course Q&A Agent - Stage 3 (Full Agent without Memory)

A LangGraph-based agent for answering questions about courses using semantic search
and context engineering techniques. This is Stage 3 of the progressive learning path.

Adapted from the caching-agent architecture with CourseManager integration.
"""

from .setup import cleanup_courses, initialize_course_manager, setup_agent
from .state import WorkflowMetrics, WorkflowState, initialize_metrics
from .tools import optimize_course_text, search_courses, transform_course_to_text
from .workflow import create_workflow, run_agent

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
