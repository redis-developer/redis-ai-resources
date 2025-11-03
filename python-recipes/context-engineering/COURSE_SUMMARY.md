# Context Engineering Course - Complete Syllabus

**A comprehensive, hands-on course teaching production-ready context engineering for AI agents.**

---

## 📊 Course Overview

**Duration**: 18-23 hours
**Format**: Self-paced, hands-on Jupyter notebooks
**Level**: Intermediate to Advanced
**Prerequisites**: Python, basic AI/ML understanding, familiarity with LLMs

### What You'll Build

A complete **Redis University Course Advisor Agent** that:
- Helps students find courses using semantic search with Redis and RedisVL
- Remembers student preferences and goals across sessions using Agent Memory Server
- Provides personalized recommendations based on student profile
- Uses intelligent tool selection with LangGraph
- Optimizes context for production deployment with cost management

### Technologies Used

- **Python 3.10+** - Primary programming language
- **Redis 8.0+** - Vector storage and caching
- **LangChain 0.2+** - LLM application framework
- **LangGraph 0.2+** - Stateful agent workflows
- **Agent Memory Server 0.12.3+** - Memory management
- **OpenAI GPT-4** - Language model
- **RedisVL** - Vector search library
- **Pydantic** - Data validation and models

---

## 📖 Course Structure

### **Section 1: Context Engineering Foundations** (2-3 hours)

**Notebooks**: 2 | **Prerequisites**: None

#### Notebooks
1. **What is Context Engineering?** - Four context types, principles, and architecture
2. **Context Assembly Strategies** - How to combine contexts effectively

#### Learning Outcomes
- ✅ Understand the four context types (system, user, retrieved, conversation)
- ✅ Learn context assembly strategies and patterns
- ✅ Grasp the importance of context engineering in AI systems
- ✅ Understand the role of context in LLM performance

#### Key Concepts
- **Four Context Types**: System, User, Retrieved, Conversation
- **Context Assembly**: How to combine different context sources
- **Context Optimization**: Managing context window limits
- **Production Considerations**: Scalability, cost, performance

#### Reference Agent Components Used
None (pure theory and conceptual foundation)

---

### **Section 2: Retrieved Context Engineering** (3-4 hours)

**Notebooks**: 1 | **Prerequisites**: Section 1

#### Notebooks
1. **Engineering Retrieved Context with RAG** - Vector embeddings, semantic search, course recommendations

#### Learning Outcomes
- ✅ Implement vector embeddings with OpenAI
- ✅ Build semantic search with Redis and RedisVL
- ✅ Create a course recommendation system
- ✅ Understand RAG architecture patterns
- ✅ Ingest and query vector data

#### Key Concepts
- **Vector Embeddings**: Converting text to numerical representations
- **Semantic Search**: Finding similar items using vector similarity
- **RAG Pattern**: Retrieval Augmented Generation
- **Redis Vector Search**: Using Redis for vector storage and retrieval
- **Course Catalog Management**: Storing and querying course data

#### Reference Agent Components Used
- `CourseManager` - Course storage and semantic search
- `redis_config` - Redis configuration and connection management
- `CourseGenerator` - Generate sample course data
- `CourseIngestionPipeline` - Ingest courses into Redis

#### Key Patterns
- Vector index creation and management
- Semantic search with similarity scoring
- Hybrid search (keyword + semantic)
- Course recommendation algorithms

---

### **Section 3: Memory Systems for Context Engineering** (4-5 hours)

**Notebooks**: 3 | **Prerequisites**: Sections 1-2

#### Notebooks
1. **Working and Long-Term Memory** - Working memory, long-term memory, Agent Memory Server
2. **Combining Memory with Retrieved Context** - Combining memory with RAG, building stateful agents
3. **Managing Long Conversations with Compression Strategies** - Compression strategies for long conversations

#### Learning Outcomes
- ✅ Implement working memory (session-scoped) and long-term memory (cross-session)
- ✅ Use Agent Memory Server for automatic memory extraction
- ✅ Apply memory extraction strategies (discrete, summary, preferences)
- ✅ Implement working memory compression (truncation, priority-based, summarization)
- ✅ Build memory-enhanced RAG systems
- ✅ Create stateful agents with persistent memory

#### Key Concepts
- **Dual Memory System**: Working memory + Long-term memory
- **Working Memory**: Session-scoped, task-focused context
- **Long-term Memory**: Cross-session, persistent knowledge
- **Memory Extraction**: Automatic extraction of important facts
- **Memory Extraction Strategies**: Discrete (facts), Summary (summaries), Preferences (user preferences)
- **Working Memory Compression**: Truncation, Priority-Based, Summarization
- **Agent Memory Server**: Production-ready memory management

#### Reference Agent Components Used
- Data models: `Course`, `StudentProfile`, `DifficultyLevel`, `CourseFormat`, `Semester`
- Enums for type safety and validation
- `CourseManager` for course operations

#### Key Patterns
- Memory extraction strategies (discrete vs. summary)
- Working memory compression techniques
- Cross-session memory persistence
- Memory-enhanced RAG workflows
- Automatic memory extraction with Agent Memory Server

---

### **Section 4: Tool Selection & LangGraph** (5-6 hours)

**Notebooks**: 3 | **Prerequisites**: Sections 1-3

#### Notebooks
1. **Tools and LangGraph Fundamentals** - Tool creation, LangGraph basics, state management
2. **Redis University Course Advisor Agent** - Complete production agent with all features
3. **Course Advisor with Compression** - Enhanced agent demonstrating compression strategies

#### Learning Outcomes
- ✅ Create and orchestrate multiple tools
- ✅ Build stateful agents with LangGraph
- ✅ Implement semantic tool selection
- ✅ Manage agent state and conversation flow
- ✅ Apply compression in production agents
- ✅ Build complete production-ready agents

#### Key Concepts
- **Tool Creation**: Defining tools with schemas and descriptions
- **LangGraph**: Stateful agent workflow framework
- **State Management**: Managing agent state across turns
- **Tool Orchestration**: Coordinating multiple tools
- **Semantic Tool Selection**: Choosing tools based on context
- **Production Agents**: Building scalable, production-ready agents

#### Reference Agent Components Used
- All data models and enums
- `CourseManager` for course operations
- `redis_config` for Redis connections
- Agent Memory Server integration

#### Key Patterns
- LangGraph StateGraph for agent workflows
- Tool binding and invocation
- State persistence with checkpointers
- Multi-turn conversations
- Working memory compression in production

---

### **Section 5: Optimization & Production** (4-5 hours)

**Notebooks**: 3 | **Prerequisites**: Sections 1-4 | **Status**: ✅ Complete

#### Notebooks
1. **Measuring and Optimizing Performance** - Token counting, cost tracking, performance metrics
2. **Scaling with Semantic Tool Selection** - 🆕 **RedisVL Semantic Router & Semantic Cache**
3. **Production Readiness and Quality Assurance** - Validation, monitoring, error handling

#### Learning Outcomes
- ✅ Implement token counting and budget management
- ✅ Optimize context assembly for cost reduction
- ✅ 🆕 **Use RedisVL Semantic Router for production tool selection**
- ✅ 🆕 **Implement Semantic Cache for 92% latency reduction**
- ✅ 🆕 **Apply industry-standard semantic routing patterns**
- ✅ Build production monitoring and analytics
- ✅ Handle errors and edge cases gracefully
- ✅ Deploy scalable AI agents
- ✅ Implement advanced tool selection strategies

#### Key Concepts
- **Token Counting**: Accurate token estimation for cost management
- **Token Budgets**: Allocating context window space efficiently
- **Cost Optimization**: Reducing LLM API costs
- **🆕 Semantic Routing**: Production-ready tool selection with RedisVL
- **🆕 Semantic Caching**: Intelligent caching for similar queries
- **Performance Monitoring**: Tracking agent performance metrics
- **Production Deployment**: Scaling to thousands of users
- **Error Handling**: Graceful degradation and recovery

#### 🆕 RedisVL Extensions Used (Notebook 2)
- **`SemanticRouter`**: Production-ready semantic routing for tool selection
  - Automatic index creation and management
  - Route-based tool organization
  - Distance threshold configuration
  - Serialization support (YAML/dict)
  - 60% code reduction vs custom implementation

- **`SemanticCache`**: Intelligent caching for LLM operations
  - Semantic similarity-based cache matching
  - TTL policies for cache expiration
  - Filterable fields for multi-tenant scenarios
  - 30-40% cache hit rate typical
  - 92% latency reduction on cache hits (5ms vs 65ms)

#### Reference Agent Components Used
- Optimization helpers: `count_tokens`, `estimate_token_budget`, `hybrid_retrieval`
- Production utilities: `create_summary_view`, `filter_tools_by_intent`
- `classify_intent_with_llm` - LLM-based intent classification
- `extract_references` - Reference extraction for grounding
- `format_context_for_llm` - Context formatting utilities

#### Production Patterns Demonstrated
```python
# Semantic Router Pattern (Notebook 2)
from redisvl.extensions.router import Route, SemanticRouter

# Define routes for tools
route = Route(
    name="search_courses",
    references=["Find courses", "Search catalog", ...],
    metadata={"tool": search_tool},
    distance_threshold=0.3
)

# Initialize router (handles everything automatically)
router = SemanticRouter(
    name="tool-router",
    routes=[route1, route2, ...],
    redis_url=REDIS_URL
)

# Select tools (one line!)
matches = router.route_many(query, max_k=3)
selected_tools = [m.metadata["tool"] for m in matches]

# Semantic Cache Pattern (Notebook 2)
from redisvl.extensions.llmcache import SemanticCache

# Initialize cache
cache = SemanticCache(
    name="tool_selection_cache",
    distance_threshold=0.1,
    ttl=3600
)

# Check cache first (fast path)
if cached := cache.check(prompt=query):
    return cached[0]["response"]  # 5ms

# Cache miss - compute and store (slow path)
result = compute_expensive_operation(query)  # 65ms
cache.store(prompt=query, response=result)
```

#### Key Patterns
- Token budget estimation and tracking
- Hybrid retrieval (summary + targeted search)
- Tool filtering by intent
- Structured view creation for efficiency
- Production monitoring and analytics

---

## 🎯 Complete Learning Outcomes

By completing this course, you will be able to:

### Technical Skills
- ✅ **Design context-aware AI agents** from scratch
- ✅ **Implement production-ready memory systems** with Agent Memory Server
- ✅ **Build RAG applications** using Redis and vector search
- ✅ **Optimize context assembly** for cost and performance
- ✅ **Create stateful agents** with LangGraph
- ✅ **Deploy scalable AI systems** to production
- ✅ **Apply context engineering patterns** to any domain

### Professional Skills
- ✅ Production AI development experience
- ✅ System optimization and performance tuning
- ✅ Cost management and efficiency optimization
- ✅ Enterprise-grade monitoring and analytics
- ✅ Scalable architecture design
- ✅ Production deployment best practices

### Portfolio Project
- ✅ Complete Redis University Course Advisor
- ✅ Production-ready codebase with comprehensive features
- ✅ Demonstrated scalability and optimization
- ✅ Professional documentation and testing

---

## 📦 Reference Agent Package

The `redis-context-course` package provides production-ready components used throughout the course.

### Core Modules

**`models.py`**
- `Course` - Course data model with validation
- `StudentProfile` - Student information and preferences
- `DifficultyLevel`, `CourseFormat`, `Semester` - Enums for type safety
- `CourseRecommendation`, `AgentResponse` - Response models
- `Prerequisite`, `CourseSchedule`, `Major` - Additional models

**`course_manager.py`**
- Course catalog management with Redis
- Vector search for semantic course discovery
- Course recommendation algorithms
- RedisVL integration for vector operations

**`redis_config.py`**
- Redis connection management
- Vector index configuration
- Environment variable handling
- Connection pooling and error handling

**`tools.py`** (Used in Section 4)
- `create_course_tools()` - Search, get details, check prerequisites
- `create_memory_tools()` - Store and search memories
- `select_tools_by_keywords()` - Simple tool filtering

**`optimization_helpers.py`** (Used in Section 5)
- `count_tokens()` - Token counting for any model
- `estimate_token_budget()` - Budget breakdown and estimation
- `hybrid_retrieval()` - Combine summary + targeted search
- `create_summary_view()` - Structured summaries for efficiency
- `create_user_profile_view()` - User profile generation
- `filter_tools_by_intent()` - Keyword-based tool filtering
- `classify_intent_with_llm()` - LLM-based intent classification
- `extract_references()` - Find grounding needs in queries
- `format_context_for_llm()` - Combine context sources

### Scripts

**`scripts/generate_courses.py`**
- Generate realistic course catalog data
- Create diverse course offerings
- Populate with prerequisites and schedules

**`scripts/ingest_courses.py`**
- Ingest courses into Redis
- Create vector embeddings
- Build vector search index

### Examples

**`examples/basic_usage.py`**
- Simple agent example
- Basic tool usage
- Memory integration

**`examples/advanced_agent_example.py`** (Future)
- Complete agent using all patterns
- Tool filtering enabled
- Token budget tracking
- Memory integration
- Production-ready structure

---

## 🔑 Key Concepts Summary

### Context Engineering Fundamentals
- **Four Context Types**: System, User, Retrieved, Conversation
- **Context Assembly**: Combining different context sources effectively
- **Context Optimization**: Managing context window limits
- **Production Considerations**: Scalability, cost, performance

### RAG (Retrieval Augmented Generation)
- **Vector Embeddings**: Converting text to numerical representations
- **Semantic Search**: Finding similar items using vector similarity
- **Redis Vector Search**: Using Redis for vector storage and retrieval
- **Hybrid Search**: Combining keyword and semantic search

### Memory Systems for Context Engineering
- **Dual Memory System**: Working memory (session) + Long-term memory (cross-session)
- **Memory Types**: Semantic (facts), Episodic (events), Message (conversations)
- **Memory Extraction Strategies**: Discrete, Summary, Preferences, Custom
- **Working Memory Compression**: Truncation, Priority-Based, Summarization
- **Agent Memory Server**: Production-ready automatic memory management

### Tool Selection & LangGraph
- **Tool Schemas**: Name, description, parameters with clear documentation
- **LangGraph**: Stateful agent workflow framework
- **State Management**: Managing agent state across conversation turns
- **Tool Orchestration**: Coordinating multiple tools effectively
- **Semantic Tool Selection**: Choosing tools based on context and intent

### Optimization & Production
- **Token Budgets**: Allocating context window space efficiently
- **Retrieval Strategies**: Full context (bad), RAG (good), Summaries (compact), Hybrid (best)
- **Tool Filtering**: Show only relevant tools based on intent
- **Structured Views**: Pre-computed summaries for LLM consumption
- **Cost Optimization**: Reducing token usage by 50-70%
- **Performance Monitoring**: Tracking metrics for production deployment

---

## 🏗️ Production Patterns

### 1. Complete Memory Flow
```python
from agent_memory_client import MemoryClient

# Initialize memory client
memory_client = MemoryClient(
    base_url="http://localhost:8088",
    user_id="student_123"
)

# Load working memory for session
working_memory = await memory_client.get_working_memory(
    session_id="session_456",
    model_name="gpt-4"
)

# Search long-term memory for relevant facts
memories = await memory_client.search_memories(
    query="What courses is the student interested in?",
    limit=5
)

# Build context with memories
system_prompt = build_prompt(instructions, memories)

# Process with LLM
response = llm.invoke(messages)

# Save working memory (triggers automatic extraction)
await memory_client.save_working_memory(
    session_id="session_456",
    messages=messages
)
```

### 2. Hybrid Retrieval Pattern
```python
from redis_context_course import CourseManager, hybrid_retrieval

# Pre-computed summary (cached)
summary = """
Redis University offers 50+ courses across 5 categories:
- Data Structures (15 courses)
- AI/ML (12 courses)
- Web Development (10 courses)
...
"""

# Targeted semantic search
course_manager = CourseManager()
specific_courses = await course_manager.search_courses(
    query="machine learning with Python",
    limit=3
)

# Combine for optimal context
context = f"{summary}\n\nMost Relevant Courses:\n{specific_courses}"
```

### 3. Tool Filtering by Intent
```python
from redis_context_course import filter_tools_by_intent

# Define tool groups
tool_groups = {
    "search": ["search_courses", "find_prerequisites"],
    "memory": ["store_preference", "recall_history"],
    "recommendation": ["recommend_courses", "suggest_path"]
}

# Filter based on user query
query = "What courses should I take for machine learning?"
relevant_tools = filter_tools_by_intent(
    query=query,
    tool_groups=tool_groups,
    keywords={"search": ["find", "what", "which"],
              "recommendation": ["should", "recommend", "suggest"]}
)

# Bind only relevant tools to LLM
llm_with_tools = llm.bind_tools(relevant_tools)
```

### 4. Token Budget Management
```python
from redis_context_course import count_tokens, estimate_token_budget

# Estimate token budget
budget = estimate_token_budget(
    system_prompt=system_prompt,
    working_memory_messages=10,
    long_term_memories=5,
    retrieved_context_items=3,
    model="gpt-4"
)

print(f"Estimated tokens: {budget['total_with_response']}")
print(f"Cost estimate: ${budget['estimated_cost']}")

# Check if within limits
if budget['total_with_response'] > 128000:
    # Trigger compression or reduce context
    compressed_memory = compress_working_memory(
        messages=messages,
        strategy="summarization",
        target_tokens=5000
    )
```

### 5. Structured Views for Efficiency
```python
from redis_context_course import create_summary_view

# Retrieve all courses
courses = await course_manager.get_all_courses()

# Create structured summary (one-time or cached)
summary = await create_summary_view(
    items=courses,
    group_by="category",
    include_stats=True
)

# Cache for reuse
redis_client.set("course_catalog_summary", summary, ex=3600)

# Use in system prompts
system_prompt = f"""
You are a course advisor with access to:

{summary}

Use search_courses() for specific queries.
"""
```

### 6. Memory Extraction Strategies
```python
# Discrete Strategy (individual facts)
await memory_client.save_working_memory(
    session_id=session_id,
    messages=messages,
    extraction_strategy="discrete"  # Extracts individual facts
)

# Summary Strategy (conversation summaries)
await memory_client.save_working_memory(
    session_id=session_id,
    messages=messages,
    extraction_strategy="summary"  # Creates summaries
)

# Preferences Strategy (user preferences)
await memory_client.save_working_memory(
    session_id=session_id,
    messages=messages,
    extraction_strategy="preferences"  # Extracts preferences
)
```

### 7. Working Memory Compression
```python
# Truncation (keep recent messages)
compressed = truncate_memory(messages, keep_last=10)

# Priority-Based (score by importance)
compressed = priority_compress(
    messages=messages,
    target_tokens=5000,
    scoring_fn=importance_score
)

# Summarization (LLM-based)
compressed = await summarize_memory(
    messages=messages,
    llm=llm,
    target_tokens=5000
)
```

---

## 📚 How to Use This Course

### Notebook Structure

All patterns are demonstrated in notebooks with:
- ✅ **Conceptual explanations** - Theory and principles
- ✅ **Bad examples** - What not to do and why
- ✅ **Good examples** - Best practices and patterns
- ✅ **Runnable code** - Complete, executable examples
- ✅ **Testing and verification** - Validate your implementation
- ✅ **Exercises for practice** - Hands-on challenges

### Importing Components in Your Code

```python
from redis_context_course import (
    # Core Classes
    CourseManager,          # Course storage and search
    RedisConfig,            # Redis configuration
    redis_config,           # Redis config instance

    # Data Models
    Course,                 # Course data model
    StudentProfile,         # Student information
    DifficultyLevel,        # Difficulty enum
    CourseFormat,           # Format enum (online, in-person, hybrid)
    Semester,               # Semester enum

    # Tools (Section 4)
    create_course_tools,    # Create course-related tools
    create_memory_tools,    # Create memory management tools
    select_tools_by_keywords,  # Simple tool filtering

    # Optimization Helpers (Section 5)
    count_tokens,           # Token counting
    estimate_token_budget,  # Budget estimation
    hybrid_retrieval,       # Hybrid search strategy
    create_summary_view,    # Summary generation
    create_user_profile_view,  # User profile formatting
    filter_tools_by_intent, # Intent-based tool filtering
    classify_intent_with_llm,  # LLM-based intent classification
    extract_references,     # Reference extraction
    format_context_for_llm, # Context formatting
)
```

### Recommended Learning Path

#### For Beginners (3-4 weeks, 6-8 hours/week)
1. **Week 1**: Complete Section 1 (Foundations) and Section 2 (RAG)
2. **Week 2**: Work through Section 3 (Memory Systems for Context Engineering)
3. **Week 3**: Build agents in Section 4 (Tool Selection & LangGraph)
4. **Week 4**: Optimize in Section 5 (Production)

#### For Experienced Developers (1-2 weeks full-time)
- **Skip to Section 2** if familiar with context engineering basics
- **Jump to Section 3** if you've built RAG systems before
- **Start at Section 4** if you want to focus on LangGraph and agents

#### Time Commitment Options
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

## 🎯 Key Takeaways

### What Makes a Production-Ready Agent?

1. **Clear System Instructions** - Tell the agent what to do and how to behave
2. **Well-Designed Tools** - Give it capabilities with clear descriptions and examples
3. **Memory Integration** - Remember context across sessions with dual memory system
4. **Token Management** - Stay within limits efficiently with budget tracking
5. **Smart Retrieval** - Hybrid approach (summary + targeted RAG)
6. **Tool Filtering** - Show only relevant tools based on intent
7. **Structured Views** - Pre-compute summaries for efficiency
8. **Error Handling** - Graceful degradation and recovery
9. **Monitoring** - Track performance, costs, and quality metrics
10. **Scalability** - Design for thousands of concurrent users

### Common Pitfalls to Avoid

❌ **Don't:**
- Include all tools on every request (causes confusion and token waste)
- Use vague tool descriptions (LLM won't know when to use them)
- Ignore token budgets (leads to errors and high costs)
- Use only full context or only RAG (inefficient or incomplete)
- Forget to save working memory (no automatic extraction)
- Store everything in long-term memory (noise and retrieval issues)
- Skip error handling (production failures)
- Ignore performance monitoring (can't optimize what you don't measure)

✅ **Do:**
- Filter tools by intent (show only relevant tools)
- Write detailed tool descriptions with examples (clear guidance for LLM)
- Estimate and monitor token usage (stay within budgets)
- Use hybrid retrieval (summary + targeted search for best results)
- Save working memory to trigger extraction (automatic memory management)
- Store only important facts in long-term memory (high signal-to-noise ratio)
- Implement graceful error handling (production resilience)
- Track metrics and optimize (continuous improvement)

---

## 🌍 Real-World Applications

The patterns learned in this course apply directly to:

### Enterprise AI Systems
- **Customer service chatbots** with sophisticated memory and tool routing
- **Technical support agents** with intelligent knowledge retrieval
- **Sales assistants** with personalized recommendations and context
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
- **Cost optimization** reducing LLM API expenses significantly

### Skills Gained
- 💼 **Portfolio project** demonstrating context engineering mastery
- 📊 **Performance monitoring expertise** for production deployment
- 🛠️ **Production-ready patterns** for building AI agents
- 🎯 **Cost optimization skills** for managing LLM expenses
- 🚀 **Scalable architecture design** for enterprise deployments

---

## 🚀 Next Steps

After completing this course, you can:

1. **Extend the reference agent** - Add new tools and capabilities for your domain
2. **Apply to your use case** - Adapt patterns to your specific requirements
3. **Optimize further** - Experiment with different strategies and measure results
4. **Deploy to production** - Use learned patterns for real-world applications
5. **Share your learnings** - Contribute back to the community
6. **Build your portfolio** - Showcase your context engineering expertise

---

## 📚 Resources

### Documentation
- **[Main README](README.md)** - Course overview and quick start
- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[notebooks/README.md](notebooks/README.md)** - Notebook-specific documentation
- **[notebooks/SETUP_GUIDE.md](notebooks/SETUP_GUIDE.md)** - Comprehensive setup guide
- **[reference-agent/README.md](reference-agent/README.md)** - Reference agent documentation

### External Resources
- **[Agent Memory Server](https://github.com/redis/agent-memory-server)** - Memory management system
- **[Redis Documentation](https://redis.io/docs/)** - Redis official documentation
- **[LangChain Documentation](https://python.langchain.com/)** - LangChain framework docs
- **[LangGraph Documentation](https://langchain-ai.github.io/langgraph/)** - LangGraph stateful agents
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

**Course Stats**:
- **Duration**: 18-23 hours
- **Sections**: 5
- **Notebooks**: 12
- **Hands-on Exercises**: 30+
- **Production Patterns**: 15+

---

**🎉 Ready to master context engineering? [Get started now!](README.md#-quick-start-5-minutes)**

---

*This comprehensive course provides hands-on education in context engineering - taking you from fundamentals to production-ready expertise through a single, evolving project that demonstrates real-world impact.*

