# Stage 3: Agentic Implementation Summary

## Overview

Stage 3 has been updated from a **scripted workflow** to an **agentic workflow** using LangChain tool calling. This demonstrates the transition from hardcoded retrieval operations (Section 2) to LLM-controlled tool usage (Section 4).

## Key Changes

### Before (Scripted Workflow)
- **8 nodes**: classify_intent → decompose_query → check_cache → research → evaluate_quality → synthesize
- **Hardcoded operations**: Every query goes through the same pipeline
- **No LLM decision-making**: Research node always calls search_courses_sync()
- **Fixed behavior**: Cannot skip or adapt the workflow

### After (Agentic Workflow)
- **3 nodes**: classify_intent → agent → END
- **LLM-controlled**: Agent decides when to search and what parameters to use
- **Tool calling**: LangChain tool with schema validation
- **Adaptive behavior**: LLM can skip search if not needed, or search multiple times

## Architecture

### Workflow Graph

```
START
  ↓
classify_intent
  ↓
  ├─ GREETING → handle_greeting → END
  └─ OTHER → agent → END
```

### Agent Node

The agent node replaces the entire scripted pipeline (decompose → cache → research → evaluate → synthesize) with a single LLM-driven node that:

1. **Receives the query** with system instructions
2. **Decides whether to use tools** (search_courses)
3. **Executes tool calls** if needed
4. **Synthesizes final answer** based on tool results

### Tool: search_courses

**Input Schema:**
- `query`: Search query
- `intent`: GENERAL, PREREQUISITES, SYLLABUS_OBJECTIVES, ASSIGNMENTS
- `search_strategy`: Accepted but ignored (Stage 3 always uses semantic search)
- `course_codes`: Accepted but ignored
- `information_type`: Accepted but ignored
- `departments`: Accepted but ignored
- `difficulty_level`: Accepted but ignored

**Implementation:**
- Calls `search_courses_sync(query, top_k=5, use_optimized_format=False, intent=intent)`
- Uses **hierarchical retrieval** with progressive disclosure
- Intent determines what details are included (summaries vs full details)

**Why accept unused parameters?**
- Maintains consistent tool interface across stages
- LLM can provide these parameters without errors
- Educational: shows that Stage 3 uses simpler retrieval than Stages 4/5

## Hierarchical Retrieval (Section 2 Technique)

Stage 3 demonstrates **Section 2: Retrieved Context Engineering** concepts:

### Two-Tier Retrieval

1. **Tier 1: Semantic Search**
   - Uses `course_manager.search_courses()` to find top-k courses
   - Returns basic Course objects

2. **Tier 2: Hierarchical Assembly**
   - Matches basic courses to hierarchical courses (summaries + details)
   - Assembles context based on intent

### Progressive Disclosure

**GENERAL Intent:**
- Returns summaries ONLY for all matches (~87 tokens per course)
- Provides broad awareness without overwhelming detail

**Other Intents (PREREQUISITES, SYLLABUS_OBJECTIVES, ASSIGNMENTS):**
- Returns summaries for ALL matches
- Returns FULL DETAILS for top 2-3 courses
- Details filtered by intent:
  - PREREQUISITES: ~881 tokens (summary + prerequisite details)
  - SYLLABUS_OBJECTIVES: ~950 tokens (summary + syllabus details)
  - ASSIGNMENTS: ~995 tokens (summary + assignment details)

## Test Results

### Test 1: Simple Questions (test_simple.py)

Tests 4 basic questions (one per intent):

| Intent | Question | Result |
|--------|----------|--------|
| GENERAL | "What is CS004?" | ✅ Pass |
| PREREQUISITES | "What are the prerequisites for CS004?" | ✅ Pass |
| SYLLABUS | "What's the syllabus for CS004?" | ✅ Pass |
| ASSIGNMENTS | "What are the assignments for CS004?" | ✅ Pass |

**Success Rate: 4/4 (100%)**

### Test 2: Topic-Based Queries (test_linear_algebra.py)

Tests semantic search with topic-based queries:

| Query | Result |
|-------|--------|
| "I am interested in linear algebra" | ✅ Pass |
| "What are the prerequisites for linear algebra?" | ✅ Pass |
| "What's the topics for linear algebra?" | ✅ Pass |
| "What are the assignments for linear algebra course?" | ✅ Pass |

**Success Rate: 4/4 (100%)**

All queries correctly use semantic search to find MATH028 (Linear Algebra for Machine Learning).

## Educational Value

### Stage 3 Purpose

Stage 3 demonstrates the **transition from scripted to agentic workflows**:

1. **Section 2 Technique**: Hierarchical retrieval with progressive disclosure
2. **Section 4 Technique**: LLM-controlled tool calling
3. **Hybrid Approach**: Uses Section 2 retrieval method, but with Section 4 control mechanism

### Learning Progression

| Stage | Section | Workflow | Retrieval | Memory |
|-------|---------|----------|-----------|--------|
| **Stage 3** | 2 + 4 | Agentic | Hierarchical (semantic only) | No |
| **Stage 4** | 4 | Agentic | Hybrid (exact + semantic + NER) | No |
| **Stage 5** | 3 + 4 | Agentic | Hybrid (exact + semantic + NER) | Yes |

### Key Insight

Stage 3 shows that you can:
- Use **simple retrieval** (semantic search only)
- With **agentic control** (LLM decides when/how to search)
- Before adding **advanced retrieval** (exact match, hybrid, NER)
- And before adding **memory** (working memory, long-term memory)

This creates a clean learning path:
1. **Stage 3**: Agentic workflow basics with simple retrieval
2. **Stage 4**: Add advanced retrieval strategies
3. **Stage 5**: Add working memory

## Implementation Details

### Files Modified

1. **tools.py**
   - Added `SearchCoursesInput` schema
   - Added `search_courses_tool` with LangChain `@tool` decorator
   - Tool accepts advanced parameters but only uses query + intent

2. **nodes.py**
   - Added `get_agent_llm()` to create LLM with tool binding
   - Added `agent_node()` to replace scripted pipeline
   - Agent handles tool calling and synthesis

3. **workflow.py**
   - Simplified from 8 nodes to 3 nodes
   - Removed: decompose_query, check_cache, research, evaluate_quality, synthesize
   - Kept: classify_intent, handle_greeting, agent (new)

### LLM Calls

**Before (Scripted):**
- classify_intent: 1 call
- decompose_query: 1 call
- evaluate_quality: 1 call
- synthesize: 1 call
- **Total: 4 LLM calls**

**After (Agentic):**
- classify_intent: 1 call
- agent (tool decision): 1 call
- agent (synthesis): 1 call
- **Total: 3 LLM calls**

The agentic approach is actually **more efficient** (fewer LLM calls) while being more flexible!

## Comparison with Other Stages

### Stage 3 vs Stage 4

| Feature | Stage 3 | Stage 4 |
|---------|---------|---------|
| **Workflow** | Agentic | Agentic |
| **Tool** | ✅ Same interface | ✅ Same interface |
| **Retrieval** | Semantic only | Hybrid (exact + semantic + NER) |
| **Entity Extraction** | ❌ No | ✅ Yes (NER) |
| **Search Strategies** | 1 (semantic) | 3 (exact, hybrid, semantic) |
| **Memory** | ❌ No | ❌ No |

### Stage 3 vs Stage 5

| Feature | Stage 3 | Stage 5 |
|---------|---------|---------|
| **Workflow** | Agentic | Agentic |
| **Tool** | ✅ Same interface | ✅ Same interface |
| **Retrieval** | Semantic only | Hybrid (exact + semantic + NER) |
| **Memory** | ❌ No | ✅ Yes (working memory) |
| **Multi-turn** | ❌ No | ✅ Yes |

## Conclusion

Stage 3 successfully demonstrates:
- ✅ Transition from scripted to agentic workflows
- ✅ LLM-controlled tool calling with LangChain
- ✅ Hierarchical retrieval with progressive disclosure (Section 2)
- ✅ Intent-based context adaptation
- ✅ Simplified workflow (3 nodes vs 8 nodes)
- ✅ 100% test pass rate

The agentic implementation is **simpler, more flexible, and more efficient** than the scripted version, while maintaining the same hierarchical retrieval capabilities!

