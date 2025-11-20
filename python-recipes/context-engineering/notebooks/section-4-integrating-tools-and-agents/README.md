# Section 4: Integrating Tools and Agents

**⏱️ Estimated Time:** 3.5-4.5 hours total

## 🎯 Overview

This section teaches you how to build intelligent agents that combine RAG, memory, and tools to create adaptive, multi-step workflows. You'll progress from understanding tool fundamentals to building a complete course advisor agent, and then learn how to scale it with semantic tool selection.

## 📚 Notebooks

### 1. Memory Tools and LangGraph Fundamentals (45-60 minutes)
**File:** `01_tools_and_langgraph_fundamentals.ipynb`

**What You'll Learn:**
- How memory tools enable active context engineering
- Building the 3 essential memory tools: store, search, retrieve
- LangGraph fundamentals (nodes, edges, state)
- Passive vs active memory management
- When to use memory tools vs automatic memory

**Key Concepts:**
- Memory tools for context engineering
- Active vs passive memory management
- LangGraph state management
- Tool-driven context construction

### 2. Building a Course Advisor Agent (60-75 minutes)
**File:** `02_building_course_advisor_agent.ipynb`

**What You'll Build:**
A complete course advisor agent with:
- **3 Tools (Memory-Focused):**
  1. `store_memory` - Save important information to long-term memory
  2. `search_memories` - Recall user preferences and facts
  3. `search_courses` - Semantic search over course catalog

- **Active Memory Management:**
  - LLM decides what to remember
  - LLM searches memories strategically
  - Dynamic context construction

- **LangGraph Workflow:**
  - Load memory → Agent decision → Tools → Save memory
  - Conditional routing based on LLM decisions
  - Graph visualization

**Key Concepts:**
- Building agents with LangGraph
- Memory-driven tool design
- Active context engineering
- Multi-step reasoning with memory
- Personalized recommendations using stored preferences

### 3. Agent with Memory Compression (90-120 minutes)
**File:** `03_agent_with_memory_compression.ipynb`

**What You'll Learn:**
- Memory compression strategies for long conversations
- Truncation and sliding window techniques
- Production memory patterns
- Managing token budgets

**Key Concepts:**
- Working memory compression
- Conversation history management
- Token optimization
- Production memory patterns

### 4. Semantic Tool Selection (60-75 minutes)
**File:** `04_semantic_tool_selection.ipynb`

**What You'll Build:**
An enhanced agent that scales from 3 to 5 tools using semantic selection:
- **2 New Tools:**
  1. `check_prerequisites` - Course prerequisite checking
  2. `compare_courses` - Side-by-side course comparison

- **Tool Selection Strategies:**
  - Static/hardcoded selection
  - Pre-filtered/rule-based selection
  - Semantic/dynamic selection with RedisVL

- **Production Patterns:**
  - RedisVL Semantic Router for intelligent tool routing
  - 60% token reduction through selective tool loading
  - Scalability to 100+ tools

**Key Concepts:**
- Tool token cost and scaling challenges
- Tool selection strategy comparison
- Semantic tool routing with embeddings
- Production-ready routing patterns
- Trade-offs and best practices

## 🔗 Connection to Previous Sections

### Section 1: Context Types
- System, User, Conversation, Retrieved context
- Foundation for understanding how agents use context

### Section 2: RAG Foundations
- Semantic search with vector embeddings
- Course catalog retrieval
- Single-step retrieval → generation

### Section 3: Memory Systems for Context Engineering
- Working memory for conversation continuity
- Long-term memory for persistent knowledge
- Memory-enhanced RAG systems

### Section 4: Integrating Tools and Agents (This Section)
- **Combines everything:** RAG + Memory + Tools + Decision-Making
- Agents can decide when to search, store, and recall
- Multi-step reasoning and adaptive workflows

## 📊 Progression: RAG → Memory-RAG → Agent

| Feature | RAG (S2) | Memory-RAG (S3) | Agent (S4) |
|---------|----------|-----------------|------------|
| **Retrieval** | ✅ | ✅ | ✅ |
| **Conversation Memory** | ❌ | ✅ | ✅ |
| **Long-term Memory** | ❌ | ⚠️ (manual) | ✅ (automatic) |
| **Decision Making** | ❌ | ❌ | ✅ |
| **Multi-step Reasoning** | ❌ | ❌ | ✅ |
| **Tool Selection** | ❌ | ❌ | ✅ |

## ⚠️ Prerequisites

**CRITICAL: This section requires ALL services to be running.**

### Required Services:
1. **Redis** - Vector storage and caching (port 6379)
2. **Agent Memory Server** - Memory management (port 8088)
3. **OpenAI API** - LLM functionality

### 🚀 Quick Setup:

**Option 1: Automated Setup (Recommended)**
```bash
# Navigate to notebooks_v2 directory
cd ../

# Run setup script
./setup_memory_server.sh
```

**Option 2: Manual Setup**
See `../SETUP_GUIDE.md` for detailed instructions.

### Additional Requirements:
1. **Completed Sections 1-3** - This section builds on previous concepts
2. **Docker Desktop running** - Required for containerized services
3. **Course data** - Will be generated automatically by notebooks

## 🚀 Getting Started

1. **Start with Notebook 1** to learn tool fundamentals
2. **Then Notebook 2** to build the complete agent
3. **Continue with Notebook 3** to learn memory compression
4. **Finish with Notebook 4** to scale with semantic tool selection
5. **Experiment** with different queries and watch the agent work
6. **Extend** the agent with additional tools (see suggestions in notebooks)

## 🎓 Learning Outcomes

By the end of this section, you will be able to:

- ✅ Design and implement tools for LLM agents
- ✅ Build LangGraph workflows with conditional routing
- ✅ Integrate memory systems with agents
- ✅ Create agents that make multi-step decisions
- ✅ Compress conversation history for long interactions
- ✅ Implement semantic tool selection for scalability
- ✅ Scale agents to 100+ tools without token explosion
- ✅ Choose between RAG, Memory-RAG, and Agent architectures
- ✅ Make informed decisions about tool selection strategies
- ✅ Understand trade-offs (complexity, latency, cost, capabilities)

## 📁 Archive

The `_archive/` directory contains previous versions of Section 4 notebooks:
- `01_defining_tools.ipynb` - Original tool definition content
- `02_tool_selection_strategies.ipynb` - Tool selection patterns
- `03_building_multi_tool_intelligence.ipynb` - Multi-tool agent examples

These were consolidated and improved in the current notebooks.

## 🔗 Additional Resources

### Core Technologies
- [Redis Agent Memory Server](https://github.com/redis/agent-memory-server) - Dual-memory architecture for agents
- [RedisVL](https://github.com/redis/redis-vl) - Redis Vector Library for semantic search
- [Redis Vector Search](https://redis.io/docs/stack/search/reference/vectors/) - Vector similarity search documentation

### LangChain & LangGraph
- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/agents/tools/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)

### OpenAI
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

## 💡 Next Steps

After completing this section:

1. **Explore the reference-agent** - See a production implementation with 7 tools
2. **Build your own agent** - Apply these concepts to your use case
3. **Experiment with tools** - Try different tool combinations
4. **Optimize performance** - Explore caching, parallel execution, etc.

---

**Ready to build intelligent agents? Start with Notebook 1! 🚀**

