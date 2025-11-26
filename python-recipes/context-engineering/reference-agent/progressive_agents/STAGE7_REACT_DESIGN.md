# Stage 7: ReAct (Reasoning + Acting) Loop

## Executive Summary

**Stage 7** implements a **true ReAct loop** where the agent explicitly outputs its reasoning before each action, following the **Thought → Action → Observation** pattern.

**Key Difference from Stage 6:**
- **Stage 6**: Iterative tool calling (implicit reasoning)
- **Stage 7**: ReAct loop (explicit reasoning traces)

---

## What is ReAct?

**ReAct** = **Rea**soning + **Act**ing

A prompting pattern where the LLM:
1. **Thinks** about what to do next (explicit reasoning)
2. **Acts** by calling a tool or providing final answer
3. **Observes** the result
4. Repeats until task is complete

### ReAct Pattern

```
User: "What ML courses would you recommend for me?"

Thought: I should first check if I have any stored preferences for this user.
Action: search_memories
Action Input: {"query": "course preferences and interests", "limit": 5}
Observation: Found 2 memories: "User is interested in machine learning", "User prefers online courses"

Thought: Now I know the user's preferences. I should search for ML courses that are available online.
Action: search_courses
Action Input: {"query": "machine learning", "intent": "GENERAL", "search_strategy": "hybrid"}
Observation: Found 5 courses: CS101, CS102, CS103, CS104, CS105

Thought: I have enough information to provide a personalized recommendation.
Final Answer: Based on your interest in machine learning and preference for online courses, 
I recommend: CS101 (Introduction to ML), CS102 (Deep Learning Fundamentals)...
```

---

## Stage 6 vs Stage 7 Comparison

| Feature | Stage 6 (Iterative) | Stage 7 (ReAct) |
|---------|---------------------|-----------------|
| **Reasoning** | Implicit (inside LLM) | Explicit (in output) |
| **Pattern** | Tool calling loop | Thought → Action → Observation |
| **Observability** | Tool calls only | Full reasoning trace |
| **Debugging** | Moderate | Excellent |
| **Educational Value** | Tool iteration | Reasoning transparency |
| **Token Usage** | Lower | Higher (reasoning text) |
| **Complexity** | Simple | Moderate (prompt engineering) |
| **LLM Calls** | 2-4 per query | 3-6 per query |

---

## Implementation Approach

### 1. ReAct Prompt Template

```python
REACT_SYSTEM_PROMPT = """You are a helpful Redis University course advisor assistant.

You have access to THREE tools:
1. search_courses - Search the course catalog
2. search_memories - Search student's long-term memory
3. store_memory - Store information to long-term memory

Use the following format:

Thought: [Your reasoning about what to do next]
Action: [One of: search_courses, search_memories, store_memory, or FINISH]
Action Input: [JSON input for the action]

You will receive:
Observation: [Result of the action]

Repeat Thought/Action/Observation as needed.

When you have enough information, use:
Thought: I have enough information to answer
Action: FINISH
Action Input: [Your final answer to the user]

IMPORTANT:
- Always start with a Thought
- Only use one Action per turn
- Action Input must be valid JSON
- Use search_memories FIRST if the query might benefit from knowing preferences
- Use store_memory when users share preferences, goals, or constraints
- Use FINISH when ready to provide final answer

Example:
Thought: I should check if the user has any stored preferences.
Action: search_memories
Action Input: {"query": "preferences", "limit": 5}
"""
```

### 2. ReAct Parser

Parse LLM output to extract Thought, Action, and Action Input:

```python
def parse_react_output(text: str) -> dict:
    """Parse ReAct format output."""
    thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|\Z)", text, re.DOTALL)
    action_match = re.search(r"Action:\s*(\w+)", text)
    action_input_match = re.search(r"Action Input:\s*({.+?}|\[.+?\])", text, re.DOTALL)
    
    return {
        "thought": thought_match.group(1).strip() if thought_match else None,
        "action": action_match.group(1).strip() if action_match else None,
        "action_input": action_input_match.group(1).strip() if action_input_match else None,
    }
```

### 3. ReAct Agent Node

```python
async def react_agent_node(state: WorkflowState) -> WorkflowState:
    """ReAct agent with explicit reasoning."""
    messages = [SystemMessage(content=REACT_SYSTEM_PROMPT)]
    messages.append(HumanMessage(content=state["query"]))
    
    max_iterations = 10
    iteration = 0
    reasoning_trace = []
    
    while iteration < max_iterations:
        iteration += 1
        
        # Call LLM
        response = await llm.ainvoke(messages)
        
        # Parse ReAct output
        parsed = parse_react_output(response.content)
        
        # Log reasoning
        if parsed["thought"]:
            logger.info(f"💭 Thought: {parsed['thought']}")
            reasoning_trace.append({"type": "thought", "content": parsed["thought"]})
        
        # Check action
        action = parsed["action"]
        
        if action == "FINISH":
            # Extract final answer
            final_answer = parsed["action_input"]
            break
        
        # Execute tool
        logger.info(f"🔧 Action: {action}")
        logger.info(f"📝 Action Input: {parsed['action_input']}")
        
        tool_result = await execute_tool(action, parsed["action_input"])
        
        logger.info(f"👁️ Observation: {tool_result[:100]}...")
        reasoning_trace.append({
            "type": "action",
            "action": action,
            "input": parsed["action_input"],
            "observation": tool_result
        })
        
        # Add observation to messages
        messages.append(AIMessage(content=response.content))
        messages.append(HumanMessage(content=f"Observation: {tool_result}"))
    
    state["final_response"] = final_answer
    state["reasoning_trace"] = reasoning_trace
    return state
```

---

## File Changes from Stage 6

### New Files

1. **`agent/react_parser.py`** (~100 lines)
   - `parse_react_output()` - Parse Thought/Action/Observation
   - `format_observation()` - Format tool results
   - `validate_action_input()` - Validate JSON inputs

2. **`agent/react_prompts.py`** (~150 lines)
   - `REACT_SYSTEM_PROMPT` - Main ReAct prompt
   - `REACT_EXAMPLES` - Few-shot examples
   - `format_react_prompt()` - Dynamic prompt generation

### Modified Files

1. **`agent/nodes.py`** (~100 lines changed)
   - Replace `agent_node()` with `react_agent_node()`
   - Add ReAct parsing logic
   - Add reasoning trace logging
   - Add FINISH action handling

2. **`agent/state.py`** (~10 lines added)
   - Add `reasoning_trace: List[dict]` to WorkflowState
   - Add `react_iterations: int` to track loop count

3. **`cli.py`** (~20 lines changed)
   - Add `--show-reasoning` flag to display reasoning traces
   - Update output formatting for ReAct

---

## Example Conversation Flow

### Session 1: Store Preferences

```
User: "I'm interested in machine learning and I prefer online courses."

💭 Thought: The user is sharing their interests and preferences. I should store these 
   for future personalization.
🔧 Action: store_memory
📝 Action Input: {"text": "User is interested in machine learning", "topics": ["interests"]}
👁️ Observation: ✅ Memory stored successfully

💭 Thought: I should also store the format preference.
🔧 Action: store_memory
📝 Action Input: {"text": "User prefers online courses", "topics": ["preferences"]}
👁️ Observation: ✅ Memory stored successfully

💭 Thought: Now I should search for ML courses to show the user what's available.
🔧 Action: search_courses
📝 Action Input: {"query": "machine learning", "intent": "GENERAL", "search_strategy": "hybrid"}
👁️ Observation: Found 5 courses: CS101, CS102, CS103, CS104, CS105

💭 Thought: I have stored the preferences and found relevant courses. I can now provide 
   a helpful response.
🔧 Action: FINISH
📝 Final Answer: I've noted your interest in machine learning and preference for online 
   courses! Here are some ML courses available online: [course list]
```

### Session 2: Personalized Recommendations

```
User: "What courses would you recommend for me?"

💭 Thought: I should check if I have any stored preferences for this user to personalize 
   my recommendations.
🔧 Action: search_memories
📝 Action Input: {"query": "course preferences and interests", "limit": 5}
👁️ Observation: Found 2 memories: "User is interested in machine learning", 
   "User prefers online courses"

💭 Thought: Great! I know the user is interested in ML and prefers online format. 
   Let me search for ML courses.
🔧 Action: search_courses
📝 Action Input: {"query": "machine learning", "intent": "GENERAL", "search_strategy": "hybrid"}
👁️ Observation: Found 5 courses: CS101, CS102, CS103, CS104, CS105

💭 Thought: I have enough information to provide personalized recommendations.
🔧 Action: FINISH
📝 Final Answer: Based on your interest in machine learning and preference for online 
   courses, I recommend: CS101 (Introduction to ML), CS102 (Deep Learning)...
```

---

## Educational Value

### What Students Learn from Stage 7

1. **ReAct Pattern**
   - Thought → Action → Observation loop
   - Explicit reasoning vs implicit reasoning
   - When to use ReAct vs simple tool calling

2. **Prompt Engineering**
   - Structured output formats
   - Few-shot examples
   - Constraining LLM behavior

3. **Parsing & Validation**
   - Regex-based parsing
   - JSON validation
   - Error handling for malformed outputs

4. **Observability**
   - Reasoning trace logging
   - Debugging agent decisions
   - Understanding agent behavior

5. **Trade-offs**
   - Transparency vs efficiency
   - Token usage vs interpretability
   - Complexity vs simplicity

---

## Testing Strategy

### Test Suite: `test_react_loop.py`

1. **Test 1: Single Action**
   - Query: "What is CS004?"
   - Expected: 1 Thought → 1 Action (search_courses) → FINISH

2. **Test 2: Multi-Action Sequence**
   - Query: "I prefer online courses. Show me ML courses."
   - Expected: store_memory → search_courses → FINISH

3. **Test 3: Memory Retrieval**
   - Session 1: Store preferences
   - Session 2: "What would you recommend?"
   - Expected: search_memories → search_courses → FINISH

4. **Test 4: Reasoning Trace Validation**
   - Verify all thoughts are logged
   - Verify all actions are logged
   - Verify observations are captured

---

## Performance Comparison

### Stage 6 (Iterative) vs Stage 7 (ReAct)

**Simple Query: "What is CS004?"**

| Metric | Stage 6 | Stage 7 |
|--------|---------|---------|
| LLM Calls | 2 | 3 |
| Tokens | ~500 | ~800 |
| Latency | 1.5s | 2.0s |
| Reasoning Visible | ❌ | ✅ |

**Complex Query: "Recommend courses for me" (with stored preferences)**

| Metric | Stage 6 | Stage 7 |
|--------|---------|---------|
| LLM Calls | 3 | 5 |
| Tokens | ~1200 | ~2000 |
| Latency | 3.0s | 4.5s |
| Reasoning Visible | ❌ | ✅ |

**Trade-off:** Stage 7 uses ~50% more tokens and is ~30% slower, but provides full reasoning transparency.

---

## Next Steps After Implementation

1. **Test ReAct loop** with all test cases
2. **Compare performance** with Stage 6
3. **Document reasoning traces** for educational purposes
4. **Create visualization** of Thought → Action → Observation flow
5. **Update progressive agents README** with Stage 7

---

## References

- [ReAct Paper](https://arxiv.org/abs/2210.03629) - Original research
- [LangChain ReAct Agent](https://python.langchain.com/docs/modules/agents/agent_types/react) - Implementation guide
- [Anthropic's Guide to Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) - Best practices

