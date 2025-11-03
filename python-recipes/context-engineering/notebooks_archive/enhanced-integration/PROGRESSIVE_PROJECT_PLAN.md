# Progressive Context Engineering Projects Using Reference-Agent

## Project Architecture Overview

```
Section 2: RAG Foundations → Section 3: Memory Architecture → Section 4: Tool Selection → Section 5: Context Optimization
     ↓                           ↓                              ↓                         ↓
Basic RAG Agent          → Enhanced Memory Agent        → Multi-Tool Agent      → Optimized Production Agent
```

## Section 2: RAG Foundations - "Build Your Course Advisor Agent"

### Project: Redis University Course Advisor with RAG
**Goal**: Build a complete RAG system using the reference-agent as foundation

### Step-by-Step Learning Journey:

#### Step 1: Install and Explore the Reference Agent
```python
# Install the reference agent as editable package
!pip install -e ../../../reference-agent

# Explore the components
from redis_context_course.models import Course, StudentProfile, DifficultyLevel
from redis_context_course.course_manager import CourseManager
from redis_context_course.agent import ClassAgent
```

#### Step 2: Create Your First RAG Pipeline
- Load course catalog from `course_catalog.json`
- Build vector search using the CourseManager
- Create student profiles with different backgrounds
- Implement basic retrieval → augmentation → generation

#### Step 3: Test Different RAG Scenarios
- New student: "I'm interested in machine learning"
- Returning student: "What should I take after RU201?"
- Advanced student: "I need courses for my ML thesis"

### Learning Outcomes:
- Understand RAG architecture (Retrieval + Augmentation + Generation)
- Use professional data models (Pydantic)
- Build vector similarity search
- Create context assembly pipelines

## Section 3: Memory Architecture - "Add Sophisticated Memory"

### Project: Enhance Your Agent with Redis-Based Memory
**Goal**: Replace basic conversation history with sophisticated memory system

### Cross-Reference with Original Notebooks:
- **Memory concepts** from `section-3-memory-architecture/01_memory_fundamentals.ipynb`
- **Working vs long-term memory** patterns from existing notebooks
- **Redis-based persistence** examples from reference-agent

### Step-by-Step Enhancement:

#### Step 1: Integrate Agent Memory Server
```python
from agent_memory_client import MemoryAPIClient
from redis_context_course.agent import ClassAgent

# Upgrade from basic dict to Redis-based memory
agent = ClassAgent(student_id="sarah_chen")
```

#### Step 2: Implement Working Memory
- Session-scoped context for current conversation
- Task-focused information (current course search, preferences)
- Automatic fact extraction to long-term storage

#### Step 3: Add Long-Term Memory
- Cross-session knowledge (student preferences, completed courses)
- Semantic vector search for memory retrieval
- Memory consolidation and forgetting strategies

#### Step 4: Test Memory Persistence
- Session 1: Student explores ML courses, expresses preferences
- Session 2: Agent remembers preferences, builds on previous conversation
- Session 3: Agent recalls past recommendations and progress

### Learning Outcomes:
- Understand working vs long-term memory
- Implement Redis-based memory persistence
- Build semantic memory retrieval
- Design memory consolidation strategies

## Section 4: Semantic Tool Selection - "Build Multi-Tool Intelligence"

### Project: Add Intelligent Tool Routing
**Goal**: Extend your agent with multiple specialized tools and smart routing

### Cross-Reference with Original Notebooks:
- **Tool selection patterns** from `section-4-tool-selection/` notebooks
- **Semantic routing** concepts from existing implementations
- **Intent classification** examples from reference-agent

### Step-by-Step Tool Enhancement:

#### Step 1: Explore Existing Tools
```python
from redis_context_course.tools import create_course_tools
from redis_context_course.semantic_tool_selector import SemanticToolSelector

# Understand the tool ecosystem
tools = create_course_tools(course_manager)
```

#### Step 2: Add New Specialized Tools
- Enrollment tool: Check course availability and enroll
- Schedule tool: Find courses that fit student's schedule
- Prerequisite tool: Verify and plan prerequisite chains
- Progress tool: Track student's degree progress

#### Step 3: Implement Semantic Tool Selection
- Replace keyword matching with embedding-based selection
- Intent classification with confidence scoring
- Dynamic tool filtering based on context
- Fallback strategies for ambiguous queries

#### Step 4: Test Complex Multi-Tool Scenarios
- "I want to take ML courses but need to check my schedule" → Schedule + Course Search
- "Can I enroll in RU301 and what do I need first?" → Prerequisites + Enrollment
- "Show my progress toward a data science focus" → Progress + Course Planning

### Learning Outcomes:
- Build semantic tool selection systems
- Implement intent classification
- Design multi-tool coordination
- Handle complex query routing

## Section 5: Context Optimization - "Scale for Production"

### Project: Optimize Your Agent for Production Scale
**Goal**: Add compression, efficiency, and cost optimization

### Cross-Reference with Original Notebooks:
- **Context optimization** techniques from `section-5-optimization/` notebooks
- **Token management** strategies from existing implementations
- **Performance monitoring** patterns from reference-agent

### Step-by-Step Optimization:

#### Step 1: Implement Context Compression
```python
from redis_context_course.optimization_helpers import ContextOptimizer

# Add intelligent context compression
optimizer = ContextOptimizer()
compressed_context = optimizer.compress_context(full_context)
```

#### Step 2: Add Context Pruning
- Relevance scoring for context elements
- Token budget management for different query types
- Dynamic context selection based on query complexity
- Context summarization for long conversations

#### Step 3: Optimize Vector Search
- Upgrade to OpenAI embeddings from TF-IDF
- Implement semantic caching for common queries
- Add query expansion and rewriting
- Batch processing for multiple students

#### Step 4: Add Production Monitoring
- Token usage tracking and cost analysis
- Response quality metrics and A/B testing
- Performance monitoring and optimization alerts
- Context effectiveness measurement

### Learning Outcomes:
- Implement production-grade context optimization
- Build cost-effective scaling strategies
- Add monitoring and observability
- Design efficient vector search systems

## Section 6: Production Deployment (Optional)

### Project: Deploy Your Complete Context Engineering System
**Goal**: Create a production-ready, scalable deployment

**Note**: This section is optional and focuses on deployment rather than core context engineering concepts.

### Key Topics (if implemented):
- Containerization with Docker
- Redis clustering for high availability
- API gateway with FastAPI
- Kubernetes deployment
- Monitoring and observability

## Why This Progressive Approach Works

### 1. Builds Real Skills
- Students start with working code from reference-agent
- Each section adds meaningful functionality
- Progressive complexity from basic to production-ready
- Real-world patterns they can use in jobs

### 2. Maintains Continuity
- Same agent evolves through all sections
- Students see their work compound and improve
- Clear progression from simple to sophisticated
- Investment in learning pays off across sections

### 3. Production-Ready Results
- Final agent handles real-world complexity
- Scalable architecture patterns
- Enterprise-grade features (monitoring, optimization)
- Portfolio-worthy project for students

### 4. Educational Excellence
- Hands-on learning with immediate results
- Professional tools and patterns
- Step-by-step guidance with clear outcomes
- Jupyter-friendly interactive development

## Implementation Style Guidelines

### Preferred Style (Clean & Educational):
- Standard headers: Simple #, ##, ### without decorative elements
- Natural text flow: Reads like educational content, not marketing material
- Bullet points with standard markdown: Simple - or * bullets
- Code blocks with simple comments: Clean, simple, readable code
- Professional tone: Educational and informative
- Clean structure: Good use of headers and sections
- Practical focus: Step-by-step approach
- Minimal decoration: Not over-formatted
- Clear explanations: Direct and to the point

### Avoid:
- Excessive emojis or decorative formatting
- Verbose print statements for explanation
- Marketing-like enthusiastic tone
- Over-engineered examples for simple concepts
- Complex setup requirements
