# 🧠 Section 3: Memory Architecture

## Overview

This section teaches **memory-enhanced context engineering** by building on Section 2's retrieved context system. You'll learn how to add **working memory** (conversation history) and **long-term memory** (persistent knowledge) to create stateful, personalized conversations.

## Learning Objectives

By the end of this section, you will:

1. **Understand** why memory is essential for context engineering (the grounding problem)
2. **Implement** working memory for conversation continuity
3. **Use** long-term memory for persistent user knowledge
4. **Integrate** memory with Section 2's retrieved context system
5. **Build** a complete memory-enhanced course advisor

## Prerequisites

- ✅ Completed Section 1 (Context Engineering Foundations)
- ✅ Completed Section 2 (Retrieved Context Engineering)
- ✅ Redis instance running
- ✅ Agent Memory Server running (see reference-agent/README.md)
- ✅ OpenAI API key configured

## Notebooks

### 01_memory_fundamentals_and_integration.ipynb

**⏱️ Estimated Time:** 45-60 minutes

**What You'll Learn:**
- The grounding problem (why agents need memory)
- Working memory fundamentals (session-scoped conversation history)
- Long-term memory fundamentals (cross-session persistent knowledge)
- Memory integration with RAG
- Complete memory-enhanced RAG system

**What You'll Build:**
- Working memory demo (multi-turn conversations)
- Long-term memory demo (persistent knowledge storage and search)
- Complete `memory_enhanced_rag_query()` function
- End-to-end memory-enhanced course advisor

**Key Concepts:**
- Reference resolution ("it", "that course", "the first one")
- Conversation continuity across turns
- Semantic memory search
- All four context types working together

## Architecture

### Memory Types

**1. Working Memory (Session-Scoped)**
- Stores conversation messages for current session
- Enables reference resolution and conversation continuity
- TTL-based (default: 1 hour)
- Automatically extracts important facts to long-term storage

**2. Long-term Memory (Cross-Session)**
- Stores persistent facts, preferences, goals
- Enables personalization across sessions
- Vector-indexed for semantic search
- Three types: semantic (facts), episodic (events), message

### Integration Pattern

```
User Query
    ↓
1. Load Working Memory (conversation history)
2. Search Long-term Memory (user preferences, facts)
3. RAG Search (relevant courses)
4. Assemble Context (System + User + Conversation + Retrieved)
5. Generate Response
6. Save Working Memory (updated conversation)
```

### Four Context Types (Complete!)

1. **System Context** (Static) - ✅ Section 2
2. **User Context** (Dynamic, User-Specific) - ✅ Section 2 + Long-term Memory
3. **Conversation Context** (Dynamic, Session-Specific) - ✨ **Working Memory**
4. **Retrieved Context** (Dynamic, Query-Specific) - ✅ Section 2

## Technology Stack

- **Agent Memory Server** - Production-ready dual-memory system
- **Redis** - Backend storage for memory
- **LangChain** - LLM interaction (no LangGraph needed yet)
- **OpenAI** - GPT-4o for generation, text-embedding-3-small for vectors
- **RedisVL** - Vector search (via reference-agent utilities)

## Key Differences from Section 2

| Feature | Section 2 (Retrieved Context) | Section 3 (Memory-Enhanced) |
|---------|---------------------------|----------------------------------|
| Conversation History | ❌ None | ✅ Working Memory |
| Multi-turn Conversations | ❌ Each query independent | ✅ Context carries forward |
| Reference Resolution | ❌ Can't resolve "it", "that" | ✅ Resolves from history |
| Personalization | ⚠️ Profile only | ✅ Profile + Long-term Memory |
| Cross-Session Knowledge | ❌ None | ✅ Persistent memories |

## Practice Exercises

1. **Cross-Session Personalization** - Store and use preferences across sessions
2. **Memory-Aware Filtering** - Use long-term memories to filter RAG results
3. **Conversation Summarization** - Summarize long conversations to manage context
4. **Multi-User Memory Management** - Handle multiple students with separate memories
5. **Memory Search Quality** - Experiment with semantic search for memories

## What's Next?

**Section 4: Tool Selection & Agentic Workflows**

You'll add **tools** and **LangGraph** to create a complete agent that:
- Decides which tools to use
- Takes actions (enroll courses, check prerequisites)
- Manages complex multi-step workflows
- Handles errors and retries

## Resources

- **Reference Agent** - `python-recipes/context-engineering/reference-agent/`
- **Agent Memory Server** - https://github.com/redis/agent-memory-server
- **LangChain Memory** - https://python.langchain.com/docs/modules/memory/
- **Redis Agent Memory** - https://redis.io/docs/latest/develop/clients/agent-memory/

## Troubleshooting

### Agent Memory Server Not Available

If you see "⚠️ Agent Memory Server not available":

1. Check if the server is running:
   ```bash
   curl http://localhost:8088/health
   ```

2. Start the server (see reference-agent/README.md):
   ```bash
   cd reference-agent
   docker-compose up -d
   ```

3. Verify environment variable:
   ```bash
   echo $AGENT_MEMORY_URL
   # Should be: http://localhost:8088
   ```

### Memory Not Persisting

If memories aren't persisting across sessions:

1. Check Redis connection:
   ```python
   from redis_context_course.redis_config import redis_config
   print(redis_config.health_check())  # Should be True
   ```

2. Verify user_id and session_id are consistent:
   ```python
   # Same user_id for same student across sessions
   # Different session_id for different conversations
   ```

3. Check memory client configuration:
   ```python
   print(memory_client.config.base_url)
   print(memory_client.config.default_namespace)
   ```

## Notes

- **LangChain is sufficient** for this section (no LangGraph needed)
- **LangGraph becomes necessary in Section 4** for tool calling and complex workflows
- **Agent Memory Server** is production-ready (Redis-backed, scalable)
- **Working memory** automatically extracts important facts to long-term storage
- **Semantic search** enables natural language queries for memories

---

**Ready to add memory to your RAG system? Start with `01_memory_fundamentals_and_integration.ipynb`!** 🚀

