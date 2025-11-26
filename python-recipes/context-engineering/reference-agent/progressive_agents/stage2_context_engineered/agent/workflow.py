"""
Workflow builder for Stage 2 Context-Engineered Agent.

This is a SIMPLE 2-node workflow (same as Stage 1):
1. Research (semantic search with ENGINEERED context)
2. Synthesize (LLM answer generation)

No decomposition, no quality evaluation, no iteration.
The ONLY difference from Stage 1 is context engineering!
"""

import logging

from langgraph.graph import END, START, StateGraph

from .nodes import research_node, synthesize_node
from .state import AgentState

logger = logging.getLogger("stage2-engineered")


def create_workflow() -> StateGraph:
    """
    Create a simple 2-node RAG workflow with context engineering.

    Workflow:
    START → research (with context engineering) → synthesize → END

    Same structure as Stage 1, but research node applies Section 2 techniques.
    This makes it easy to compare and see the impact of context engineering.

    Returns:
        Compiled LangGraph workflow
    """
    logger.info("🏗️  Building Stage 2 Context-Engineered workflow...")

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
    logger.info("📊 Workflow: START → research (engineered) → synthesize → END")

    return app
