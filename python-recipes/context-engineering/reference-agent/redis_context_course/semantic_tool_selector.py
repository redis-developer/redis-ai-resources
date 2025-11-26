"""
Semantic Tool Selection for Context Engineering.

This module implements advanced tool selection using embeddings and semantic similarity,
replacing simple keyword-based approaches with intelligent intent understanding.

Key Features:
- Embedding-based tool matching
- Intent classification with confidence scoring
- Dynamic tool filtering based on context
- Fallback strategies for ambiguous queries
- Integration with existing tool system

Usage:
    from redis_context_course.semantic_tool_selector import SemanticToolSelector

    selector = SemanticToolSelector(available_tools)
    selected_tools = await selector.select_tools(user_query, max_tools=3)
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from langchain_core.tools import BaseTool
from langchain_openai import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


@dataclass
class ToolIntent:
    """Represents a tool's intended use with semantic information."""

    tool: BaseTool
    description: str
    examples: List[str]
    keywords: List[str]
    embedding: Optional[np.ndarray] = None
    confidence_threshold: float = 0.6


class SemanticToolSelector:
    """
    Advanced tool selection using semantic similarity.

    This replaces keyword-based tool selection with embedding-based matching,
    providing more accurate tool selection for complex queries.
    """

    def __init__(
        self, tools: List[BaseTool], embeddings_model: Optional[OpenAIEmbeddings] = None
    ):
        """
        Initialize semantic tool selector.

        Args:
            tools: List of available tools
            embeddings_model: OpenAI embeddings model (optional)
        """
        self.embeddings_model = embeddings_model or OpenAIEmbeddings()
        self.tool_intents: List[ToolIntent] = []
        self._initialize_tool_intents(tools)

    def _initialize_tool_intents(self, tools: List[BaseTool]):
        """Initialize tool intents with semantic information."""

        # Define semantic information for each tool
        tool_semantics = {
            "search_courses_tool": {
                "description": "Find and discover courses based on topics, levels, or requirements",
                "examples": [
                    "I want to learn machine learning",
                    "Show me beginner programming courses",
                    "Find courses about data science",
                    "What Redis courses are available?",
                    "Search for advanced Python classes",
                ],
                "keywords": [
                    "search",
                    "find",
                    "show",
                    "discover",
                    "browse",
                    "list",
                    "available",
                ],
            },
            "get_recommendations_tool": {
                "description": "Get personalized course recommendations based on student profile and goals",
                "examples": [
                    "What courses should I take next?",
                    "Recommend courses for my career goals",
                    "What's the best learning path for me?",
                    "Suggest courses based on my background",
                    "Help me plan my education",
                ],
                "keywords": [
                    "recommend",
                    "suggest",
                    "should",
                    "best",
                    "plan",
                    "path",
                    "next",
                ],
            },
            "store_preference_tool": {
                "description": "Save student preferences for learning style, schedule, or course types",
                "examples": [
                    "I prefer online courses",
                    "Remember that I like hands-on learning",
                    "I want self-paced classes",
                    "Save my preference for evening courses",
                    "I prefer video-based content",
                ],
                "keywords": [
                    "prefer",
                    "like",
                    "remember",
                    "save",
                    "store",
                    "want",
                    "style",
                ],
            },
            "store_goal_tool": {
                "description": "Save student academic or career goals for personalized recommendations",
                "examples": [
                    "I want to become a data scientist",
                    "My goal is to learn machine learning",
                    "I'm working toward a Redis certification",
                    "I want to build AI applications",
                    "My career goal is software engineering",
                ],
                "keywords": [
                    "goal",
                    "want to become",
                    "working toward",
                    "aim",
                    "target",
                    "career",
                ],
            },
            "get_student_context_tool": {
                "description": "Retrieve relevant student context including preferences, goals, and history",
                "examples": [
                    "What do you know about me?",
                    "Show my learning history",
                    "What are my preferences?",
                    "Display my profile",
                    "What goals have I set?",
                ],
                "keywords": [
                    "know about me",
                    "my",
                    "profile",
                    "history",
                    "preferences",
                    "goals",
                ],
            },
        }

        # Create tool intents with embeddings
        for tool in tools:
            tool_name = tool.name
            if tool_name in tool_semantics:
                semantics = tool_semantics[tool_name]

                # Create semantic text for embedding
                semantic_text = f"{semantics['description']}. Examples: {' '.join(semantics['examples'])}"

                # Generate embedding
                try:
                    embedding = np.array(
                        self.embeddings_model.embed_query(semantic_text)
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate embedding for {tool_name}: {e}")
                    embedding = None

                tool_intent = ToolIntent(
                    tool=tool,
                    description=semantics["description"],
                    examples=semantics["examples"],
                    keywords=semantics["keywords"],
                    embedding=embedding,
                )

                self.tool_intents.append(tool_intent)
            else:
                logger.warning(f"No semantic information defined for tool: {tool_name}")

    async def select_tools(
        self, query: str, max_tools: int = 3, min_confidence: float = 0.5
    ) -> List[BaseTool]:
        """
        Select most relevant tools for a query using semantic similarity.

        Args:
            query: User's query
            max_tools: Maximum number of tools to return
            min_confidence: Minimum confidence threshold

        Returns:
            List of selected tools ordered by relevance
        """
        if not query.strip():
            return []

        try:
            # Get query embedding
            query_embedding = np.array(self.embeddings_model.embed_query(query))

            # Calculate similarities
            tool_scores = []
            for tool_intent in self.tool_intents:
                if tool_intent.embedding is not None:
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        tool_intent.embedding.reshape(1, -1),
                    )[0][0]

                    # Boost score if keywords match
                    keyword_boost = self._calculate_keyword_boost(
                        query, tool_intent.keywords
                    )
                    final_score = similarity + keyword_boost

                    tool_scores.append((tool_intent.tool, final_score, similarity))

            # Sort by score and filter by confidence
            tool_scores.sort(key=lambda x: x[1], reverse=True)
            selected_tools = [
                tool
                for tool, score, similarity in tool_scores
                if similarity >= min_confidence
            ][:max_tools]

            # Log selection for debugging
            logger.info(
                f"Selected {len(selected_tools)} tools for query: '{query[:50]}...'"
            )
            for tool, score, similarity in tool_scores[:max_tools]:
                logger.debug(
                    f"  {tool.name}: similarity={similarity:.3f}, final_score={score:.3f}"
                )

            return selected_tools

        except Exception as e:
            logger.error(f"Error in semantic tool selection: {e}")
            # Fallback to keyword-based selection
            return self._fallback_keyword_selection(query, max_tools)

    def _calculate_keyword_boost(self, query: str, keywords: List[str]) -> float:
        """Calculate boost score based on keyword matches."""
        query_lower = query.lower()
        matches = sum(1 for keyword in keywords if keyword in query_lower)
        return min(matches * 0.1, 0.3)  # Max boost of 0.3

    def _fallback_keyword_selection(self, query: str, max_tools: int) -> List[BaseTool]:
        """Fallback to simple keyword-based selection."""
        query_lower = query.lower()
        scored_tools = []

        for tool_intent in self.tool_intents:
            score = sum(1 for keyword in tool_intent.keywords if keyword in query_lower)
            if score > 0:
                scored_tools.append((tool_intent.tool, score))

        scored_tools.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, _ in scored_tools[:max_tools]]

    async def explain_selection(self, query: str, max_tools: int = 3) -> Dict[str, Any]:
        """
        Explain why specific tools were selected for debugging and transparency.

        Args:
            query: User's query
            max_tools: Maximum number of tools to analyze

        Returns:
            Dictionary with selection explanation
        """
        try:
            query_embedding = np.array(self.embeddings_model.embed_query(query))

            explanations = []
            for tool_intent in self.tool_intents:
                if tool_intent.embedding is not None:
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        tool_intent.embedding.reshape(1, -1),
                    )[0][0]

                    keyword_matches = [
                        kw for kw in tool_intent.keywords if kw in query.lower()
                    ]

                    explanations.append(
                        {
                            "tool_name": tool_intent.tool.name,
                            "similarity_score": float(similarity),
                            "keyword_matches": keyword_matches,
                            "description": tool_intent.description,
                            "selected": similarity >= 0.5,
                        }
                    )

            explanations.sort(key=lambda x: x["similarity_score"], reverse=True)

            return {
                "query": query,
                "explanations": explanations[:max_tools],
                "selection_method": "semantic_similarity",
            }

        except Exception as e:
            logger.error(f"Error explaining selection: {e}")
            return {"query": query, "error": str(e), "selection_method": "fallback"}

    def get_tool_coverage(self) -> Dict[str, Any]:
        """Get information about tool coverage and semantic setup."""
        return {
            "total_tools": len(self.tool_intents),
            "tools_with_embeddings": sum(
                1 for ti in self.tool_intents if ti.embedding is not None
            ),
            "tools": [
                {
                    "name": ti.tool.name,
                    "has_embedding": ti.embedding is not None,
                    "example_count": len(ti.examples),
                    "keyword_count": len(ti.keywords),
                }
                for ti in self.tool_intents
            ],
        }


# Utility function for easy integration
async def create_semantic_selector(tools: List[BaseTool]) -> SemanticToolSelector:
    """
    Create and initialize a semantic tool selector.

    Args:
        tools: List of available tools

    Returns:
        Initialized SemanticToolSelector
    """
    return SemanticToolSelector(tools)


# Example usage and testing
async def test_semantic_selection():
    """Test function to demonstrate semantic tool selection."""
    from langchain_core.tools import tool

    @tool
    def search_courses_tool(query: str) -> str:
        """Search for courses based on query."""
        return f"Searching for courses: {query}"

    @tool
    def get_recommendations_tool() -> str:
        """Get personalized course recommendations."""
        return "Getting recommendations..."

    @tool
    def store_preference_tool(preference: str) -> str:
        """Store a student preference."""
        return f"Stored preference: {preference}"

    tools = [search_courses_tool, get_recommendations_tool, store_preference_tool]
    selector = SemanticToolSelector(tools)

    test_queries = [
        "I want to learn machine learning",
        "What courses should I take next?",
        "I prefer online classes",
        "Show me Redis courses",
    ]

    for query in test_queries:
        selected = await selector.select_tools(query, max_tools=2)
        print(f"Query: '{query}'")
        print(f"Selected: {[t.name for t in selected]}")
        print()


if __name__ == "__main__":
    asyncio.run(test_semantic_selection())
