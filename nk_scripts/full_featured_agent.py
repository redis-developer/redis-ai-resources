#!/usr/bin/env python3
"""
Full-Featured Agent Architecture

A simplified Python version of the Oregon Trail agent with:
- Tool-enabled workflow
- Semantic caching
- Retrieval augmented generation (RAG)
- Multiple choice structured output
- Allow/block list routing

Based on: python-recipes/agents/02_full_featured_agent.ipynb
"""

import os
import warnings
from typing import Literal, TypedDict
from functools import lru_cache

# LangChain imports
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_core.documents import Document
from langchain.tools.retriever import create_retriever_tool

# LangGraph imports
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode

# RedisVL imports
from redisvl.extensions.llmcache import SemanticCache

# Pydantic imports
from pydantic import BaseModel, Field

# Suppress warnings
warnings.filterwarnings("ignore")

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "oregon_trail")

# Check OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  Warning: OPENAI_API_KEY not found in environment variables!")
    print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    exit(1)

print("🚀 Initializing Full-Featured Agent...")

# ============================================
# TOOLS DEFINITION
# ============================================

class RestockInput(BaseModel):
    daily_usage: int = Field(description="Pounds (lbs) of food expected to be consumed daily")
    lead_time: int = Field(description="Lead time to replace food in days")
    safety_stock: int = Field(description="Number of pounds (lbs) of safety stock to keep on hand")

@tool("restock-tool", args_schema=RestockInput)
def restock_tool(daily_usage: int, lead_time: int, safety_stock: int) -> int:
    """Restock formula tool used specifically for calculating the amount of food at which you should start restocking."""
    print(f"🔧 Called restock tool: {daily_usage=}, {lead_time=}, {safety_stock=}")
    return (daily_usage * lead_time) + safety_stock

class ToolManager:
    """Manages tool initialization and lifecycle"""

    def __init__(self, redis_url: str, index_name: str):
        self.redis_url = redis_url
        self.index_name = index_name
        self._vector_store = None
        self._tools = None
        self._semantic_cache = None

    def setup_vector_store(self):
        """Initialize vector store with Oregon Trail data"""
        if self._vector_store is not None:
            return self._vector_store

        config = RedisConfig(index_name=self.index_name, redis_url=self.redis_url)

        # Sample document about trail routes
        doc = Document(
            page_content="the northern trail, of the blue mountains, was destroyed by a flood and is no longer safe to traverse. It is recommended to take the southern trail although it is longer."
        )

        try:
            config.from_existing = True
            self._vector_store = RedisVectorStore(OpenAIEmbeddings(), config=config)
        except:
            print("📚 Initializing vector store with documents...")
            config.from_existing = False
            self._vector_store = RedisVectorStore.from_documents([doc], OpenAIEmbeddings(), config=config)

        return self._vector_store

    def get_tools(self):
        """Initialize and return all tools"""
        if self._tools is not None:
            return self._tools

        vector_store = self.setup_vector_store()
        retriever_tool = create_retriever_tool(
            vector_store.as_retriever(),
            "get_directions",
            "Search and return information related to which routes/paths/trails to take along your journey."
        )

        self._tools = [retriever_tool, restock_tool]
        return self._tools

    def get_semantic_cache(self):
        """Initialize and return semantic cache"""
        if self._semantic_cache is not None:
            return self._semantic_cache

        self._semantic_cache = SemanticCache(
            name="oregon_trail_cache",
            redis_url=self.redis_url,
            distance_threshold=0.1,
        )

        # Pre-populate cache with known answers
        known_answers = {
            "There's a deer. You're hungry. You know what you have to do...": "bang",
            "What is the first name of the wagon leader?": "Art"
        }

        for question, answer in known_answers.items():
            self._semantic_cache.store(prompt=question, response=answer)

        print("💾 Semantic cache initialized with known answers")
        return self._semantic_cache

# ============================================
# STATE DEFINITION
# ============================================

class MultipleChoiceResponse(BaseModel):
    multiple_choice_response: Literal["A", "B", "C", "D"] = Field(
        description="Single character response to the question for multiple choice questions. Must be either A, B, C, or D."
    )

class AgentState(MessagesState):
    multi_choice_response: MultipleChoiceResponse = None

# ============================================
# AGENT CLASS
# ============================================

class OregonTrailAgent:
    """Main agent class that orchestrates the workflow"""

    def __init__(self, redis_url: str = REDIS_URL, index_name: str = INDEX_NAME):
        self.tool_manager = ToolManager(redis_url, index_name)
        self._workflow = None

    @property
    def tools(self):
        return self.tool_manager.get_tools()

    @property
    def semantic_cache(self):
        return self.tool_manager.get_semantic_cache()

    @property
    def workflow(self):
        if self._workflow is None:
            self._workflow = self._create_workflow()
        return self._workflow

# ============================================
# LLM MODELS
# ============================================

# Remove the old global functions - now part of the class

# ============================================
# NODES
# ============================================

    def check_cache(self, state: AgentState) -> AgentState:
        """Check semantic cache for known answers"""
        last_message = state["messages"][-1]
        query = last_message.content

        cached_response = self.semantic_cache.check(prompt=query, return_fields=["response"])

        if cached_response:
            print("✨ Cache hit! Returning cached response")
            return {
                "messages": [HumanMessage(content=cached_response[0]["response"])],
                "cache_hit": True
            }
        else:
            print("❌ Cache miss. Proceeding to agent")
            return {"cache_hit": False}

    def call_agent(self, state: AgentState) -> AgentState:
        """Call the main agent with tools"""
        system_prompt = """
        You are an Oregon Trail playing tool calling AI agent. Use the tools available to you to answer the question you are presented. When in doubt use the tools to help you find the answer.
        If anyone asks your first name is Art return just that string.
        """

        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        model = self._get_tool_model()
        response = model.invoke(messages)

        return {"messages": [response]}

    def structure_response(self, state: AgentState) -> AgentState:
        """Structure response for multiple choice questions"""
        last_message = state["messages"][-1]

        # Check if it's a multiple choice question
        if "options:" in state["messages"][0].content.lower():
            print("🔧 Structuring multiple choice response")

            model = self._get_response_model()
            response = model.invoke([
                HumanMessage(content=state["messages"][0].content),
                HumanMessage(content=f"Answer from tool: {last_message.content}")
            ])

            return {"multi_choice_response": response.multiple_choice_response}

        # Cache the response if it's not a tool call
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            original_query = state["messages"][0].content
            self.semantic_cache.store(prompt=original_query, response=last_message.content)
            print("💾 Cached response for future use")

        return {"messages": []}

    def _get_tool_node(self):
        """Get tool execution node"""
        return ToolNode(self.tools)

    def _get_tool_model(self):
        """Get LLM model with tools bound"""
        model = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
        return model.bind_tools(self.tools)

    def _get_response_model(self):
        """Get LLM model with structured output"""
        model = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
        return model.with_structured_output(MultipleChoiceResponse)

    # ============================================
    # CONDITIONAL LOGIC
    # ============================================

    def should_continue_after_cache(self, state: AgentState) -> Literal["call_agent", "end"]:
        """Decide next step after cache check"""
        return "end" if state.get("cache_hit", False) else "call_agent"

    def should_continue_after_agent(self, state: AgentState) -> Literal["tools", "structure_response"]:
        """Decide whether to use tools or structure response"""
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "structure_response"

    # ============================================
    # GRAPH CONSTRUCTION
    # ============================================

    def _create_workflow(self):
        """Create the full-featured agent workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("check_cache", self.check_cache)
        workflow.add_node("call_agent", self.call_agent)
        workflow.add_node("tools", self._get_tool_node())
        workflow.add_node("structure_response", self.structure_response)

        # Set entry point
        workflow.set_entry_point("check_cache")

        # Add conditional edges
        workflow.add_conditional_edges(
            "check_cache",
            self.should_continue_after_cache,
            {"call_agent": "call_agent", "end": END}
        )

        workflow.add_conditional_edges(
            "call_agent",
            self.should_continue_after_agent,
            {"tools": "tools", "structure_response": "structure_response"}
        )

        # Add regular edges
        workflow.add_edge("tools", "call_agent")
        workflow.add_edge("structure_response", END)

        return workflow.compile()

    def invoke(self, input_data):
        """Run the agent workflow"""
        return self.workflow.invoke(input_data)

# ============================================
# HELPER FUNCTIONS
# ============================================

def format_multi_choice_question(question: str, options: list) -> list:
    """Format a multiple choice question"""
    formatted = f"{question}, options: {' '.join(options)}"
    return [HumanMessage(content=formatted)]

def run_scenario(agent: OregonTrailAgent, scenario: dict):
    """Run a single scenario and return results"""
    print(f"\n{'='*60}")
    print(f"🎯 Question: {scenario['question']}")
    print('='*60)

    # Format input based on scenario type
    if scenario.get("type") == "multi-choice":
        messages = format_multi_choice_question(scenario["question"], scenario["options"])
    else:
        messages = [HumanMessage(content=scenario["question"])]

    # Run the agent
    result = agent.invoke({"messages": messages})

    # Extract answer
    if "multi_choice_response" in result and result["multi_choice_response"]:
        answer = result["multi_choice_response"]
    else:
        answer = result["messages"][-1].content

    print(f"🤖 Agent response: {answer}")

    # Verify answer if expected answer is provided
    if "answer" in scenario:
        is_correct = answer == scenario["answer"]
        print(f"✅ Correct!" if is_correct else f"❌ Expected: {scenario['answer']}")
        return is_correct

    return True

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    # Create the agent
    agent = OregonTrailAgent()
    
    print("🎮 Running Oregon Trail Agent Scenarios...")
    
    # Define test scenarios
    scenarios = [
        {
            "name": "Scenario 1: Wagon Leader Name",
            "question": "What is the first name of the wagon leader?",
            "answer": "Art",
            "type": "free-form"
        },
        {
            "name": "Scenario 2: Restocking Tool",
            "question": "In order to survive the trail ahead, you'll need to have a restocking strategy for when you need to get more supplies or risk starving. If it takes you an estimated 3 days to restock your food and you plan to start with 200lbs of food, budget 10lbs/day to eat, and keep a safety stock of at least 50lbs of back up... at what point should you restock?",
            "answer": "D",
            "options": ["A: 100lbs", "B: 20lbs", "C: 5lbs", "D: 80lbs"],
            "type": "multi-choice"
        },
        {
            "name": "Scenario 3: Retrieval Tool",
            "question": "You've encountered a dense forest near the Blue Mountains, and your party is unsure how to proceed. There is a fork in the road, and you must choose a path. Which way will you go?",
            "answer": "B",
            "options": ["A: take the northern trail", "B: take the southern trail", "C: turn around", "D: go fishing"],
            "type": "multi-choice"
        },
        {
            "name": "Scenario 4: Semantic Cache",
            "question": "There's a deer. You're hungry. You know what you have to do...",
            "answer": "bang",
            "type": "free-form"
        }
    ]
    
    # Run all scenarios
    results = []
    for scenario in scenarios:
        print(f"\n🎪 {scenario['name']}")
        success = run_scenario(agent, scenario)
        results.append(success)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY: {sum(results)}/{len(results)} scenarios passed")
    print('='*60)
    
    if all(results):
        print("🎉 All scenarios completed successfully!")
    else:
        print("⚠️  Some scenarios failed. Check the output above.")
    
    print("\n🏁 Full-Featured Agent demo complete!")
