"""
Main workflow builder and runner for the Memory-Augmented Course Q&A Agent.

Extends Stage 4 workflow with working memory nodes for multi-turn conversations.
"""

import asyncio
import logging
import time
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from .edges import (
    initialize_edges,
    route_after_cache_check,
    route_after_quality_evaluation,
)
from .nodes import (
    check_cache_node,
    classify_intent_node,
    decompose_query_node,
    evaluate_quality_node,
    extract_entities_node,
    handle_greeting_node,
    initialize_nodes,
    load_working_memory_node,
    research_node,
    save_working_memory_node,
    synthesize_response_node,
)
from .state import WorkflowState, initialize_state
from .tools import initialize_tools

# Configure logger
logger = logging.getLogger("course-qa-workflow")


def create_workflow(course_manager):
    """
    Create and compile the complete Memory-Augmented Course Q&A agent workflow.

    Args:
        course_manager: CourseManager instance for course search

    Returns:
        Compiled LangGraph workflow
    """
    # Initialize all components
    initialize_nodes()
    initialize_edges()
    initialize_tools(course_manager)

    # Create workflow graph
    workflow = StateGraph(WorkflowState)

    # Add nodes (including NEW memory nodes)
    workflow.add_node("load_memory", load_working_memory_node)  # NEW: Load at start
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("handle_greeting", handle_greeting_node)
    workflow.add_node("extract_entities", extract_entities_node)
    workflow.add_node("decompose_query", decompose_query_node)
    workflow.add_node("check_cache", check_cache_node)
    workflow.add_node("research", research_node)
    workflow.add_node("evaluate_quality", evaluate_quality_node)
    workflow.add_node("synthesize", synthesize_response_node)
    workflow.add_node("save_memory", save_working_memory_node)  # NEW: Save at end

    # Set entry point to load memory first
    workflow.set_entry_point("load_memory")

    # Add routing function for intent classification
    def route_after_intent(state: WorkflowState) -> str:
        """Route based on query intent."""
        intent = state.get("query_intent", "GENERAL")

        if intent == "GREETING":
            return "handle_greeting"
        else:
            return "extract_entities"

    # Add edges
    workflow.add_edge("load_memory", "classify_intent")  # NEW: Load memory first
    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "handle_greeting": "handle_greeting",
            "extract_entities": "extract_entities",
        },
    )
    workflow.add_edge("handle_greeting", "save_memory")  # NEW: Save even for greetings
    workflow.add_edge("extract_entities", "decompose_query")
    workflow.add_edge("decompose_query", "check_cache")
    workflow.add_conditional_edges(
        "check_cache",
        route_after_cache_check,
        {
            "research": "research",
            "synthesize": "synthesize",
        },
    )
    workflow.add_edge("research", "evaluate_quality")
    workflow.add_conditional_edges(
        "evaluate_quality",
        route_after_quality_evaluation,
        {
            "research": "research",
            "synthesize": "synthesize",
        },
    )
    workflow.add_edge("synthesize", "save_memory")  # NEW: Save memory at end
    workflow.add_edge("save_memory", END)  # NEW: End after saving

    # Compile and return
    return workflow.compile()


async def run_agent_async(
    agent,
    query: str,
    session_id: str,
    student_id: str,
    enable_caching: bool = False,
) -> Dict[str, Any]:
    """
    Run the Memory-Augmented Course Q&A agent on a query (async version).

    Args:
        agent: Compiled LangGraph workflow
        query: User query about courses
        session_id: Session identifier for conversation continuity
        student_id: User identifier
        enable_caching: Whether to use semantic caching (currently disabled)

    Returns:
        Dictionary with results and metrics
    """
    start_time = time.perf_counter()

    # Initialize state using the new initialize_state function
    initial_state = initialize_state(
        query=query,
        session_id=session_id,
        student_id=student_id,
        cache_enabled=enable_caching,
        max_research_iterations=2,
        comparison_mode=False,
    )

    logger.info("=" * 80)
    logger.info(f"🚀 Starting Memory-Augmented workflow for query: '{query[:50]}...'")
    logger.info(f"👤 Student: {student_id} | 🔗 Session: {session_id}")

    try:
        # Execute the workflow (async)
        final_state = await agent.ainvoke(initial_state)

        # Calculate final metrics
        total_time = (time.perf_counter() - start_time) * 1000
        final_state["metrics"]["total_latency"] = total_time

        # Create execution path string
        execution_path = " → ".join(final_state["execution_path"])
        final_state["metrics"]["execution_path"] = execution_path

        logger.info("=" * 80)
        logger.info(f"✅ Workflow completed in {total_time:.2f}ms")
        logger.info(f"📊 Execution path: {execution_path}")

        return final_state

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        import traceback

        traceback.print_exc()
        return {
            "original_query": query,
            "final_response": f"Error: {e}",
            "execution_path": ["failed"],
            "metrics": {"total_latency": (time.perf_counter() - start_time) * 1000},
        }


def run_agent(
    agent,
    query: str,
    session_id: str,
    student_id: str,
    enable_caching: bool = False,
) -> Dict[str, Any]:
    """
    Run the Memory-Augmented Course Q&A agent on a query (sync wrapper).

    Args:
        agent: Compiled LangGraph workflow
        query: User query about courses
        session_id: Session identifier for conversation continuity
        student_id: User identifier
        enable_caching: Whether to use semantic caching (currently disabled)

    Returns:
        Dictionary with results and metrics
    """
    # Check if we're already in an event loop
    try:
        loop = asyncio.get_running_loop()
        # We're in an event loop, so we need to create a task
        import nest_asyncio

        nest_asyncio.apply()
        return asyncio.run(
            run_agent_async(agent, query, session_id, student_id, enable_caching)
        )
    except RuntimeError:
        # No event loop running, safe to use asyncio.run()
        return asyncio.run(
            run_agent_async(agent, query, session_id, student_id, enable_caching)
        )
