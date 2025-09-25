# Context Engineering Recipes

This section contains comprehensive recipes and tutorials for **Context Engineering** - the practice of designing, implementing, and optimizing context management systems for AI agents and applications.

## What is Context Engineering?

Context Engineering is the discipline of building systems that help AI agents understand, maintain, and utilize context effectively. This includes:

- **System Context**: What the AI should know about its role, capabilities, and environment
- **Memory Management**: How to store, retrieve, and manage both short-term and long-term memory
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
│   └── section-3-memory/        # Memory management concepts
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
- **Short-term/Working Memory** - Managing conversation context
- **Summarizing Short-term Memory** - Context window optimization
- **Long-term Memory** - Persistent knowledge storage and retrieval

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

## Getting Started

1. **Set up the environment**: Install required dependencies
2. **Run the reference agent**: Start with the complete implementation
3. **Explore the notebooks**: Work through the educational content
4. **Experiment**: Modify and extend the agent for your use cases

## Prerequisites

- Python 3.8+
- Redis Stack (local or cloud)
- OpenAI API key
- Basic understanding of AI agents and vector databases

## Quick Start

```bash
# Navigate to the reference agent directory
cd python-recipes/context-engineering/reference-agent

# Install dependencies
pip install -r requirements.txt

# Generate sample course data
python -m redis_context_course.scripts.generate_courses

# Ingest data into Redis
python -m redis_context_course.scripts.ingest_courses

# Start the CLI agent
python -m redis_context_course.cli
```

## Learning Path

1. Start with **Section 1** notebooks to understand core concepts
2. Explore the **reference agent** codebase to see concepts in practice
3. Work through **Section 2** to learn system context setup
4. Complete **Section 3** to master memory management
5. Experiment with extending the agent for your own use cases

## Contributing

This is an educational resource. Contributions that improve clarity, add examples, or extend the reference implementation are welcome.
