# Stage 6: Long-term Memory Tools

**Building on Stage 5:** Adds long-term memory tools for cross-session personalization.

## What's New in Stage 6

Stage 6 extends Stage 5 by adding **two new LangChain tools** that enable the agent to manage long-term memory:

1. **`search_memories_tool`** - Search student's long-term memory for preferences, goals, and facts
2. **`store_memory_tool`** - Store important information to long-term memory

### Key Capabilities

✅ **Store student preferences** ("I prefer online courses")  
✅ **Store career goals** ("I want to work in AI research")  
✅ **Store constraints** ("I can only take evening classes")  
✅ **Search memories** to personalize recommendations  
✅ **Cross-session persistence** (memories survive across sessions)  
✅ **Multi-tool decision-making** (LLM chooses between 3 tools)  

---

## Architecture

### Workflow Graph

```
START
  ↓
load_working_memory (scripted)
  ↓
classify_intent
  ↓
  ├─ GREETING → handle_greeting → save_working_memory → END
  └─ OTHER → agent → save_working_memory → END
```

**Same workflow structure as Stage 5!** Only the agent's capabilities expand.

### Tools Available

| Tool | Purpose | When LLM Uses It |
|------|---------|------------------|
| **search_courses** | Search course catalog | Find courses matching query |
| **search_memories** | Search long-term memory | Recall student preferences/goals |
| **store_memory** | Store to long-term memory | Student shares preferences/goals |

---

## Comparison: Stage 5 vs Stage 6

| Feature | Stage 5 | Stage 6 |
|---------|---------|---------|
| **Working Memory** | ✅ Yes | ✅ Yes |
| **Long-term Memory** | ❌ No | ✅ Yes |
| **Tools** | 1 (search_courses) | 3 (search_courses, search_memories, store_memory) |
| **Personalization** | Session-only | Cross-session |
| **Memory Control** | Scripted (load/save) | Hybrid (scripted working + agentic long-term) |
| **Use Case** | Multi-turn Q&A | Personalized advisor |

---

## Usage

### Prerequisites

1. **Agent Memory Server** running on `http://localhost:8088`
2. **Redis** running on `localhost:6379`
3. **OpenAI API key** set in environment
4. **Student ID** required for all queries

### Interactive Mode

```bash
# Start interactive session (STUDENT ID REQUIRED)
python cli.py --student-id alice

# Resume existing session
python cli.py --student-id alice --session-id sess_001
```

**Note:** `--student-id` is required! This identifies the student for long-term memory storage.

### Example Conversations

#### Session 1: Store Preferences

```
User: "Hi! I'm interested in machine learning. I prefer online courses."

Agent:
1. store_memory("Student is interested in machine learning", topics=["interests", "ML"])
2. store_memory("Student prefers online course format", topics=["preferences", "format"])
3. search_courses("machine learning")

Response: "I've noted that you're interested in machine learning and prefer online courses! 
Here are some ML courses available online: [course list]"
```

#### Session 2: Personalized Recommendations (New Session)

```
User: "What courses would you recommend?"

Agent:
1. search_memories("student preferences and interests")
   → Returns: "interested in ML", "prefers online"
2. search_courses("machine learning", ...)

Response: "Based on your interest in machine learning and preference for online courses, 
I recommend: [personalized course list]"
```

---

## Testing

### Run Memory Tools Test Suite

```bash
python test_memory_tools.py
```

This tests:
- ✅ Storing student preferences
- ✅ Retrieving memories in new session
- ✅ Multi-tool decision-making
- ✅ Cross-session persistence

### Run Simple Tests

```bash
python test_simple.py
```

---

## Implementation Details

### Memory Tools

#### search_memories_tool

```python
@tool("search_memories", args_schema=SearchMemoriesInput)
async def search_memories_tool(query: str, limit: int = 5) -> str:
    """Search student's long-term memory for preferences and facts."""
```

**Parameters:**
- `query`: Natural language query (e.g., "career goals", "preferences")
- `limit`: Max number of memories to return (default: 5)

**Returns:** Formatted list of memories with topics

#### store_memory_tool

```python
@tool("store_memory", args_schema=StoreMemoryInput)
async def store_memory_tool(
    text: str, 
    memory_type: str = "semantic", 
    topics: List[str] = []
) -> str:
    """Store important information to student's long-term memory."""
```

**Parameters:**
- `text`: Information to store (e.g., "Student prefers online courses")
- `memory_type`: "semantic" (facts) or "episodic" (events)
- `topics`: Tags for organization (e.g., ["preferences", "format"])

**Returns:** Confirmation message

---

## Educational Value

### What Stage 6 Teaches

1. **Long-term Memory Tools**
   - How to implement memory search/store as LangChain tools
   - When to use long-term vs working memory
   - Memory types (semantic vs episodic)

2. **Multi-Tool Decision Making**
   - LLM decides between 3 tools
   - Tool selection based on query intent
   - Combining multiple tools in single turn

3. **Personalization Patterns**
   - Storing user preferences
   - Retrieving context for personalization
   - Cross-session continuity

4. **Memory Management**
   - What to store (preferences, goals, constraints)
   - What NOT to store (temporary info, course details)
   - Using topics for organization

---

## Files Modified from Stage 5

| File | Changes | Lines Added |
|------|---------|-------------|
| `agent/tools.py` | Added 2 new tools + schemas | ~160 lines |
| `agent/nodes.py` | Updated tool binding + system prompt | ~30 lines |
| `agent/workflow.py` | Updated docstring | ~2 lines |
| `cli.py` | Updated titles | ~5 lines |

**Total:** ~200 lines of code added

---

## Troubleshooting

### "Error: Student ID not set"

**Cause:** `student_id` not passed to `run_agent_async()`

**Solution:** Always provide `student_id` parameter:
```python
result = await run_agent_async(
    agent=agent,
    query=query,
    session_id=session_id,
    student_id="alice",  # Required!
    enable_caching=False,
)
```

### "No relevant memories found"

**Cause:** No memories stored yet for this student

**Solution:** First share preferences to store memories:
```
User: "I prefer online courses and I'm interested in ML"
```

### Agent Memory Server not available

**Cause:** Agent Memory Server not running

**Solution:** Start the server:
```bash
# Check if running
curl http://localhost:8088/health

# Start if needed (see Agent Memory Server docs)
```

---

## References

- **Stage 5:** Working memory (multi-turn conversations)
- **Section 3 Notebooks:** Long-term memory patterns
- **Section 4 Notebooks:** Memory tools implementation
- **Agent Memory Server:** https://github.com/redis/agent-memory-server

