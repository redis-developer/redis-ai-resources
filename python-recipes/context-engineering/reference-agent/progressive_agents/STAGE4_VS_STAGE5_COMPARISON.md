# Stage 4 vs Stage 5: Agentic Workflow Comparison

## Overview

Both Stage 4 and Stage 5 now use the **same agentic workflow pattern** with a complex LLM-controlled tool. The **only difference** is working memory.

## Architecture Comparison

### Stage 4: Agentic Workflow (No Memory)

```
┌─────────────────┐
│ classify_intent │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  agent   │ ← LLM with tool calling
    └────┬─────┘
         │
       ┌─▼──┐
       │ END│
       └────┘
```

**Characteristics:**
- ✅ Agentic (LLM decides when/how to search)
- ❌ No memory (single-turn only)
- ✅ Simple workflow (2 nodes)
- ✅ Fast (no memory I/O)

### Stage 5: Agentic Workflow (With Memory)

```
┌──────────────┐
│ load_memory  │ ← Load conversation history
└──────┬───────┘
       │
┌──────▼───────┐
│classify_intent│
└──────┬───────┘
       │
  ┌────▼─────┐
  │  agent   │ ← LLM with tool calling + history
  └────┬─────┘
       │
┌──────▼───────┐
│ save_memory  │ ← Save conversation history
└──────┬───────┘
       │
     ┌─▼──┐
     │ END│
     └────┘
```

**Characteristics:**
- ✅ Agentic (LLM decides when/how to search)
- ✅ Memory (multi-turn conversations)
- ✅ Context across turns
- ⚠️ Slower (memory I/O overhead)

## Feature Comparison

| Feature | Stage 4 | Stage 5 |
|---------|---------|---------|
| **Workflow Type** | Agentic | Agentic |
| **Tool** | Complex (LLM-controlled) | Complex (LLM-controlled) |
| **Working Memory** | ❌ No | ✅ Yes (Redis Agent Memory Server) |
| **Multi-turn** | ❌ No | ✅ Yes |
| **Conversation History** | ❌ No | ✅ Yes (last 4 messages) |
| **Session Management** | ❌ No | ✅ Yes (session_id) |
| **Nodes** | 3 (classify, greeting, agent) | 5 (load, classify, greeting, agent, save) |
| **Use Case** | Simple Q&A | Interactive advisor |
| **Latency** | Lower | Higher (memory I/O) |
| **Complexity** | Lower | Higher |

## The Tool (Identical in Both Stages)

Both stages use the **exact same tool**:

```python
@tool("search_courses", args_schema=SearchCoursesInput)
async def search_courses_tool(
    query: str,
    intent: str = "GENERAL",
    search_strategy: str = "hybrid",
    course_codes: List[str] = [],
    information_type: List[str] = [],
    departments: List[str] = [],
    difficulty_level: Optional[str] = None,
) -> str:
```

**LLM Controls:**
1. **When** to search (decides if tool is needed)
2. **Intent** (GENERAL, PREREQUISITES, SYLLABUS_OBJECTIVES, ASSIGNMENTS)
3. **Strategy** (exact_match, hybrid, semantic_only)
4. **Entities** (course_codes, departments, information_type)
5. **Filters** (difficulty_level)

## Agent Node (Nearly Identical)

### Stage 4 Agent Node

```python
async def agent_node(state: WorkflowState) -> WorkflowState:
    # Build messages
    messages = []
    messages.append(HumanMessage(content=system_prompt))
    messages.append(HumanMessage(content=query))
    
    # LLM call with tool binding
    llm = get_agent_llm()
    response = await llm.ainvoke(messages)
    
    # Execute tools if requested
    if response.tool_calls:
        # Execute tools
        # Second LLM call to synthesize
    
    return state
```

**No conversation history** - just system prompt + current query

### Stage 5 Agent Node

```python
async def agent_node(state: WorkflowState) -> WorkflowState:
    # Build messages with conversation history
    messages = []
    
    # Add conversation history (last 4 messages)
    if conversation_history:
        for msg in conversation_history[-4:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
    
    messages.append(HumanMessage(content=system_prompt))
    messages.append(HumanMessage(content=query))
    
    # LLM call with tool binding
    llm = get_agent_llm()
    response = await llm.ainvoke(messages)
    
    # Execute tools if requested
    if response.tool_calls:
        # Execute tools
        # Second LLM call to synthesize
    
    return state
```

**With conversation history** - includes last 2 turns for context

## Example Interactions

### Stage 4 (No Memory)

```
User: What is CS004?
Agent: CS004 is Computer Vision, an advanced course...

User: What are the prerequisites?
Agent: [Searches for "prerequisites" - doesn't know you mean CS004]
```

**Problem:** No context from previous turn

### Stage 5 (With Memory)

```
User: What is CS004?
Agent: CS004 is Computer Vision, an advanced course...

User: What are the prerequisites?
Agent: [Remembers CS004 from previous turn]
       The prerequisites for CS004 are...
```

**Solution:** Context maintained across turns

## Test Results

### Stage 4 Test Results

**Course Code Queries:**
- ✅ "What is CS004?" → GENERAL, exact_match
- ✅ "Prerequisites for CS004?" → PREREQUISITES, exact_match
- ✅ "Syllabus for CS004?" → SYLLABUS_OBJECTIVES, exact_match
- ✅ "Assignments for CS004?" → ASSIGNMENTS, exact_match

**Topic Queries:**
- ✅ "I'm interested in linear algebra" → GENERAL, semantic_only
- ✅ "Prerequisites for linear algebra?" → PREREQUISITES, semantic_only
- ✅ "Topics for linear algebra?" → SYLLABUS_OBJECTIVES, semantic_only
- ✅ "Assignments for linear algebra?" → ASSIGNMENTS, semantic_only

**Result:** 8/8 passed (100%)

### Stage 5 Test Results

**Same as Stage 4, plus:**
- ✅ Multi-turn conversations work
- ✅ Follow-up questions use context
- ✅ Memory persists across turns

**Result:** All tests passed + multi-turn capability

## When to Use Each Stage

### Use Stage 4 When:
- ✅ Single-turn Q&A is sufficient
- ✅ No follow-up questions expected
- ✅ Lower latency is important
- ✅ Simpler architecture preferred
- ✅ No session management needed

**Examples:**
- FAQ bot
- Simple course lookup
- One-off queries
- Stateless API

### Use Stage 5 When:
- ✅ Multi-turn conversations needed
- ✅ Follow-up questions expected
- ✅ Context across turns important
- ✅ Interactive advisor experience
- ✅ Session management required

**Examples:**
- Course advisor chatbot
- Interactive tutoring
- Guided course selection
- Conversational interface

## Progressive Learning Path

### Section 3: Memory Systems (Scripted)
- Stage 5 original: Scripted workflow with working memory
- **Focus:** Memory operations (load/save)
- **Pattern:** Hardcoded function calls

### Section 4: Tool Calling (Agentic)
- **Stage 4 (NEW):** Agentic workflow without memory
  - **Focus:** Tool calling basics
  - **Pattern:** LLM decides when/how to use tools
  
- **Stage 5 (NEW):** Agentic workflow with memory
  - **Focus:** Combining tools + memory
  - **Pattern:** LLM + tools + conversation history

## Code Reuse

Both stages share:
- ✅ Same tool definition (`search_courses_tool`)
- ✅ Same tool schema (`SearchCoursesInput`)
- ✅ Same search function (`search_courses_sync`)
- ✅ Same progressive disclosure logic
- ✅ Same intent classification
- ✅ Same system prompt

**Only difference:**
- Stage 4: No memory nodes
- Stage 5: Add load_memory + save_memory nodes

## Migration Path

### From Stage 4 to Stage 5

To add memory to Stage 4:

1. **Add memory nodes:**
   ```python
   workflow.add_node("load_memory", load_working_memory_node)
   workflow.add_node("save_memory", save_working_memory_node)
   ```

2. **Update workflow:**
   ```python
   # Before
   workflow.set_entry_point("classify_intent")
   workflow.add_edge("agent", END)
   
   # After
   workflow.set_entry_point("load_memory")
   workflow.add_edge("load_memory", "classify_intent")
   workflow.add_edge("agent", "save_memory")
   workflow.add_edge("save_memory", END)
   ```

3. **Update agent node:**
   ```python
   # Add conversation history to messages
   if conversation_history:
       for msg in conversation_history[-4:]:
           messages.append(...)
   ```

4. **Add session management:**
   ```python
   # Pass session_id to workflow
   initial_state = {
       "session_id": session_id,
       "original_query": query,
       ...
   }
   ```

That's it! Same tool, same logic, just add memory.

## Conclusion

**Stage 4 and Stage 5 are now architecturally identical except for memory:**

- ✅ Both use agentic workflows
- ✅ Both use the same complex tool
- ✅ Both let LLM control search parameters
- ✅ Both support all intents and strategies
- ✅ Both use progressive disclosure

**The only difference:**
- Stage 4: No memory (single-turn)
- Stage 5: With memory (multi-turn)

This makes them perfect for teaching the progression from simple agentic workflows to memory-augmented agentic workflows!

