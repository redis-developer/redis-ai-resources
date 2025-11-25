"""
Workflow edges and routing logic for the Course Q&A Agent.

Adapted from caching-agent with minimal changes for course Q&A routing.
"""

import logging
from typing import Dict, Any, Literal

# Configure logger
logger = logging.getLogger("course-qa-workflow")

# NOTE: Semantic cache initialization commented out for now
# Global cache variable
# cache = None


def initialize_edges():
    """Initialize edges with required dependencies."""
    # NOTE: Semantic cache initialization commented out
    # global cache
    # cache = semantic_cache
    pass


def route_after_cache_check(state: Dict[str, Any]) -> Literal["research", "synthesize"]:
    """
    Route after cache check based on cache hit results.
    
    Returns:
        "research" if any cache misses detected
        "synthesize" if all sub-questions are cached
    """
    cache_hits = state.get("cache_hits", {})
    
    # Count cache misses
    cache_misses = [question for question, is_cached in cache_hits.items() if not is_cached]
    
    if cache_misses:
        logger.info(f"🔀 Routing to researcher: {len(cache_misses)} cache misses detected")
        for question in cache_misses:
            logger.info(f"   🔍 Will research: '{question[:50]}...'")
        return "research"
    else:
        logger.info("🔀 Routing to synthesis: all sub-questions cached!")
        return "synthesize"


def route_after_quality_evaluation(state: Dict[str, Any]) -> Literal["research", "synthesize"]:
    """
    Route after quality evaluation based on research quality scores.
    
    Returns:
        "research" if any answers need improvement and haven't exceeded max iterations
        "synthesize" if all answers are adequate or max iterations reached
    """
    quality_scores = state.get("research_quality_scores", {})
    research_iterations = state.get("research_iterations", {})
    max_iterations = state.get("max_research_iterations", 2)
    
    # Find questions that need improvement and haven't exceeded max iterations
    needs_improvement = []
    for question, score in quality_scores.items():
        current_iterations = research_iterations.get(question, 0)
        if score < 0.7 and current_iterations < max_iterations:
            needs_improvement.append((question, score, current_iterations))
    
    if needs_improvement:
        logger.info(f"🔄 Routing to additional research: {len(needs_improvement)} questions need improvement")
        for question, score, iteration in needs_improvement:
            logger.info(f"   🔍 Improve: '{question[:40]}...' (score: {score:.2f}, iteration: {iteration + 1})")
        return "research"
    else:
        logger.info("🔀 Routing to synthesis: all research quality is adequate!")
        return "synthesize"

