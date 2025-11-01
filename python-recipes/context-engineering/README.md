# Context Engineering Recipes

This section contains comprehensive recipes and tutorials for **Context Engineering** - the practice of designing, implementing, and optimizing context management systems for AI agents and applications.

## What is Context Engineering?

Context Engineering is the discipline of building systems that help AI agents understand, maintain, and utilize context effectively. This includes:

- **System Context**: What the AI should know about its role, capabilities, and environment
- **Memory Management**: How to store, retrieve, and manage working memory (task-focused) and long-term memory (cross-session knowledge)
- **Tool Integration**: How to define and manage available tools and their usage
- **Context Optimization**: Techniques for managing context window limits and improving relevance

## Repository Structure

```
context-engineering/
├── README.md                    # This file
├── reference-agent/             # Complete reference implementation
│   ├── src/                     # Source code for the Redis University Class Agent
│   ├── scripts/                 # Data generation and ingestion scripts
│   ├── data/                    # Generated course catalogs and sample data
│   └── tests/                   # Test suite
├── notebooks/                   # Educational notebooks organized by section
│   ├── section-1-introduction/  # What is Context Engineering?
│   ├── section-2-system-context/# Setting up system context and tools
│   ├── section-3-memory/        # Memory management concepts
│   └── section-4-optimizations/ # Advanced optimization techniques
└── resources/                   # Shared resources, diagrams, and assets
```

## Course Structure

This repository supports a comprehensive web course on Context Engineering with the following sections:

### Section 1: Introduction
- **What is Context Engineering?** - Core concepts and principles
- **The Role of a Context Engine** - How context engines work in AI systems
- **Project Overview: Redis University Class Agent** - Hands-on project introduction

### Section 2: Setting up System Context
- **Prepping the System Context** - Defining what the AI should know
- **Defining Available Tools** - Tool integration and management

### Section 3: Memory
- **Memory Overview** - Concepts and architecture
- **Working Memory** - Managing task-focused context (conversation, task data)
- **Long-term Memory** - Cross-session knowledge storage and retrieval
- **Memory Integration** - Combining working and long-term memory
- **Memory Tools** - Giving the LLM control over memory operations

### Section 4: Optimizations
- **Context Window Management** - Handling token limits and summarization
- **Retrieval Strategies** - RAG, summaries, and hybrid approaches
- **Grounding with Memory** - Using memory to resolve references
- **Tool Optimization** - Selective tool exposure and filtering
- **Crafting Data for LLMs** - Creating structured views and dashboards

## Reference Agent: Redis University Class Agent

The reference implementation is a complete **Redis University Class Agent** that demonstrates all context engineering concepts in practice. This agent can:

- Help students find courses based on their interests and requirements
- Maintain conversation context across sessions
- Remember student preferences and academic history
- Provide personalized course recommendations
- Answer questions about course prerequisites, schedules, and content

### Key Technologies

- **LangGraph**: Agent workflow orchestration
- **Redis Agent Memory Server**: Long-term memory management
- **langgraph-redis-checkpointer**: Short-term memory and state persistence
- **RedisVL**: Vector storage for course catalog and semantic search
- **OpenAI GPT**: Language model for natural conversation

### Code Organization

The reference agent includes reusable modules that implement patterns from the notebooks:

- **`tools.py`** - Tool definitions used throughout the course (Section 2)
- **`optimization_helpers.py`** - Production-ready optimization patterns (Section 4)
- **`examples/advanced_agent_example.py`** - Complete example combining all techniques

These modules are designed to be imported in notebooks and used as building blocks for your own agents.

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (for running Redis and Agent Memory Server)
- OpenAI API key
- Basic understanding of AI agents and vector databases

### Quick Start

#### 1. Start Required Services

The notebooks and reference agent require Redis and the Agent Memory Server to be running:

```bash
# Navigate to the context-engineering directory
cd python-recipes/context-engineering

# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-key-here

# Start Redis and
docker-compose up -d

# Verify services are running
docker-compose ps

# Check Agent Memory Server health
curl http://localhost:8088/v1/health
```

#### 2. Set Up the Reference Agent

```bash
# Navigate to the reference agent directory
cd reference-agent

# Install dependencies
pip install -e .

# Generate sample course data
python -m redis_context_course.scripts.generate_courses

# Ingest data into Redis
python -m redis_context_course.scripts.ingest_courses

# Start the CLI agent
python -m redis_context_course.cli
```

#### 3. Run the Notebooks

```bash
# Install Jupyter
pip install jupyter

# Start Jupyter
jupyter notebook notebooks/

# Open any notebook and run the cells
```

### Stopping Services

```bash
# Stop services but keep data
docker-compose stop

# Stop and remove services (keeps volumes)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

## Learning Path

1. Start with **Section 1** notebooks to understand core concepts
2. Explore the **reference agent** codebase to see concepts in practice
3. Work through **Section 2** to learn system context setup
4. Complete **Section 3** to master memory management
5. Experiment with extending the agent for your own use cases

## Contributing

This is an educational resource. Contributions that improve clarity, add examples, or extend the reference implementation are welcome.
