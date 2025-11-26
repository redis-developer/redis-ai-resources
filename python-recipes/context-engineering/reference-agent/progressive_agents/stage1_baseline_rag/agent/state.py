"""
State definitions for Stage 1 Baseline RAG Agent.

This is a simplified state compared to Stage 3 - no metrics tracking,
no quality scores, no iteration tracking. Just the basics.
"""

from typing import Optional, TypedDict


class AgentState(TypedDict):
    """
    Simple state for baseline RAG agent.

    This is intentionally minimal to show the baseline approach
    without any advanced features.
    """

    # Input
    query: str

    # Research results
    raw_context: str  # Raw course data (JSON or basic string)
    courses_found: int

    # Output
    final_answer: str

    # Simple metrics
    total_tokens: Optional[int]
    total_time_ms: Optional[float]


def initialize_state(query: str) -> AgentState:
    """
    Initialize agent state with a query.

    Args:
        query: User's question

    Returns:
        Initialized state dictionary
    """
    return {
        "query": query,
        "raw_context": "",
        "courses_found": 0,
        "final_answer": "",
        "total_tokens": None,
        "total_time_ms": None,
    }
