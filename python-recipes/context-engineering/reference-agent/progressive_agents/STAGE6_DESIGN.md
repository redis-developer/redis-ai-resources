# Stage 6: Long-term Memory Tools - Complete Design Document

## Executive Summary

Stage 6 adds **long-term memory tools** to the agent, enabling it to store and retrieve persistent facts about students across sessions. This demonstrates the transition from **scripted memory operations** (Section 3) to **LLM-controlled memory tools** (Section 4).

**Key Addition:** Two new LangChain tools (`search_memories`, `store_memory`) that the LLM can use to manage long-term memory.

---

## 1. Summary Comparison: Stage 5 vs Stage 6

| Feature | Stage 5 | Stage 6 |
|---------|---------|---------|
| **Working Memory** | ✅ Yes (load/save nodes) | ✅ Yes (load/save nodes) |
| **Long-term Memory** | ❌ No | ✅ Yes (via tools) |
| **Tools Available** | 1 (`search_courses`) | 3 (`search_courses`, `search_memories`, `store_memory`) |
| **Memory Operations** | Scripted (automatic load/save) | Hybrid (scripted working + agentic long-term) |
| **LLM Decides** | When to search courses | When to search courses + when to store/retrieve memories |
| **Personalization** | Session-only (working memory) | Cross-session (long-term memory) |
| **Use Case** | Multi-turn course Q&A | Personalized course advisor with memory |
| **Workflow Nodes** | 5 nodes | 5 nodes (same structure) |
| **Educational Focus** | Working memory + tool calling | Long-term memory tools + decision-making |

---

## 2. Complete Stage 5 Architecture Analysis

### Current Workflow Graph

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

### Current State Fields

**Core Query:**
- `original_query`, `sub_questions`, `sub_answers`, `final_response`

**Intent & NER:**
- `query_intent`, `extracted_entities`, `search_strategy`, `exact_matches`, `metadata_filters`

**Working Memory (NEW in Stage 5):**
- `session_id`, `student_id`, `working_memory_loaded`, `conversation_history`, `current_turn_messages`

**Cache & Research:**
- `cache_hits`, `cache_confidences`, `research_iterations`, `research_quality_scores`

**Coordination:**
- `execution_path`, `active_sub_question`, `metrics`, `timestamp`, `llm_calls`

### Current Tools

**1. search_courses_tool**
- **Purpose:** Search course catalog with hybrid strategies
- **Parameters:** query, intent, search_strategy, course_codes, information_type, departments, difficulty_level
- **When LLM uses it:** To find courses matching user's question

### Current Nodes

1. **load_working_memory_node** - Loads conversation history from Agent Memory Server
2. **classify_intent_node** - Classifies query intent (GREETING, GENERAL, PREREQUISITES, etc.)
3. **handle_greeting_node** - Handles greetings without course search
4. **agent_node** - LLM with tool calling (decides when to use search_courses)
5. **save_working_memory_node** - Saves conversation to Agent Memory Server

### Current Capabilities

✅ Multi-turn conversations (working memory)  
✅ Intent-based context adaptation  
✅ Hybrid search (exact + semantic + NER)  
✅ LLM-controlled course search  
✅ Conversation history across turns  

### Current Limitations

❌ No long-term memory (facts don't persist across sessions)  
❌ No personalization based on student preferences  
❌ No memory of past course interests or goals  
❌ Cannot remember student constraints (schedule, difficulty preferences, etc.)  

---

## 3. Stage 6 Design

### Goal

Add **long-term memory tools** that enable the agent to:
1. **Store** important facts about students (preferences, goals, constraints)
2. **Search** long-term memory to personalize recommendations
3. **Decide** when to use memory tools vs course search

### Design Principles

1. **Minimal Changes:** Build incrementally on Stage 5
2. **Agentic Control:** LLM decides when to store/retrieve memories
3. **Educational Clarity:** Clear distinction between working memory (scripted) and long-term memory (agentic)
4. **Notebook Consistency:** Follow exact patterns from Section 4 notebooks

---

## 4. New Tools Specification

### Tool 1: search_memories

**Purpose:** Search long-term memory for student facts, preferences, and past interactions

**Input Schema:**
```python
class SearchMemoriesInput(BaseModel):
    """Input schema for searching memories."""
    
    query: str = Field(
        description="Natural language query to search for in user's long-term memory. "
        "Examples: 'career goals', 'course preferences', 'learning style'"
    )
    limit: int = Field(
        default=5,
        description="Maximum number of memories to return. Default is 5."
    )
```

**Implementation:**
```python
@tool("search_memories", args_schema=SearchMemoriesInput)
async def search_memories_tool(query: str, limit: int = 5) -> str:
    """
    Search the user's long-term memory for relevant facts, preferences, and past interactions.
    
    Use this tool when you need to:
    - Recall user preferences: "What format does the user prefer?"
    - Remember past goals: "What career path is the user interested in?"
    - Find previous interactions: "What courses did we discuss before?"
    - Personalize recommendations: "What are the user's interests?"
    
    The search uses semantic matching to find relevant memories.
    
    Returns: List of relevant memories with content and metadata.
    """
    try:
        from agent_memory_client.filters import UserId
        
        memory_client = get_memory_client()
        student_id = state.get("student_id")  # Get from state
        
        # Search long-term memory
        results = await memory_client.search_long_term_memory(
            text=query,
            user_id=UserId(eq=student_id),
            limit=limit
        )
        
        if not results.memories or len(results.memories) == 0:
            return "No relevant memories found."
        
        output = []
        for i, memory in enumerate(results.memories, 1):
            output.append(f"{i}. {memory.text}")
            if memory.topics:
                output.append(f"   Topics: {', '.join(memory.topics)}")
        
        return "\n".join(output)
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        return f"Error searching memories: {str(e)}"
```

**When LLM Uses It:**
- User asks about their preferences: "What kind of courses do I like?"
- Agent wants to personalize: "Let me check your preferences..."
- Follow-up questions: "Based on what you told me before..."

---

### Tool 2: store_memory

**Purpose:** Store important information to student's long-term memory

**Input Schema:**
```python
class StoreMemoryInput(BaseModel):
    """Input schema for storing memories."""
    
    text: str = Field(
        description="The information to store. Should be a clear, factual statement. "
        "Examples: 'User prefers online courses', 'User's career goal is AI research'"
    )
    memory_type: str = Field(
        default="semantic",
        description="Type of memory: 'semantic' (facts/preferences), 'episodic' (events/interactions). "
        "Default is 'semantic'."
    )
    topics: List[str] = Field(
        default=[],
        description="Optional tags to categorize the memory, such as ['preferences', 'courses']"
    )
```

**Implementation:**
```python
@tool("store_memory", args_schema=StoreMemoryInput)
async def store_memory_tool(
    text: str,
    memory_type: str = "semantic",
    topics: List[str] = []
) -> str:
    """
    Store important information to the user's long-term memory.
    
    Use this tool when the user shares:
    - Preferences: "I prefer online courses", "I like hands-on projects"
    - Goals: "I want to work in AI", "I'm preparing for grad school"
    - Important facts: "I have a part-time job", "I'm interested in startups"
    - Constraints: "I can only take 2 courses per semester"
    
    Do NOT store:
    - Temporary information (use conversation context instead)
    - Course details (already in course catalog)
    - General questions
    
    Returns: Confirmation message.
    """
    try:
        from agent_memory_client.models import ClientMemoryRecord
        
        memory_client = get_memory_client()
        student_id = state.get("student_id")  # Get from state
        
        # Create memory record
        memory = ClientMemoryRecord(
            text=text,
            user_id=student_id,
            memory_type=memory_type,
            topics=topics or []
        )
        
        # Store in long-term memory
        await memory_client.create_long_term_memory([memory])
        
        logger.info(f"💾 Stored memory: {text}")
        return f"✅ Stored to long-term memory: {text}"
    except Exception as e:
        logger.error(f"Memory storage failed: {e}")
        return f"Error storing memory: {str(e)}"
```

**When LLM Uses It:**
- User shares preferences: "I prefer online courses" → Store it
- User states goals: "I want to work in AI" → Store it
- User mentions constraints: "I can only take evening classes" → Store it

---

## 5. File-by-File Changes

### 5.1 tools.py

**Changes:**
1. Add `SearchMemoriesInput` schema
2. Add `search_memories_tool` function
3. Add `StoreMemoryInput` schema
4. Add `store_memory_tool` function
5. Import `get_memory_client` from nodes.py (or define it in tools.py)

**What Stays the Same:**
- `search_courses_tool` (unchanged)
- `search_courses_sync` (unchanged)
- All hierarchical retrieval logic (unchanged)

**New Imports:**
```python
from agent_memory_client.models import ClientMemoryRecord
from agent_memory_client.filters import UserId
```

---

### 5.2 nodes.py

**Changes:**
1. Update `get_agent_llm()` to bind 3 tools instead of 1:
   ```python
   _agent_llm = llm.bind_tools([search_courses_tool, search_memories_tool, store_memory_tool])
   ```

2. Update `agent_node()` system prompt to include memory tool instructions:
   ```python
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

3. Add helper to pass `student_id` to tools (tools need access to state)

**What Stays the Same:**
- `load_working_memory_node` (unchanged)
- `save_working_memory_node` (unchanged)
- `classify_intent_node` (unchanged)
- `handle_greeting_node` (unchanged)
- Agent node structure (only system prompt and tool binding changes)

---

### 5.3 workflow.py

**Changes:**
- Import new tools: `search_memories_tool`, `store_memory_tool`

**What Stays the Same:**
- Workflow graph structure (5 nodes, same edges)
- Entry point (load_memory)
- Routing logic (unchanged)
- All edges (unchanged)

**No workflow changes needed!** The beauty of the agentic approach is that adding tools doesn't require workflow changes.

---

### 5.4 state.py

**Changes:**
- None! State structure remains the same.

**Why?**
- `student_id` already exists in state
- Long-term memory operations don't need new state fields
- Tools access state through closure or global context

---

## 6. Workflow Diagram

### Before (Stage 5)

```
START → load_memory → classify_intent → [greeting/agent] → save_memory → END

Agent Node:
  - Tools: [search_courses]
  - Decides: When to search courses
```

### After (Stage 6)

```
START → load_memory → classify_intent → [greeting/agent] → save_memory → END

Agent Node:
  - Tools: [search_courses, search_memories, store_memory]
  - Decides: When to search courses + when to use memory tools
```

**Key Insight:** Workflow structure is IDENTICAL. Only the agent's capabilities expand.

---

## 7. Example Conversation Scenarios

### Scenario 1: First Interaction (Store Preferences)

**Turn 1:**
```
User: "Hi! I'm interested in machine learning courses. I prefer online format."

Agent thinks:
1. User shared preferences → Use store_memory
2. User asked about ML courses → Use search_courses

Agent actions:
- store_memory(text="Student is interested in machine learning", topics=["interests", "ML"])
- store_memory(text="Student prefers online course format", topics=["preferences", "format"])
- search_courses(query="machine learning", search_strategy="semantic_only")

Response: "I've noted that you're interested in machine learning and prefer online courses! 
Here are some ML courses available online: [course list]"
```

### Scenario 2: Second Session (Retrieve Preferences)

**Turn 1 (New Session):**
```
User: "What courses would you recommend for me?"

Agent thinks:
1. Generic question → Check if I know student preferences
2. Use search_memories to recall preferences

Agent actions:
- search_memories(query="student preferences and interests")
  → Returns: "Student is interested in machine learning", "Student prefers online format"
- search_courses(query="machine learning", departments=[], difficulty_level=None)

Response: "Based on your interest in machine learning and preference for online courses, 
I recommend: [personalized course list]"
```

### Scenario 3: Multi-turn with Memory

**Turn 1:**
```
User: "I want to prepare for a career in AI research"
Agent: store_memory(text="Student's career goal is AI research", topics=["goals", "career"])
Response: "Great goal! Let me help you find courses for AI research..."
```

**Turn 2 (same session):**
```
User: "What prerequisites do I need?"
Agent: search_memories(query="career goals")
       → "Student's career goal is AI research"
       search_courses(query="AI research prerequisites", intent="PREREQUISITES")
Response: "For AI research, you'll need strong foundations in..."
```

**Turn 3 (new session, days later):**
```
User: "Show me advanced courses"
Agent: search_memories(query="career goals and interests")
       → "Student's career goal is AI research", "Student is interested in machine learning"
       search_courses(query="advanced AI machine learning", difficulty_level="advanced")
Response: "Based on your AI research goal, here are advanced courses..."
```

---

## 8. Educational Progression

### What Stage 5 Teaches

- Working memory for multi-turn conversations
- Session-scoped context
- Agentic tool calling (1 tool)
- LLM decides when to search

### What Stage 6 Adds

- Long-term memory for cross-session persistence
- LLM decides when to store vs retrieve memories
- Multi-tool decision-making (3 tools)
- Personalization based on stored facts
- Memory management strategies (what to store, when to retrieve)

### Learning Path

| Stage | Memory Type | Control | Tools | Key Concept |
|-------|-------------|---------|-------|-------------|
| **Stage 3** | None | Scripted | 1 (search) | Hierarchical retrieval |
| **Stage 4** | None | Agentic | 1 (search) | Hybrid search + NER |
| **Stage 5** | Working | Hybrid | 1 (search) | Multi-turn conversations |
| **Stage 6** | Working + Long-term | Hybrid | 3 (search + memory) | Personalization + memory tools |

---

## 9. Implementation Checklist

### Phase 1: Add Memory Tools
- [ ] Add `SearchMemoriesInput` schema to tools.py
- [ ] Implement `search_memories_tool` in tools.py
- [ ] Add `StoreMemoryInput` schema to tools.py
- [ ] Implement `store_memory_tool` in tools.py
- [ ] Test tools independently

### Phase 2: Update Agent Node
- [ ] Update `get_agent_llm()` to bind 3 tools
- [ ] Update agent system prompt with memory tool instructions
- [ ] Ensure tools can access `student_id` from state
- [ ] Test agent with new tools

### Phase 3: Testing
- [ ] Test storing preferences
- [ ] Test retrieving memories
- [ ] Test cross-session persistence
- [ ] Test multi-tool decision-making
- [ ] Test personalized recommendations

### Phase 4: Documentation
- [ ] Create test scripts (test_memory_tools.py)
- [ ] Document example conversations
- [ ] Create comparison with Stage 5
- [ ] Update README

---

## 10. Technical Considerations

### Tool Access to State

**Challenge:** Tools need access to `student_id` from state, but LangChain tools are stateless.

**Solution Options:**

**Option 1: Global State (Simple)**
```python
# In nodes.py
_current_student_id = None

def agent_node(state):
    global _current_student_id
    _current_student_id = state["student_id"]
    # ... rest of agent logic

# In tools.py
def search_memories_tool(query, limit):
    from .nodes import _current_student_id
    # Use _current_student_id
```

**Option 2: Closure (Cleaner)**
```python
# In tools.py
def create_memory_tools(student_id):
    @tool("search_memories")
    async def search_memories(query: str, limit: int = 5):
        # student_id is captured in closure
        results = await memory_client.search_long_term_memory(
            text=query,
            user_id=UserId(eq=student_id),
            limit=limit
        )
    
    return [search_memories, store_memory]

# In nodes.py
def agent_node(state):
    student_id = state["student_id"]
    memory_tools = create_memory_tools(student_id)
    llm = ChatOpenAI(...).bind_tools([search_courses_tool] + memory_tools)
```

**Recommendation:** Use Option 1 (global state) for consistency with existing Stage 5 pattern.

---

## 11. Success Criteria

Stage 6 is successful if:

✅ Agent can store student preferences when shared  
✅ Agent can retrieve memories to personalize recommendations  
✅ Memories persist across sessions  
✅ LLM correctly decides when to use each of 3 tools  
✅ Workflow structure remains unchanged from Stage 5  
✅ All Stage 5 functionality still works  
✅ Test scripts demonstrate memory capabilities  

---

## 12. Next Steps After Stage 6

Potential Stage 7 ideas:
- **Semantic tool selection** (routing between specialized tools)
- **Memory compression** (summarization strategies)
- **Multi-agent collaboration** (specialized sub-agents)
- **Semantic caching** (enable the commented-out cache nodes)

---

## Conclusion

Stage 6 is a **minimal, high-impact addition** that:
- Adds 2 new tools (search_memories, store_memory)
- Requires changes to only 2 files (tools.py, nodes.py)
- Maintains identical workflow structure
- Demonstrates agentic memory management
- Enables powerful personalization capabilities

This design follows the progressive learning philosophy: **incremental complexity, maximum educational value**.

