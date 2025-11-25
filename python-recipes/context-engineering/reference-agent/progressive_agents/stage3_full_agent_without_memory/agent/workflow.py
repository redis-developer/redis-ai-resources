"""
Main workflow builder and runner for the Course Q&A Agent.

Adapted from caching-agent to use CourseManager for course search.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any

from langgraph.graph import StateGraph, END, START

from .state import WorkflowState, initialize_metrics
from .nodes import (
    initialize_nodes,
    decompose_query_node,
    check_cache_node,
    research_node,
    evaluate_quality_node,
    synthesize_response_node,
)
from .edges import (
    initialize_edges,
    route_after_cache_check,
    route_after_quality_evaluation,
)
from .tools import initialize_tools

# Configure logger
logger = logging.getLogger("course-qa-workflow")


def create_workflow(course_manager):
    """
    Create and compile the complete Course Q&A agent workflow.
    
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
    
    # Add nodes
    workflow.add_node("decompose_query", decompose_query_node)
    workflow.add_node("check_cache", check_cache_node)
    workflow.add_node("research", research_node)
    workflow.add_node("evaluate_quality", evaluate_quality_node)
    workflow.add_node("synthesize", synthesize_response_node)
    
    # Set entry point
    workflow.set_entry_point("decompose_query")
    
    # Add edges
    workflow.add_edge("decompose_query", "check_cache")
    workflow.add_conditional_edges(
        "check_cache",
        route_after_cache_check,
        {
            "research": "research",      # Go to research if cache misses
            "synthesize": "synthesize",  # Skip to synthesis if all cached
        },
    )
    workflow.add_edge("research", "evaluate_quality")
    workflow.add_conditional_edges(
        "evaluate_quality",
        route_after_quality_evaluation,
        {
            "research": "research",      # Additional research if needed
            "synthesize": "synthesize",  # Proceed to synthesis
        },
    )
    workflow.add_edge("synthesize", END)
    
    # Compile and return
    return workflow.compile()


def run_agent(agent, query: str, enable_caching: bool = False) -> Dict[str, Any]:
    """
    Run the Course Q&A agent on a query.
    
    Args:
        agent: Compiled LangGraph workflow
        query: User query about courses
        enable_caching: Whether to use semantic caching (currently disabled)
        
    Returns:
        Dictionary with results and metrics
    """
    start_time = time.perf_counter()
    
    # Initialize state for the workflow
    initial_state: WorkflowState = {
        "original_query": query,
        "sub_questions": [],
        "sub_answers": {},
        "cache_hits": {},
        "cache_confidences": {},
        "cache_enabled": enable_caching,  # Currently always False
        "research_iterations": {},
        "max_research_iterations": 2,
        "research_quality_scores": {},
        "research_feedback": {},
        "current_research_strategy": {},
        "final_response": None,
        "execution_path": [],
        "active_sub_question": None,
        "metrics": initialize_metrics(),
        "timestamp": datetime.now().isoformat(),
        "comparison_mode": False,
        "llm_calls": {},
    }
    
    logger.info("=" * 80)
    logger.info(f"🚀 Starting Course Q&A workflow for query: '{query[:50]}...'")
    
    try:
        # Execute the workflow
        final_state = agent.invoke(initial_state)
        
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
        return {
            "original_query": query,
            "final_response": f"Error: {e}",
            "execution_path": ["failed"],
            "metrics": {"total_latency": (time.perf_counter() - start_time) * 1000}
        }

