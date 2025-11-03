# Redis AI Reference Agents - Setup Guide

This guide helps you set up and test the Redis AI reference agents in this repository.

## Overview

There are two reference agents available:

1. **Oregon Trail Agent** (`nk_scripts/full_featured_agent.py`)
   - Simple tool-calling agent demonstrating semantic caching, RAG, and structured output
   - Based on the Oregon Trail game scenario
   - Good for learning basic agent concepts

2. **Context Course Agent** (`python-recipes/context-engineering/reference-agent/`)
   - Complex agent with dual memory system for course recommendations
   - Demonstrates advanced context engineering concepts
   - Production-ready architecture with Redis Agent Memory Server

## Prerequisites

### 1. Redis Server
You need Redis 8+ running locally:

```bash
# Option 1: Using Docker (recommended)
docker run -d --name redis -p 6379:6379 redis:8-alpine

# Option 2: Install Redis locally
# See: https://redis.io/docs/latest/operate/oss_and_stack/install/
```

### 2. OpenAI API Key
Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Python Environment
Activate the virtual environment:

```bash
source python-recipes/context-engineering/venv/bin/activate
```

## Quick Test

Run the test script to check if everything is working:

```bash
python test_reference_agents.py
```

## Testing Oregon Trail Agent

### Manual Test
```bash
# Activate virtual environment
source python-recipes/context-engineering/venv/bin/activate

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run the agent
python nk_scripts/full_featured_agent.py
```

### Expected Output
The agent will run 4 scenarios:
1. **Wagon Leader Name**: Tests basic response (should return "Art")
2. **Restocking Tool**: Tests tool calling with math calculations
3. **Retrieval Tool**: Tests RAG with vector search
4. **Semantic Cache**: Tests cached responses

## Testing Context Course Agent

### 1. Install the Package
```bash
cd python-recipes/context-engineering/reference-agent
pip install -e .
```

### 2. Start Redis Agent Memory Server
```bash
# Install Agent Memory Server
pip install agent-memory-server

# Start the server (in a separate terminal)
uv run agent-memory api --no-worker

# Or with Docker
docker run -d --name agent-memory \
  -p 8088:8000 \
  -e REDIS_URL=redis://localhost:6379 \
  -e OPENAI_API_KEY=your-key \
  redis/agent-memory-server
```

### 3. Generate and Ingest Course Data
```bash
# Generate sample course catalog
generate-courses --courses-per-major 15 --output course_catalog.json

# Ingest into Redis
ingest-courses --catalog course_catalog.json --clear
```

### 4. Run the Agent
```bash
redis-class-agent --student-id test_student
```

## Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
python -c "import redis; r = redis.Redis(); print('Redis OK:', r.ping())"
```

### Missing Dependencies
```bash
# Install missing packages
pip install langchain langchain-openai langchain-redis langgraph redisvl
```

### OpenAI API Issues
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connection
python -c "
import openai
client = openai.OpenAI()
try:
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=5
    )
    print('OpenAI API OK')
except Exception as e:
    print(f'OpenAI API Error: {e}')
"
```

### Virtual Environment Issues
```bash
# Recreate virtual environment if needed
cd python-recipes/context-engineering
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## What Each Agent Demonstrates

### Oregon Trail Agent Features:
- **Tool Calling**: Restock calculation tool
- **Semantic Caching**: Caches responses to avoid redundant LLM calls
- **RAG (Retrieval Augmented Generation)**: Vector search for trail information
- **Structured Output**: Multiple choice response formatting
- **LangGraph Workflow**: State-based agent orchestration

### Context Course Agent Features:
- **Dual Memory System**: Working memory + long-term memory
- **Vector Search**: Semantic course discovery
- **Context Awareness**: Maintains student preferences across sessions
- **Tool Integration**: Course search, recommendations, memory management
- **Production Architecture**: Uses Redis Agent Memory Server

## Next Steps

1. **Start with Oregon Trail Agent**: It's simpler and good for learning basics
2. **Explore the Code**: Read through the source code to understand the patterns
3. **Modify and Experiment**: Try changing prompts, adding tools, or modifying workflows
4. **Move to Context Course Agent**: Once comfortable, explore the more complex agent

## Getting Help

- Check the test script output for specific error messages
- Review the individual README files in each agent directory
- Look at the notebook tutorials in `python-recipes/context-engineering/notebooks/`
- Ensure all environment variables are set correctly
