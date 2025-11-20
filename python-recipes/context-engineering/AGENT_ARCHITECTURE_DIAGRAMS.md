# Agent Architecture Diagrams - Context Engineering Course

**Complete architectural documentation for all fully functional agents in the Context Engineering course.**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Course Advisor Agent v1](#course-advisor-agent-v1)
3. [Course Advisor Agent v2](#course-advisor-agent-v2)
4. [Course Advisor Agent v3](#course-advisor-agent-v3)
5. [ClassAgent (Reference)](#classagent-reference-implementation)
6. [AugmentedClassAgent](#augmentedclassagent-extended-reference)
7. [Evolution Summary](#evolution-summary)
8. [Key Differences](#key-differences-between-versions)

---

## Overview

This document provides detailed architecture diagrams and specifications for all fully functional agents developed throughout the Context Engineering course. The course follows a **progressive enhancement approach** where a single agent (Redis University Course Advisor) evolves across multiple notebooks, with each version adding new capabilities.

### Agent Versions

| Version | Notebook | Tools | Key Features | Status |
|---------|----------|-------|--------------|--------|
| **v1** | 02_building_course_advisor_agent.ipynb | 3 | Base agent with dual-memory | ✅ Complete |
| **v2** | 03_agent_with_memory_compression.ipynb | 3 | + Memory compression | ✅ Complete |
| **v3** | 04_semantic_tool_selection.ipynb | 5 | + Semantic routing | ✅ Complete |
| **ClassAgent** | reference-agent/agent.py | 2 | Production reference | ✅ Complete |
| **AugmentedClassAgent** | reference-agent/augmented_agent.py | 4 | Extension pattern | ✅ Complete |

---

## Course Advisor Agent v1

**Location**: `notebooks/section-4-integrating-tools-and-agents/02_building_course_advisor_agent.ipynb`

**Purpose**: First complete production agent demonstrating LangGraph orchestration, dual-memory architecture, and tool calling.

### Architecture Diagram

See rendered Mermaid diagram: **Course Advisor Agent v1 - Architecture**

### Component Breakdown

#### 1. **LangGraph Orchestration Layer**

**Workflow**: `START → Load Memory → Agent → [Tools → Agent]* → Save Memory → END`

**Nodes** (4 total):
- `load_memory` - Load working memory from Agent Memory Server
- `agent` - LLM reasoning with tool calling (OpenAI GPT-4)
- `tools` - Execute selected tool
- `save_memory` - Save to working memory, auto-extract to long-term

**Decision Logic**:
- If agent response contains tool calls → route to `tools` node
- If no tool calls → route to `save_memory` node
- Tools always loop back to `agent` for final response

#### 2. **Tool Inventory** (3 Tools)

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| **search_courses** | Semantic course search using vector embeddings | query: str, limit: int | Course list with descriptions |
| **search_memories** | Search long-term memory for user facts | query: str, limit: int | Relevant memories |
| **store_memory** | Save important information to long-term memory | text: str, type: str, topics: List[str] | Confirmation |

#### 3. **Memory Architecture** (Dual-Memory System)

**Working Memory** (Session-scoped):
- Conversation history for current session
- Loaded at start of each turn
- Saved at end of each turn
- Enables conversation continuity and grounding

**Long-term Memory** (Cross-session):
- Persistent facts about the student
- Preferences, goals, completed courses
- Searchable via semantic vector search
- Accessible via `search_memories` tool

**Graph State** (Turn-scoped):
- `messages`: List[BaseMessage] - Conversation messages
- `student_id`: str - Student identifier
- `session_id`: str - Session identifier
- `context`: Dict - Retrieved context from long-term memory

**Memory Extraction**:
- Strategy: **Discrete** (default)
- Automatically extracts individual facts from conversations
- Stores in long-term memory for future retrieval

#### 4. **Data Flow**

```
User Query
    ↓
Load Working Memory (conversation history)
    ↓
Agent Node (LLM reasoning with 3 tools)
    ↓
Tool Call? → Yes → Execute Tool → Back to Agent
           → No  → Save Memory → Response
```

#### 5. **Storage Backends**

- **Redis** (Port 6379): Vector search for courses, memory storage
- **Agent Memory Server** (Port 8088): Memory management, extraction engine

#### 6. **External Integrations**

- **OpenAI API**: GPT-4 for LLM, embeddings for vector search
- **CourseManager**: Course search, vector embeddings, course data

### Context Engineering Techniques

- ✅ System context (role, instructions)
- ✅ User context (student profile)
- ✅ Conversation context (working memory)
- ✅ Retrieved context (RAG via search_courses)
- ✅ Memory-based context (long-term memory)

### Key Learning Objectives

1. Build stateful agents with LangGraph StateGraph
2. Implement dual-memory architecture (working + long-term)
3. Create and integrate multiple tools
4. Design conversation flow control
5. Integrate Agent Memory Server with LangGraph

---

## Course Advisor Agent v2

**Location**: `notebooks/section-4-integrating-tools-and-agents/03_agent_with_memory_compression.ipynb`

**Purpose**: Enhanced version of v1 that adds working memory compression for long conversations.

### Architecture Diagram

See rendered Mermaid diagram: **Course Advisor Agent v2 - Architecture with Memory Compression**

### What's New in v2

#### 🆕 Memory Compression Layer

**Problem**: Unbounded conversation growth leads to:
- Token limits exceeded (128K for GPT-4o)
- High API costs (quadratic growth)
- Increased latency
- Context rot (LLMs struggle with very long contexts)

**Solution**: Three compression strategies

### Compression Strategies

#### 1. **Truncation** (Fast, Simple)

**How it works**: Keep only the most recent N messages within token budget

**Pros**:
- ✅ Fast (no LLM calls)
- ✅ Predictable token usage
- ✅ Simple implementation

**Cons**:
- ❌ Loses all old context
- ❌ No intelligence in selection

**Use when**:
- Speed is critical (real-time chat)
- Recent context is all that matters
- Cost-sensitive (no LLM calls)

#### 2. **Priority-Based** (Balanced)

**How it works**: Score messages by importance, keep highest-scoring ones

**Scoring factors**:
- System messages (high priority)
- Tool calls and results (high priority)
- User questions (medium priority)
- Recency (recent messages scored higher)
- Keywords (domain-specific importance)

**Pros**:
- ✅ Preserves important context
- ✅ No LLM calls (fast)
- ✅ Balanced approach

**Cons**:
- ❌ Requires good scoring logic
- ❌ May lose temporal flow

**Use when**:
- Need balance between speed and quality
- Important context scattered throughout conversation
- No LLM calls allowed (cost/latency constraints)

#### 3. **Summarization** (High Quality)

**How it works**: LLM creates intelligent summaries of old messages, keep recent ones

**Process**:
1. Split conversation into old (to summarize) and recent (to keep)
2. Format old messages for summarization
3. LLM generates comprehensive summary
4. Return summary + recent messages

**Pros**:
- ✅ Preserves meaning
- ✅ High quality compression
- ✅ Intelligent context preservation

**Cons**:
- ❌ Slower (requires LLM call)
- ❌ Costs tokens
- ❌ Additional latency

**Use when**:
- Quality is critical
- Long conversations (30+ turns)
- Can afford LLM call latency
- Comprehensive context needed

### Enhanced Components

**Graph State** (v2 additions):
- `compression_stats`: Dict - Compression metrics and statistics

**Agent Memory Server** (v2 configuration):
- `WINDOW_SIZE` environment variable for auto-compression
- Automatic compression when threshold exceeded
- Background processing (async workers)

### Compression Comparison

| Strategy | Messages | Tokens | Savings | Quality | Speed |
|----------|----------|--------|---------|---------|-------|
| Original | 60 | 1,500 | 0% | N/A | N/A |
| Truncation | 20 | 1,000 | 33% | Low | Fast |
| Priority-Based | 22 | 980 | 35% | Medium | Fast |
| Summarization | 5 | 850 | 43% | High | Slow |

### Key Learning Objectives

1. Implement working memory compression strategies
2. Understand token cost management
3. Apply compression in production agents
4. Balance context preservation vs token efficiency

---

## Course Advisor Agent v3

**Location**: `notebooks/section-4-integrating-tools-and-agents/04_semantic_tool_selection.ipynb`

**Purpose**: Scales agent from 3 to 5 tools using semantic tool selection to reduce token costs.

### Architecture Diagram

See rendered Mermaid diagram: **Course Advisor Agent v3 - Architecture with Semantic Tool Selection**

### What's New in v3

#### 🆕 Expanded Tool Set (5 Tools)

**New Tools** (2 added):

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| **check_prerequisites** | Check course requirements | course_id: str | Prerequisites list, eligibility status |
| **compare_courses** | Compare courses side-by-side | course_ids: List[str] | Comparison table |

**All Tools** (5 total):
1. search_courses (from v1)
2. search_memories (from v1)
3. store_memory (from v1)
4. check_prerequisites (NEW)
5. compare_courses (NEW)

#### 🆕 Semantic Tool Selection Layer

**Problem**: Token cost scales linearly with number of tools
- 3 tools = ~1,200 tokens
- 5 tools = ~2,200 tokens (83% increase)
- 10 tools = ~4,000 tokens
- Sending all tools every time is wasteful

**Solution**: RedisVL Semantic Router for intelligent tool selection

### Semantic Router Architecture

**How it works**:
1. Define **Routes** for each tool with reference examples
2. Router automatically creates Redis vector index
3. Generates embeddings for all route references
4. For each query, embed query and find top-k most similar routes
5. Send only selected tools to LLM

**Route Structure**:
```python
Route(
    name="check_prerequisites",
    references=[
        "Check course prerequisites",
        "Verify readiness for a course",
        "Understand course requirements",
        ...
    ],
    metadata={"category": "course_planning"},
    distance_threshold=0.3
)
```

**Selection Process**:
```
User Query: "What are the prerequisites for RU202?"
    ↓
Embed Query → [0.23, -0.45, 0.67, ...]
    ↓
Compare to Route Embeddings:
    check_prerequisites:    similarity = 0.92 ✅
    search_courses:         similarity = 0.45
    compare_courses:        similarity = 0.38
    search_memories:        similarity = 0.12
    store_memory:           similarity = 0.08
    ↓
Select Top-k (k=3):
    → check_prerequisites
    → search_courses
    → compare_courses
    ↓
Send only these 3 tools to LLM (instead of all 5)
```

### Tool Selection Strategies Comparison

| Strategy | Description | Pros | Cons | Use When |
|----------|-------------|------|------|----------|
| **Static** | Send all tools | Simple | Wasteful tokens | ≤3 tools |
| **Pre-filtered** | Keyword matching | Fast | Brittle, manual rules | 4-7 tools |
| **Semantic** | Embedding similarity | Robust, scalable | Requires embeddings | 8+ tools |

### Token Cost Optimization

**Without Semantic Selection**:
- 5 tools sent every time = 2,200 tokens per query
- 100 queries = 220,000 tokens
- Cost: ~$0.55 (at $0.0025/1K tokens)

**With Semantic Selection** (top-3):
- 3 tools sent per query = ~1,000 tokens per query
- 100 queries = 100,000 tokens
- Cost: ~$0.25 (at $0.0025/1K tokens)
- **Savings: 55% reduction in token costs**

### Enhanced Components

**Graph State** (v3 additions):
- `selected_tools`: List - Tools selected by semantic router
- `tool_selection_method`: str - Selection strategy used

**Redis** (v3 additions):
- Tool route index for semantic routing
- Route embeddings stored in Redis

**OpenAI** (v3 usage):
- Route embeddings generation
- Query embeddings for routing

### Key Learning Objectives

1. Implement semantic tool selection at scale
2. Use RedisVL Semantic Router for production routing
3. Understand token cost scaling with tools
4. Design scalable tool architectures

---


