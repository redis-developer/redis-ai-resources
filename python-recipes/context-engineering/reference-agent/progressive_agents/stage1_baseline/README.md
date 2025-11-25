# Stage 1: Baseline RAG Agent

A deliberately simple RAG implementation that demonstrates basic semantic search and retrieval without optimization.

## Overview

This stage shows the **naive approach** that many developers start with:
- ✅ Works correctly (retrieves relevant courses)
- ❌ Inefficient (uses 2-3x more tokens than necessary)
- ❌ Poor formatting (raw JSON harder for LLM to parse)
- ❌ No personalization (stateless, no memory)

**Educational Purpose:** Students see that basic RAG works but has clear room for improvement, setting the stage for optimization in Stage 2 and Stage 3.

## Architecture

```
User Query → Semantic Search → Raw JSON Context → LLM → Answer
```

**Key Characteristics:**
- **Retrieval:** Semantic search via RedisVL (5 courses by default)
- **Context Format:** Raw JSON with ALL fields (including internal IDs, timestamps)
- **Optimization:** None
- **Memory:** None (stateless)
- **Token Usage:** ~2,500 tokens for 5 courses

## Files

- **`agent.py`** - BaselineRAGAgent implementation
- **`cli.py`** - Interactive command-line interface
- **`notebook.ipynb`** - Step-by-step educational notebook
- **`README.md`** - This file

## Quick Start

### Using the CLI

```bash
cd progressive_agents/stage1_baseline
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
   - Deep learning, reinforcement learning, NLP
```

**Check metrics:**
```
You: metrics

📊 Metrics:
• Token count: 2,487
• Format: raw_json
• Optimization: none
⚠️  This is 2-3x higher than optimized formats!
```

### Using the Python API

```python
import asyncio
from progressive_agents.stage1_baseline.agent import BaselineRAGAgent

async def main():
    agent = BaselineRAGAgent()
    
    # Ask a question
    response = await agent.chat("What database courses are available?")
    print(response)
    
    # Check token usage
    courses = await agent.retrieve_courses("database courses")
    context = agent.format_context_as_json(courses)
    metrics = agent.get_metrics(context)
    print(f"Tokens used: {metrics['token_count']:,}")

asyncio.run(main())
```

## What's Wrong with This Approach?

### 1. **Inefficient Context Formatting**

**Raw JSON includes unnecessary fields:**
```json
{
  "id": "01JQWXYZ123ABC",           // ❌ Internal ID (not needed)
  "created_at": "2024-01-15...",    // ❌ Timestamp (not needed)
  "updated_at": "2024-01-20...",    // ❌ Timestamp (not needed)
  "current_enrollment": 45,         // ❌ May not be relevant
  "max_enrollment": 50,             // ❌ May not be relevant
  "course_code": "CS-401",          // ✅ Needed
  "title": "Machine Learning",      // ✅ Needed
  "description": "...",             // ✅ Needed
}
```

**Result:** ~40% of tokens are wasted on metadata.

### 2. **Poor Format for LLMs**

JSON is verbose and harder for LLMs to parse compared to natural text:

**JSON format (verbose):**
```json
{
  "course_code": "CS-401",
  "title": "Machine Learning Fundamentals",
  "description": "Introduction to machine learning concepts"
}
```

**Natural text format (concise):**
```
CS-401: Machine Learning Fundamentals
Introduction to machine learning concepts
```

**Result:** Natural text uses ~30% fewer tokens and is easier for LLMs to understand.

### 3. **No Context Optimization**

- No deduplication (repeated information across courses)
- No compression (verbose descriptions)
- No prioritization (all fields treated equally)

### 4. **No Personalization**

- Stateless (no memory of previous conversations)
- No user preferences
- No learning from interactions

## Metrics Comparison

| Metric | Stage 1 (Baseline) | Stage 2 (Optimized) | Stage 3 (Hybrid) |
|--------|-------------------|---------------------|------------------|
| Token count (5 courses) | ~2,500 | ~1,200 | ~800 |
| Cost per 1K queries | $6.25 | $3.00 | $2.00 |
| Context format | Raw JSON | Natural text | Structured views |
| Optimization | None | Cleaning + formatting | Multi-strategy |
| Memory | None | None | Working + LTM |

## Learning Objectives

After completing Stage 1, students should understand:

1. ✅ **Basic RAG works** - Semantic search + LLM generation is functional
2. ✅ **Token efficiency matters** - Raw formats waste tokens and money
3. ✅ **Context quality impacts results** - Better formatting = better answers
4. ✅ **There's room for improvement** - Sets motivation for Stage 2

## Next Steps

**Stage 2: Context-Engineered Agent**
- Apply context cleaning (remove unnecessary fields)
- Transform to natural text format
- Implement token optimization techniques
- Reduce token usage by ~50%

See `../stage2_optimized/README.md` for details.

## Educational Notes

### Why Start with a "Bad" Implementation?

Teaching context engineering by starting with an inefficient baseline helps students:

1. **Understand the problem** - See waste firsthand
2. **Appreciate optimization** - Measure concrete improvements
3. **Make informed decisions** - Know trade-offs of each technique
4. **Build confidence** - Progress from simple to complex

### Common Student Questions

**Q: Why use JSON if it's inefficient?**
A: Many developers default to JSON because it's familiar and "just works." This stage shows that "works" ≠ "optimal."

**Q: Is 2,500 tokens really that bad?**
A: For 1,000 queries/day with GPT-4:
- Stage 1: ~$6.25/day = $2,281/year
- Stage 2: ~$3.00/day = $1,095/year
- **Savings: $1,186/year** just from better formatting!

**Q: Should I always optimize context?**
A: It depends! Sometimes raw JSON is fine (prototyping, low volume). Context engineering is about making informed trade-offs, not blindly optimizing everything.

## References

- **Section 2 Notebooks:** Context transformation techniques
- **RedisVL Documentation:** Vector search and semantic retrieval
- **LangChain Documentation:** LLM integration patterns

