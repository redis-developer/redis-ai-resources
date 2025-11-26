# Section 2: Retrieved Context Engineering

## Overview

This section teaches you to build production-ready RAG (Retrieval-Augmented Generation) systems and engineer high-quality context for LLMs. You'll learn both the fundamentals of RAG and the engineering discipline required to make it production-ready.

**What You'll Build:**
- Complete RAG pipeline with Redis vector store
- Production-ready context engineering workflows
- Systematic quality optimization processes

**Time to Complete:** 135-155 minutes (2.25-2.5 hours)

---

## Learning Objectives

By the end of this section, you will be able to:

1. **Build RAG Systems**
   - Understand vector embeddings and semantic search
   - Implement complete RAG pipeline (Retrieve → Assemble → Generate)
   - Use Redis vector store for production-scale retrieval
   - Combine multiple context types (System + User + Retrieved)

2. **Engineer Context for Production**
   - Apply data engineering discipline to context preparation
   - Transform raw data through systematic pipeline (Extract → Clean → Transform → Optimize → Store)
   - Choose appropriate engineering approaches (RAG, Structured Views, Hybrid)
   - Implement chunking strategies with LangChain

3. **Optimize Context Quality**
   - Define domain-specific quality metrics
   - Measure context quality systematically
   - Optimize through experimentation (Baseline → Experiment → Measure → Iterate)
   - Build production-ready context pipelines

---

## Prerequisites

- Completed Section 1 (Context Engineering Foundations)
- Redis 8 running locally
- OpenAI API key configured
- Python 3.10+ with dependencies installed

---

## Notebooks

### 01_rag_fundamentals_and_implementation.ipynb

**Time:** 45-50 minutes

**What You'll Learn:**
- Why RAG matters for context engineering
- Vector embeddings fundamentals
- Building your first RAG system with Redis
- Why context quality matters (preview)

**Key Topics:**
- Part 1: Why RAG Matters
- Part 2: Vector Embeddings Fundamentals
- Part 3: Building Your First RAG System
- Part 4: Context Quality Matters

**Hands-On:**
- Generate course data using reference-agent utilities
- Set up Redis vector store
- Implement RAG pipeline
- Compare poor vs. well-engineered context

---

### 02_crafting_and_optimizing_context.ipynb

**Time:** 90-105 minutes

**What You'll Learn:**
- Data engineering workflows for context
- Chunking strategies and when to use them
- Production pipeline architectures
- Quality optimization techniques

**Key Topics:**
- Part 1: The Engineering Mindset
- Part 2: Data Engineering Pipeline
- Part 3: Engineering Approaches (RAG, Structured Views, Hybrid)
- Part 4: Chunking Strategies (4 strategies with LangChain)
- Part 5: Production Pipeline Architectures
- Part 6: Quality Optimization

**Hands-On:**
- Transform raw data through 5-step pipeline
- Implement three engineering approaches
- Use LangChain text splitters (RecursiveCharacterTextSplitter, SemanticChunker)
- Build batch processing pipeline
- Optimize context quality systematically

---

## Key Concepts

### RAG (Retrieval-Augmented Generation)

RAG solves the problem of static knowledge by dynamically retrieving relevant information:

```
User Query → Semantic Search → Retrieved Context → LLM Generation → Response
```

**Benefits:**
- Scales to millions of documents
- Token efficient (only retrieve what's relevant)
- Easy to update (no code changes)
- Personalized results

### Three Engineering Approaches

1. **RAG (Semantic Search)**
   - Use when: Data changes frequently, huge dataset, need specific details
   - Pros: Scalable, efficient, personalized
   - Cons: May miss overview, requires good embeddings

2. **Structured Views (Pre-Computed Summaries)**
   - Use when: Data changes infrequently, need overview + details
   - Pros: Complete overview, optimized format, fast
   - Cons: Higher maintenance, storage overhead

3. **Hybrid (Best of Both)**
   - Use when: Need both overview and specific details
   - Pros: Completeness + efficiency, best quality
   - Cons: More complex, higher cost

### Chunking Strategies

**Critical First Question:** Does your data need chunking?

**When NOT to chunk:**
- Documents are already small (<1000 tokens)
- Each document is a complete, self-contained unit
- Documents have clear structure (courses, products, articles)

**When TO chunk:**
- Long documents (>2000 tokens)
- Books, research papers, documentation
- Need to retrieve specific sections

**Four Strategies:**
1. **Document-Based** - Structure-aware splitting
2. **Fixed-Size** - LangChain RecursiveCharacterTextSplitter
3. **Semantic** - LangChain SemanticChunker with embeddings
4. **Hierarchical** - Multi-level chunking

### Production Pipeline Architectures

1. **Request-Time Processing**
   - Transform data when query arrives
   - Use when: Data changes frequently, simple transformations

2. **Batch Processing**
   - Pre-process data on schedule (e.g., weekly)
   - Use when: Data changes infrequently, complex transformations

3. **Event-Driven Processing**
   - Process data when it changes
   - Use when: Real-time updates required, event-driven architecture

### Quality Metrics

**Four Dimensions:**
1. **Relevance** - Does context include information needed to answer?
2. **Completeness** - Does context include ALL necessary information?
3. **Efficiency** - Is context optimized for token usage?
4. **Accuracy** - Is context factually correct and up-to-date?

**Key Insight:** Define domain-specific metrics, not generic benchmarks.

---

## Technologies Used

- **LangChain** - RAG framework and text splitters
- **Redis** - Vector store for semantic search
- **RedisVL** - Redis Vector Library for Python
- **OpenAI** - Embeddings and LLM (GPT-4o)
- **HuggingFace** - Local embeddings (sentence-transformers)
- **tiktoken** - Token counting

---

## Common Patterns

### RAG Pipeline Pattern

```python
# 1. Retrieve relevant documents
results = await course_manager.search_courses(query, top_k=3)

# 2. Assemble context
context = assemble_context(system_context, user_context, results)

# 3. Generate response
messages = [SystemMessage(content=context), HumanMessage(content=query)]
response = llm.invoke(messages)
```

### Data Engineering Pattern

```python
# Extract → Clean → Transform → Optimize → Store
raw_data = extract_from_source()
cleaned_data = clean_and_filter(raw_data)
transformed_data = transform_to_llm_format(cleaned_data)
optimized_data = optimize_tokens(transformed_data)
store_in_vector_db(optimized_data)
```

### Quality Optimization Pattern

```python
# Baseline → Experiment → Measure → Iterate
baseline_metrics = measure_quality(baseline_approach)
experiment_metrics = measure_quality(new_approach)
if experiment_metrics > baseline_metrics:
    deploy(new_approach)
else:
    iterate(new_approach)
```

---

## What's Next?

After completing this section, you'll move to:

**Section 3: Memory Systems for Context Engineering**
- Add working memory and long-term memory to your RAG system
- Manage conversation context across multiple turns
- Implement memory compression and summarization
- Use Redis Agent Memory Server

**Section 4: Tool Use and Agents**
- Add tools for course enrollment, schedule management
- Build complete autonomous agent with LangGraph
- Combine all four context types into production system

---

## Additional Resources

### RAG and Vector Search
- [Retrieval-Augmented Generation Paper](https://arxiv.org/abs/2005.11401) - Original RAG paper
- [Redis Vector Similarity Search](https://redis.io/docs/stack/search/reference/vectors/) - Official Redis VSS docs
- [RedisVL Documentation](https://redisvl.com/) - Redis Vector Library

### LangChain Integration
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) - Building RAG applications
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/) - Chunking strategies
- [LangChain Redis Integration](https://python.langchain.com/docs/integrations/vectorstores/redis/) - Using Redis with LangChain

### Embeddings and Semantic Search
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings) - Understanding text embeddings
- [Sentence Transformers](https://www.sbert.net/) - Open-source embedding models
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320) - Hierarchical Navigable Small World graphs

### Advanced RAG Techniques
- [Advanced RAG Patterns](https://blog.langchain.dev/deconstructing-rag/) - LangChain blog on RAG optimization
- [Advanced Search with RedisVL](https://docs.redisvl.com/en/latest/user_guide/11_advanced_queries.html) - Hybrid search techniques
- [RAG Evaluation](https://arxiv.org/abs/2309.15217) - Measuring RAG system performance

---

## Tips for Success

1. **Start Simple** - Build basic RAG first, then optimize
2. **Measure Everything** - Define metrics before optimizing
3. **Test with Real Queries** - Use queries from your actual domain
4. **Iterate Systematically** - Baseline → Experiment → Measure → Iterate
5. **Balance Trade-offs** - Relevance vs. Efficiency, Completeness vs. Token Budget

**Remember:** Context engineering is real engineering. Apply the same rigor you would to any data engineering problem.

