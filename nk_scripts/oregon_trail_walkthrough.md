Oregon Trail


￼


# Demo Talking Points: Full-Featured Agent Notebook

## 🎯 Introduction Slide

**What to say:**
"Today we're building a production-ready AI agent using the Oregon Trail as our teaching metaphor. By the end, you'll have an agent with routing, caching, tools, RAG, and memory - all the components you need for enterprise applications. 

This isn't just a toy example; this is the same architecture powering customer support bots, sales assistants, and internal tools at major companies."

---

## 📦 CELL 1: Package Installation

```python
%pip install -q langchain langchain-openai "langchain-redis>=0.2.0" langgraph sentence-transformers
```

**Talking Points:**

### **langchain** - The Framework Foundation
- "LangChain is our orchestration layer - think of it as the glue between components"
- "It provides abstractions for working with LLMs, tools, and memory without getting locked into vendor-specific APIs"

- **Under the hood:** LangChain creates a standardized interface. When you call `llm.invoke()`, it handles API formatting, retries, streaming, and error handling

- **Why needed:** Without it, you'd be writing custom code for each LLM provider (OpenAI, Anthropic, etc.)

### **langchain-openai** - LLM Provider Integration
- "This gives us OpenAI-specific implementations - the ChatGPT models we'll use"

- **What it does:** Implements LangChain's base classes for OpenAI's API (chat models, embeddings, function calling)
- **Alternative:** Could swap for `langchain-anthropic`, `langchain-google-vertexai`, etc.

### **langchain-redis>=0.2.0** - Redis Integration
- "This is our Redis connector for LangChain - handles vector storage, caching, and checkpointing"

- **Under the hood:** Wraps Redis commands in LangChain interfaces (VectorStore, BaseCache, etc.)

- **Why version 0.2.0+:** Earlier versions lacked checkpointer support needed for conversation memory
- **What it provides:**
  - RedisVectorStore for RAG
  - RedisCache for semantic caching
  - RedisSaver for conversation checkpointing

### **langgraph** - State Machine for Agents
- "LangGraph is our state machine - it turns our agent into a controllable workflow"
- **Why not just LangChain:** LangChain's AgentExecutor is a black box. LangGraph makes every decision explicit and debuggable
- **What it provides:**
  - StateGraph for defining nodes and edges
  - Conditional routing
  - Built-in checkpointing
  - Graph visualization
- **Under the hood:** Creates a directed graph where each node is a function that transforms state

### **sentence-transformers** - Embedding Models
- "This runs embedding models locally - we'll use it for semantic similarity in caching and routing"
- **What it does:** Loads pre-trained models (like `all-MiniLM-L6-v2`) that convert text to vectors
- **Why not just OpenAI embeddings:** Cost and latency. Local embeddings are free and instant
- **Use cases here:** Cache similarity checks, router classification

**Demo tip:** "Notice the `-q` flag - keeps output quiet. In production, pin exact versions in `requirements.txt`"

---

## 🔧 CELL 2: Environment Setup

```python
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"
```

**Talking Points:**

"Setting up credentials. In production, never hardcode keys like this:"
- **Better approach:** Use `.env` files with `python-dotenv`
- **Best approach:** Use secret managers (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
- **Why it matters:** Accidentally committing API keys costs thousands when bots mine them from GitHub

"Also good to set:"
```python
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["LANGCHAIN_TRACING_V2"] = "true"  # Enable LangSmith tracing
```

---

## 🔗 CELL 3: Redis Connection Test

```python
from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
client = Redis.from_url(REDIS_URL)
client.ping()
```

**Talking Points:**

### **Why Test the Connection First:**
- "This is the foundation - if Redis is down, nothing else works"
- "Better to fail fast here than 20 minutes into setup"

### **Redis.from_url() Explained:**
- **What it does:** Parses connection string and creates client
- **Formats supported:** 
  - `redis://localhost:6379` (standard)
  - `rediss://...` (SSL/TLS)
  - `redis://user:password@host:port/db`
- **Connection pooling:** Under the hood, creates a connection pool (default 50 connections)

### **client.ping():**
- **What it does:** Sends PING command, expects PONG response
- **Returns:** `True` if connected, raises exception if not
- **Why it's important:** Validates authentication, network connectivity, and that Redis is running

**Demo tip:** "Let's run this. If it returns `True`, we're good. If it fails, check Docker is running: `docker ps` should show redis-stack-server"

---

## 🛠️ CELL 4: Defining Tools - Restock Calculator

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class RestockInput(BaseModel):
    daily_usage: int = Field(description="Pounds (lbs) of food expected to be consumed daily")
    lead_time: int = Field(description="Lead time to replace food in days")
    safety_stock: int = Field(description="Number of pounds (lbs) of safety stock to keep on hand")

@tool("restock-tool", args_schema=RestockInput)
def restock_tool(daily_usage: int, lead_time: int, safety_stock: int) -> str:
    """
    Calculate reorder point for food supplies on the Oregon Trail.
    
    Formula: restock_point = (daily_usage × lead_time) + safety_stock
    
    Returns when you need to buy more supplies to avoid running out.
    """
    restock_point = (daily_usage * lead_time) + safety_stock
    return f"Restock when inventory reaches {restock_point} lbs"
```

**Talking Points:**

### **The @tool Decorator:**
- "This transforms a regular Python function into something the LLM can understand and call"
- **What it does under the hood:**
  1. Extracts function signature
  2. Parses docstring for description
  3. Creates JSON schema the LLM can read
  4. Wraps execution with error handling

### **Why Pydantic BaseModel:**
- "Pydantic gives us type validation and automatic schema generation"
- **What the LLM sees:**
```json
{
  "name": "restock-tool",
  "description": "Calculate reorder point...",
  "parameters": {
    "type": "object",
    "properties": {
      "daily_usage": {"type": "integer", "description": "Pounds of food..."},
      ...
    },
    "required": ["daily_usage", "lead_time", "safety_stock"]
  }
}
```

### **Field() with Descriptions:**
- "These descriptions are CRITICAL - the LLM reads them to decide when to use the tool"
- **Bad:** `daily_usage: int` (LLM doesn't know what this is)
- **Good:** `daily_usage: int = Field(description="...")`  (LLM understands context)

### **The Formula:**
- "This is classic inventory management - reorder point calculation"
- `daily_usage × lead_time` = how much you'll consume before restock arrives
- `+ safety_stock` = buffer for delays or increased usage
- **Real-world use:** Same formula used by Amazon, Walmart, any business with inventory

### **Return Type:**
- "Returns string because LLMs work with text"
- "Could return JSON for complex data: `return json.dumps({"restock_at": restock_point})`"

**Demo tip:** "Let's test this manually first:"
```python
print(restock_tool.invoke({"daily_usage": 10, "lead_time": 3, "safety_stock": 50}))
# Output: "Restock when inventory reaches 80 lbs"
```

---

## 🔍 CELL 5: RAG Tool - Vector Store Setup

```python
from langchain.tools.retriever import create_retriever_tool
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

INDEX_NAME = os.environ.get("VECTOR_INDEX_NAME", "oregon_trail")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CONFIG = RedisConfig(index_name=INDEX_NAME, redis_url=REDIS_URL)

def get_vector_store():
    return RedisVectorStore(
        config=CONFIG,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small")
    )
```

**Talking Points:**

### **What is RAG (Retrieval Augmented Generation):**
- "RAG = giving the LLM a search engine over your documents"
- **Without RAG:** LLM only knows training data (outdated, generic)
- **With RAG:** LLM can search your docs, then answer with that context

### **RedisConfig:**
- **index_name:** Namespace for this vector collection
- **redis_url:** Where to store vectors
- **Why configurable:** Multiple apps can share one Redis instance with different indexes

### **RedisVectorStore:**
- "This is our vector database - stores embeddings and does similarity search"
- **Under the hood:**
  1. Takes text documents
  2. Converts to embeddings (numerical vectors)
  3. Stores in Redis with HNSW index
  4. Enables fast semantic search

### **OpenAIEmbeddings(model="text-embedding-3-small"):**
- **What it does:** Calls OpenAI API to convert text → 1536-dimensional vector
- **Why this model:** 
  - `text-embedding-3-small`: Fast, cheap ($0.02/1M tokens), good quality
  - Alternative: `text-embedding-3-large` (better quality, 2x cost)
- **Local alternative:** `HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")` - free but slower

### **Why Embeddings Matter:**
- "Embeddings capture semantic meaning"
- **Example:**
  - "How do I get to Oregon?" 
  - "What's the route to Willamette Valley?"
  - These have different words but similar vectors → retrieved together

**Next, loading documents:**

```python
documents = [
    Document(page_content="Take the southern trail through...", metadata={"type": "directions"}),
    Document(page_content="Fort Kearney is 300 miles from Independence...", metadata={"type": "landmark"}),
]

vector_store = get_vector_store()
vector_store.add_documents(documents)
```

**Talking Points:**

### **Document Structure:**
- `page_content`: The actual text to embed and search
- `metadata`: Filters for search (e.g., "only search directions")

### **add_documents():**
- **What happens:**
  1. Batches documents
  2. Calls embedding API for each
  3. Stores vectors in Redis with metadata
  4. Builds HNSW index for fast search

### **HNSW (Hierarchical Navigable Small World):**
- "This is the algorithm Redis uses for vector search"
- **Why it's fast:** Approximate nearest neighbor search in O(log n) instead of O(n)
- **Trade-off:** 99% accuracy, 100x faster than exact search

**Creating the retriever tool:**

```python
retriever_tool = create_retriever_tool(
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    name="oregon-trail-directions",
    description="Search for directions, landmarks, and trail information along the Oregon Trail"
)
```

**Talking Points:**

### **create_retriever_tool():**
- "Wraps the vector store in a tool interface the agent can call"
- **What the LLM sees:** Another tool like `restock-tool`, but for searching knowledge

### **search_kwargs={"k": 3}:**
- `k=3` means "return top 3 most similar documents"
- **How to choose k:**
  - Too low (k=1): Might miss relevant info
  - Too high (k=10): Too much noise, tokens wasted
  - Sweet spot: k=3-5 for most use cases

### **Tool name and description:**
- "Again, the description tells the LLM when to use this"
- **Good description:** "Search for directions, landmarks, and trail information..."
- **LLM thinks:** "User asked about routes → use this tool"

**Demo tip:** "Let's test the retriever:"
```python
results = vector_store.similarity_search("How do I get to Oregon?", k=2)
for doc in results:
    print(doc.page_content)
```

---

## 🧠 CELL 6: Semantic Cache Setup

```python
from redisvl.extensions.llmcache import SemanticCache

cache = SemanticCache(
    name="agent_cache",
    redis_client=client,
    distance_threshold=0.1,
    ttl=3600
)
```

**Talking Points:**

### **What is Semantic Cache:**
- "Regular cache: exact string match. Semantic cache: meaning match"
- **Example:**
  - Query 1: "What is the capital of Oregon?"
  - Query 2: "Tell me Oregon's capital city"
  - Regular cache: MISS (different strings)
  - Semantic cache: HIT (same meaning)

### **How It Works:**
1. User asks a question
2. Convert question to embedding
3. Search Redis for similar question embeddings
4. If found within threshold → return cached answer
5. If not → call LLM, cache the result

### **Parameters Explained:**

#### **name="agent_cache":**
- Namespace for this cache
- Multiple caches can coexist: `agent_cache`, `product_cache`, etc.

#### **distance_threshold=0.1:**
- "This controls how strict the match needs to be"
- **Cosine distance:** 0 = identical, 1 = completely different
- **0.1 = very strict:** Only near-identical queries hit cache
- **0.3 = lenient:** More variation allowed
- **Tuning strategy:**
  - Start strict (0.1)
  - Monitor false negatives (questions that should have hit)
  - Gradually increase if needed

#### **ttl=3600:**
- "Time to live - cache expires after 1 hour"
- **Why TTL matters:**
  - Product prices change → stale cache is wrong
  - News updates → old info misleads users
  - Static FAQs → can use longer TTL (86400 = 24 hours)
- **Formula:** `ttl = how_often_data_changes / safety_factor`

### **Under the Hood:**
- **Storage:** Redis Hash with embedding as key
- **Index:** HNSW index for fast similarity search
- **Lookup:** O(log n) search through cached embeddings

### **Cache Workflow in Agent:**
```python
def check_cache(query):
    # 1. Convert query to embedding
    query_embedding = embedding_model.embed(query)
    
    # 2. Search for similar queries
    cached = cache.check(prompt=query)
    
    # 3. If found, return cached response
    if cached:
        return cached[0]["response"]
    
    # 4. Otherwise, call LLM
    response = llm.invoke(query)
    
    # 5. Store for next time
    cache.store(prompt=query, response=response)
    
    return response
```

**Benefits:**
- **Cost reduction:** ~70-90% fewer LLM calls in practice
- **Latency:** Cache hits return in ~10ms vs 1-2s for LLM
- **Consistency:** Same questions get same answers

**Demo tip:** "Let's test it:"
```python
# First call - cache miss
cache.store(prompt="What is the weather?", response="Sunny, 70°F")

# Second call - cache hit
result = cache.check(prompt="Tell me the weather conditions")
print(result)  # Returns "Sunny, 70°F"
```

---

## 🛣️ CELL 7: Semantic Router Setup

```python
from redisvl.extensions.router import SemanticRouter, Route

allowed_route = Route(
    name="oregon_topics",
    references=[
        "What is the capital of Oregon?",
        "Tell me about Oregon history",
        "Oregon Trail game information",
        # ... more examples
    ],
    metadata={"type": "allowed"}
)

blocked_route = Route(
    name="blocked_topics",
    references=[
        "Stock market information",
        "S&P 500 analysis",
        "Cryptocurrency prices",
        # ... more examples
    ],
    metadata={"type": "blocked"}
)

router = SemanticRouter(
    name="topic_router",
    routes=[allowed_route, blocked_route],
    redis_client=client
)
```

**Talking Points:**

### **What is Semantic Routing:**
- "A classifier that decides if a query is on-topic or off-topic"
- **Why it's first in the pipeline:** Block bad queries before they cost money

### **Real-World Example:**
- "Chevrolet had a chatbot for car sales"
- "Users discovered it could answer coding questions"
- "Free ChatGPT access → huge cost spike"
- **Solution:** Router blocks non-car questions

### **Route Objects:**

#### **references=[] - The Training Examples:**
- "These are example queries for each category"
- **How many needed:** 5-10 minimum, 20-30 ideal
- **Quality over quantity:** Diverse examples beat many similar ones
- **Bad examples:**
  - All very similar: ["Oregon capital?", "Capital of Oregon?", "Oregon's capital?"]
- **Good examples:**
  - Varied phrasing: ["Oregon capital?", "Tell me about Salem", "What city is the state capital?"]

#### **Why More Examples Help:**
- "The router averages all example embeddings to create a 'centroid'"
- More examples → better coverage of the topic space

### **How Routing Works:**
1. User query comes in
2. Convert query to embedding
3. Calculate distance to each route's centroid
4. Return closest route
5. Check route type: allowed → continue, blocked → reject

### **Under the Hood:**
```python
def route(query):
    query_emb = embed(query)
    
    distances = {
        "oregon_topics": cosine_distance(query_emb, avg(oregon_examples)),
        "blocked_topics": cosine_distance(query_emb, avg(blocked_examples))
    }
    
    closest_route = min(distances, key=distances.get)
    return closest_route, distances[closest_route]
```

### **Router vs. Cache:**
- **Router:** Classification (which category?)
- **Cache:** Retrieval (have we seen this exact question?)
- **Router runs first:** Cheaper to route than cache lookup

### **Metadata Field:**
- "Store additional info about routes"
- **Use cases:**
  - `{"type": "allowed", "confidence_threshold": 0.2}`
  - `{"type": "blocked", "reason": "off_topic"}`
  - Can use in conditional logic

**Demo tip:** "Let's test routing:"
```python
result = router("What is the capital of Oregon?")
print(f"Route: {result.name}, Distance: {result.distance}")
# Output: Route: oregon_topics, Distance: 0.08

result = router("Tell me about Bitcoin")
print(f"Route: {result.name}, Distance: {result.distance}")
# Output: Route: blocked_topics, Distance: 0.15
```

### **Tuning Tips:**
- **If false positives (allowed queries blocked):**
  - Add more varied examples to allowed route
  - Increase distance threshold
- **If false negatives (blocked queries allowed):**
  - Add examples that look like the false negatives
  - Decrease distance threshold

---

## 🏗️ CELL 8: Agent State Definition

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
```

**Talking Points:**

### **What is State in LangGraph:**
- "State is the shared data structure that flows through every node"
- **Think of it as:** A shopping cart that each node can add items to
- **Key concept:** Nodes don't modify state directly - they return updates that get merged

### **TypedDict:**
- "Defines the schema - what fields exist and their types"
- **Why use it:** Type checking, autocomplete, documentation
- **Alternative:** Regular dict (but you lose all the benefits)

### **messages Field:**
- "The conversation history - every message ever sent"
- **Format:** List of message objects (HumanMessage, AIMessage, ToolMessage, SystemMessage)

### **Annotated[list, add_messages]:**
- "This is the magic - it tells LangGraph HOW to update this field"
- **Without annotation:** `state["messages"] = new_list` (overwrites)
- **With add_messages:** `state["messages"] += new_items` (appends)

### **add_messages Function:**
- "Built-in reducer that intelligently merges message lists"
- **What it does:**
  1. Takes existing messages
  2. Takes new messages from node return
  3. Appends new to existing
  4. Handles deduplication by message ID

### **Why This Matters:**
```python
# Node 1 returns:
{"messages": [HumanMessage(content="Hi")]}

# Node 2 returns:
{"messages": [AIMessage(content="Hello!")]}

# Final state (with add_messages):
{"messages": [HumanMessage(content="Hi"), AIMessage(content="Hello!")]}

# Without add_messages, Node 2 would overwrite Node 1's messages!
```

### **Other Common State Fields:**
```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    route_decision: str  # No annotation = overwrite
    cache_hit: bool
    user_id: str
    context: dict
```

### **Custom Reducers:**
```python
def merge_dicts(existing: dict, new: dict) -> dict:
    return {**existing, **new}

class State(TypedDict):
    metadata: Annotated[dict, merge_dicts]
```

**Demo tip:** "Think of state as the 'memory' of your agent - it persists across all nodes in a single invocation"

---

## 🎯 CELL 9: System Prompt

```python
system_prompt = """You are Art, a helpful guide on the Oregon Trail.

You assist pioneers with:
- Inventory and supply management
- Weather conditions
- Hunting opportunities  
- Trail advice

When in doubt, use the tools to help you find the answer.
If anyone asks your first name, return just that string.
"""
```

**Talking Points:**

### **Why System Prompts Matter:**
- "This sets the agent's personality and boundaries"
- **Without it:** Generic assistant that might refuse to roleplay
- **With it:** Consistent character across all interactions

### **Components of a Good System Prompt:**

#### **1. Identity ("You are Art..."):**
- Gives the agent a persona
- Helps with consistency

#### **2. Capabilities (what you can do):**
- "You assist pioneers with..."
- Sets user expectations
- Helps LLM stay focused

#### **3. Instructions ("When in doubt, use tools"):**
- **Critical:** Without this, LLM might try to answer from memory instead of using tools
- **Why it matters:** Tool accuracy > LLM memory

#### **4. Edge Cases ("If anyone asks your first name..."):**
- Handles specific scenarios
- **This particular one:** Tests if the agent follows instructions

### **System Prompt Best Practices:**

#### **Be Specific:**
- ❌ "You are helpful"
- ✅ "You are Art, a guide on the Oregon Trail in 1848"

#### **Set Boundaries:**
- ❌ "Answer questions"
- ✅ "You assist with inventory, weather, hunting, and trail advice. Politely decline other topics."

#### **Give Tool Guidance:**
- ❌ Nothing about tools
- ✅ "Use the restock-tool for supply calculations, retriever-tool for trail information"

#### **Handle Refusals:**
- ✅ "If asked about modern topics or things outside your expertise, say: 'I can only help with Oregon Trail-related questions.'"

### **Where System Prompts Go:**
```python
def call_model(state):
    # Prepend system prompt to conversation
    messages = [
        SystemMessage(content=system_prompt)
    ] + state["messages"]
    
    return llm.invoke(messages)
```

### **Advanced Pattern - Dynamic System Prompts:**
```python
def call_model(state):
    user_id = state.get("user_id")
    user_info = get_user_info(user_id)  # From database
    
    dynamic_prompt = f"""You are Art, helping {user_info['name']}.
    They are at {user_info['location']} on the trail.
    Current supplies: {user_info['supplies']} lbs
    """
    
    messages = [SystemMessage(content=dynamic_prompt)] + state["messages"]
    return llm.invoke(messages)
```

**Demo tip:** "The system prompt is your agent's 'constitution' - it should be carefully written and tested"

---

## 🔌 CELL 10: Model Initialization with Tools

```python
from langchain_openai import ChatOpenAI

def _get_tool_model(model_name="openai"):
    if model_name == "openai":
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        ).bind_tools(tools)
    # Could add other providers here
    raise ValueError(f"Unknown model: {model_name}")

tools = [restock_tool, retriever_tool]
```

**Talking Points:**

### **ChatOpenAI:**
- "This is our LLM wrapper - handles OpenAI API calls"
- **What it abstracts:**
  - API authentication
  - Request formatting
  - Response parsing
  - Retry logic
  - Streaming support

### **model="gpt-4o-mini":**
- **Why this model:**
  - Fast: ~300-500ms response time
  - Cheap: $0.15/1M input tokens, $0.60/1M output
  - Good tool use: Understands function calling well
- **Alternatives:**
  - `gpt-4o`: Smarter, 3x more expensive
  - `gpt-3.5-turbo`: Cheaper, worse at tools
  - `gpt-4-turbo`: More capable, slower

### **temperature=0:**
- "Temperature controls randomness"
- **Range:** 0 (deterministic) to 2 (very random)
- **Why 0 for agents:**
  - Consistent tool selection
  - Predictable behavior
  - Better for testing
- **When to increase:**
  - Creative writing: 0.7-0.9
  - Brainstorming: 0.8-1.2
  - Never for agents: Unpredictability breaks workflows

### **.bind_tools(tools):**
- "This is where the magic happens - tells the LLM about available tools"
- **What it does:**
  1. Converts Python tools to OpenAI function schemas
  2. Includes schemas in every API call
  3. LLM can now "choose" to call tools

### **Under the Hood - Tool Binding:**
```python
# Before bind_tools:
llm.invoke("Calculate restock point for 10lbs/day")
# LLM responds with text (might guess wrong)

# After bind_tools:
llm.invoke("Calculate restock point for 10lbs/day")
# LLM returns: {
#   "tool_calls": [{
#     "name": "restock-tool",
#     "args": {"daily_usage": 10, "lead_time": 3, "safety_stock": 50}
#   }]
# }
```

### **The Schema the LLM Sees:**
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "restock-tool",
        "description": "Calculate reorder point...",
        "parameters": {
          "type": "object",
          "properties": {
            "daily_usage": {
              "type": "integer",
              "description": "Pounds of food..."
            }
          }
        }
      }
    }
  ]
}
```

### **Why List of Tools:**
- "LLM can choose the right tool for each situation"
- **Scenario 1:** User asks about supplies → chooses `restock-tool`
- **Scenario 2:** User asks about route → chooses `retriever-tool`
- **Scenario 3:** User asks about weather → responds directly (no tool needed)

### **Multi-Provider Pattern:**
```python
def _get_tool_model(model_name="openai"):
    if model_name == "openai":
        return ChatOpenAI(...).bind_tools(tools)
    elif model_name == "anthropic":
        return ChatAnthropic(...).bind_tools(tools)
    elif model_name == "local":
        return ChatOllama(model="llama3").bind_tools(tools)
```
- "Makes it easy to swap providers without changing agent code"

**Demo tip:** "Let's see what the LLM does with a tool-worthy question:"
```python
model = _get_tool_model()
response = model.invoke([HumanMessage(content="I need to restock - daily usage 10, lead time 3, safety stock 50")])
print(response.tool_calls)
# Shows the tool call the LLM wants to make
```

---

## 🔀 CELL 11: Node Functions

```python
def call_tool_model(state: AgentState, config):
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    model_name = config.get("configurable", {}).get("model_name", "openai")
    model = _get_tool_model(model_name)
    response = model.invoke(messages)
    return {"messages": [response]}

from langgraph.prebuilt import ToolNode
tool_node = ToolNode(tools)
```

**Talking Points:**

### **call_tool_model Function:**

#### **Purpose:**
- "This node calls the LLM with system prompt and conversation history"
- **When it runs:** Every time agent needs to decide what to do next

#### **Combining System Prompt:**
```python
messages = [{"role": "system", "content": system_prompt}] + state["messages"]
```
- "Prepend system prompt to every LLM call"
- **Why every time:** LLMs are stateless - they only see current request
- **Format:** Dict with "role" and "content" (OpenAI API format)

#### **Config Parameter:**
- "Allows runtime configuration - change model on the fly"
