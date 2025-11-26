# Stage 6 Quick Reference

## TL;DR

**Stage 6 = Stage 5 + Long-term Memory Tools**

Add 2 new tools (`search_memories`, `store_memory`) that enable cross-session personalization.

---

## What Changes

### Files to Modify

| File | Changes | Lines Changed |
|------|---------|---------------|
| `agent/tools.py` | Add 2 new tools + schemas | ~100 lines |
| `agent/nodes.py` | Update tool binding + system prompt | ~20 lines |
| `agent/workflow.py` | Import new tools | ~2 lines |
| `agent/state.py` | None | 0 lines |

**Total:** ~120 lines of code

---

## New Tools

### 1. search_memories_tool

```python
@tool("search_memories", args_schema=SearchMemoriesInput)
async def search_memories_tool(query: str, limit: int = 5) -> str:
    """Search student's long-term memory for preferences and facts."""
    # Implementation: ~30 lines
```

**When LLM uses it:**
- "What are my preferences?"
- Agent wants to personalize recommendations
- Follow-up questions referencing past conversations

### 2. store_memory_tool

```python
@tool("store_memory", args_schema=StoreMemoryInput)
async def store_memory_tool(text: str, memory_type: str = "semantic", topics: List[str] = []) -> str:
    """Store important information to student's long-term memory."""
    # Implementation: ~30 lines
```

**When LLM uses it:**
- User shares preferences: "I prefer online courses"
- User states goals: "I want to work in AI"
- User mentions constraints: "I can only take evening classes"

---

## Code Changes Summary

### tools.py

```python
# ADD: Input schemas
class SearchMemoriesInput(BaseModel):
    query: str = Field(description="...")
    limit: int = Field(default=5, description="...")

class StoreMemoryInput(BaseModel):
    text: str = Field(description="...")
    memory_type: str = Field(default="semantic", description="...")
    topics: List[str] = Field(default=[], description="...")

# ADD: Tool implementations
@tool("search_memories", args_schema=SearchMemoriesInput)
async def search_memories_tool(query: str, limit: int = 5) -> str:
    # ... implementation

@tool("store_memory", args_schema=StoreMemoryInput)
async def store_memory_tool(text: str, memory_type: str = "semantic", topics: List[str] = []) -> str:
    # ... implementation
```

### nodes.py

```python
# MODIFY: Update tool binding
def get_agent_llm():
    # OLD: llm.bind_tools([search_courses_tool])
    # NEW:
    llm.bind_tools([search_courses_tool, search_memories_tool, store_memory_tool])

# MODIFY: Update system prompt
system_prompt = """You are a helpful Redis University course advisor assistant with memory capabilities.

You have access to THREE tools:

1. **search_courses**: Search the Redis University course catalog using semantic search, exact course code matching,
   or hybrid strategies. Use this to find courses based on topics, prerequisites, difficulty levels, or specific
   course codes. The tool supports filtering by department, difficulty, and information type (syllabus, assignments, etc.).

2. **search_memories**: Search the student's long-term memory for their preferences, goals, past interactions, and
   important facts. Use this to recall what the student has told you before (e.g., "I prefer online courses",
   "I want to work in AI", "I'm interested in machine learning"). This enables personalized recommendations.

3. **store_memory**: Store important information about the student to long-term memory for future sessions.
   Use this when students share preferences, career goals, constraints, or interests. Do NOT store temporary
   information, course details (already in catalog), or general questions.

Guidelines:
- Use search_memories FIRST if the query might benefit from knowing student preferences or past interactions
- Use store_memory when students share preferences, goals, constraints, or interests
- Use search_courses to find relevant courses based on the query and any retrieved preferences
- Personalize recommendations by combining memory search results with course search results
- Be conversational and helpful
"""
```

### workflow.py

```python
# ADD: Import new tools
from .tools import search_courses_tool, search_memories_tool, store_memory_tool
```

---

## Testing Checklist

### Test 1: Store Preferences
```python
# User: "I prefer online courses and I'm interested in machine learning"
# Expected: Agent calls store_memory twice
# Verify: Memories stored in Agent Memory Server
```

### Test 2: Retrieve Memories
```python
# User: "What courses would you recommend?" (in new session)
# Expected: Agent calls search_memories, then search_courses
# Verify: Response mentions stored preferences
```

### Test 3: Cross-Session Persistence
```python
# Session 1: Store preference
# Session 2 (new session_id): Retrieve preference
# Verify: Same student_id retrieves same memories
```

### Test 4: Multi-Tool Decision
```python
# User: "I want to work in AI. Show me relevant courses."
# Expected: Agent calls store_memory (goal), then search_courses
# Verify: Both tools used in single turn
```

---

## Example Conversations

### Example 1: First Interaction

**Input:**
```
User: "Hi! I'm interested in machine learning. I prefer online courses."
```

**Agent Actions:**
1. `store_memory(text="Student is interested in machine learning", topics=["interests", "ML"])`
2. `store_memory(text="Student prefers online course format", topics=["preferences", "format"])`
3. `search_courses(query="machine learning", search_strategy="semantic_only")`

**Output:**
```
"I've noted that you're interested in machine learning and prefer online courses! 
Here are some ML courses available online:

1. CS101: Introduction to Machine Learning (Online)
   - Beginner-friendly introduction to ML concepts
   
2. CS201: Applied Machine Learning (Online)
   - Hands-on projects with real datasets
..."
```

---

### Example 2: Second Session (Personalization)

**Input (New Session):**
```
User: "What courses would you recommend for me?"
```

**Agent Actions:**
1. `search_memories(query="student preferences and interests")`
   - Returns: "Student is interested in machine learning", "Student prefers online format"
2. `search_courses(query="machine learning", ...)`

**Output:**
```
"Based on your interest in machine learning and preference for online courses, 
I recommend:

1. CS101: Introduction to Machine Learning (Online)
   - Perfect for your ML interest
   - Fully online format as you prefer
..."
```

---

### Example 3: Multi-Turn with Memory

**Turn 1:**
```
User: "I want to prepare for a career in AI research"

Agent:
- store_memory(text="Student's career goal is AI research", topics=["goals", "career"])
- search_courses(query="AI research preparation", ...)

Response: "Great goal! For AI research, I recommend starting with..."
```

**Turn 2 (Same Session):**
```
User: "What prerequisites do I need?"

Agent:
- search_memories(query="career goals") → "Student's career goal is AI research"
- search_courses(query="AI research prerequisites", intent="PREREQUISITES")

Response: "For your AI research goal, you'll need strong foundations in..."
```

**Turn 3 (New Session, Days Later):**
```
User: "Show me advanced courses"

Agent:
- search_memories(query="career goals and interests")
  → "Student's career goal is AI research", "Student is interested in machine learning"
- search_courses(query="advanced AI machine learning", difficulty_level="advanced")

Response: "Based on your AI research goal, here are advanced courses..."
```

---

## Comparison: Stage 5 vs Stage 6

| Feature | Stage 5 | Stage 6 |
|---------|---------|---------|
| **Working Memory** | ✅ Yes | ✅ Yes |
| **Long-term Memory** | ❌ No | ✅ Yes |
| **Tools** | 1 | 3 |
| **Personalization** | Session-only | Cross-session |
| **Memory Control** | Scripted (load/save) | Hybrid (scripted working + agentic long-term) |
| **Use Case** | Multi-turn Q&A | Personalized advisor |
| **Workflow Nodes** | 5 | 5 (same) |
| **State Fields** | Same | Same |
| **Code Changes** | - | ~120 lines |

---

## Educational Value

### What Students Learn

1. **Long-term Memory Tools**
   - How to implement memory search/store as LangChain tools
   - When to use long-term vs working memory
   - Memory types (semantic vs episodic)

2. **Multi-Tool Decision Making**
   - LLM decides between 3 tools (search_courses, search_memories, store_memory)
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

## Key Design Decisions

### Why 2 Tools (Not 3)?

**Considered:** `search_memories`, `store_memory`, `update_memory`

**Decision:** Only 2 tools (`search_memories`, `store_memory`)

**Rationale:**
- Agent Memory Server doesn't have explicit "update" API
- Updates can be handled by storing new memories
- Keeps tool set simple for learning
- Can add `update_memory` in future stage if needed

### Why Global State for student_id?

**Considered:** Closure, dependency injection, global state

**Decision:** Global state (simple, consistent with Stage 5 patterns)

**Implementation:**
```python
# In nodes.py
_current_student_id = None

def agent_node(state):
    global _current_student_id
    _current_student_id = state["student_id"]
    # ... rest of logic

# In tools.py
from .nodes import _current_student_id
# Use in tool implementations
```

### Why No Workflow Changes?

**Key Insight:** Agentic architecture means adding tools doesn't require workflow changes!

- Stage 5: 5 nodes, 1 tool
- Stage 6: 5 nodes, 3 tools
- Workflow graph: IDENTICAL

This demonstrates the power of the agentic approach.

---

## Common Pitfalls

### ❌ Pitfall 1: Storing Everything

**Wrong:**
```python
User: "What is machine learning?"
Agent: store_memory("User asked about machine learning")  # DON'T DO THIS
```

**Right:**
```python
User: "I'm interested in machine learning"
Agent: store_memory("Student is interested in machine learning")  # ✅ Preference
```

**Rule:** Only store preferences, goals, and constraints. Not questions or course details.

---

### ❌ Pitfall 2: Not Using Memories

**Wrong:**
```python
User: "What courses do you recommend?" (in new session)
Agent: search_courses("general courses")  # Ignores stored preferences
```

**Right:**
```python
User: "What courses do you recommend?"
Agent: 
  1. search_memories("preferences and interests")
  2. search_courses("machine learning")  # Based on retrieved preferences
```

**Rule:** Always check memories first for personalization opportunities.

---

### ❌ Pitfall 3: Wrong Memory Type

**Wrong:**
```python
store_memory(
    text="Student asked about CS101 on 2024-01-15",
    memory_type="semantic"  # This is episodic, not semantic!
)
```

**Right:**
```python
# Semantic (timeless facts)
store_memory(text="Student prefers online courses", memory_type="semantic")

# Episodic (time-bound events)
store_memory(text="Student enrolled in CS101 on 2024-01-15", memory_type="episodic")
```

**Rule:** Semantic = facts/preferences, Episodic = events/interactions

---

## Next Steps

After implementing Stage 6:

1. **Test thoroughly** with example conversations
2. **Document** example outputs
3. **Compare** with Stage 5 to verify all functionality preserved
4. **Create** test scripts (test_memory_tools.py)
5. **Update** README with Stage 6 description

---

## Questions?

**Q: Does Stage 6 change the workflow graph?**  
A: No! Workflow structure is identical to Stage 5. Only the agent's capabilities expand.

**Q: How many LLM calls does Stage 6 make?**  
A: Same as Stage 5 (2-3 calls per turn). Tool calling doesn't increase LLM calls significantly.

**Q: Can memories be deleted?**  
A: Not in Stage 6. This could be added as `delete_memory` tool in future stage.

**Q: What if Agent Memory Server is down?**  
A: Tools should handle gracefully with try/except and return error messages.

**Q: How do I test cross-session persistence?**  
A: Use different `session_id` but same `student_id` in test scripts.

---

## Implementation Time Estimate

- **Add tools.py changes:** 30 minutes
- **Update nodes.py:** 15 minutes
- **Test basic functionality:** 30 minutes
- **Create test scripts:** 30 minutes
- **Documentation:** 30 minutes

**Total:** ~2.5 hours for complete Stage 6 implementation

