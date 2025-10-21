# Redis Context Course

A complete reference implementation of a context-aware AI agent for university course recommendations and academic planning. This package demonstrates key context engineering concepts using Redis, LangGraph, and OpenAI.

## Features

- 🧠 **Dual Memory System**: Working memory (task-focused) and long-term memory (cross-session knowledge)
- 🔍 **Semantic Search**: Vector-based course discovery and recommendations
- 🛠️ **Tool Integration**: Extensible tool system for course search and memory management
- 💬 **Context Awareness**: Maintains student preferences, goals, and conversation history
- 🎯 **Personalized Recommendations**: AI-powered course suggestions based on student profile
- 📚 **Course Catalog Management**: Complete system for storing and retrieving course information

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

### 6. Start the Agent

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

## Architecture

### Core Components

- **Agent**: LangGraph-based workflow orchestration
- **Memory Client**: Interface to Redis Agent Memory Server
  - Working memory: Session-scoped, task-focused context
  - Long-term memory: Cross-session, persistent knowledge
- **Course Manager**: Course storage and recommendation engine
- **Models**: Data structures for courses and students
- **Redis Config**: Redis connections and index management

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

## Educational Use

This reference implementation is designed for educational purposes to demonstrate:

- Context engineering principles
- Memory management in AI agents (working memory vs. long-term memory)
- Tool integration patterns
- Vector search and semantic retrieval
- LangGraph workflow design
- Redis as an AI infrastructure component

See the accompanying notebooks in the `../notebooks/` directory for detailed explanations and tutorials.

### Learning Path

1. **Start with the notebooks**: `../notebooks/` contains step-by-step tutorials
2. **Explore the examples**: `examples/basic_usage.py` shows basic package usage
3. **Read the source code**: Well-documented code in `redis_context_course/`
4. **Run the agent**: Try the interactive CLI to see it in action
5. **Extend and experiment**: Modify the code to learn by doing
