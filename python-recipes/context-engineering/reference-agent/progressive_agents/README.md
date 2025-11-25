# Progressive RAG Agents

A 3-stage learning system that teaches context engineering from basic RAG to production-ready patterns.

## Overview

This directory contains three progressively optimized RAG agents that demonstrate the evolution from naive to production-ready context engineering:

| Stage | Name | Token Usage | Cost/1K | Key Feature |
|-------|------|-------------|---------|-------------|
| **Stage 1** | Baseline RAG | ~2,500 | $6.25 | Raw JSON, no optimization |
| **Stage 2** | Context-Engineered | ~1,200 | $3.00 | Natural text, cleaning |
| **Stage 3** | Hybrid RAG | ~800 | $2.00 | Structured views, smart selection |

**Total Improvement:** 70% token reduction, 68% cost savings

## Educational Philosophy

### Why Progressive Learning?

Instead of showing a complete, production-ready agent all at once, we break it down into stages:

1. **Stage 1 (Baseline)** - Shows that basic RAG works but is inefficient
2. **Stage 2 (Optimized)** - Applies context engineering for 50% improvement
3. **Stage 3 (Hybrid)** - Adds production patterns for another 33% improvement

**Benefits:**
- ✅ Students see the **why** behind each optimization
- ✅ Clear **before/after** comparisons with metrics
- ✅ Builds confidence through **incremental complexity**
- ✅ Learn to make **informed trade-off decisions**

## Quick Start

### Prerequisites

1. **Redis 8** running locally or remotely
2. **OpenAI API key** configured
3. **Course data** ingested into Redis

```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export REDIS_URL="redis://localhost:6379"

# Generate and ingest course data (from reference-agent root)
cd ../..
generate-courses --courses-per-major 15 --output course_catalog.json
ingest-courses --catalog course_catalog.json --clear
```

### Try Each Stage

**Stage 1: Baseline RAG**
```bash
cd stage1_baseline
python cli.py
```

**Stage 2: Context-Engineered**
```bash
cd stage2_optimized
python cli.py
```

**Stage 3: Hybrid RAG**
```bash
cd stage3_hybrid
python cli.py
```

## Stage Details

### Stage 1: Baseline RAG

**Purpose:** Show that basic RAG works but has inefficiencies

**Architecture:**
```
User Query → Semantic Search → Raw JSON Context → LLM → Answer
```

**Characteristics:**
- ✅ Works correctly
- ❌ Inefficient (raw JSON with all fields)
- ❌ Poor formatting (JSON harder for LLM)
- ❌ No personalization (stateless)

**Metrics:**
- Token count: ~2,500 (5 courses)
- Cost per 1K queries: $6.25
- Format: Raw JSON

**Learn more:** [stage1_baseline/README.md](stage1_baseline/README.md)

---

### Stage 2: Context-Engineered

**Purpose:** Apply context engineering techniques for 50% improvement

**Architecture:**
```
User Query → Semantic Search → Context Cleaning → Text Transformation → LLM → Answer
```

**Improvements:**
- ✅ Context cleaning (remove unnecessary fields)
- ✅ Natural text transformation (JSON → text)
- ✅ Token optimization (~50% reduction)
- ✅ Better LLM comprehension

**Metrics:**
- Token count: ~1,200 (5 courses)
- Cost per 1K queries: $3.00
- Format: Natural text
- Reduction vs Stage 1: **-50%**

**Learn more:** [stage2_optimized/README.md](stage2_optimized/README.md)

---

### Stage 3: Hybrid RAG

**Purpose:** Production-ready patterns with structured views

**Architecture:**
```
User Query → Semantic Search + Catalog Retrieval
          → Smart View Selection → Hybrid Assembly → LLM → Answer
```

**Innovations:**
- ✅ Structured catalog views (hierarchical organization)
- ✅ Hybrid assembly (overview + details)
- ✅ Query-aware optimization (smart view selection)
- ✅ Multi-strategy retrieval
- ✅ Scalable to large catalogs

**Metrics:**
- Token count: ~800 (5 courses + catalog)
- Cost per 1K queries: $2.00
- Format: Hybrid views
- Reduction vs Stage 1: **-68%**
- Reduction vs Stage 2: **-33%**

**Learn more:** [stage3_hybrid/README.md](stage3_hybrid/README.md)

## Comparison

### Token Usage Progression

```
Stage 1: ████████████████████████████████████████ 2,500 tokens
Stage 2: ████████████████████ 1,200 tokens (-50%)
Stage 3: ████████████ 800 tokens (-68%)
```

### Cost Savings (per 1M queries)

| Stage | Cost | Savings vs Stage 1 |
|-------|------|-------------------|
| Stage 1 | $6,250 | — |
| Stage 2 | $3,000 | **-$3,250 (52%)** |
| Stage 3 | $2,000 | **-$4,250 (68%)** |

### When to Use Each Stage

**Use Stage 1 (Baseline) when:**
- Prototyping / debugging
- Need exact field names
- ⚠️ Not recommended for production

**Use Stage 2 (Optimized) when:**
- Small catalog (<50 items)
- Specific queries only
- Good balance of simplicity and efficiency

**Use Stage 3 (Hybrid) when:**
- Large catalog (50+ items)
- Diverse query types (browsing + specific)
- Production deployment
- Need scalability

## Learning Path

### Recommended Order

1. **Start with Stage 1**
   - Run the CLI and ask questions
   - Use `metrics` command to see token usage
   - Understand the baseline

2. **Move to Stage 2**
   - See the impact of context engineering
   - Use `compare` command to see improvements
   - Learn optimization techniques

3. **Finish with Stage 3**
   - Explore different query types
   - See smart view selection in action
   - Compare all three stages

### Key Learning Objectives

After completing all stages, students should understand:

1. ✅ **Basic RAG works** - But has room for improvement
2. ✅ **Context engineering matters** - 50-70% token reduction possible
3. ✅ **Trade-offs exist** - Balance clarity, efficiency, complexity
4. ✅ **Measurement is critical** - Always measure impact
5. ✅ **Production patterns** - Structured views, hybrid assembly, smart selection

## CLI Commands

All stages support these commands:

- **Ask questions** - Natural language queries about courses
- **`metrics`** - Show token usage for last query
- **`compare`** - Compare with other stages (Stage 2 & 3)
- **`help`** - Show available commands
- **`quit`** - Exit the CLI

### Example Session

```bash
$ python cli.py

You: What machine learning courses are available?
Agent: [Detailed response about ML courses]

You: metrics
📊 Metrics:
• Token count: 847
• Format: hybrid
• Views included: include_catalog

You: compare
[Shows comparison table across all stages]

You: quit
Goodbye! 👋
```

## Python API

All agents can also be used programmatically:

```python
import asyncio
from progressive_agents.stage3_hybrid.agent import HybridRAGAgent

async def main():
    agent = HybridRAGAgent()
    
    # Chat
    response = await agent.chat("What courses are available?")
    print(response)
    
    # Get metrics
    metrics = await agent.get_metrics("What courses are available?")
    print(f"Tokens: {metrics['token_count']:,}")
    
    # Compare stages
    comparison = await agent.compare_all_stages("machine learning")
    print(f"Stage 1: {comparison['stage1']['tokens']:,} tokens")
    print(f"Stage 3: {comparison['stage3']['tokens']:,} tokens")

asyncio.run(main())
```

## Architecture Diagrams

Each stage includes a Mermaid diagram showing the flow:

- **Stage 1:** Simple linear flow
- **Stage 2:** Added optimization steps
- **Stage 3:** Multi-strategy retrieval with smart selection

See individual README files for detailed diagrams.

## Next Steps

### Future Enhancements (Stage 4+)

The progressive agent system can be extended with:

1. **Memory Integration** (Section 3 patterns)
   - Working memory (conversation history)
   - Long-term memory (user preferences)
   - Memory-aware context selection

2. **Tool Calling** (Section 4 patterns)
   - Course search tools
   - Memory management tools
   - LangGraph integration

3. **Advanced Optimization** (Section 5 patterns)
   - Prompt caching
   - Batch processing
   - Streaming responses

## References

- **Section 2 Notebooks:** Context engineering techniques
- **Section 3 Notebooks:** Memory integration patterns
- **Section 4 Notebooks:** Tool calling and LangGraph
- **Original Agent:** See `../archive/original_agent/` for full-featured implementation

## Contributing

This is an educational resource. If you find issues or have suggestions:

1. Test all three stages
2. Document the issue with metrics
3. Propose improvements with trade-off analysis
4. Consider educational impact

## License

MIT License - See repository root for details.

