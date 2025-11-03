# Context Engineering Course - Notebooks

**Hands-on Jupyter notebooks for learning production-ready context engineering.**

> 📚 **Main Course Documentation**: See **[../README.md](../README.md)** for complete course overview, setup instructions, and syllabus.
>
> 📖 **Course Syllabus**: See **[../COURSE_SUMMARY.md](../COURSE_SUMMARY.md)** for detailed learning outcomes and course structure.

---

## 📖 About These Notebooks

This directory contains the hands-on Jupyter notebooks for the Context Engineering course. The notebooks are organized into 5 sections that progressively build your skills from fundamentals to production deployment.

### Quick Links
- **[Course Overview & Setup](../README.md)** - Start here for setup and course introduction
- **[Course Syllabus](../COURSE_SUMMARY.md)** - Complete syllabus with learning outcomes
- **[Setup Guide](SETUP_GUIDE.md)** - Detailed setup instructions and troubleshooting
- **[Reference Agent Usage](REFERENCE_AGENT_USAGE_ANALYSIS.md)** - Component usage analysis

---

## 🚀 Quick Start

**Already set up?** Jump right in:

```bash
# Start Jupyter from the context-engineering directory
cd python-recipes/context-engineering
jupyter notebook notebooks_v2/

# Open: section-1-context-engineering-foundations/01_what_is_context_engineering.ipynb
```

**Need to set up?** Follow the [5-minute quick start](../README.md#-quick-start-5-minutes) in the main README.

**Having issues?** Check the [Setup Guide](SETUP_GUIDE.md) for detailed instructions and troubleshooting.

---

## 📚 Notebook Sections Overview

### Learning Journey

```
Section 1: Foundations → Section 2: RAG → Section 3: Memory → Section 4: Tools → Section 5: Production
     ↓                        ↓                 ↓                  ↓                  ↓
Basic Concepts        → RAG Agent      → Memory Agent    → Multi-Tool Agent → Production Agent
(2-3 hrs)              (3-4 hrs)        (4-5 hrs)         (5-6 hrs)          (4-5 hrs)
```

**🏆 End Result**: A complete, production-ready AI agent that can handle thousands of users with sophisticated memory, intelligent tool routing, and optimized performance.

> 💡 **For detailed learning outcomes and syllabus**, see [../COURSE_SUMMARY.md](../COURSE_SUMMARY.md)

## ✨ What Makes This Approach Unique

### 1. 📈 Progressive Complexity
- **Same agent evolves** through all sections - see your work compound
- **Each section builds directly** on the previous one
- **Clear progression** from educational concepts to production deployment
- **Investment in learning** pays off across all sections

### 2. 🏗️ Professional Foundation
- **Reference-agent integration** - Built on production-ready architecture
- **Type-safe Pydantic models** throughout all sections
- **Industry best practices** from day one
- **Real-world patterns** that work in production systems

### 3. 🛠️ Hands-On Learning
- **Working code** in every notebook cell
- **Jupyter-friendly** interactive development
- **Immediate results** and feedback
- **Experimentation encouraged** - modify and test variations

### 4. 🌍 Real-World Relevance
- **Production patterns** used in enterprise AI systems
- **Scalable architecture** ready for deployment
- **Portfolio-worthy** final project
- **Career-relevant** skills and experience

## 📚 Complete Course Syllabus

### 🎯 **Section 1: Foundations**
**Goal**: Master context engineering basics and the four context types
**Duration**: ~2-3 hours
**Prerequisites**: Basic Python knowledge, familiarity with LLMs

**What You'll Build**:
- Understanding of the four types of context (system, user, retrieved, conversation)
- Foundation patterns for context assembly and management
- Conceptual framework for building context-aware AI systems

**Key Learning**:
- Context engineering fundamentals and why it matters
- The four context types and when to use each
- Foundation for building sophisticated AI systems

**Notebooks**:
1. `01_what_is_context_engineering.ipynb` - Core concepts and why context engineering matters
2. `02_context_assembly_strategies.ipynb` - Hands-on exploration of each context type

**Reference Agent Components Used**: None (conceptual foundation)

### 🤖 **Section 2: Retrieved Context Engineering**
**Goal**: Build a complete RAG system with vector search and retrieval
**Duration**: ~3-4 hours
**Prerequisites**: Section 1 completed, Redis running, OpenAI API key

**What You'll Build**:
- Complete RAG pipeline (Retrieval + Augmentation + Generation)
- Vector-based course search using Redis and RedisVL
- Context assembly from multiple information sources
- Course recommendation system with semantic search

**Key Learning**:
- RAG architecture and implementation patterns
- Vector similarity search for intelligent retrieval
- Redis as a vector database for AI applications
- Course data generation and ingestion workflows

**Notebooks**:
1. `01_rag_retrieved_context_in_practice.ipynb` - Complete RAG system with Redis University Course Advisor

**Reference Agent Components Used**:
- `CourseGenerator` - Generate sample course data
- `CourseIngestionPipeline` - Ingest courses into Redis
- `CourseManager` - Course search and recommendations
- `redis_config` - Redis configuration and connection

### 🧠 **Section 3: Memory Architecture**
**Goal**: Master memory management with Agent Memory Server
**Duration**: ~4-5 hours
**Prerequisites**: Section 2 completed, Agent Memory Server running

**What You'll Build**:
- Dual memory system (working memory + long-term memory)
- Memory extraction strategies (discrete, summary, preferences)
- Memory-enhanced RAG with semantic retrieval
- Working memory compression for long conversations

**Key Learning**:
- Working vs long-term memory patterns and use cases
- Memory extraction strategies and when to use each
- Agent Memory Server integration and configuration
- Memory compression strategies (truncation, priority-based, summarization)
- Session management and cross-session persistence

**Notebooks**:
1. `01_memory_fundamentals_and_integration.ipynb` - Memory basics and Agent Memory Server integration
2. `02_memory_enhanced_rag_and_agents.ipynb` - Memory extraction strategies in practice
3. `03_memory_management_long_conversations.ipynb` - Compression strategies for long conversations

**Reference Agent Components Used**:
- `redis_config` - Redis configuration
- `CourseManager` - Course management
- `Course`, `StudentProfile` - Data models
- `DifficultyLevel`, `CourseFormat`, `Semester` - Enums

---

### 🔧 **Section 4: Tool Selection & LangGraph Agents**
**Goal**: Build production agents with LangGraph and intelligent tool selection
**Duration**: ~5-6 hours
**Prerequisites**: Section 3 completed, understanding of LangGraph basics

**What You'll Build**:
- LangGraph-based stateful agent workflows
- Course advisor agent with multiple tools
- Memory-integrated agent with Agent Memory Server
- Working memory compression for long conversations

**Key Learning**:
- LangGraph StateGraph and agent workflows
- Tool creation and integration patterns
- Agent Memory Server integration with LangGraph
- Working memory compression strategies in production agents
- State management and conversation flow control

**Notebooks**:
1. `01_tools_and_langgraph_fundamentals.ipynb` - LangGraph basics and tool integration
2. `02_redis_university_course_advisor_agent.ipynb` - Complete course advisor agent
3. `02_redis_university_course_advisor_agent_with_compression.ipynb` - Agent with memory compression

**Reference Agent Components Used**:
- `CourseManager` - Course search and recommendations
- `StudentProfile`, `DifficultyLevel`, `CourseFormat` - Data models

**Note**: This section demonstrates building custom agents rather than using the reference `ClassAgent` directly, showing students how to build production agents from scratch.

---

### ⚡ **Section 5: Optimization & Production**
**Goal**: Optimize agents for production deployment
**Duration**: ~4-5 hours
**Prerequisites**: Section 4 completed

**What You'll Build**:
- Performance measurement and optimization techniques
- Semantic tool selection at scale
- Production readiness checklist and quality assurance
- Cost optimization and monitoring

**Key Learning**:
- Performance profiling and optimization
- Semantic tool selection with embeddings
- Production deployment best practices
- Quality assurance and testing strategies
- Cost management and token optimization

**Notebooks**:
1. `01_measuring_optimizing_performance.ipynb` - Performance measurement and optimization
2. `02_scaling_semantic_tool_selection.ipynb` - Advanced tool selection strategies
3. `03_production_readiness_quality_assurance.ipynb` - Production deployment guide

**Reference Agent Components Used**:
- Optimization helpers (to be demonstrated)
- Production patterns from reference agent

**Status**: ⏳ Section 5 notebooks are in development

---

## 📦 Reference Agent Package

The course uses the `redis-context-course` reference agent package, which provides production-ready components for building context-aware AI agents.

### What's in the Reference Agent?

**Core Components** (used in notebooks):
- `CourseManager` - Course search, recommendations, and catalog management
- `redis_config` - Redis configuration and connection management
- Data models: `Course`, `StudentProfile`, `DifficultyLevel`, `CourseFormat`, `Semester`
- Scripts: `CourseGenerator`, `CourseIngestionPipeline`

**Advanced Components** (for production use):
- `ClassAgent` - Complete LangGraph-based agent implementation
- `AugmentedClassAgent` - Enhanced agent with additional features
- Tool creators: `create_course_tools`, `create_memory_tools`
- Optimization helpers: `count_tokens`, `estimate_token_budget`, `hybrid_retrieval`, etc.

### How the Course Uses the Reference Agent

**Educational Approach**: The notebooks demonstrate **building agents from scratch** using reference agent components as building blocks, rather than using the pre-built `ClassAgent` directly.

**Why?** This approach helps you:
- ✅ Understand how agents work internally
- ✅ Learn to build custom agents for your use cases
- ✅ See production patterns in action
- ✅ Gain hands-on experience with LangGraph and memory systems

**Component Usage by Section**:
- **Section 1**: None (conceptual foundation)
- **Section 2**: CourseManager, redis_config, data generation scripts
- **Section 3**: CourseManager, redis_config, data models
- **Section 4**: CourseManager, data models
- **Section 5**: Optimization helpers (in development)

For a detailed analysis of reference agent usage, see [REFERENCE_AGENT_USAGE_ANALYSIS.md](REFERENCE_AGENT_USAGE_ANALYSIS.md).

For reference agent documentation, see [../reference-agent/README.md](../reference-agent/README.md).

---

## 🏗️ Technical Architecture Evolution

### **Agent Architecture Progression**

#### **Section 2: Basic RAG**
```python
class SimpleRAGAgent:
    - CourseManager integration
    - Vector similarity search  
    - Context assembly
    - Basic conversation history
```

#### **Section 3: Memory-Enhanced**
```python
class MemoryEnhancedAgent:
    - Redis-based persistence
    - Working vs long-term memory
    - Memory consolidation
    - Cross-session continuity
```

#### **Section 4: Multi-Tool**
```python
class MultiToolAgent:
    - Specialized tool suite
    - Semantic tool selection
    - Intent classification
    - Memory-aware routing
```

#### **Section 5: Production-Optimized**
```python
class OptimizedProductionAgent:
    - Context optimization
    - Performance monitoring
    - Caching system
    - Cost tracking
    - Scalability support
```

## 🎓 Learning Outcomes by Section

### **After Section 1: Foundations**
Students can:
- ✅ Explain the four context types and when to use each
- ✅ Understand context engineering principles and best practices
- ✅ Design context strategies for AI applications
- ✅ Identify context engineering patterns in production systems

### **After Section 2: Retrieved Context Engineering**
Students can:
- ✅ Build complete RAG systems with Redis and RedisVL
- ✅ Implement vector similarity search for intelligent retrieval
- ✅ Generate and ingest course data into Redis
- ✅ Create course recommendation systems with semantic search

### **After Section 3: Memory Architecture**
Students can:
- ✅ Integrate Agent Memory Server with AI agents
- ✅ Implement dual memory systems (working + long-term)
- ✅ Apply memory extraction strategies (discrete, summary, preferences)
- ✅ Implement memory compression for long conversations
- ✅ Design cross-session conversation continuity

### **After Section 4: Tool Selection & LangGraph**
Students can:
- ✅ Build stateful agents with LangGraph StateGraph
- ✅ Create and integrate multiple tools in agents
- ✅ Implement memory-integrated agents with Agent Memory Server
- ✅ Apply working memory compression in production agents
- ✅ Design conversation flow control and state management

### **After Section 5: Optimization & Production**
Students can:
- ✅ Measure and optimize agent performance
- ✅ Implement semantic tool selection at scale
- ✅ Apply production deployment best practices
- ✅ Build quality assurance and testing strategies
- ✅ Optimize costs and token usage

### **Complete Program Outcomes**
Students will have:
- 🏆 **Production-ready AI agent** with memory, tools, and optimization
- 📈 **Hands-on experience** with Redis, LangGraph, and Agent Memory Server
- 🔧 **Real-world skills** applicable to enterprise AI systems
- 💼 **Portfolio project** demonstrating context engineering mastery

---

## 📋 System Requirements

### Required
- **Python 3.10+** (Python 3.8+ may work but 3.10+ recommended)
- **Docker Desktop** (for Redis and Agent Memory Server)
- **OpenAI API Key** ([get one here](https://platform.openai.com/api-keys))
- **8GB RAM minimum** (16GB recommended for Section 5)
- **5GB disk space** for dependencies and data

### Optional
- **Jupyter Lab** (alternative to Jupyter Notebook)
- **VS Code** with Jupyter extension
- **Redis Insight** for visualizing Redis data

---

## 🛠️ Detailed Setup Instructions

For complete setup instructions including troubleshooting, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

### Quick Setup Summary

1. **Set environment variables** (`.env` file with OpenAI API key)
2. **Start services** (`docker-compose up -d`)
3. **Install dependencies** (`pip install -r requirements.txt`)
4. **Install reference agent** (`cd reference-agent && pip install -e .`)
5. **Start Jupyter** (`jupyter notebook notebooks_v2/`)

### Verification

After setup, verify everything works:

```bash
# Check Redis
docker exec redis-context-engineering redis-cli ping  # Should return: PONG

# Check Agent Memory Server
curl http://localhost:8088/v1/health  # Should return: {"now":<timestamp>}

# Check Python packages
python -c "import redis_context_course; print('✅ Reference agent installed')"
```

---

## 📖 Recommended Learning Path

### For Beginners
1. **Start with Section 1** - Build conceptual foundation
2. **Complete Section 2** - Get hands-on with RAG
3. **Work through Section 3** - Master memory systems
4. **Build in Section 4** - Create production agents
5. **Optimize in Section 5** - Deploy to production

### For Experienced Developers
- **Skip to Section 2** if familiar with context engineering basics
- **Jump to Section 3** if you've built RAG systems before
- **Start at Section 4** if you want to focus on LangGraph and agents

### Time Commitment
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

## 🔧 Troubleshooting

### **Common Issues and Solutions**

#### **OpenAI API Key Issues**
```
Error: "OPENAI_API_KEY not found. Please create a .env file..."
```
**Solutions:**
1. Create `.env` file with `OPENAI_API_KEY=your_key_here`
2. Set environment variable: `export OPENAI_API_KEY=your_key_here`
3. Get your API key from: https://platform.openai.com/api-keys

#### **Redis Connection Issues**
```
Error: "Connection refused" or "Redis not available"
```
**Solutions:**
1. Start Redis: `docker run -d -p 6379:6379 redis/redis-stack`
2. Check Redis URL in `.env`: `REDIS_URL=redis://localhost:6379`
3. Some features may work without Redis (varies by notebook)

#### **Import Errors**
```
Error: "No module named 'redis_context_course'"
```
**Solutions:**
1. Install reference agent: `pip install -e ../../../reference-agent`
2. Check Python path in notebook cells
3. Restart Jupyter kernel

#### **Notebook JSON Errors**
```
Error: "NotJSONError" or "Notebook does not appear to be JSON"
```
**Solutions:**
1. All notebooks are now JSON-valid (fixed in this update)
2. Try refreshing the browser
3. Restart Jupyter server

### **Getting Help**
- **Check notebook output** - Error messages include troubleshooting tips
- **Environment validation** - Notebooks validate setup and provide clear guidance
- **Standard tools** - Uses industry-standard `python-dotenv` for configuration

## 🌍 Real-World Applications

The patterns and techniques learned apply directly to:

### **Enterprise AI Systems**
- **Customer service chatbots** with sophisticated memory and tool routing
- **Technical support agents** with intelligent knowledge retrieval
- **Sales assistants** with personalized recommendations and context
- **Knowledge management systems** with optimized context assembly

### **Educational Technology**
- **Personalized learning assistants** that remember student progress
- **Academic advising systems** with comprehensive course knowledge
- **Intelligent tutoring systems** with adaptive responses
- **Student support chatbots** with institutional knowledge

### **Production AI Services**
- **Multi-tenant SaaS AI platforms** with user isolation and scaling
- **API-based AI services** with cost optimization and monitoring
- **Scalable conversation systems** with memory persistence
- **Enterprise AI deployments** with comprehensive analytics

## 📊 Expected Results and Benefits

### **Measurable Improvements**
- **50-70% token reduction** through intelligent context optimization
- **Semantic tool selection** replacing brittle keyword matching
- **Cross-session memory** enabling natural conversation continuity
- **Production scalability** supporting thousands of concurrent users

### **Cost Optimization**
- **Significant API cost savings** through context compression
- **Efficient caching** reducing redundant LLM calls
- **Smart token budgeting** preventing cost overruns
- **Performance monitoring** enabling continuous optimization

### **Professional Skills**
- **Production-ready AI development** with industry best practices
- **Scalable system architecture** for enterprise deployment
- **Performance optimization** and cost management expertise
- **Advanced context engineering** techniques for complex applications

## 📁 Project Structure

```
enhanced-integration/
├── README.md                           # This comprehensive guide
├── PROGRESSIVE_PROJECT_PLAN.md         # Detailed project planning
├── PROGRESSIVE_PROJECT_COMPLETE.md     # Project completion summary
├── setup.py                            # One-command environment setup
├── setup.sh                            # Alternative shell setup script
├── .env.example                        # Environment configuration template
│
├── section-1-context-engineering-foundations/  # Foundation concepts
│   ├── 01_what_is_context_engineering.ipynb
│   ├── 02_context_assembly_strategies.ipynb
│   └── README.md
│
├── section-2-retrieved-context-engineering/  # Complete RAG system
│   ├── 01_building_your_rag_agent.ipynb
│   └── README.md
│
├── section-4-tool-selection/           # Multi-tool intelligence
│   ├── 01_building_multi_tool_intelligence.ipynb
│   └── README.md
│
├── section-5-context-optimization/     # Production optimization
│   ├── 01_optimizing_for_production.ipynb
│   └── README.md
│
└── old/                               # Archived previous versions
    ├── README.md                      # Archive explanation
    └── [previous notebook versions]   # Reference materials
```

## 🎯 Why This Progressive Approach Works

### **1. Compound Learning**
- **Same agent evolves** - Students see their work improve continuously
- **Skills build on each other** - Each section leverages previous learning
- **Investment pays off** - Time spent early benefits all later sections
- **Natural progression** - Logical flow from simple to sophisticated

### **2. Production Readiness**
- **Real architecture** - Built on production-ready reference-agent
- **Industry patterns** - Techniques used in enterprise systems
- **Scalable design** - Architecture that handles real-world complexity
- **Professional quality** - Code and patterns ready for production use

### **3. Hands-On Mastery**
- **Working code** - Every concept demonstrated with runnable examples
- **Immediate feedback** - See results of every change instantly
- **Experimentation friendly** - Easy to modify and test variations
- **Problem-solving focus** - Learn by solving real challenges

### **4. Measurable Impact**
- **Quantified improvements** - See exact performance gains
- **Cost optimization** - Understand business impact of optimizations
- **Performance metrics** - Track and optimize system behavior
- **Production monitoring** - Real-world performance indicators

## 🏆 Success Metrics

By completing this progressive learning path, you will have:

### **Technical Achievements**
- ✅ Built 5 increasingly sophisticated AI agents
- ✅ Implemented production-ready architecture patterns
- ✅ Mastered context engineering best practices
- ✅ Created scalable, cost-effective AI systems

### **Professional Skills**
- ✅ Production AI development experience
- ✅ System optimization and performance tuning
- ✅ Cost management and efficiency optimization
- ✅ Enterprise-grade monitoring and analytics

### **Portfolio Project**
- ✅ Complete Redis University Course Advisor
- ✅ Production-ready codebase with comprehensive features
- ✅ Demonstrated scalability and optimization
- ✅ Professional documentation and testing

**🎉 Ready to transform your context engineering skills? Start your journey today!**

---

## 📚 Additional Resources

### Documentation
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions and troubleshooting
- **[REFERENCE_AGENT_USAGE_ANALYSIS.md](REFERENCE_AGENT_USAGE_ANALYSIS.md)** - Analysis of reference agent usage across notebooks
- **[Reference Agent README](../reference-agent/README.md)** - Complete reference agent documentation
- **[Main Course README](../README.md)** - Top-level context engineering documentation

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
**Maintainer**: Redis AI Resources Team
**License**: MIT

**Technologies**:
- Python 3.10+
- Redis 8.0+
- LangChain 0.2+
- LangGraph 0.2+
- Agent Memory Server 0.12.3+
- OpenAI GPT-4

---

**This progressive learning path provides the most comprehensive, hands-on education in context engineering available - taking you from fundamentals to production-ready expertise through a single, evolving project that demonstrates real-world impact.**
