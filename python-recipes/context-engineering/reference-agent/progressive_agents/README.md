# Progressive Agents - Context Engineering Learning Path

This directory contains a progressive learning experience that teaches students how to evolve from basic RAG to optimized context engineering, using a LangGraph-based agent architecture.

## 🎯 Learning Objectives

Students will learn how to:

1. **Build RAG systems** from basic to advanced implementations
2. **Apply context engineering techniques** to optimize LLM performance
3. **Use LangGraph** for observable, stateful agent workflows
4. **Implement quality evaluation** and iterative improvement
5. **Integrate memory systems** for personalized, multi-turn interactions

## 📚 Progressive Stages

### Stage 1: Baseline RAG (Future)
**Goal**: Show that basic retrieval works but is inefficient

- Simple Q&A flow (no memory, no optimization)
- Raw JSON context formatting
- No context cleaning or transformation
- Demonstrates: ✅ It works, but ❌ Inefficient

### Stage 2: Context-Engineered RAG (Future)
**Goal**: Apply Section 2 techniques to optimize context quality

- Fill-in-the-blanks exercises for students
- Context cleaning (remove noise fields)
- Context transformation (JSON → natural text)
- Context optimization (token reduction)
- Demonstrates: How context engineering improves efficiency

### Stage 3: Full Agent without Memory (Current)
**Goal**: Production-ready patterns with quality evaluation

- ✅ **Currently Implemented**
- Complete LangGraph workflow
- Query decomposition
- Semantic course search with CourseManager
- Quality evaluation and iterative improvement
- Context engineering techniques applied
- Semantic caching commented out (for future stages)
- Demonstrates: Advanced RAG patterns

**Location**: `stage3_full_agent_without_memory/`

### Stage 4: Memory-Augmented Agent (Future)
**Goal**: Add personalization through memory integration

- Integrate Redis Agent Memory Server
- Add memory tools (store/search memories)
- Multi-turn conversations with context
- Personalized recommendations
- Demonstrates: How memory + RAG complement each other

## 🏗️ Architecture Overview

All stages follow the same LangGraph architecture pattern:

```
User Query
    ↓
[Decompose Query] - Break into sub-questions
    ↓
[Check Cache] - Look for cached answers
    ↓
[Research/Search] - Find relevant information
    ↓
[Evaluate Quality] - Assess answer quality
    ↓
[Synthesize Response] - Combine into final answer
    ↓
Final Response
```

**Key Differences Between Stages**:
- **Stage 1**: Raw context, no optimization
- **Stage 2**: Optimized context, student exercises
- **Stage 3**: Full workflow, quality evaluation
- **Stage 4**: + Memory integration

## 🚀 Getting Started

### Prerequisites

```bash
# Install the redis-context-course package
cd python-recipes/context-engineering/reference-agent
pip install -e .

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export REDIS_URL="redis://localhost:6379"
```

### Running Stage 3 (Current)

```bash
cd progressive_agents/stage3_full_agent_without_memory
python examples/basic_usage.py
```

## 📖 Educational Flow

### For Instructors

1. **Start with Stage 3** (working backwards approach)
   - Show students the complete, working agent
   - Demonstrate all features and capabilities
   - Explain the architecture and design decisions

2. **Deconstruct to Stage 2**
   - Remove quality evaluation
   - Create fill-in-the-blanks exercises
   - Focus on context engineering techniques

3. **Deconstruct to Stage 1**
   - Remove context optimization
   - Use raw JSON formatting
   - Show inefficiencies to motivate improvements

4. **Build up to Stage 4**
   - Add memory integration
   - Show multi-turn conversations
   - Demonstrate personalization

### For Students

**Recommended Learning Path**:

1. **Understand the Goal** (Stage 3)
   - Run the complete agent
   - See what's possible
   - Understand the architecture

2. **Learn Context Engineering** (Stage 2)
   - Complete fill-in-the-blanks exercises
   - Apply transformation techniques
   - Measure improvements

3. **Appreciate the Baseline** (Stage 1)
   - See the naive approach
   - Understand why optimization matters
   - Compare performance metrics

4. **Add Memory** (Stage 4)
   - Integrate memory tools
   - Build multi-turn conversations
   - Create personalized experiences

## 🔧 Technical Details

### Context Engineering Techniques

All stages use techniques from Section 2 notebooks:

1. **Context Transformation** (`transform_course_to_text`)
   - Converts structured data to natural text
   - Easier for LLMs to process

2. **Context Optimization** (`optimize_course_text`)
   - Ultra-compact format
   - Reduces token count

3. **Semantic Search**
   - Vector-based retrieval
   - Finds relevant courses by meaning

### LangGraph Workflow

- **State Management**: Explicit state tracking with TypedDict
- **Node Functions**: Pure functions that transform state
- **Conditional Edges**: Dynamic routing based on state
- **Observable**: Clear execution path and metrics

### CourseManager Integration

- **Semantic Search**: `search_courses(query, filters, limit, threshold)`
- **Course Retrieval**: `get_all_courses()`
- **Redis Vector Index**: Powered by RedisVL

## 📊 Comparison Across Stages

| Feature | Stage 1 | Stage 2 | Stage 3 | Stage 4 |
|---------|---------|---------|---------|---------|
| **Context Format** | Raw JSON | Optimized Text | Optimized Text | Optimized Text |
| **Query Decomposition** | ❌ | ❌ | ✅ | ✅ |
| **Quality Evaluation** | ❌ | ❌ | ✅ | ✅ |
| **Semantic Caching** | ❌ | ❌ | 🚧 Commented | ✅ |
| **Memory Integration** | ❌ | ❌ | ❌ | ✅ |
| **Token Efficiency** | Low | High | High | High |
| **Multi-turn Support** | ❌ | ❌ | ❌ | ✅ |

## 🎓 Learning Outcomes

By completing this progressive learning path, students will:

1. **Understand RAG fundamentals** and evolution
2. **Master context engineering** techniques
3. **Build production-ready agents** with LangGraph
4. **Implement quality assurance** mechanisms
5. **Integrate memory systems** for personalization
6. **Make informed design decisions** based on trade-offs

## 📚 Related Resources

- **Section 2 Notebooks**: Context engineering techniques
- **Section 3 Notebooks**: Memory systems integration
- **CourseManager**: `redis_context_course.course_manager`
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Original Caching Agent**: Inspiration for architecture

## 🤝 Contributing

This is part of the Redis University context engineering course. Improvements and extensions are welcome!

## 📄 License

MIT License - See LICENSE file for details

