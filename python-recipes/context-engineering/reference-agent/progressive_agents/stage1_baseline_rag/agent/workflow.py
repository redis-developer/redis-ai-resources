"""
Workflow builder for Stage 1 Baseline RAG Agent.

This is a SIMPLE 2-node workflow:
1. Research (semantic search with raw context)
2. Synthesize (LLM answer generation)

No decomposition, no quality evaluation, no iteration.
Just the basics to show the baseline approach.
"""

import logging

from langgraph.graph import END, START, StateGraph

from .nodes import research_node, synthesize_node
from .state import AgentState

logger = logging.getLogger("stage1-baseline")


def create_workflow() -> StateGraph:
    """
    Create a simple 2-node RAG workflow.

    Workflow:
    START → research → synthesize → END

    This is intentionally simple to show the baseline approach.
    Stage 2 will have the same structure but with context engineering.
    Stage 3 adds decomposition and quality evaluation.

    Returns:
        Compiled LangGraph workflow
    """
    logger.info("🏗️  Building Stage 1 Baseline RAG workflow...")

    # Create state graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("synthesize", synthesize_node)

    # Define edges (linear flow)
    workflow.add_edge(START, "research")
    workflow.add_edge("research", "synthesize")
    workflow.add_edge("synthesize", END)

    # Compile
    app = workflow.compile()

    logger.info("✅ Workflow created successfully")
    logger.info("📊 Workflow: START → research → synthesize → END")

    return app
