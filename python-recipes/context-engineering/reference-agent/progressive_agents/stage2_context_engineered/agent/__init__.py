"""
Stage 2: Context-Engineered Agent

A RAG agent that applies Section 2 context engineering techniques:
- Semantic search with Redis vector embeddings (same as Stage 1)
- CONTEXT ENGINEERING: Clean, transform, and optimize retrieved data
- Simple 2-node LangGraph workflow (same as Stage 1)
- No query decomposition (same as Stage 1)
- No quality evaluation (same as Stage 1)

This agent demonstrates the VALUE of context engineering by comparing
to Stage 1's baseline approach. Same architecture, better context!

Context Engineering Techniques Applied:
1. CLEANING: Remove noise fields (id, timestamps, enrollment data)
2. TRANSFORMATION: Convert JSON → natural text format
3. OPTIMIZATION: Efficient token usage while preserving information

Students will see:
- 40-50% token reduction compared to Stage 1
- Better LLM understanding (natural text vs JSON)
- Same functionality, better efficiency
- Clear ROI on context engineering
"""

from .context_engineering import (
    format_courses_for_llm,
    optimize_course_text,
    transform_course_to_text,
)
from .setup import cleanup_courses, load_courses_if_needed, setup_agent
from .state import AgentState, initialize_state
from .workflow import create_workflow

__all__ = [
    "setup_agent",
    "load_courses_if_needed",
    "cleanup_courses",
    "create_workflow",
    "AgentState",
    "initialize_state",
    "transform_course_to_text",
    "optimize_course_text",
    "format_courses_for_llm",
]
