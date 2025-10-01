# Memory Client Migration Status

## Overview

We've migrated from a custom wrapper (`redis_context_course.memory_client.MemoryClient`) to using the official `agent_memory_client.MemoryAPIClient` directly.

## Completed ✅

### 1. Infrastructure
- ✅ Removed custom `memory_client.py` wrapper
- ✅ Updated `__init__.py` to export `MemoryAPIClient` as `MemoryClient`
- ✅ Updated `docker-compose.yml` with correct `LOG_LEVEL=INFO`
- ✅ Updated CI workflow with correct `LOG_LEVEL=INFO`

### 2. Core Code
- ✅ **agent.py**: Fully migrated to use `MemoryAPIClient`
  - Uses `get_or_create_working_memory()` with tuple unpacking
  - Uses `put_working_memory()` with `WorkingMemory` objects
  - Uses `create_long_term_memory()` with `ClientMemoryRecord` list
  - Uses `search_long_term_memory()` with proper parameters
  
- ✅ **tools.py**: Fully migrated to use `MemoryAPIClient`
  - Uses `create_long_term_memory()` with `ClientMemoryRecord`
  - Uses `search_long_term_memory()` returning `MemoryRecordResults`

### 3. Tests
- ✅ Updated `test_package.py` to import from `agent_memory_client`

## In Progress 🚧

### Notebooks
- ✅ Updated imports to use `agent_memory_client`
- ✅ Fixed `get_or_create_working_memory()` tuple unpacking
- ✅ Fixed `search_long_term_memory()` parameter names (`text=` instead of `query=`)
- ❌ **Still TODO**: Fix `save_working_memory()` calls

## API Differences

### Old Wrapper API (Removed)
```python
# Initialization
memory_client = MemoryClient(
    user_id="user123",
    namespace="my_namespace"
)

# Get/create working memory
working_memory = await memory_client.get_or_create_working_memory(
    session_id="session_001",
    model_name="gpt-4o"
)

# Save working memory
await memory_client.save_working_memory(
    session_id="session_001",
    messages=[{"role": "user", "content": "Hello"}]
)

# Create long-term memory
await memory_client.create_memory(
    text="User prefers dark mode",
    memory_type="semantic",
    topics=["preferences"]
)

# Search memories
memories = await memory_client.search_memories(
    query="preferences",
    limit=10
)
```

### New MemoryAPIClient API (Current)
```python
# Initialization
from agent_memory_client import MemoryAPIClient, MemoryClientConfig

config = MemoryClientConfig(
    base_url="http://localhost:8000",
    default_namespace="my_namespace"
)
memory_client = MemoryAPIClient(config=config)

# Get/create working memory (returns tuple!)
created, working_memory = await memory_client.get_or_create_working_memory(
    session_id="session_001",
    user_id="user123",
    model_name="gpt-4o"
)

# Save working memory (requires WorkingMemory object)
from agent_memory_client import WorkingMemory, MemoryMessage

messages = [MemoryMessage(role="user", content="Hello")]
working_memory = WorkingMemory(
    session_id="session_001",
    user_id="user123",
    messages=messages,
    memories=[],
    data={}
)

await memory_client.put_working_memory(
    session_id="session_001",
    memory=working_memory,
    user_id="user123",
    model_name="gpt-4o"
)

# Create long-term memory (requires list of ClientMemoryRecord)
from agent_memory_client import ClientMemoryRecord

memory = ClientMemoryRecord(
    text="User prefers dark mode",
    user_id="user123",
    memory_type="semantic",
    topics=["preferences"]
)

await memory_client.create_long_term_memory([memory])

# Search memories (returns MemoryRecordResults)
from agent_memory_client import UserId

results = await memory_client.search_long_term_memory(
    text="preferences",  # Note: 'text' not 'query'
    user_id=UserId(eq="user123"),
    limit=10
)

# Access memories via results.memories
for memory in results.memories:
    print(memory.text)
```

## Key Changes

1. **Initialization**: Requires `MemoryClientConfig` object
2. **get_or_create_working_memory**: Returns `tuple[bool, WorkingMemory]` - must unpack!
3. **save_working_memory → put_working_memory**: Requires `WorkingMemory` object
4. **create_memory → create_long_term_memory**: Takes list of `ClientMemoryRecord`
5. **search_memories → search_long_term_memory**: 
   - Parameter is `text=` not `query=`
   - Returns `MemoryRecordResults` not list
   - Access memories via `results.memories`
6. **user_id**: Must be passed to most methods (not stored in client)

## Remaining Work

### Notebooks to Fix

All notebooks in `section-3-memory/` and some in `section-4-optimizations/` need manual fixes for `save_working_memory()` calls.

**Pattern to find:**
```bash
grep -r "save_working_memory" notebooks/
```

**Fix required:**
Replace:
```python
await memory_client.save_working_memory(
    session_id=session_id,
    messages=messages
)
```

With:
```python
from agent_memory_client import WorkingMemory, MemoryMessage

memory_messages = [MemoryMessage(**msg) for msg in messages]
working_memory = WorkingMemory(
    session_id=session_id,
    user_id=user_id,  # Need to add user_id!
    messages=memory_messages,
    memories=[],
    data={}
)

await memory_client.put_working_memory(
    session_id=session_id,
    memory=working_memory,
    user_id=user_id,
    model_name="gpt-4o"
)
```

## Testing

After fixing notebooks, run:
```bash
cd python-recipes/context-engineering
source venv/bin/activate
pytest --nbval-lax --disable-warnings notebooks/section-3-memory/
pytest --nbval-lax --disable-warnings notebooks/section-4-optimizations/
```

## CI Status

Current status: **9/15 notebooks passing (60%)**

Expected after notebook fixes: **12-13/15 notebooks passing (80-87%)**

The remaining failures will likely be due to:
- OpenAI API rate limits
- Agent Memory Server extraction timing
- Network issues in CI

## References

- [Agent Memory Server GitHub](https://github.com/redis/agent-memory-server)
- [Agent Memory Client Source](https://github.com/redis/agent-memory-server/tree/main/agent-memory-client)
- [Agent Memory Server Docs](https://redis.github.io/agent-memory-server/)

