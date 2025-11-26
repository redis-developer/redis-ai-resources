"""
Stage 1: Baseline RAG Agent

A simple RAG agent that demonstrates the BASELINE approach:
- Semantic search with Redis vector embeddings
- RAW, unoptimized context (no context engineering)
- Simple 2-node LangGraph workflow
- No query decomposition
- No quality evaluation

This agent intentionally shows the problems that context engineering solves.
Students will see:
- Noisy context (unnecessary fields)
- Token waste (inefficient)
- Poor LLM parsing (verbose JSON)

Stage 2 will apply Section 2 context engineering techniques to fix these issues.
"""

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
]
