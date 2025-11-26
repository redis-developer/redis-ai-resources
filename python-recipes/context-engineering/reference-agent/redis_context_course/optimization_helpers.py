"""
Optimization helpers for context engineering.

This module contains helper functions and patterns demonstrated in Section 4
of the Context Engineering course. These are production-ready patterns for:
- Context window management
- Retrieval strategies
- Tool optimization
- Data crafting for LLMs
"""

from typing import Any, Dict, List, Optional

import tiktoken
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


# Token Counting (from Section 4, notebook 01_context_window_management.ipynb)
def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Count tokens in text for a specific model.

    Args:
        text: Text to count tokens for
        model: Model name (default: gpt-4o)

    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def estimate_token_budget(
    system_prompt: str,
    working_memory_messages: int,
    long_term_memories: int,
    retrieved_context_items: int,
    avg_message_tokens: int = 50,
    avg_memory_tokens: int = 100,
    avg_context_tokens: int = 200,
    response_tokens: int = 2000,
) -> Dict[str, int]:
    """
    Estimate token budget for a conversation turn.

    Args:
        system_prompt: System prompt text
        working_memory_messages: Number of messages in working memory
        long_term_memories: Number of long-term memories to include
        retrieved_context_items: Number of retrieved context items
        avg_message_tokens: Average tokens per message
        avg_memory_tokens: Average tokens per memory
        avg_context_tokens: Average tokens per context item
        response_tokens: Tokens reserved for response

    Returns:
        Dictionary with token breakdown
    """
    system_tokens = count_tokens(system_prompt)
    working_memory_tokens = working_memory_messages * avg_message_tokens
    long_term_tokens = long_term_memories * avg_memory_tokens
    context_tokens = retrieved_context_items * avg_context_tokens

    total_input = (
        system_tokens + working_memory_tokens + long_term_tokens + context_tokens
    )
    total_with_response = total_input + response_tokens

    return {
        "system_prompt": system_tokens,
        "working_memory": working_memory_tokens,
        "long_term_memory": long_term_tokens,
        "retrieved_context": context_tokens,
        "response_space": response_tokens,
        "total_input": total_input,
        "total_with_response": total_with_response,
        "percentage_of_128k": (total_with_response / 128000) * 100,
    }


# Retrieval Strategies (from Section 4, notebook 02_retrieval_strategies.ipynb)
async def hybrid_retrieval(
    query: str, summary_view: str, search_function, limit: int = 3
) -> str:
    """
    Hybrid retrieval: Combine pre-computed summary with targeted search.

    This is the recommended strategy for production systems.

    Args:
        query: User's query
        summary_view: Pre-computed summary/overview
        search_function: Async function that searches for specific items
        limit: Number of specific items to retrieve

    Returns:
        Combined context string
    """
    # Get specific relevant items
    specific_items = await search_function(query, limit=limit)

    # Combine summary + specific items
    context = f"""{summary_view}

Relevant items for this query:
{specific_items}
"""

    return context


# Structured Views (from Section 4, notebook 05_crafting_data_for_llms.ipynb)
async def create_summary_view(
    items: List[Any],
    group_by_field: str,
    llm: Optional[ChatOpenAI] = None,
    max_items_per_group: int = 10,
) -> str:
    """
    Create a structured summary view of items.

    This implements the "Retrieve → Summarize → Stitch → Save" pattern.

    Args:
        items: List of items to summarize
        group_by_field: Field to group items by
        llm: LLM for generating summaries (optional)
        max_items_per_group: Max items to include per group

    Returns:
        Formatted summary view
    """
    # Step 1: Group items
    groups = {}
    for item in items:
        group_key = getattr(item, group_by_field, "Other")
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)

    # Step 2 & 3: Summarize and stitch
    summary_parts = ["Summary View\n" + "=" * 50 + "\n"]

    for group_name, group_items in sorted(groups.items()):
        summary_parts.append(f"\n{group_name} ({len(group_items)} items):")

        # Include first N items
        for item in group_items[:max_items_per_group]:
            # Customize this based on your item type
            summary_parts.append(f"- {str(item)[:100]}...")

        if len(group_items) > max_items_per_group:
            summary_parts.append(
                f"  ... and {len(group_items) - max_items_per_group} more"
            )

    return "\n".join(summary_parts)


async def create_user_profile_view(
    user_data: Dict[str, Any], memories: List[Any], llm: ChatOpenAI
) -> str:
    """
    Create a comprehensive user profile view.

    This combines structured data with LLM-summarized memories.

    Args:
        user_data: Structured user data (dict)
        memories: List of user memories
        llm: LLM for summarizing memories

    Returns:
        Formatted profile view
    """
    # Structured sections (no LLM needed)
    profile_parts = [
        f"User Profile: {user_data.get('user_id', 'Unknown')}",
        "=" * 50,
        "",
    ]

    # Add structured data
    if "academic_info" in user_data:
        profile_parts.append("Academic Info:")
        for key, value in user_data["academic_info"].items():
            profile_parts.append(f"- {key}: {value}")
        profile_parts.append("")

    # Summarize memories with LLM
    if memories:
        memory_text = "\n".join([f"- {m.text}" for m in memories[:20]])

        prompt = f"""Summarize these user memories into organized sections.
Be concise. Use bullet points.

Memories:
{memory_text}

Create sections for:
1. Preferences
2. Goals
3. Important Facts
"""

        messages = [
            SystemMessage(
                content="You are a helpful assistant that summarizes user information."
            ),
            HumanMessage(content=prompt),
        ]

        response = llm.invoke(messages)
        profile_parts.append(response.content)

    return "\n".join(profile_parts)


# Tool Optimization (from Section 4, notebook 04_tool_optimization.ipynb)
def filter_tools_by_intent(
    query: str, tool_groups: Dict[str, List], default_group: str = "search"
) -> List:
    """
    Filter tools based on query intent using keyword matching.

    For production, consider using LLM-based intent classification.

    Args:
        query: User's query
        tool_groups: Dictionary mapping intent to tool lists
        default_group: Default group if no match

    Returns:
        List of relevant tools
    """
    query_lower = query.lower()

    # Define keyword patterns for each intent
    intent_patterns = {
        "search": ["search", "find", "show", "what", "which", "tell me about", "list"],
        "memory": ["remember", "recall", "know about", "preferences", "store", "save"],
        "enrollment": ["enroll", "register", "drop", "add", "remove", "conflict"],
        "review": ["review", "rating", "feedback", "opinion", "rate"],
    }

    # Check each intent
    for intent, keywords in intent_patterns.items():
        if any(keyword in query_lower for keyword in keywords):
            return tool_groups.get(intent, tool_groups.get(default_group, []))

    # Default
    return tool_groups.get(default_group, [])


async def classify_intent_with_llm(
    query: str, intents: List[str], llm: ChatOpenAI
) -> str:
    """
    Classify user intent using LLM.

    More accurate than keyword matching but requires an LLM call.

    Args:
        query: User's query
        intents: List of possible intents
        llm: LLM for classification

    Returns:
        Classified intent
    """
    intent_list = "\n".join([f"- {intent}" for intent in intents])

    prompt = f"""Classify the user's intent into one of these categories:
{intent_list}

User query: "{query}"

Respond with only the category name.
"""

    messages = [
        SystemMessage(
            content="You are a helpful assistant that classifies user intents."
        ),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    intent = response.content.strip().lower()

    # Validate
    if intent not in intents:
        intent = intents[0]  # Default to first intent

    return intent


# Grounding Helpers (from Section 4, notebook 03_grounding_with_memory.ipynb)
def extract_references(query: str) -> Dict[str, List[str]]:
    """
    Extract references from a query that need grounding.

    This is a simple pattern matcher. For production, consider using NER.

    Args:
        query: User's query

    Returns:
        Dictionary of reference types and their values
    """
    references = {"pronouns": [], "demonstratives": [], "implicit": []}

    query_lower = query.lower()

    # Pronouns
    pronouns = ["it", "that", "this", "those", "these", "he", "she", "they", "them"]
    for pronoun in pronouns:
        if f" {pronoun} " in f" {query_lower} ":
            references["pronouns"].append(pronoun)

    # Demonstratives
    if "the one" in query_lower or "the other" in query_lower:
        references["demonstratives"].append("the one/other")

    # Implicit references (questions without explicit subject)
    implicit_patterns = [
        "what are the prerequisites",
        "when is it offered",
        "how many credits",
        "is it available",
    ]
    for pattern in implicit_patterns:
        if pattern in query_lower:
            references["implicit"].append(pattern)

    return references


# Utility Functions
def format_context_for_llm(
    system_instructions: str,
    summary_view: Optional[str] = None,
    user_profile: Optional[str] = None,
    retrieved_items: Optional[str] = None,
    memories: Optional[str] = None,
) -> str:
    """
    Format various context sources into a single system prompt.

    This is the recommended way to combine different context sources.

    Args:
        system_instructions: Base system instructions
        summary_view: Pre-computed summary view
        user_profile: User profile view
        retrieved_items: Retrieved specific items
        memories: Relevant memories

    Returns:
        Formatted system prompt
    """
    parts = [system_instructions]

    if summary_view:
        parts.append(f"\n## Overview\n{summary_view}")

    if user_profile:
        parts.append(f"\n## User Profile\n{user_profile}")

    if memories:
        parts.append(f"\n## Relevant Memories\n{memories}")

    if retrieved_items:
        parts.append(f"\n## Specific Information\n{retrieved_items}")

    return "\n".join(parts)
