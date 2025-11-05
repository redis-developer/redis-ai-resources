# Context Engineering Course

**A comprehensive, hands-on course teaching practical context engineering patterns for AI agents using Redis, Agent Memory Server, LangChain, and LangGraph.**

[![Redis](https://img.shields.io/badge/Redis-8.0+-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-1C3C3C?logo=chainlink&logoColor=white)](https://python.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?logo=openai&logoColor=white)](https://openai.com/)

---

## 📚 What is Context Engineering?

**Context Engineering** is the practice of designing, implementing, and optimizing context management systems for AI agents. It's the difference between a chatbot that forgets everything and an intelligent assistant that understands your needs.

### The Four Context Types

1. **System Context** - What the AI should know about its role, capabilities, and environment
2. **User Context** - Information about the user, their preferences, and history
3. **Retrieved Context** - Dynamically fetched information from databases, APIs, or vector stores
4. **Conversation Context** - The ongoing dialogue and task-focused working memory

### Why Context Engineering Matters

- 🎯 **Better AI Performance** - Agents with proper context make better decisions
- 💰 **Cost Optimization** - Efficient context management reduces token usage by 50-70%
- 🔄 **Cross-Session Memory** - Users don't have to repeat themselves
- 🚀 **Scalable Patterns** - Design agents that can handle high-volume scenarios
- 🛠️ **Tool Orchestration** - Intelligent tool selection based on context

---

## 🎓 Course Overview

**Format**: Self-paced, hands-on notebooks
**Level**: Intermediate to Advanced
**Prerequisites**: Python, basic AI/ML understanding, familiarity with LLMs

### What You'll Build

A complete **Redis University Course Advisor Agent** that:
- Helps students find courses using semantic search
- Remembers student preferences and goals across sessions
- Provides personalized recommendations
- Uses intelligent tool selection with LangGraph
- Demonstrates practical context optimization patterns

### What You'll Learn

- ✅ Context types and assembly strategies
- ✅ RAG (Retrieval Augmented Generation) with RedisVL
- ✅ Dual memory systems (working + long-term) with Agent Memory Server
- ✅ Memory extraction strategies (discrete, summary, preferences)
- ✅ Working memory compression techniques
- ✅ LangGraph for stateful agent workflows
- ✅ Semantic tool selection and orchestration
- ✅ Context optimization and cost management patterns

---

## 📖 Course Structure

**📚 For complete syllabus with detailed learning outcomes, see [COURSE_SUMMARY.md](COURSE_SUMMARY.md)**

### **Section 1: Context Engineering Foundations** (2-3 hours)
**2 notebooks** | **Prerequisites**: None

Learn the foundational concepts of context engineering and the different context types.

**Notebooks**:
1. What is Context Engineering?
2. Context Assembly Strategies

---

### **Section 2: Retrieved Context Engineering** (2.5-3 hours)
**2 notebooks** | **Prerequisites**: Section 1

Build RAG systems with Redis, from fundamentals to advanced engineering patterns.

**Notebooks**:
1. RAG Fundamentals and Implementation
2. Crafting and Optimizing Context

---

### **Section 3: Memory Systems for Context Engineering** (4-5 hours)
**3 notebooks** | **Prerequisites**: Sections 1-2

Master dual memory systems with Agent Memory Server, including extraction and compression strategies.

**Notebooks**:
1. Memory Fundamentals and Integration
2. Memory-Enhanced RAG and Agents
3. Working Memory Compression

---

### **Section 4: Integrating Tools and Agents** (3.5-4.5 hours)
**4 notebooks** | **Prerequisites**: Sections 1-3

Build agents with LangGraph, semantic tool selection, and state management.

**Notebooks**:
1. Tools and LangGraph Fundamentals
2. Redis University Course Advisor Agent
3. Course Advisor with Compression
4. Semantic Tool Selection

---

## 📁 Repository Structure

```
context-engineering/
├── README.md                           # 👈 This file - Main entry point
├── COURSE_SUMMARY.md                   # Complete course syllabus and learning outcomes
├── SETUP.md                            # Detailed setup guide
├── docker-compose.yml                  # Redis + Agent Memory Server setup
├── requirements.txt                    # Python dependencies
│
├── notebooks/                       # 👈 Course notebooks (main content)
│   ├── README.md                       # Notebook-specific documentation
│   ├── SETUP_GUIDE.md                  # Detailed setup instructions
│   ├── REFERENCE_AGENT_USAGE_ANALYSIS.md  # Component usage analysis
│   ├── section-1-context-engineering-foundations/  # Section 1 notebooks
│   ├── section-2-retrieved-context-engineering/  # Section 2 notebooks
│   ├── section-3-memory-systems-for-context-engineering/  # Section 3 notebooks
│   └── section-4-integrating-tools-and-agents/  # Section 4 notebooks
│
└── reference-agent/                    # Reusable reference implementation
    ├── README.md                       # Reference agent documentation
    ├── redis_context_course/           # Python package
    │   ├── __init__.py                 # Package exports
    │   ├── models.py                   # Data models (Course, StudentProfile, etc.)
    │   ├── course_manager.py           # Course storage and search
    │   ├── redis_config.py             # Redis configuration
    │   ├── tools.py                    # Tool creation helpers
    │   ├── optimization_helpers.py     # Optimization utilities
    │   └── scripts/                    # Data generation scripts
    ├── examples/                       # Usage examples
    └── tests/                          # Test suite
```

---

## 🚀 Quick Start (5 Minutes)

Get up and running with the course in 5 simple steps:

### **Step 1: Clone the Repository**
```bash
git clone <repository-url>
cd redis-ai-resources/python-recipes/context-engineering
```

### **Step 2: Set Environment Variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### **Step 3: Start Services with Docker**
```bash
# Start Redis and Agent Memory Server
docker-compose up -d

# Verify services are running
docker-compose ps
```

### **Step 4: Install Dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install reference agent package (editable mode)
cd reference-agent
pip install -e .
cd ..
```

### **Step 5: Start Learning!**
```bash
# Start Jupyter
jupyter notebook notebooks/

# Open: section-1-context-engineering-foundations/01_what_is_context_engineering.ipynb
```

### **Verification**

Check that everything is working:

```bash
# Check Redis
docker exec redis-context-engineering redis-cli ping
# Expected output: PONG

# Check Agent Memory Server
curl http://localhost:8088/v1/health
# Expected output: {"now":<timestamp>}

# Check Python packages
python -c "import redis_context_course; print('✅ Reference agent installed')"
# Expected output: ✅ Reference agent installed
```

**🎉 You're ready to start!** Open the first notebook and begin your context engineering journey.

---

## 🛠️ Detailed Setup Instructions

For complete setup instructions including troubleshooting, see **[SETUP.md](SETUP.md)** and **[notebooks/SETUP_GUIDE.md](notebooks/SETUP_GUIDE.md)**.

### System Requirements

#### Required
- **Python 3.10+** (Python 3.8+ may work but 3.10+ recommended)
- **Docker Desktop** (for Redis and Agent Memory Server)

#### Optional
- **Redis Insight** for visualizing Redis data

### Services Architecture

The course uses three main services:

1. **Redis** (port 6379) - Vector storage for course catalog
2. **Agent Memory Server** (port 8088) - Memory management
3. **Jupyter** (port 8888) - Interactive notebooks

All services are configured in `docker-compose.yml` for easy setup.

### Environment Variables

Create a `.env` file with the following:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional (defaults provided)
REDIS_URL=redis://localhost:6379
AGENT_MEMORY_SERVER_URL=http://localhost:8088
REDIS_INDEX_NAME=course_catalog
```

### Docker Compose Services

The `docker-compose.yml` file includes:

```yaml
services:
  redis:
    image: redis/redis-stack:latest
    ports:
      - "6379:6379"   # Redis
      - "8001:8001"   # RedisInsight
    volumes:
      - redis-data:/data

  agent-memory-server:
    image: redis/agent-memory-server:latest
    ports:
      - "8088:8088"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
```

### Installation Steps

#### 1. Install Python Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# This installs:
# - langchain>=0.2.0
# - langgraph>=0.2.0
# - langchain-openai>=0.1.0
# - agent-memory-client>=0.12.6
# - redis>=6.0.0
# - redisvl>=0.8.0
# - openai>=1.0.0
# - jupyter
# - python-dotenv
# - pydantic>=2.0.0
```

#### 2. Install Reference Agent Package

```bash
cd reference-agent
pip install -e .
cd ..
```

This installs the `redis-context-course` package in editable mode, allowing you to:
- Import components in notebooks
- Modify the package and see changes immediately
- Use reusable utilities and patterns

#### 3. Generate Sample Data (Optional)

```bash
cd reference-agent

# Generate course catalog
python -m redis_context_course.scripts.generate_courses

# Ingest into Redis
python -m redis_context_course.scripts.ingest_courses

cd ..
```

**Note**: Most notebooks generate their own data, so this step is optional.

### Troubleshooting

#### OpenAI API Key Issues
```
Error: "OPENAI_API_KEY not found"
```
**Solution**: Create `.env` file with `OPENAI_API_KEY=your_key_here`

#### Redis Connection Issues
```
Error: "Connection refused" or "Redis not available"
```
**Solutions**:
1. Start Redis: `docker-compose up -d`
2. Check Redis URL in `.env`: `REDIS_URL=redis://localhost:6379`
3. Verify: `docker exec redis-context-engineering redis-cli ping`

#### Agent Memory Server Issues
```
Error: "Cannot connect to Agent Memory Server"
```
**Solutions**:
1. Check service: `docker-compose ps`
2. Check health: `curl http://localhost:8088/v1/health`
3. Restart: `docker-compose restart agent-memory-server`

#### Import Errors
```
Error: "No module named 'redis_context_course'"
```
**Solutions**:
1. Install reference agent: `cd reference-agent && pip install -e .`
2. Restart Jupyter kernel
3. Check Python path in notebook cells

### Stopping Services

```bash
# Stop services but keep data
docker-compose stop

# Stop and remove services (keeps volumes)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

---

## 📖 Recommended Learning Path

### For Beginners
**Timeline**: 2-3 weeks (6-8 hours/week)

1. **Week 1**: Complete Section 1 (Foundations) and Section 2 (RAG)
2. **Week 2**: Work through Section 3 (Memory Systems for Context Engineering)
3. **Week 3**: Build agents in Section 4 (Integrating Tools and Agents)

### Learning Tips

1. **Start with Section 1** - Build foundational understanding
2. **Progress sequentially** - Each section builds on the previous
3. **Complete all exercises** - Hands-on practice is essential
4. **Experiment freely** - Modify code and test variations
5. **Build your own variations** - Apply patterns to your domain

---

## 🎯 Learning Outcomes

**📚 For detailed learning outcomes by section, see [COURSE_SUMMARY.md](COURSE_SUMMARY.md)**

By completing this course, you will be able to:

- ✅ Design context-aware AI agents from scratch
- ✅ Implement memory systems with Agent Memory Server
- ✅ Build RAG applications using Redis and vector search
- ✅ Optimize context assembly for cost and performance
- ✅ Create stateful agents with LangGraph
- ✅ Apply scalable patterns to real-world use cases
- ✅ Use context engineering patterns in any domain

---

## 🏗️ Reference Agent Package

The `redis-context-course` package provides reusable components used throughout the course.

**Key Components**:
- `CourseManager` - Course storage and semantic search
- `RedisConfig` - Redis configuration
- Data models: `Course`, `StudentProfile`, etc.
- Tools and optimization helpers

**📚 For complete component details, see [COURSE_SUMMARY.md](COURSE_SUMMARY.md) and [reference-agent/README.md](reference-agent/README.md)**

---

## 🌍 Real-World Applications

The patterns and techniques learned apply directly to:

- **Enterprise AI Systems** - Customer service, technical support, sales assistants
- **Educational Technology** - Learning assistants, academic advising, tutoring systems
- **AI Services** - Multi-tenant SaaS, API services, scalable conversation systems

**📚 For detailed use cases, see [COURSE_SUMMARY.md](COURSE_SUMMARY.md)**

---

## 📊 Expected Results

**Measurable Improvements**:
- 50-70% token reduction through intelligent context optimization
- Semantic tool selection replacing brittle keyword matching
- Cross-session memory enabling natural conversation continuity
- Scalable patterns that can handle high-volume scenarios

**Skills Gained**:
- Portfolio project demonstrating context engineering mastery
- Practical patterns for building AI agents
- Cost optimization skills for managing LLM expenses

---

## 📚 Additional Resources

### Documentation
- **[COURSE_SUMMARY.md](COURSE_SUMMARY.md)** - Complete course syllabus and learning outcomes
- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[notebooks/README.md](notebooks/README.md)** - Notebook-specific documentation
- **[notebooks/SETUP_GUIDE.md](notebooks/SETUP_GUIDE.md)** - Comprehensive setup guide
- **[notebooks/REFERENCE_AGENT_USAGE_ANALYSIS.md](notebooks/REFERENCE_AGENT_USAGE_ANALYSIS.md)** - Component usage analysis
- **[reference-agent/README.md](reference-agent/README.md)** - Reference agent documentation

### External Resources
- **[Redis Documentation](https://redis.io/docs/)** - Redis official documentation
- **[LangChain Documentation](https://python.langchain.com/)** - LangChain framework docs
- **[LangGraph Documentation](https://langchain-ai.github.io/langgraph/)** - LangGraph stateful agents
- **[Agent Memory Server](https://github.com/redis/agent-memory-server)** - Memory management system
- **[OpenAI API Reference](https://platform.openai.com/docs/api-reference)** - OpenAI API documentation

### Community
- **[Redis Discord](https://discord.gg/redis)** - Join the Redis community
- **[GitHub Issues](https://github.com/redis-developer/redis-ai-resources/issues)** - Report issues or ask questions
- **[Redis AI Resources](https://github.com/redis-developer/redis-ai-resources)** - More AI examples and recipes

---

## 📝 Course Metadata

**Version**: 2.0
**Last Updated**: November 2025
**Maintainer**: Redis AI Team
**License**: MIT

**Technologies**: Python 3.10+, Redis 8.0+, LangChain 0.2+, LangGraph 0.2+, Agent Memory Server 0.12.3+, OpenAI GPT-4

**Course Stats**: 4 sections | 11 notebooks | 25+ hands-on exercises

---

**Ready to transform your context engineering skills? [Start your journey today!](#-quick-start-5-minutes)**
