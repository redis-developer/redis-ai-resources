"""
Full-Featured AI Agent with LangGraph and Redis
================================================
Oregon Trail-themed agent with semantic routing, caching, tools, and memory.

Features:
- Semantic Router: Filters off-topic queries
- Semantic Cache: Reduces LLM costs
- Tool Calling: External function execution
- Conversation Memory: Persistent context
"""

import os
from typing import TypedDict, Annotated, Literal
from operator import add

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver
from pydantic import BaseModel, Field
from redis import Redis
from redisvl.extensions.llmcache import SemanticCache
from redisvl.extensions.router import SemanticRouter, Route


# ============================================
# Configuration
# ============================================
class Config:
    """Configuration settings"""
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-4o-mini"
    CACHE_TTL = 3600
    CACHE_THRESHOLD = 0.1


# ============================================
# State Definition
# ============================================
class AgentState(TypedDict):
    """Agent state schema"""
    messages: Annotated[list, add]
    route_decision: str
    cache_hit: bool


# ============================================
# Tools Definition
# ============================================
class RestockInput(BaseModel):
    """Input schema for restock calculation"""
    daily_usage: int = Field(description="Pounds of food consumed daily")
    lead_time: int = Field(description="Lead time to replace food in days")
    safety_stock: int = Field(description="Pounds of safety stock to keep")


@tool("restock-tool", args_schema=RestockInput)
def restock_tool(daily_usage: int, lead_time: int, safety_stock: int) -> str:
    """
    Calculate restock point for Oregon Trail supplies.

    Returns the inventory level at which new supplies should be ordered
    to avoid running out during the lead time.
    """
    restock_point = (daily_usage * lead_time) + safety_stock
    return f"Restock when inventory reaches {restock_point} lbs"


@tool("weather-tool")
def weather_tool() -> str:
    """Get current weather conditions on the Oregon Trail."""
    return "Current conditions: Partly cloudy, 68°F. Good travel weather."


@tool("hunting-tool")
def hunting_tool() -> str:
    """Check hunting opportunities along the trail."""
    return "Buffalo spotted nearby. Good hunting conditions. Remember to say 'bang'!"


# ============================================
# Redis Components Setup
# ============================================
class RedisComponents:
    """Manages Redis-based components"""

    def __init__(self, config: Config):
        self.redis_client = Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            decode_responses=False
        )

        # Semantic cache
        self.cache = SemanticCache(
            name="oregon_trail_cache",
            redis_client=self.redis_client,
            distance_threshold=config.CACHE_THRESHOLD,
            ttl=config.CACHE_TTL
        )

        # Memory checkpointer
        self.memory = RedisSaver(self.redis_client)

        # Semantic router
        self._setup_router()

    def _setup_router(self):
        """Configure semantic router with allowed/blocked topics"""
        allowed = Route(
            name="oregon_topics",
            references=[
                "Oregon Trail information",
                "Pioneer life and travel",
                "Hunting and supplies",
                "Weather along the trail",
                "Inventory management",
                "Oregon geography and history",
                "Trail challenges and solutions",
            ],
            metadata={"type": "allowed"}
        )

        blocked = Route(
            name="blocked_topics",
            references=[
                "Stock market analysis",
                "Cryptocurrency trading",
                "Python programming",
                "Machine learning tutorials",
                "Modern politics",
                "Celebrity gossip",
                "Sports scores",
            ],
            metadata={"type": "blocked"}
        )

        self.router = SemanticRouter(
            name="topic_router",
            routes=[allowed, blocked],
            redis_client=self.redis_client
        )


# ============================================
# Agent Nodes
# ============================================
class AgentNodes:
    """Node functions for the agent graph"""

    def __init__(self, redis_components: RedisComponents, config: Config):
        self.redis = redis_components
        self.llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0)
        self.llm_with_tools = self.llm.bind_tools(TOOLS)
        self.system_prompt = """You are Art, a helpful guide on the Oregon Trail.

You assist pioneers with:
- Inventory and supply management
- Weather conditions
- Hunting opportunities
- Trail advice

Use the tools available to help answer questions accurately.
If asked your first name, respond with just 'Art'.
Keep responses concise and helpful."""

    def check_route(self, state: AgentState) -> dict:
        """Filter queries using semantic router"""
        query = self._get_last_human_message(state)
        if not query:
            return {"route_decision": "unknown"}

        route_result = self.redis.router(query)
        print(f"🛣️  Route: {route_result.name} (distance: {route_result.distance:.3f})")

        if route_result.name == "blocked_topics":
            return {
                "messages": [SystemMessage(
                    content="I can only help with Oregon Trail-related questions. "
                            "Please ask about pioneer life, supplies, or trail conditions."
                )],
                "route_decision": "blocked"
            }

        return {"route_decision": "allowed"}

    def check_cache(self, state: AgentState) -> dict:
        """Check semantic cache for similar queries"""
        query = self._get_last_human_message(state)
        if not query:
            return {"cache_hit": False}

        cached = self.redis.cache.check(prompt=query)
        if cached:
            print("✨ Cache hit!")
            return {
                "messages": [SystemMessage(content=cached[0]["response"])],
                "cache_hit": True
            }

        print("❌ Cache miss")
        return {"cache_hit": False}

    def call_llm(self, state: AgentState) -> dict:
        """Call LLM with system prompt and conversation history"""
        messages = [SystemMessage(content=self.system_prompt)] + state["messages"]
        response = self.llm_with_tools.invoke(messages)

        # Cache final responses (not tool calls)
        if not (hasattr(response, "tool_calls") and response.tool_calls):
            query = self._get_last_human_message(state)
            if query:
                self.redis.cache.store(prompt=query, response=response.content)
                print("💾 Cached response")

        return {"messages": [response]}

    def execute_tools(self, state: AgentState) -> dict:
        """Execute tool calls from LLM"""
        from langchain_core.messages import ToolMessage

        last_message = state["messages"][-1]
        tool_calls = last_message.tool_calls

        tool_messages = []
        for tool_call in tool_calls:
            tool = TOOL_MAP[tool_call["name"]]
            result = tool.invoke(tool_call["args"])
            print(f"🔧 {tool_call['name']}: {result}")

            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
            )

        return {"messages": tool_messages}

    @staticmethod
    def _get_last_human_message(state: AgentState) -> str:
        """Extract last human message from state"""
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                return msg.content
        return ""


# ============================================
# Conditional Logic
# ============================================
def should_continue_after_route(state: AgentState) -> Literal["check_cache", "end"]:
    """Decide whether to proceed after routing"""
    return "end" if state.get("route_decision") == "blocked" else "check_cache"


def should_continue_after_cache(state: AgentState) -> Literal["call_llm", "end"]:
    """Decide whether to proceed after cache check"""
    return "end" if state.get("cache_hit") else "call_llm"


def should_continue_after_llm(state: AgentState) -> Literal["execute_tools", "end"]:
    """Decide whether to execute tools or end"""
    last_message = state["messages"][-1]
    has_tool_calls = hasattr(last_message, "tool_calls") and last_message.tool_calls
    return "execute_tools" if has_tool_calls else "end"


# ============================================
# Graph Builder
# ============================================
def create_agent(config: Config = Config()) -> tuple:
    """
    Create the full-featured agent graph.

    Returns:
        tuple: (compiled_graph, redis_components)
    """
    # Initialize components
    redis_components = RedisComponents(config)
    nodes = AgentNodes(redis_components, config)

    # Build graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("check_route", nodes.check_route)
    workflow.add_node("check_cache", nodes.check_cache)
    workflow.add_node("call_llm", nodes.call_llm)
    workflow.add_node("execute_tools", nodes.execute_tools)

    # Define flow
    workflow.set_entry_point("check_route")

    workflow.add_conditional_edges(
        "check_route",
        should_continue_after_route,
        {"check_cache": "check_cache", "end": END}
    )

    workflow.add_conditional_edges(
        "check_cache",
        should_continue_after_cache,
        {"call_llm": "call_llm", "end": END}
    )

    workflow.add_conditional_edges(
        "call_llm",
        should_continue_after_llm,
        {"execute_tools": "execute_tools", "end": END}
    )

    workflow.add_edge("execute_tools", "call_llm")

    # Compile with memory
    app = workflow.compile(checkpointer=redis_components.memory)

    return app, redis_components


# ============================================
# Main Execution
# ============================================
TOOLS = [restock_tool, weather_tool, hunting_tool]
TOOL_MAP = {tool.name: tool for tool in TOOLS}


def run_agent_conversation(queries: list[str], thread_id: str = "demo_session"):
    """Run a conversation with the agent"""
    config_dict = {"configurable": {"thread_id": thread_id}}
    app, _ = create_agent()

    for query in queries:
        print(f"\n{'=' * 70}")
        print(f"👤 User: {query}")
        print('=' * 70)

        result = app.invoke(
            {
                "messages": [HumanMessage(content=query)],
                "route_decision": "",
                "cache_hit": False
            },
            config=config_dict
        )

        final_message = result["messages"][-1]
        print(f"🤖 Agent: {final_message.content}")


if __name__ == "__main__":
    # Example conversation
    queries = [
        "What's the weather like on the trail?",
        "Calculate restock point if we use 50 lbs daily, 5 day lead time, 100 lbs safety stock",
        "What should I do when I see buffalo?",
        "Tell me about the S&P 500",  # Should be blocked
        "What's your first name?",
    ]

    run_agent_conversation(queries)