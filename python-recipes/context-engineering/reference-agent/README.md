# Redis Context Course - Reference Agent

A complete reference implementation of a context-aware AI agent for university course recommendations and academic planning. This package demonstrates production-ready context engineering patterns using Redis, LangGraph, Agent Memory Server, and OpenAI.

**🎓 Part of the [Context Engineering Course](../notebooks_v2/README.md)** - This reference agent provides reusable components used throughout the course notebooks.

## Overview

This package serves two purposes:

1. **Educational Resource**: Provides production-ready components used in the [Context Engineering Course](../notebooks_v2/README.md)
2. **Reference Implementation**: Demonstrates best practices for building context-aware AI agents

The course notebooks use this package as a foundation, importing components like `CourseManager`, `redis_config`, and data models while demonstrating how to build custom agents from scratch.

## Features

- 🧠 **Dual Memory System**: Working memory (task-focused) and long-term memory (cross-session knowledge) via Agent Memory Server
- 🔍 **Semantic Search**: Vector-based course discovery and recommendations using Redis and RedisVL
- 🛠️ **Tool Integration**: Extensible tool system for course search and memory management
- 💬 **Context Awareness**: Maintains student preferences, goals, and conversation history
- 🎯 **Personalized Recommendations**: AI-powered course suggestions based on student profile
- 📚 **Course Catalog Management**: Complete system for storing and retrieving course information
- ⚡ **Production-Ready**: Optimization helpers, token counting, and performance utilities

## Installation

### From PyPI (Recommended)

```bash
pip install redis-context-course
```

### From Source

```bash
git clone https://github.com/redis-developer/redis-ai-resources.git
cd redis-ai-resources/python-recipes/context-engineering/reference-agent
pip install -e .
```

## Quick Start

### 1. Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your OpenAI API key and Redis URL
export OPENAI_API_KEY="your-openai-api-key"
export REDIS_URL="redis://localhost:6379"
```

### 2. Start Redis 8

For local development:
```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:8-alpine

# Or install Redis 8 locally
# See: https://redis.io/docs/latest/operate/oss_and_stack/install/
```

### 3. Start Redis Agent Memory Server

The agent uses [Redis Agent Memory Server](https://github.com/redis/agent-memory-server) for memory management:

```bash
# Install Agent Memory Server
pip install agent-memory-server

# Start the server (in a separate terminal)
uv run agent-memory api --no-worker

# Or with Docker
docker run -d --name agent-memory \
  -p 8088:8000 \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  -e OPENAI_API_KEY=your-key \
  redis/agent-memory-server
```

Set the Agent Memory Server URL (optional, defaults to localhost:8088):
```bash
export AGENT_MEMORY_URL="http://localhost:8088"
```

### 4. Generate Sample Data

```bash
generate-courses --courses-per-major 15 --output course_catalog.json
```

### 5. Ingest Data into Redis

```bash
ingest-courses --catalog course_catalog.json --clear
```

### 6. Verify Setup

Run the health check to ensure everything is working:

```bash
python simple_health_check.py
```

This will verify:
- Redis connection
- Environment variables
- Course data ingestion
- Agent functionality

### 7. Start the Agent

```bash
redis-class-agent --student-id your_student_id
```

## Python API Usage

```python
import asyncio
from redis_context_course import ClassAgent, MemoryClient, CourseManager

async def main():
    # Initialize the agent (uses Agent Memory Server)
    agent = ClassAgent("student_123")

    # Chat with the agent
    response = await agent.chat("I'm interested in machine learning courses")
    print(response)

    # Use individual components
    memory_manager = MemoryManager("student_123")
    await memory_manager.store_preference("I prefer online courses")

    course_manager = CourseManager()
    courses = await course_manager.search_courses("programming")

if __name__ == "__main__":
    asyncio.run(main())
```

## Package Exports

The package exports the following components for use in your applications:

### Core Classes
```python
from redis_context_course import (
    ClassAgent,              # LangGraph-based agent implementation
    AugmentedClassAgent,     # Enhanced agent with additional features
    AgentState,              # Agent state management
    MemoryClient,            # Memory API client (from agent-memory-client)
    MemoryClientConfig,      # Memory configuration
    CourseManager,           # Course storage and recommendation engine
    RedisConfig,             # Redis configuration
    redis_config,            # Redis config instance
)
```

### Data Models
```python
from redis_context_course import (
    Course,                  # Course data model
    Major,                   # Major/program model
    StudentProfile,          # Student information model
    CourseRecommendation,    # Recommendation model
    AgentResponse,           # Agent response model
    Prerequisite,            # Course prerequisite model
    CourseSchedule,          # Schedule information model
)
```

### Enums
```python
from redis_context_course import (
    DifficultyLevel,         # Course difficulty levels
    CourseFormat,            # Course format types (online, in-person, hybrid)
    Semester,                # Semester enumeration
    DayOfWeek,               # Day of week enumeration
)
```

### Tools (for notebooks and custom agents)
```python
from redis_context_course import (
    create_course_tools,     # Create course-related tools
    create_memory_tools,     # Create memory management tools
    select_tools_by_keywords,# Keyword-based tool selection
)
```

### Optimization Helpers
```python
from redis_context_course import (
    count_tokens,            # Token counting utility
    estimate_token_budget,   # Budget estimation
    hybrid_retrieval,        # Hybrid search strategy
    create_summary_view,     # Summary generation
    create_user_profile_view,# User profile formatting
    filter_tools_by_intent,  # Intent-based tool filtering
    classify_intent_with_llm,# LLM-based intent classification
    extract_references,      # Reference extraction
    format_context_for_llm,  # Context formatting
)
```

## Architecture

### Core Components

- **Agent**: LangGraph-based workflow orchestration (`ClassAgent`, `AugmentedClassAgent`)
- **Memory Client**: Interface to Redis Agent Memory Server
  - Working memory: Session-scoped, task-focused context
  - Long-term memory: Cross-session, persistent knowledge
- **Course Manager**: Course storage and recommendation engine using Redis and RedisVL
- **Models**: Type-safe Pydantic data structures for courses and students
- **Redis Config**: Redis connections and vector index management
- **Optimization Helpers**: Production utilities for token counting, cost management, and performance

### Command Line Tools

After installation, you have access to these command-line tools:

- `redis-class-agent`: Interactive chat interface with the agent
- `generate-courses`: Generate sample course catalog data
- `ingest-courses`: Load course data into Redis

### Memory System

The agent uses [Redis Agent Memory Server](https://github.com/redis/agent-memory-server) for a production-ready dual-memory architecture:

1. **Working Memory**: Session-scoped, task-focused context
   - Conversation messages
   - Current task state
   - Task-related data
   - TTL-based (default: 1 hour)
   - Automatic extraction to long-term storage

2. **Long-term Memory**: Cross-session, persistent knowledge
   - Student preferences and goals
   - Important facts learned over time
   - Vector-indexed for semantic search
   - Automatic deduplication
   - Three memory types: semantic, episodic, message

**Key Features:**
- Automatic memory extraction from conversations
- Semantic vector search with OpenAI embeddings
- Hash-based and semantic deduplication
- Rich metadata (topics, entities, timestamps)
- MCP server support for Claude Desktop

### Tool System

The agent has access to several tools:

- `search_courses_tool`: Find courses based on queries and filters
- `get_recommendations_tool`: Get personalized course recommendations
- `store_preference_tool`: Save student preferences
- `store_goal_tool`: Save student goals
- `get_student_context_tool`: Retrieve relevant student context

## Usage Examples

### Basic Conversation

```
You: I'm interested in learning programming
Agent: I'd be happy to help you find programming courses! Let me search for some options...

[Agent searches courses and provides recommendations]

You: I prefer online courses
Agent: I'll remember that you prefer online courses. Let me find online programming options for you...
```

### Course Search

```
You: What data science courses are available?
Agent: [Searches and displays relevant data science courses with details]

You: Show me beginner-friendly options
Agent: [Filters results for beginner difficulty level]
```

### Memory and Context

```
You: I want to focus on machine learning
Agent: I'll remember that you're interested in machine learning. This will help me provide better recommendations in the future.

[Later in conversation or new session]
You: What courses should I take?
Agent: Based on your interest in machine learning and preference for online courses, here are my recommendations...
```

## Troubleshooting

### Health Check

Use the built-in health check to diagnose issues:

```bash
python simple_health_check.py
```

The health check will verify:
- ✅ Environment variables are set correctly
- ✅ Redis connection is working
- ✅ Course and major data is present
- ✅ Course search functionality works
- ✅ Agent can respond to queries

If any checks fail, the script will provide specific fix commands.

### Common Issues

**"No courses found"**
```bash
# Re-run data ingestion
ingest-courses --catalog course_catalog.json --clear
```

**"Redis connection failed"**
```bash
# Start Redis with Docker
docker run -d --name redis -p 6379:6379 redis:8-alpine
```

**"Agent query failed"**
- Check that your OpenAI API key is valid
- Ensure course data has been ingested with embeddings
- Verify Agent Memory Server is running

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `REDIS_URL`: Redis connection URL (default: redis://localhost:6379)
- `VECTOR_INDEX_NAME`: Name for course vector index (default: course_catalog)
- `MEMORY_INDEX_NAME`: Name for memory vector index (default: agent_memory)

### Customization

The agent is designed to be easily extensible:

1. **Add New Tools**: Extend the tool system in `agent.py`
2. **Modify Memory Logic**: Customize memory storage and retrieval in `memory.py`
3. **Extend Course Data**: Add new fields to course models in `models.py`
4. **Custom Recommendations**: Modify recommendation logic in `course_manager.py`

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ scripts/
isort src/ scripts/
```

### Type Checking

```bash
mypy src/
```

## Project Structure

```
reference-agent/
├── redis_context_course/       # Main package
│   ├── agent.py               # LangGraph agent implementation
│   ├── memory.py              # Long-term memory manager
│   ├── working_memory.py      # Working memory implementation
│   ├── working_memory_tools.py # Memory management tools
│   ├── course_manager.py      # Course search and recommendations
│   ├── models.py              # Data models
│   ├── redis_config.py        # Redis configuration
│   ├── cli.py                 # Command-line interface
│   └── scripts/               # Data generation and ingestion
├── tests/                      # Test suite
├── examples/                   # Usage examples
│   └── basic_usage.py         # Basic package usage demo
├── data/                       # Generated course data
├── README.md                   # This file
├── requirements.txt            # Dependencies
└── setup.py                    # Package setup

```

## Educational Use & Course Integration

This reference implementation is designed for educational purposes and is integrated with the **[Context Engineering Course](../notebooks_v2/README.md)**.

### How the Course Uses This Package

The course notebooks demonstrate **building agents from scratch** using this package's components as building blocks:

**Components Used in Notebooks**:
- ✅ `CourseManager` - Course search and recommendations (Sections 2, 3, 4)
- ✅ `redis_config` - Redis configuration (Sections 2, 3)
- ✅ Data models: `Course`, `StudentProfile`, `DifficultyLevel`, `CourseFormat`, `Semester` (Sections 3, 4)
- ✅ Scripts: `CourseGenerator`, `CourseIngestionPipeline` (Section 2)

**Components for Production Use** (not directly used in notebooks):
- `ClassAgent`, `AugmentedClassAgent` - Complete agent implementations
- `create_course_tools`, `create_memory_tools` - Tool creation helpers
- Optimization helpers: `count_tokens`, `estimate_token_budget`, `hybrid_retrieval`, etc.

**Why This Approach?**
- Students learn to build custom agents rather than using pre-built ones
- Demonstrates how production agents are constructed from components
- Provides flexibility to adapt patterns to different use cases
- Shows both educational and production-ready patterns

For detailed analysis of component usage, see [notebooks_v2/REFERENCE_AGENT_USAGE_ANALYSIS.md](../notebooks_v2/REFERENCE_AGENT_USAGE_ANALYSIS.md).

### Learning Path

**For Course Students**:
1. **Complete the course**: Follow the [Context Engineering Course](../notebooks_v2/README.md)
2. **Use this package**: Import components as shown in notebooks
3. **Explore the source**: See production implementations in `redis_context_course/`
4. **Extend for your use case**: Adapt patterns to your domain

**For Independent Learners**:
1. **Explore the examples**: `examples/basic_usage.py` shows basic package usage
2. **Read the source code**: Well-documented code in `redis_context_course/`
3. **Run the agent**: Try the interactive CLI to see it in action
4. **Check the notebooks**: See step-by-step tutorials in `../notebooks_v2/`

### Key Concepts Demonstrated

- **Context Engineering**: Four context types and assembly strategies
- **Memory Management**: Working memory vs. long-term memory with Agent Memory Server
- **Tool Integration**: Creating and orchestrating multiple tools
- **Vector Search**: Semantic retrieval with Redis and RedisVL
- **LangGraph Workflows**: Stateful agent design patterns
- **Production Optimization**: Token counting, cost management, performance tuning

---

## Related Resources

### Course Materials
- **[Context Engineering Course](../notebooks_v2/README.md)** - Complete learning path using this package
- **[Reference Agent Usage Analysis](../notebooks_v2/REFERENCE_AGENT_USAGE_ANALYSIS.md)** - How notebooks use this package
- **[Setup Guide](../notebooks_v2/SETUP_GUIDE.md)** - Detailed setup instructions

### Documentation
- **[Main Course README](../README.md)** - Top-level context engineering documentation
- **[Agent Memory Server](https://github.com/redis/agent-memory-server)** - Memory management system
- **[Redis Documentation](https://redis.io/docs/)** - Redis official documentation
- **[LangGraph Documentation](https://langchain-ai.github.io/langgraph/)** - LangGraph stateful agents

### Community
- **[Redis Discord](https://discord.gg/redis)** - Join the Redis community
- **[GitHub Issues](https://github.com/redis-developer/redis-ai-resources/issues)** - Report issues or ask questions
- **[Redis AI Resources](https://github.com/redis-developer/redis-ai-resources)** - More AI examples and recipes

---

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please see the main repository for contribution guidelines.

---

**Ready to learn context engineering?** Start with the [Context Engineering Course](../notebooks_v2/README.md) to see this reference agent in action!
