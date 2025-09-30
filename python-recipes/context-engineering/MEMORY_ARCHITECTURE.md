# Memory Architecture

## Overview

The context engineering reference agent uses a sophisticated memory architecture that combines two complementary systems:

1. **LangGraph Checkpointer** (Redis) - Low-level graph state persistence
2. **Redis Agent Memory Server** - High-level memory management (working + long-term)

This document explains how these systems work together and why both are needed.

## The Two Systems

### 1. LangGraph Checkpointer (Redis)

**Purpose**: Low-level graph state persistence for resuming execution at specific nodes.

**What it does**:
- Saves the entire graph state at each super-step
- Enables resuming execution from any point in the graph
- Supports time-travel debugging and replay
- Handles fault-tolerance and error recovery

**What it stores**:
- Graph node states
- Execution position (which node to execute next)
- Intermediate computation results
- Tool call results

**Key characteristics**:
- Thread-scoped (one checkpoint per thread)
- Automatic (managed by LangGraph)
- Low-level (graph execution details)
- Not designed for semantic search or memory extraction

**When it's used**:
- Automatically at each super-step during graph execution
- When resuming a conversation (loads last checkpoint)
- When implementing human-in-the-loop workflows
- For debugging and replay

### 2. Redis Agent Memory Server

**Purpose**: High-level memory management with automatic extraction and semantic search.

**What it does**:
- Manages working memory (session-scoped conversation context)
- Manages long-term memory (cross-session knowledge)
- Automatically extracts important facts from conversations
- Provides semantic vector search
- Handles deduplication and compaction

**What it stores**:

#### Working Memory (Session-Scoped)
- Conversation messages
- Structured memories awaiting promotion
- Session-specific data
- TTL-based (default: 1 hour)

#### Long-term Memory (Cross-Session)
- User preferences
- Goals and objectives
- Important facts learned over time
- Semantic, episodic, and message memories

**Key characteristics**:
- Session-scoped (working) and user-scoped (long-term)
- Explicit (you control when to load/save)
- High-level (conversation and knowledge)
- Designed for semantic search and memory extraction

**When it's used**:
- Explicitly loaded at the start of each conversation turn
- Explicitly saved at the end of each conversation turn
- Searched via tools when relevant context is needed
- Automatically extracts memories in the background

## How They Work Together

### Graph Execution Flow

```
1. Load Working Memory (Agent Memory Server)
   ↓
2. Retrieve Context (Search long-term memories)
   ↓
3. Agent Reasoning (LLM with tools)
   ↓
4. Tool Execution (if needed)
   ↓
5. Generate Response
   ↓
6. Save Working Memory (Agent Memory Server)
```

At each step, the **LangGraph Checkpointer** automatically saves the graph state.

### Example: Multi-Turn Conversation

**Turn 1:**
```python
# User: "I'm interested in machine learning courses"

# 1. LangGraph loads checkpoint (empty for first turn)
# 2. Agent Memory Server loads working memory (empty for first turn)
# 3. Agent processes message
# 4. Agent Memory Server saves working memory with conversation
# 5. LangGraph saves checkpoint with graph state
```

**Turn 2:**
```python
# User: "What are the prerequisites?"

# 1. LangGraph loads checkpoint (has previous graph state)
# 2. Agent Memory Server loads working memory (has previous conversation)
# 3. Agent has full context from working memory
# 4. Agent processes message with context
# 5. Agent Memory Server saves updated working memory
#    - Automatically extracts "interested in ML" to long-term memory
# 6. LangGraph saves checkpoint with updated graph state
```

**Turn 3 (New Session, Same User):**
```python
# User: "Remind me what I was interested in?"

# 1. LangGraph loads checkpoint (new thread, empty)
# 2. Agent Memory Server loads working memory (new session, empty)
# 3. Agent searches long-term memories (finds "interested in ML")
# 4. Agent responds with context from long-term memory
# 5. Agent Memory Server saves working memory
# 6. LangGraph saves checkpoint
```

## Key Differences

| Feature | LangGraph Checkpointer | Agent Memory Server |
|---------|------------------------|---------------------|
| **Purpose** | Graph execution state | Conversation memory |
| **Scope** | Thread-scoped | Session + User-scoped |
| **Granularity** | Low-level (nodes) | High-level (messages) |
| **Management** | Automatic | Explicit (load/save) |
| **Search** | No | Yes (semantic) |
| **Extraction** | No | Yes (automatic) |
| **Cross-session** | No | Yes (long-term) |
| **Use case** | Resume execution | Remember context |

## Why Both Are Needed

### LangGraph Checkpointer Alone Is Not Enough

The checkpointer is designed for graph execution, not memory management:
- ❌ No semantic search
- ❌ No automatic memory extraction
- ❌ No cross-session memory
- ❌ No deduplication
- ❌ Thread-scoped only

### Agent Memory Server Alone Is Not Enough

The memory server doesn't handle graph execution state:
- ❌ Can't resume at specific graph nodes
- ❌ Can't replay graph execution
- ❌ Can't handle human-in-the-loop at node level
- ❌ Doesn't store tool call results

### Together They Provide Complete Memory

✅ **LangGraph Checkpointer**: Handles graph execution state
✅ **Agent Memory Server**: Handles conversation and knowledge memory
✅ **Combined**: Complete memory architecture for AI agents

## Implementation in the Reference Agent

### Node: `load_working_memory`

```python
async def _load_working_memory(self, state: AgentState) -> AgentState:
    """
    Load working memory from Agent Memory Server.
    
    This is the first node in the graph, loading context for the current turn.
    """
    working_memory = await self.memory_client.get_working_memory(
        session_id=self.session_id,
        model_name="gpt-4o"
    )
    
    # Add previous messages to state
    if working_memory and working_memory.messages:
        for msg in working_memory.messages:
            # Convert to LangChain messages
            ...
    
    return state
```

### Node: `save_working_memory`

```python
async def _save_working_memory(self, state: AgentState) -> AgentState:
    """
    Save working memory to Agent Memory Server.
    
    This is the final node in the graph. The Agent Memory Server automatically:
    1. Stores the conversation messages
    2. Extracts important facts to long-term storage
    3. Manages memory deduplication and compaction
    """
    messages = [...]  # Convert from LangChain messages
    
    await self.memory_client.save_working_memory(
        session_id=self.session_id,
        messages=messages
    )
    
    return state
```

## Best Practices

### For Learners

1. **Understand the distinction**: Checkpointer = graph state, Memory Server = conversation memory
2. **Focus on Memory Server**: This is where the interesting memory concepts are
3. **Mention checkpointer in passing**: It's important but not the focus of memory lessons
4. **Use explicit load/save nodes**: Makes memory management visible and teachable

### For Developers

1. **Always use both systems**: They complement each other
2. **Load working memory first**: Get conversation context before reasoning
3. **Save working memory last**: Ensure all messages are captured
4. **Use tools for long-term memory**: Let the LLM decide what to remember
5. **Let Agent Memory Server handle extraction**: Don't manually extract memories

## Configuration

### LangGraph Checkpointer

```python
from langgraph.checkpoint.redis import RedisSaver

checkpointer = RedisSaver.from_conn_info(
    host="localhost",
    port=6379,
    db=0
)

graph = workflow.compile(checkpointer=checkpointer)
```

### Agent Memory Server

```python
from redis_context_course import MemoryClient

memory_client = MemoryClient(
    user_id=student_id,
    namespace="redis_university"
)

# Load working memory
working_memory = await memory_client.get_working_memory(
    session_id=session_id
)

# Save working memory
await memory_client.save_working_memory(
    session_id=session_id,
    messages=messages
)
```

## Summary

The reference agent uses a **dual-memory architecture**:

1. **LangGraph Checkpointer** (Redis): Low-level graph state persistence
   - Automatic, thread-scoped, for resuming execution
   - Mentioned in passing, not the focus

2. **Agent Memory Server**: High-level memory management
   - Explicit load/save, session + user-scoped
   - Focus of memory lessons and demonstrations
   - Automatic extraction, semantic search, deduplication

This architecture provides complete memory capabilities while keeping the concepts clear and teachable.

