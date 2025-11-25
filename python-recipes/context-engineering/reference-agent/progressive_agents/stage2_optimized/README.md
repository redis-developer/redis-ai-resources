# Stage 2: Context-Engineered Agent

An optimized RAG implementation demonstrating context engineering techniques from Section 2 of the course.

## Overview

This stage applies **context engineering** to reduce token usage by ~50% while maintaining or improving answer quality:
- ✅ Context cleaning (remove unnecessary fields)
- ✅ Natural text transformation (JSON → readable text)
- ✅ Token optimization (~50% reduction)
- ✅ Better LLM comprehension
- ✅ Lower costs ($6.25 → $3.00 per 1K queries)

**Educational Purpose:** Students see the concrete impact of context engineering techniques and learn to make informed optimization decisions.

## Architecture

```
User Query → Semantic Search → Context Cleaning → Text Transformation → LLM → Answer
```

**Key Improvements over Stage 1:**
- **Context Cleaning:** Remove internal IDs, timestamps, enrollment data
- **Text Transformation:** Convert JSON to natural language format
- **Token Optimization:** ~50% fewer tokens (2,500 → 1,200)
- **Better Parsing:** Natural text easier for LLM to understand

## Files

- **`agent.py`** - ContextEngineeredAgent implementation
- **`context_utils.py`** - Context transformation and optimization utilities
- **`cli.py`** - Interactive command-line interface (primary interface)
- **`README.md`** - This file

## Quick Start

### Using the CLI (Recommended)

```bash
cd progressive_agents/stage2_optimized
python cli.py
```

**Example interaction:**
```
You: What machine learning courses are available?

Agent: Based on the available courses, here are the machine learning options:

1. CS-401: Machine Learning Fundamentals
   - 3 credits, Intermediate level
   - Covers supervised learning, neural networks, model evaluation
   
2. CS-501: Advanced Machine Learning
   - 4 credits, Advanced level
   - Prerequisites: CS-401
```

**Check metrics:**
```
You: metrics

📊 Metrics:
• Token count: 1,247
• Format: natural_text
• Optimization: standard
• Est. cost per 1K queries: $3.00
✅ ~50% fewer tokens than Stage 1!
```

**Compare with baseline:**
```
You: compare

Stage 1 vs Stage 2 Comparison:
┌─────────────────┬──────────────────────┬──────────────────────┬──────────────┐
│ Metric          │ Stage 1 (Baseline)   │ Stage 2 (Optimized)  │ Improvement  │
├─────────────────┼──────────────────────┼──────────────────────┼──────────────┤
│ Token Count     │ 2,487                │ 1,247                │ -1,240       │
│ Cost per Query  │ $0.0037              │ $0.0019              │ -50.1%       │
│ Format          │ Raw JSON             │ Natural Text         │ Better       │
└─────────────────┴──────────────────────┴──────────────────────┴──────────────┘
```

### Using the Python API

```python
import asyncio
from progressive_agents.stage2_optimized.agent import ContextEngineeredAgent

async def main():
    agent = ContextEngineeredAgent()
    
    # Ask a question
    response = await agent.chat("What database courses are available?")
    print(response)
    
    # Compare with baseline
    comparison = await agent.compare_with_baseline("database courses")
    print(f"Token reduction: {comparison['reduction_percentage']}")
    print(f"Tokens saved: {comparison['token_savings']:,}")

asyncio.run(main())
```

## Context Engineering Techniques

### 1. Context Cleaning

**Remove unnecessary fields:**

```python
# Stage 1 (Baseline) - Includes everything
{
  "id": "01JQWXYZ123ABC",           # ❌ Internal ID
  "created_at": "2024-01-15...",    # ❌ Timestamp
  "updated_at": "2024-01-20...",    # ❌ Timestamp
  "current_enrollment": 45,         # ❌ Often not relevant
  "max_enrollment": 50,             # ❌ Often not relevant
  "course_code": "CS-401",          # ✅ Keep
  "title": "Machine Learning",      # ✅ Keep
  "description": "...",             # ✅ Keep
}

# Stage 2 (Cleaned) - Only relevant fields
{
  "course_code": "CS-401",
  "title": "Machine Learning",
  "description": "...",
  "prerequisites": [...]
}
```

**Result:** ~20% token reduction

### 2. Text Transformation

**Convert JSON to natural language:**

```python
# Stage 1 (JSON format)
{
  "course_code": "CS-401",
  "title": "Machine Learning Fundamentals",
  "description": "Introduction to machine learning concepts",
  "credits": 3,
  "difficulty_level": "intermediate"
}

# Stage 2 (Natural text format)
CS-401: Machine Learning Fundamentals
Credits: 3
Level: intermediate
Description: Introduction to machine learning concepts
```

**Result:** ~30% token reduction + better LLM parsing

### 3. Optimization Levels

**Standard (Recommended):**
- Natural text format
- All relevant fields included
- ~50% token reduction
- Best balance of clarity and efficiency

**Aggressive:**
- Ultra-compact format
- Only essential information
- ~60% token reduction
- Use when token budget is very tight

```bash
# Use aggressive optimization
python cli.py --optimization aggressive
```

## Metrics Comparison

| Metric | Stage 1 | Stage 2 (Standard) | Stage 2 (Aggressive) |
|--------|---------|-------------------|---------------------|
| Token count (5 courses) | ~2,500 | ~1,200 | ~900 |
| Cost per 1K queries | $6.25 | $3.00 | $2.25 |
| Format | Raw JSON | Natural text | Compact text |
| LLM comprehension | Good | Better | Good |
| Readability | Low | High | Medium |

## Learning Objectives

After completing Stage 2, students should understand:

1. ✅ **Context cleaning** - Remove unnecessary fields to reduce tokens
2. ✅ **Text transformation** - Natural language is more efficient than JSON
3. ✅ **Optimization trade-offs** - Balance between clarity and token usage
4. ✅ **Measurement** - Always measure impact of optimizations
5. ✅ **Cost implications** - Token reduction = cost savings

## When to Use Each Optimization Level

### Use Standard (Natural Text):
- ✅ General-purpose Q&A
- ✅ When clarity is important
- ✅ When you need all course details
- ✅ **Recommended for most use cases**

### Use Aggressive (Compact):
- ✅ Very high query volume
- ✅ Tight token budgets
- ✅ Simple queries (course listings)
- ⚠️ May sacrifice some detail

### Use None (JSON):
- ✅ Prototyping / debugging
- ✅ When you need exact field names
- ⚠️ Not recommended for production

## Next Steps

**Stage 3: Hybrid RAG Agent**
- Add structured catalog views
- Implement multi-strategy retrieval
- Combine semantic search + metadata filtering
- Further reduce tokens to ~800

See `../stage3_hybrid/README.md` for details.

## Educational Notes

### Key Insights

1. **Context engineering is about trade-offs**
   - More optimization = fewer tokens but potentially less detail
   - The "best" approach depends on your use case
   - Always measure and compare

2. **Natural text > JSON for LLMs**
   - LLMs are trained on natural language, not JSON
   - Text format is more token-efficient
   - Better comprehension = better answers

3. **Small changes, big impact**
   - Removing 5 unnecessary fields = 20% token reduction
   - JSON → text transformation = 30% additional reduction
   - Combined: 50% total reduction

### Common Student Questions

**Q: Will removing fields hurt answer quality?**
A: Not if you remove the right fields! Internal IDs and timestamps don't help the LLM answer questions. Test and measure.

**Q: Should I always use aggressive optimization?**
A: No. Use standard for most cases. Aggressive is for specific scenarios with tight token budgets.

**Q: How do I know which fields to keep?**
A: Ask: "Does this field help answer user questions?" If no, remove it.

**Q: What about structured data that needs exact formats?**
A: For structured output, JSON is fine. For LLM input (context), natural text is better.

## References

- **Section 2 Notebooks:** Detailed context engineering techniques
- **`context_utils.py`:** Implementation of all transformation functions
- **Stage 1:** Baseline for comparison
- **Stage 3:** Next level of optimization

