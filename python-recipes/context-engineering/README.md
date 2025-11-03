# Context Engineering Course

**A comprehensive, hands-on course teaching production-ready context engineering for AI agents using Redis, Agent Memory Server, LangChain, and LangGraph.**

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
- 🚀 **Production Scalability** - Handle thousands of concurrent users effectively
- 🛠️ **Tool Orchestration** - Intelligent tool selection based on context

---

## 🎓 Course Overview

**Duration**: 18-23 hours
**Format**: Self-paced, hands-on notebooks
**Level**: Intermediate to Advanced
**Prerequisites**: Python, basic AI/ML understanding, familiarity with LLMs

### What You'll Build

A complete **Redis University Course Advisor Agent** that:
- Helps students find courses using semantic search
- Remembers student preferences and goals across sessions
- Provides personalized recommendations
- Uses intelligent tool selection with LangGraph
- Optimizes context for production deployment

### What You'll Learn

- ✅ Four context types and assembly strategies
- ✅ RAG (Retrieval Augmented Generation) with Redis and RedisVL
- ✅ Dual memory systems (working + long-term) with Agent Memory Server
- ✅ Memory extraction strategies (discrete, summary, preferences)
- ✅ Working memory compression techniques
- ✅ LangGraph for stateful agent workflows
- ✅ Semantic tool selection and orchestration
- ✅ Production optimization and cost management

---

## 📖 Course Structure

### **Section 1: Context Engineering Foundations** (2-3 hours)
**2 notebooks** | **Prerequisites**: None

Learn the foundational concepts of context engineering and the four context types.

**Notebooks**:
1. **What is Context Engineering?** - Four context types, principles, and architecture
2. **Context Assembly Strategies** - How to combine contexts effectively

**Learning Outcomes**:
- Understand the four context types and their roles
- Learn context assembly strategies
- Grasp the importance of context engineering in AI systems

**Reference Agent Components Used**: None (pure theory)

---

### **Section 2: Retrieved Context Engineering** (3-4 hours)
**1 notebook** | **Prerequisites**: Section 1

Build a RAG system using Redis and RedisVL for semantic course search.

**Notebooks**:
1. **Engineering Retrieved Context with RAG** - Vector embeddings, semantic search, course recommendations

**Learning Outcomes**:
- Implement vector embeddings with OpenAI
- Build semantic search with Redis and RedisVL
- Create a course recommendation system
- Understand RAG architecture patterns

**Reference Agent Components Used**:
- `CourseManager` - Course storage and search
- `redis_config` - Redis configuration
- `CourseGenerator`, `CourseIngestionPipeline` - Data generation scripts

---

### **Section 3: Memory Systems for Context Engineering** (4-5 hours)
**3 notebooks** | **Prerequisites**: Sections 1-2

Master dual memory systems with Agent Memory Server, including extraction and compression strategies.

**Notebooks**:
1. **Memory Fundamentals and Integration** - Working memory, long-term memory, Agent Memory Server
2. **Memory-Enhanced RAG and Agents** - Combining memory with RAG, building stateful agents
3. **Working Memory Compression** - Compression strategies for long conversations

**Learning Outcomes**:
- Implement working memory (session-scoped) and long-term memory (cross-session)
- Use Agent Memory Server for automatic memory extraction
- Apply memory extraction strategies (discrete, summary, preferences)
- Implement working memory compression (truncation, priority-based, summarization)
- Build memory-enhanced RAG systems

**Reference Agent Components Used**:
- Data models: `Course`, `StudentProfile`, `DifficultyLevel`, `CourseFormat`, `Semester`
- Enums for type safety

---

### **Section 4: Tool Selection & LangGraph** (5-6 hours)
**3 notebooks** | **Prerequisites**: Sections 1-3

Build production agents with LangGraph, semantic tool selection, and state management.

**Notebooks**:
1. **Tools and LangGraph Fundamentals** - Tool creation, LangGraph basics, state management
2. **Redis University Course Advisor Agent** - Complete production agent with all features
3. **Course Advisor with Compression** - Enhanced agent demonstrating compression strategies

**Learning Outcomes**:
- Create and orchestrate multiple tools
- Build stateful agents with LangGraph
- Implement semantic tool selection
- Manage agent state and conversation flow
- Apply compression in production agents

**Reference Agent Components Used**:
- All data models and enums
- `CourseManager` for course operations
- `redis_config` for Redis connections

---

### **Section 5: Optimization & Production** (4-5 hours)
**3 notebooks** | **Prerequisites**: Sections 1-4 | **Status**: ✅ Complete

Optimize for production with token management, cost optimization, semantic routing, and caching.

**Notebooks**:
1. **Measuring and Optimizing Performance** - Token counting, cost tracking, performance metrics
2. **Scaling with Semantic Tool Selection** - 🆕 RedisVL Semantic Router & Semantic Cache
3. **Production Readiness and Quality Assurance** - Validation, monitoring, error handling

**Learning Outcomes**:
- Implement token counting and budget management
- Optimize context assembly for cost reduction
- 🆕 **Use RedisVL Semantic Router for production tool selection**
- 🆕 **Implement Semantic Cache for 92% latency reduction**
- Build production monitoring and analytics
- Handle errors and edge cases gracefully
- Deploy scalable AI agents

**🆕 New in Notebook 2**:
- **RedisVL Semantic Router**: Production-ready semantic routing (60% code reduction vs custom implementation)
- **RedisVL Semantic Cache**: Intelligent caching for tool selections (30-40% cache hit rate)
- **Performance**: 5ms cache hits vs 65ms cache misses (10-20x faster)
- **Industry Patterns**: Learn production-ready approaches, not custom implementations

**Reference Agent Components Used**:
- Optimization helpers: `count_tokens`, `estimate_token_budget`, `hybrid_retrieval`
- Production utilities: `create_summary_view`, `filter_tools_by_intent`

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
│   ├── section-4-tool-selection/       # Section 4 notebooks
│   └── section-5-optimization-production/  # Section 5 notebooks
│
└── reference-agent/                    # Production-ready reference implementation
    ├── README.md                       # Reference agent documentation
    ├── redis_context_course/           # Python package
    │   ├── __init__.py                 # Package exports
    │   ├── models.py                   # Data models (Course, StudentProfile, etc.)
    │   ├── course_manager.py           # Course storage and search
    │   ├── redis_config.py             # Redis configuration
    │   ├── tools.py                    # Tool creation helpers
    │   ├── optimization_helpers.py     # Production utilities
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
- **OpenAI API Key** ([get one here](https://platform.openai.com/api-keys))
- **8GB RAM minimum** (16GB recommended for Section 5)
- **5GB disk space** for dependencies and data

#### Optional
- **Jupyter Lab** (alternative to Jupyter Notebook)
- **VS Code** with Jupyter extension
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
- Use production-ready utilities

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
**Timeline**: 3-4 weeks (6-8 hours/week)

1. **Week 1**: Complete Section 1 (Foundations) and Section 2 (RAG)
2. **Week 2**: Work through Section 3 (Memory Systems for Context Engineering)
3. **Week 3**: Build agents in Section 4 (Tool Selection & LangGraph)
4. **Week 4**: Optimize in Section 5 (Production)

### For Experienced Developers
**Timeline**: 1-2 weeks (full-time) or 2-3 weeks (part-time)

- **Skip to Section 2** if familiar with context engineering basics
- **Jump to Section 3** if you've built RAG systems before
- **Start at Section 4** if you want to focus on LangGraph and agents

### Time Commitment Options

- **Intensive**: 1 week (full-time, 8 hours/day)
- **Standard**: 3-4 weeks (part-time, 6-8 hours/week)
- **Relaxed**: 6-8 weeks (casual, 3-4 hours/week)

### Learning Tips

1. **Start with Section 1** - Build foundational understanding
2. **Progress sequentially** - Each section builds on the previous
3. **Complete all exercises** - Hands-on practice is essential
4. **Experiment freely** - Modify code and test variations
5. **Build your own variations** - Apply patterns to your domain

---

## 🎯 Learning Outcomes

### By Section

**Section 1: Foundations**
- Understand the four context types (system, user, retrieved, conversation)
- Learn context assembly strategies
- Grasp the importance of context engineering

**Section 2: Retrieved Context Engineering**
- Implement vector embeddings and semantic search
- Build RAG systems with Redis and RedisVL
- Create course recommendation engines

**Section 3: Memory Systems for Context Engineering**
- Master dual memory systems (working + long-term)
- Implement memory extraction strategies
- Apply working memory compression techniques

**Section 4: Tool Selection & LangGraph**
- Build stateful agents with LangGraph
- Implement semantic tool selection
- Manage complex agent workflows

**Section 5: Optimization & Production**
- Optimize token usage and costs
- Implement production monitoring
- Deploy scalable AI agents

### Complete Program Outcomes

By completing this course, you will be able to:

- ✅ **Design context-aware AI agents** from scratch
- ✅ **Implement production-ready memory systems** with Agent Memory Server
- ✅ **Build RAG applications** using Redis and vector search
- ✅ **Optimize context assembly** for cost and performance
- ✅ **Create stateful agents** with LangGraph
- ✅ **Deploy scalable AI systems** to production
- ✅ **Apply context engineering patterns** to any domain

---

## 🏗️ Reference Agent Package

The `redis-context-course` package provides production-ready components used throughout the course.

### What's Included

**Core Classes**:
- `CourseManager` - Course storage and semantic search
- `RedisConfig` - Redis configuration and connection management
- Data models: `Course`, `StudentProfile`, `DifficultyLevel`, etc.

**Tools** (Section 2):
- `create_course_tools()` - Course search and recommendation tools
- `create_memory_tools()` - Memory management tools
- `select_tools_by_keywords()` - Simple tool filtering

**Optimization Helpers** (Section 5):
- `count_tokens()` - Token counting for any model
- `estimate_token_budget()` - Budget breakdown and estimation
- `hybrid_retrieval()` - Combine summary + search
- `filter_tools_by_intent()` - Intent-based tool filtering
- And more...

### Educational Approach

The course demonstrates **building agents from scratch** using these components as building blocks, rather than using pre-built agents. This approach:

- ✅ Teaches fundamental patterns
- ✅ Provides flexibility for customization
- ✅ Shows both educational and production-ready code
- ✅ Enables adaptation to different use cases

For detailed component usage analysis, see [notebooks/REFERENCE_AGENT_USAGE_ANALYSIS.md](notebooks/REFERENCE_AGENT_USAGE_ANALYSIS.md).

---

## 🌍 Real-World Applications

The patterns and techniques learned apply directly to:

### Enterprise AI Systems
- **Customer service chatbots** with sophisticated memory and tool routing
- **Technical support agents** with intelligent knowledge retrieval
- **Sales assistants** with personalized recommendations
- **Knowledge management systems** with optimized context assembly

### Educational Technology
- **Personalized learning assistants** that remember student progress
- **Academic advising systems** with comprehensive course knowledge
- **Intelligent tutoring systems** with adaptive responses
- **Student support chatbots** with institutional knowledge

### Production AI Services
- **Multi-tenant SaaS AI platforms** with user isolation and scaling
- **API-based AI services** with cost optimization and monitoring
- **Scalable conversation systems** with memory persistence
- **Enterprise AI deployments** with comprehensive analytics

---

## 📊 Expected Results

### Measurable Improvements
- **50-70% token reduction** through intelligent context optimization
- **Semantic tool selection** replacing brittle keyword matching
- **Cross-session memory** enabling natural conversation continuity
- **Production scalability** supporting thousands of concurrent users

### Skills Gained
- 💼 **Portfolio project** demonstrating context engineering mastery
- 📊 **Performance monitoring expertise** for production deployment
- 🛠️ **Production-ready patterns** for building AI agents
- 🎯 **Cost optimization skills** for managing LLM expenses

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

## 🤝 Contributing

This is an educational resource. Contributions that improve clarity, add examples, or extend the reference implementation are welcome!

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Areas for Contribution
- Additional notebook examples
- Improved documentation
- Bug fixes and corrections
- New optimization patterns
- Extended reference agent features

---

## 📝 Course Metadata

**Version**: 2.0
**Last Updated**: November 2025
**Maintainer**: Redis AI Resources Team
**License**: MIT

**Technologies**:
- Python 3.10+
- Redis 8.0+
- LangChain 0.2+
- LangGraph 0.2+
- Agent Memory Server 0.12.3+
- OpenAI GPT-4

**Course Stats**:
- **Duration**: 18-23 hours
- **Sections**: 5
- **Notebooks**: 12
- **Hands-on Exercises**: 30+
- **Production Patterns**: 15+

---

**🎉 Ready to transform your context engineering skills? [Start your journey today!](#-quick-start-5-minutes)**

---

*This comprehensive course provides hands-on education in context engineering - taking you from fundamentals to production-ready expertise through a single, evolving project that demonstrates real-world impact.*
