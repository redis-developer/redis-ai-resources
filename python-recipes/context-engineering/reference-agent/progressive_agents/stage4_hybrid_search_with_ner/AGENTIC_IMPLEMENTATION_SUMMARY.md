# Stage 4 Agentic Implementation Summary

## Overview

Stage 4 has been updated from a **scripted workflow** to an **agentic workflow** using **Approach 1: Complex Tool with Full LLM Control** (same as Stage 5, but without working memory).

## Architecture Change

### Before (Scripted)
```
classify_intent → extract_entities → decompose_query → check_cache
    → research → evaluate_quality → synthesize
```
- Hardcoded function calls
- LLM just processes data
- No decision-making

### After (Agentic)
```
classify_intent → agent
```
- LLM decides when to search
- LLM determines all parameters
- Full agentic behavior
- **No working memory** (unlike Stage 5)

## Key Differences from Stage 5

| Feature | Stage 4 | Stage 5 |
|---------|---------|---------|
| **Working Memory** | ❌ No | ✅ Yes (Redis Agent Memory Server) |
| **Workflow** | classify_intent → agent | load_memory → classify_intent → agent → save_memory |
| **Multi-turn** | ❌ Single-turn only | ✅ Multi-turn conversations |
| **Tool** | ✅ Same complex tool | ✅ Same complex tool |
| **Agentic** | ✅ Yes | ✅ Yes |

## Test Results

### ✅ Course Code Queries (Exact Match)

All 4 tests passed with `exact_match` strategy:

| Query | Intent | Strategy | Result |
|-------|--------|----------|--------|
| "What is CS004?" | GENERAL | exact_match | ✅ Summary only (~87 tokens) |
| "Prerequisites for CS004?" | PREREQUISITES | exact_match | ✅ Prerequisite details (~881 tokens) |
| "Syllabus for CS004?" | SYLLABUS_OBJECTIVES | exact_match | ✅ Syllabus details (~950 tokens) |
| "Assignments for CS004?" | ASSIGNMENTS | exact_match | ✅ Assignment details (~995 tokens) |

**Key Insight:** LLM correctly uses `exact_match` for course codes (no vector search).

### ✅ Topic Queries (Vector Search)

All 4 tests passed with `semantic_only` strategy:

| Query | Intent | Strategy | Courses Found |
|-------|--------|----------|---------------|
| "I'm interested in linear algebra" | GENERAL | semantic_only | MATH030, MATH029, MATH028 |
| "Prerequisites for linear algebra?" | PREREQUISITES | semantic_only | 3 courses with prerequisites |
| "Topics for linear algebra?" | SYLLABUS_OBJECTIVES | semantic_only | MATH028 syllabus (14 weeks) |
| "Assignments for linear algebra?" | ASSIGNMENTS | semantic_only | MATH028 assignments (10 total) |

**Key Insight:** LLM correctly uses `semantic_only` for topics (vector search to find relevant courses).

## Implementation Details

### 1. The Tool (`agent/tools.py`)

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
- When to search
- Intent (GENERAL, PREREQUISITES, SYLLABUS_OBJECTIVES, ASSIGNMENTS)
- Search strategy (exact_match, hybrid, semantic_only)
- Entities (course_codes, departments, information_type)
- Filters (difficulty_level)

### 2. Agent Node (`agent/nodes.py`)

```python
async def agent_node(state: WorkflowState) -> WorkflowState:
    """
    Agent node that uses LLM with tool calling to answer questions.
    
    Replaces: research → evaluate → synthesize pipeline
    With: LLM decides when/how to search + synthesizes answer
    """
```

**Process:**
1. Build system prompt with tool usage instructions
2. Add user query
3. LLM call #1: Decide if/how to use tool
4. Execute tool calls (if any)
5. LLM call #2: Synthesize final answer

### 3. Simplified Workflow (`agent/workflow.py`)

```python
# Add nodes
workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("handle_greeting", handle_greeting_node)
workflow.add_node("agent", agent_node)

# Routing
def route_after_intent(state: WorkflowState) -> str:
    intent = state.get("query_intent", "GENERAL")
    if intent == "GREETING":
        return "handle_greeting"
    else:
        return "agent"
```

**Flow:**
- Greetings → handle_greeting → END
- Questions → agent → END

## Progressive Disclosure

Same as Stage 5:

### Tier 1: Summaries (Always)
- ~87 tokens per course
- Basic info: code, title, department, instructor, credits, level, format, description

### Tier 2: Filtered Details (Intent-Based)
- **GENERAL**: No details (summary only)
- **PREREQUISITES**: Summary + prerequisites (~881 tokens)
- **SYLLABUS_OBJECTIVES**: Summary + syllabus + objectives (~950 tokens)
- **ASSIGNMENTS**: Summary + assignments (~995 tokens)

## Search Strategies

### Exact Match (Course Codes)
```
Query: "What is CS004?"
→ LLM chooses: exact_match
→ Direct lookup: course_details:CS004
→ No vector search
```

### Semantic Only (Topics)
```
Query: "I'm interested in linear algebra"
→ LLM chooses: semantic_only
→ Vector search in course_summaries index
→ Finds: MATH030, MATH029, MATH028
```

### Hybrid (Best of Both)
```
Query: "Show me machine learning courses"
→ LLM chooses: hybrid
→ Exact match + semantic search + metadata filters
→ Comprehensive results
```

## System Prompt

The agent receives detailed instructions on how to use the tool:

```
You are a helpful course advisor assistant.

When using the search_courses tool, you need to determine:

1. **intent**: What type of information does the user want?
   - "GENERAL": Just course summaries/overviews
   - "PREREQUISITES": Detailed prerequisite information
   - "SYLLABUS_OBJECTIVES": Syllabus and learning objectives
   - "ASSIGNMENTS": Assignment details

2. **search_strategy**: How should we search?
   - "exact_match": When user mentions specific course codes
   - "hybrid": Combine exact matching + semantic search
   - "semantic_only": Pure semantic search (no specific codes)

3. **course_codes**: Extract any specific course codes mentioned

4. **information_type**: What specific info is needed?

5. **departments**: Filter by department if mentioned

Examples:
- "What is CS004?" → intent="GENERAL", search_strategy="exact_match", course_codes=["CS004"]
- "Prerequisites for CS004?" → intent="PREREQUISITES", search_strategy="exact_match", course_codes=["CS004"]
- "Show me ML courses" → intent="GENERAL", search_strategy="hybrid", query="machine learning"
```

## Advantages

### ✅ Simplicity
- 2 nodes instead of 8 (classify_intent + agent)
- No complex routing logic
- Clean workflow

### ✅ Flexibility
- LLM adapts to any query pattern
- No hardcoded entity extraction
- Handles new query types automatically

### ✅ Intelligence
- LLM understands context and intent
- Correctly distinguishes course codes from topics
- Chooses appropriate search strategy

### ✅ Educational Value
- Demonstrates scripted → agentic transition
- Shows how to design complex tools
- Illustrates LLM decision-making

## Comparison: Stage 4 vs Stage 5

### Stage 4 (No Memory)
```python
# Single-turn only
workflow = classify_intent → agent → END

# No conversation history
# Each query is independent
```

**Use Case:** Simple Q&A, no context needed

### Stage 5 (With Memory)
```python
# Multi-turn conversations
workflow = load_memory → classify_intent → agent → save_memory → END

# Conversation history maintained
# Context across turns
```

**Use Case:** Interactive course advisor, follow-up questions

## Test Scripts

### `test_simple.py`
Tests 4 basic questions (one per intent):
- GENERAL: "What is CS004?"
- PREREQUISITES: "What are the prerequisites for CS004?"
- SYLLABUS: "What's the syllabus for CS004?"
- ASSIGNMENTS: "What are the assignments for CS004?"

**Result:** 4/4 passed ✅

### `test_linear_algebra.py`
Tests topic-based queries:
- "I am interested in linear algebra"
- "What are the prerequisites for linear algebra?"
- "What's the topics for linear algebra?"
- "What are the assignments for linear algebra course?"

**Result:** All queries correctly use `semantic_only` strategy ✅

## Conclusion

**Stage 4 successfully demonstrates the agentic workflow pattern!**

Key achievements:
- ✅ LLM controls all search parameters
- ✅ Correctly chooses search strategies
- ✅ Accurately extracts entities
- ✅ Intent-based filtering works
- ✅ Progressive disclosure optimizes tokens
- ✅ Vector search for topics
- ✅ Exact match for course codes
- ✅ Simplified workflow (2 nodes vs 8)

**Next Step:** Stage 5 adds working memory for multi-turn conversations!

