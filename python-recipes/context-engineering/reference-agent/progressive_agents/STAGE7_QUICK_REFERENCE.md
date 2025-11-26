# Stage 7: ReAct Loop - Quick Reference

## What's New in Stage 7

**Stage 7 implements the ReAct (Reasoning + Acting) pattern** with explicit reasoning traces.

### Key Difference from Stage 6

| Feature | Stage 6 (Iterative) | Stage 7 (ReAct) |
|---------|---------------------|-----------------|
| **Reasoning** | Implicit (inside LLM) | Explicit (Thought → Action → Observation) |
| **Pattern** | Tool calling loop | ReAct loop with reasoning traces |
| **Observability** | Tool calls only | Full reasoning trace visible |
| **Prompt** | Tool descriptions | ReAct format instructions |
| **LLM Output** | Structured tool calls | Text with Thought/Action/Observation |
| **Token Usage** | Lower | Higher (~50% more) |
| **Educational Value** | Good for production | Excellent for learning/debugging |

## ReAct Pattern

```
Loop:
  LLM → "Thought: I need to find the user's preferences first"
       → "Action: search_memories"
       → "Action Input: {...}"
  Execute tool
  LLM → "Observation: User prefers online ML courses"
       → "Thought: Now I should search for ML courses"
       → "Action: search_courses"
       → "Action Input: {...}"
  Execute tool
  LLM → "Observation: Found 5 ML courses"
       → "Thought: I have enough info to answer"
       → "Action: FINISH"
       → "Action Input: Here are your courses..."
```

## Files Added/Modified

### New Files
- `agent/react_agent.py` - ReAct agent node implementation
- `agent/react_parser.py` - Parse Thought/Action/Observation from LLM output
- `agent/react_prompts.py` - ReAct system prompt with examples
- `test_react_simple.py` - Test suite for ReAct functionality
- `STAGE7_QUICK_REFERENCE.md` - This file

### Modified Files
- `agent/state.py` - Added `reasoning_trace` and `react_iterations` fields
- `agent/nodes.py` - Imports `react_agent_node` and aliases it as `agent_node`
- `cli.py` - Updated to `ReActCLI` with `--show-reasoning` flag

## Running Stage 7

### Interactive Mode
```bash
cd progressive_agents/stage7_react_loop
python cli.py --student-id alice
```

### With Reasoning Traces
```bash
python cli.py --student-id alice --show-reasoning
```

### Single Query
```bash
python cli.py --student-id alice "What courses would you recommend for me?"
```

### Run Tests
```bash
cd /path/to/reference-agent
python -m progressive_agents.stage7_react_loop.test_react_simple
```

## Example Output

### Without --show-reasoning
```
📝 Answer:
--------------------------------------------------------------------------------
Based on your interest in machine learning and preference for online courses,
I recommend CS002 (Machine Learning Fundamentals) and CS003 (Deep Learning).
Both are available online.
--------------------------------------------------------------------------------

📊 Performance:
   Total Time: 4757.98ms
   ReAct Iterations: 3
   Reasoning Steps: 6
```

### With --show-reasoning
```
🧠 Reasoning Trace:
================================================================================
💭 Thought: I should check if I have any stored preferences for this user...

🔧 Action: search_memories
   Input: {'query': 'course preferences and interests', 'limit': 5}
👁️  Observation: 1. User prefers online courses
   Topics: preferences
2. User is interested in machine learning...

💭 Thought: I know the user is interested in ML and prefers online courses...

🔧 Action: search_courses
   Input: {'query': 'machine learning', 'intent': 'GENERAL', 'search_strategy': 'hybrid'}
👁️  Observation: # Course Search Results for: machine learning

Found 5 relevant courses:
### 1. CS002: Machine Learning...

💭 Thought: I have found several courses. I will provide recommendations...

✅ FINISH
================================================================================
```

## Key Components

### 1. ReAct Parser (`agent/react_parser.py`)

Parses LLM output into structured format:

```python
parsed = parse_react_output(llm_response)
# Returns: {
#   "thought": "I should search for user preferences",
#   "action": "search_memories",
#   "action_input": '{"query": "preferences", "limit": 5}'
# }
```

### 2. ReAct Prompts (`agent/react_prompts.py`)

Defines the ReAct format with examples:

```python
REACT_SYSTEM_PROMPT = """
You must respond in this format:

Thought: [your reasoning about what to do next]
Action: [tool name or FINISH]
Action Input: [JSON parameters for the tool]

After each action, you will receive:
Observation: [result from the tool]

Then continue with another Thought/Action cycle until you're ready to finish.
"""
```

### 3. ReAct Agent Node (`agent/react_agent.py`)

Main loop implementation:

```python
async def react_agent_node(state: WorkflowState) -> WorkflowState:
    while iteration < max_iterations:
        # Call LLM (no tool binding - text generation)
        response = await llm.ainvoke(messages)
        
        # Parse ReAct output
        parsed = parse_react_output(response.content)
        
        # Log thought
        if parsed["thought"]:
            reasoning_trace.append({"type": "thought", "content": parsed["thought"]})
        
        # Check if FINISH
        if parsed["action"] == "FINISH":
            final_answer = extract_final_answer(parsed["action_input"])
            break
        
        # Execute tool
        tool_result = await execute_react_tool(parsed["action"], parsed["action_input"])
        
        # Add observation to messages
        messages.append(AIMessage(content=response.content))
        messages.append(HumanMessage(content=f"\nObservation: {tool_result}\n"))
```

## Test Results

### Test 1: Simple Course Search
- **Query**: "What is CS004?"
- **Iterations**: 2
- **Reasoning Steps**: 4
- **Actions**: search_courses → FINISH
- **Result**: ✅ Correctly identified CS004 as Computer Vision

### Test 2: Memory Storage
- **Query**: "I'm interested in machine learning and prefer online courses."
- **Iterations**: 4
- **Reasoning Steps**: 8
- **Actions**: store_memory → store_memory → search_courses → FINISH
- **Result**: ✅ Stored both preferences and searched for ML courses

### Test 3: Memory Retrieval
- **Query**: "What courses would you recommend for me?"
- **Iterations**: 3
- **Reasoning Steps**: 6
- **Actions**: search_memories → search_courses → FINISH
- **Result**: ✅ Retrieved preferences and provided personalized recommendations

## Performance Comparison

| Metric | Stage 6 (Iterative) | Stage 7 (ReAct) |
|--------|---------------------|-----------------|
| Simple query latency | ~2.5s | ~3.3s (+32%) |
| Multi-step latency | ~5.0s | ~6.9s (+38%) |
| Token usage | Baseline | +50% (reasoning text) |
| Observability | Tool calls | Full reasoning trace |
| Debugging ease | Moderate | Excellent |

## When to Use Stage 7

### Use ReAct (Stage 7) when:
- **Learning/Education**: Teaching how agents reason
- **Debugging**: Need to see why agent made decisions
- **Transparency**: Users need to understand agent's thinking
- **Complex reasoning**: Multi-step problems benefit from explicit reasoning

### Use Iterative (Stage 6) when:
- **Production**: Lower latency and token costs matter
- **Simple tasks**: Reasoning overhead not needed
- **High volume**: Token costs add up
- **API limits**: Fewer tokens per request

## Educational Value

Stage 7 is **excellent for teaching** because:

1. **Visible reasoning**: Students see how the agent thinks
2. **Step-by-step**: Clear progression from thought to action
3. **Debugging**: Easy to identify where reasoning goes wrong
4. **Comparison**: Can compare with Stage 6 to understand trade-offs

## Next Steps

Potential Stage 8 enhancements:
- **Planning**: Multi-step planning before execution
- **Self-correction**: Agent can revise its reasoning
- **Reflection**: Agent evaluates its own performance
- **Chain-of-Thought**: More sophisticated reasoning patterns
- **Tool composition**: Combining multiple tools in one step

