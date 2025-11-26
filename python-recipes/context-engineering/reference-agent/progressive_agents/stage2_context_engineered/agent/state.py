"""
State definitions for Stage 2 Context-Engineered Agent.

Same simple state as Stage 1 - the difference is in HOW we process
the context (with context engineering), not in the state structure.
"""

from typing import Optional, TypedDict


class AgentState(TypedDict):
    """
    Simple state for context-engineered RAG agent.

    Same structure as Stage 1, but the context will be engineered
    using Section 2 techniques (cleaning, transformation, optimization).
    """

    # Input
    query: str

    # Research results
    engineered_context: str  # Context-engineered course data (natural text)
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
        "engineered_context": "",
        "courses_found": 0,
        "final_answer": "",
        "total_tokens": None,
        "total_time_ms": None,
    }
