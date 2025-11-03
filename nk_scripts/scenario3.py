"""
Scenario 3: Agent with Semantic Cache
======================================
Learning Goal: Add semantic caching to reduce LLM calls and costs

Question: "Tell me about Oregon's capital city" (similar to "What is Oregon's capital?")
Expected Behavior: Cache hit if similar question was asked before
Type: cached response
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from redisvl.extensions.llmcache import SemanticCache
import operator
import os
import redis


# ============================================
# STEP 1: Enhanced State with Cache Info
# ============================================
class AgentState(TypedDict):
    """
    State with cache tracking.

    messages: Conversation history
    cache_hit: Whether we got a cached response
    """
    messages: Annotated[list, operator.add]
    cache_hit: bool


# ============================================
# STEP 2: Setup Redis Semantic Cache
# ============================================
# Connect to Redis
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Create semantic cache
# This uses embeddings to find similar queries
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

semantic_cache = SemanticCache(
    name="agent_cache",  # Cache name
    redis_client=redis_client,  # Redis connection
    distance_threshold=0.2,  # Similarity threshold (0-1)
    ttl=3600  # Cache TTL in seconds
)


# ============================================
# STEP 3: Create Tools (from Scenario 2)
# ============================================
@tool
def get_oregon_facts(query: str) -> str:
    """Get facts about Oregon."""
    facts = {
        "founding": "Oregon became a state on February 14, 1859",
        "founding year": "1859",
        "population": "4.2 million as of 2023",
        "capital": "Salem",
        "largest city": "Portland",
        "state flower": "Oregon grape"
    }

    query_lower = query.lower()
    for key, value in facts.items():
        if key in query_lower:
            return value

    return "Fact not found."


tools = [get_oregon_facts]

# ============================================
# STEP 4: Initialize LLM
# ============================================
# Check if OpenAI API key is available
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  Warning: OPENAI_API_KEY not found in environment variables!")
    print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    exit(1)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)


# ============================================
# STEP 5: Cache Check Node (NEW!)
# ============================================
def check_cache(state: AgentState) -> AgentState:
    """
    Check if we have a cached response for this query.

    This is the first node - it looks for semantically similar
    questions in the cache before calling the LLM.
    """
    messages = state["messages"]
    last_human_message = None

    # Find the last human message
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_human_message = msg
            break

    if not last_human_message:
        return {"cache_hit": False}

    query = last_human_message.content

    # Check semantic cache
    cached_response = semantic_cache.check(prompt=query)

    if cached_response:
        print(f"✨ Cache hit! Returning cached response.")
        # Return cached response as an AI message
        return {
            "messages": [AIMessage(content=cached_response[0]["response"])],
            "cache_hit": True
        }
    else:
        print(f"❌ Cache miss. Proceeding to LLM.")
        return {"cache_hit": False}


# ============================================
# STEP 6: Enhanced LLM Node with Caching
# ============================================
def call_llm(state: AgentState) -> AgentState:
    """Call the LLM and cache the response."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)

    # If this is a final response (no tool calls), cache it
    if not (hasattr(response, "tool_calls") and response.tool_calls):
        # Find the original query
        for msg in messages:
            if isinstance(msg, HumanMessage):
                original_query = msg.content
                break

        # Store in cache
        semantic_cache.store(
            prompt=original_query,
            response=response.content
        )
        print(f"💾 Cached response for future use.")

    return {"messages": [response]}


def execute_tools(state: AgentState) -> AgentState:
    """Execute tool calls (same as Scenario 2)."""
    messages = state["messages"]
    last_message = messages[-1]
    tool_calls = last_message.tool_calls

    tool_messages = []
    for tool_call in tool_calls:
        selected_tool = {tool.name: tool for tool in tools}[tool_call["name"]]
        tool_output = selected_tool.invoke(tool_call["args"])
        tool_messages.append(
            ToolMessage(
                content=str(tool_output),
                tool_call_id=tool_call["id"]
            )
        )

    return {"messages": tool_messages}


# ============================================
# STEP 7: Conditional Logic
# ============================================
def should_continue_after_cache(state: AgentState) -> Literal["call_llm", "end"]:
    """
    After cache check, decide next step.

    If cache hit, we're done.
    If cache miss, call the LLM.
    """
    if state.get("cache_hit", False):
        return "end"
    return "call_llm"


def should_continue_after_llm(state: AgentState) -> Literal["execute_tools", "end"]:
    """After LLM, decide if we need tools."""
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "execute_tools"
    return "end"


# ============================================
# STEP 8: Build the Graph
# ============================================
def create_cached_agent():
    """
    Creates an agent with semantic caching.

    Flow:
    START -> check_cache -> [cache hit?]
                              ├─> END (cache hit)
                              └─> call_llm -> [needs tools?]
                                               ├─> execute_tools -> call_llm
                                               └─> END
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("check_cache", check_cache)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("execute_tools", execute_tools)

    # Start with cache check
    workflow.set_entry_point("check_cache")

    # After cache check
    workflow.add_conditional_edges(
        "check_cache",
        should_continue_after_cache,
        {
            "call_llm": "call_llm",
            "end": END
        }
    )

    # After LLM call
    workflow.add_conditional_edges(
        "call_llm",
        should_continue_after_llm,
        {
            "execute_tools": "execute_tools",
            "end": END
        }
    )

    # After tools, back to LLM
    workflow.add_edge("execute_tools", "call_llm")

    return workflow.compile()


# ============================================
# STEP 9: Run and Test
# ============================================
if __name__ == "__main__":
    app = create_cached_agent()

    # Test with similar questions
    questions = [
        "What is the capital of the state of Oregon?",
        "Tell me about Oregon state's capital city",  # Similar - should hit cache
        "Tell me what the capital city of Oregon is",  # Similar - should hit cache
        "What year was Oregon founded?"  # Different - cache miss
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'=' * 60}")
        print(f"Query {i}: {question}")
        print('=' * 60)

        initial_state = {
            "messages": [HumanMessage(content=question)],
            "cache_hit": False
        }

        result = app.invoke(initial_state)

        # Print final answer
        final_message = result["messages"][-1]
        print(f"\nAnswer: {final_message.content}")

        if result.get("cache_hit"):
            print("⚡ Response served from cache!")

    print("\n" + "=" * 60)
    print("✅ Scenario 3 Complete!")
    print("=" * 60)

    print("\nGraph Structure:")
    print("START -> check_cache -> [cache hit?]")
    print("                          ├─> END (cached)")
    print("                          └─> call_llm -> [tools?]")
    print("                                           ├─> execute_tools -> call_llm")
    print("                                           └─> END")

"""
KEY CONCEPTS EXPLAINED:
=======================

1. SEMANTIC CACHE:
   - Uses embeddings to find similar queries
   - Not exact string matching - understands meaning
   - "What is Oregon's capital?" ≈ "Tell me about Oregon's capital city"
   - Configurable similarity threshold (distance_threshold)

2. CACHE WORKFLOW:
   a. Query comes in
   b. Convert query to embedding
   c. Search Redis for similar embeddings
   d. If found and similar enough -> return cached response
   e. Otherwise -> proceed to LLM

3. TTL (Time To Live):
   - Cached responses expire after ttl seconds
   - Prevents stale data
   - Configurable per use case

4. DISTANCE THRESHOLD:
   - Lower = more strict (requires closer match)
   - Higher = more lenient (accepts less similar queries)
   - 0.1 is fairly strict, 0.3-0.4 is more lenient

WHAT'S NEW FROM SCENARIO 2:
============================
- Added check_cache node at the start
- Integrated Redis for cache storage
- Using embeddings for semantic similarity
- Storing successful responses for reuse
- New conditional: cache hit or miss

BENEFITS:
=========
- Reduced LLM costs (cached responses are free)
- Faster response times (no LLM call needed)
- Handles query variations naturally
- Scales well with high traffic

CACHE INVALIDATION:
===================
- Use TTL for automatic expiration
- Manually clear with semantic_cache.clear()
- Clear specific keys if data changes
"""