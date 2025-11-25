# Course Q&A Agent - Stage 3 (Full Agent without Memory)

A LangGraph-based intelligent agent for answering questions about courses using semantic search and context engineering techniques. This agent demonstrates advanced RAG patterns with query decomposition, quality evaluation, and iterative improvement.

**Stage 3** in the progressive learning path: Full-featured agent with optimized context engineering, but without memory integration (memory will be added in Stage 4).

## 🚀 Features

- **Intelligent Query Decomposition**: Breaks down complex course questions into focused sub-questions
- **Semantic Course Search**: Uses CourseManager with Redis vector search for relevant course retrieval
- **Context Engineering**: Applies transformation and optimization techniques from Section 2 notebooks
- **Quality Assurance**: Evaluates and improves research quality through iterative loops
- **LangGraph Workflow**: Clean, observable agent architecture with explicit state management

## 🎯 How It Works

The agent follows a deep research workflow adapted for course Q&A:

1. **Query Decomposition**: Complex questions are broken into focused sub-questions
2. **Cache Check**: Each sub-question is checked against semantic cache (currently disabled)
3. **Course Search**: Cache misses trigger semantic search using CourseManager
4. **Quality Evaluation**: Search results are evaluated for completeness and accuracy
5. **Iterative Improvement**: Low-quality results trigger additional search rounds
6. **Response Synthesis**: All answers are combined into a comprehensive final response

### Workflow Diagram

```mermaid
graph TD
    A[User Query] --> B[Decompose Query]
    B --> C[Check Cache]
    C -->|Cache Disabled| D[Course Search]
    C -->|Future: Cache Hits| E[Synthesize Response]
    D --> F[Evaluate Quality]
    F -->|Low Quality| D
    F -->|High Quality| G[Cache Results - Disabled]
    G --> E
    E --> H[Final Response]
    
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#f9f,stroke:#333,stroke-width:2px
    
    classDef disabled fill:#ddd,stroke:#999,stroke-dasharray: 5 5
    class C,G disabled
```

**Note**: Nodes marked in gray (Cache Check, Cache Results) are currently disabled. Semantic caching will be added in future stages.

## 📁 Project Structure

```
stage3_full_agent_without_memory/
├── agent/                      # Core agent implementation
│   ├── __init__.py            # Package exports
│   ├── edges.py               # LangGraph routing logic
│   ├── nodes.py               # LangGraph workflow nodes
│   ├── setup.py               # Initialization logic
│   ├── state.py               # Agent state definitions
│   ├── tools.py               # Course search tools
│   └── workflow.py            # LangGraph workflow definition
├── examples/                   # Example usage scripts
│   └── basic_usage.py         # Simple example
└── README.md                  # This file
```

## 🛠️ Setup

### Prerequisites

- Python 3.9+
- OpenAI API key
- Redis server (for course data)
- `redis-context-course` package installed

### Installation

From the `reference-agent` directory:

```bash
# Install the redis-context-course package
pip install -e .

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export REDIS_URL="redis://localhost:6379"
```

### Quick Start

```python
import asyncio
from agent import setup_agent, create_workflow, run_agent

async def main():
    # Initialize the agent
    course_manager, _ = await setup_agent()
    
    # Create the workflow
    agent = create_workflow(course_manager)
    
    # Run a query
    result = run_agent(
        agent, 
        "What machine learning courses are available for beginners?"
    )
    
    # Print the response
    print(result["final_response"])

if __name__ == "__main__":
    asyncio.run(main())
```

## 🧠 Context Engineering Techniques

This agent applies context engineering techniques from Section 2 notebooks:

### 1. Context Transformation (`transform_course_to_text`)

Converts structured course objects into LLM-friendly natural text format:

```python
# Before (JSON):
{"course_code": "CS101", "title": "Intro to Programming", ...}

# After (Natural Text):
CS101: Intro to Programming
Department: Computer Science
Credits: 3
Level: beginner
...
```

**Benefits**: Easier for LLMs to parse, more natural language processing

### 2. Context Optimization (`optimize_course_text`)

Creates ultra-compact course descriptions for token efficiency:

```python
# Optimized format:
CS101: Intro to Programming - Fundamental programming concepts using Python... (Prereq: None)
```

**Benefits**: Reduced token count, faster processing, lower costs

### 3. Semantic Search

Uses Redis vector search to find relevant courses based on semantic similarity:

```python
results = await course_manager.search_courses(
    query="machine learning courses",
    limit=5,
    similarity_threshold=0.6
)
```

**Benefits**: Finds relevant courses even with different wording

## 📊 Performance Metrics

The agent tracks detailed performance metrics:

- **Total Latency**: End-to-end query processing time
- **Decomposition Latency**: Time to break down query
- **Cache Latency**: Time to check cache (currently minimal)
- **Research Latency**: Time for course search
- **Synthesis Latency**: Time to combine answers
- **Cache Hit Rate**: Percentage of cached answers (currently 0%)
- **LLM Calls**: Number of LLM API calls made

Access metrics from the result:

```python
result = run_agent(agent, query)
print(f"Total time: {result['metrics']['total_latency']:.2f}ms")
print(f"Execution path: {result['metrics']['execution_path']}")
```

## 🔄 Progressive Learning Path

This is **Stage 3** of the progressive learning experience:

- **Stage 1** (Future): Baseline RAG - Naive retrieval with raw JSON context
- **Stage 2** (Future): Context-Engineered RAG - Apply Section 2 techniques
- **Stage 3** (Current): Full Agent without Memory - Complete workflow with quality evaluation
- **Stage 4** (Future): Memory-Augmented Agent - Add Redis Agent Memory Server

## 🎓 Educational Goals

Students learn:

1. **LangGraph Architecture**: How to build observable, stateful agents
2. **Query Decomposition**: Breaking complex questions into manageable parts
3. **Context Engineering**: Transforming data for optimal LLM consumption
4. **Quality Evaluation**: Iterative improvement through self-assessment
5. **Semantic Search**: Vector-based retrieval for relevant information

## 🚧 What's Commented Out (For Future Stages)

### Semantic Caching

Currently disabled to focus on core workflow. Will be added in future stages:

```python
# In nodes.py - check_cache_node
# semantic_cache.check(question, num_results=1)

# In nodes.py - synthesize_response_node  
# semantic_cache.store(question, answer)
```

### Why Disabled?

- Focus on understanding the core workflow first
- Semantic caching adds complexity (similarity thresholds, false positives)
- Will be introduced progressively with proper tuning and monitoring

## 🧪 Testing

Run the example script:

```bash
cd progressive_agents/stage3_full_agent_without_memory
python examples/basic_usage.py
```

## 📚 Related Resources

- **Section 2 Notebooks**: Context engineering techniques
- **CourseManager**: Redis-based course search (`redis_context_course.course_manager`)
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Original Caching Agent**: `/Users/nitin.kanukolanu/workspace/caching-agent`

## 🤝 Contributing

This is part of the Redis University context engineering course. Improvements and extensions are welcome!

## 📄 License

MIT License - See LICENSE file for details

