"""
Workflow state definitions for the ReAct Loop Course Q&A Agent (Stage 7).

Extends Stage 6 with reasoning trace for ReAct (Reasoning + Acting) loop.
"""

from typing import Any, Dict, List, Optional, TypedDict


class WorkflowMetrics(TypedDict):
    """Metrics tracking for workflow performance analysis."""

    total_latency: float
    decomposition_latency: float
    cache_latency: float
    research_latency: float
    synthesis_latency: float
    memory_load_latency: float  # NEW: Time to load working memory
    memory_save_latency: float  # NEW: Time to save working memory
    cache_hit_rate: float
    cache_hits_count: int
    questions_researched: int
    total_research_iterations: int
    llm_calls: Dict[str, int]
    sub_question_count: int
    execution_path: str


class WorkflowState(TypedDict):
    """
    State for ReAct Loop Course Q&A workflow (Stage 7).

    Extends Stage 6 with reasoning trace for explicit Thought → Action → Observation.
    """

    # Core query management
    original_query: str
    sub_questions: List[str]
    sub_answers: Dict[str, str]
    final_response: Optional[str]

    # NEW: ReAct reasoning trace
    reasoning_trace: List[
        Dict[str, Any]
    ]  # List of {type, thought, action, input, observation}
    react_iterations: int  # Number of ReAct loop iterations

    # Query intent classification
    query_intent: Optional[
        str
    ]  # "GREETING", "GENERAL", "SYLLABUS_OBJECTIVES", "ASSIGNMENTS", "PREREQUISITES"

    # Named Entity Recognition (NER) - from Stage 4
    extracted_entities: Optional[
        Dict[str, Any]
    ]  # course_codes, course_names, departments, etc.
    search_strategy: Optional[str]  # "exact_match", "hybrid", "semantic_only"

    # Hybrid search results - from Stage 4
    exact_matches: Optional[List[str]]  # Course codes that matched exactly
    metadata_filters: Optional[Dict[str, Any]]  # Filters extracted from query

    # NEW: Working Memory fields
    session_id: str  # Session identifier for conversation continuity
    student_id: str  # User identifier
    working_memory_loaded: bool  # Track if memory was loaded this turn
    conversation_history: List[Dict[str, str]]  # Previous messages from working memory
    current_turn_messages: List[
        Dict[str, str]
    ]  # Messages from current turn (to be saved)

    # Cache management (granular per sub-question)
    # NOTE: Semantic caching is commented out for now - will be added later
    cache_hits: Dict[str, bool]
    cache_confidences: Dict[str, float]
    cache_enabled: bool

    # Research iteration and quality control
    research_iterations: Dict[str, int]
    max_research_iterations: int
    research_quality_scores: Dict[str, float]
    research_feedback: Dict[str, str]
    current_research_strategy: Dict[str, str]

    # Agent coordination
    execution_path: List[str]
    active_sub_question: Optional[str]

    # Metrics and tracking
    metrics: WorkflowMetrics
    timestamp: str
    comparison_mode: bool
    llm_calls: Dict[str, int]


def initialize_metrics() -> WorkflowMetrics:
    """Initialize a clean metrics structure with default values."""
    return {
        "total_latency": 0.0,
        "decomposition_latency": 0.0,
        "cache_latency": 0.0,
        "research_latency": 0.0,
        "synthesis_latency": 0.0,
        "memory_load_latency": 0.0,
        "memory_save_latency": 0.0,
        "cache_hit_rate": 0.0,
        "cache_hits_count": 0,
        "questions_researched": 0,
        "total_research_iterations": 0,
        "llm_calls": {},
        "sub_question_count": 0,
        "execution_path": "",
    }


def initialize_state(
    query: str,
    session_id: str,
    student_id: str,
    cache_enabled: bool = False,
    max_research_iterations: int = 2,
    comparison_mode: bool = False,
) -> WorkflowState:
    """
    Initialize workflow state for a new query.

    Args:
        query: User's question
        session_id: Session identifier for conversation continuity
        student_id: User identifier
        cache_enabled: Whether semantic caching is enabled
        max_research_iterations: Maximum research attempts per sub-question
        comparison_mode: Whether to run in comparison mode

    Returns:
        Initialized WorkflowState
    """
    from datetime import datetime

    return {
        # Core query
        "original_query": query,
        "sub_questions": [],
        "sub_answers": {},
        "final_response": None,
        # Intent and NER
        "query_intent": None,
        "extracted_entities": None,
        "search_strategy": None,
        # Hybrid search
        "exact_matches": None,
        "metadata_filters": None,
        # Working memory (NEW)
        "session_id": session_id,
        "student_id": student_id,
        "working_memory_loaded": False,
        "conversation_history": [],
        "current_turn_messages": [],
        # Cache
        "cache_hits": {},
        "cache_confidences": {},
        "cache_enabled": cache_enabled,
        # Research
        "research_iterations": {},
        "max_research_iterations": max_research_iterations,
        "research_quality_scores": {},
        "research_feedback": {},
        "current_research_strategy": {},
        # Coordination
        "execution_path": [],
        "active_sub_question": None,
        # Metrics
        "metrics": initialize_metrics(),
        "timestamp": datetime.now().isoformat(),
        "comparison_mode": comparison_mode,
        "llm_calls": {},
    }
