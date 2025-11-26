# Stage 3 Agent - Implementation Notes

## Summary

Successfully created a working Course Q&A Agent (Stage 3) with:
- ✅ LangGraph workflow orchestration
- ✅ Semantic course search using Redis vector embeddings
- ✅ Query decomposition and quality evaluation
- ✅ Auto-loading course data on startup
- ✅ Interactive CLI with multiple modes
- ✅ Simplified architecture (no ReAct agent recursion issues)

## Key Changes from Original caching-agent

### 1. Simplified Research Node

**Original Implementation**:
```python
# Used create_react_agent with tool calling
researcher_agent = create_react_agent(
    model=research_llm, 
    tools=[search_courses_sync]
)

research_result = researcher_agent.invoke({
    "messages": [HumanMessage(content=f"Find relevant courses for: {sub_question}")]
})
```

**Problem**: Hit LangGraph recursion limit (25 iterations) because the ReAct agent creates its own internal loop.

**New Implementation**:
```python
# Direct search call - no ReAct agent
search_results = search_courses_sync(sub_question, top_k=5)

if search_results and "No relevant courses found" not in search_results:
    answer = f"Found relevant courses:\n\n{search_results}"
else:
    answer = "No relevant courses found for this question."
```

**Benefits**:
- No recursion issues
- Clearer execution flow
- Fewer LLM calls
- Easier to debug
- Better for educational purposes

### 2. Async/Sync Compatibility

**Challenge**: LangGraph nodes are synchronous, but CourseManager.search_courses() is async.

**Solution**: Created `search_courses_sync` wrapper using `nest_asyncio`:

```python
def search_courses_sync(query: str, top_k: int = 5) -> str:
    import asyncio
    import nest_asyncio
    
    # Allow nested event loops (needed when LangGraph is already running async)
    nest_asyncio.apply()
    
    # Get or create event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run async search in sync context
    results = loop.run_until_complete(course_manager.search_courses(...))
    
    # Format and return results
    return formatted_results
```

### 3. Auto-loading Course Data

**Feature**: Automatically generate and load sample courses on first run.

**Implementation** (`agent/setup.py`):

```python
async def load_courses_if_needed(course_manager: CourseManager, force_reload: bool = False) -> int:
    # Check if courses already exist
    existing_courses = await course_manager.get_all_courses()
    
    if existing_courses and not force_reload:
        logger.info(f"📚 Found {len(existing_courses)} existing courses in Redis")
        return len(existing_courses)
    
    # Generate sample courses
    generator = CourseGenerator()
    courses = generator.generate_courses(courses_per_major=10)
    
    # Ingest into Redis
    ingestion = CourseIngestionPipeline()
    ingested_count = await ingestion.ingest_courses(courses_data)
    
    return ingested_count
```

**Benefits**:
- No manual data loading required
- Courses persist between runs
- Optional cleanup on exit with `--cleanup` flag

### 4. CLI Enhancements

**Three Modes**:
1. **Interactive**: `python cli.py` - REPL for asking questions
2. **Single Query**: `python cli.py "your question"` - One-off queries
3. **Simulation**: `python cli.py --simulate` - Run example queries

**Cleanup Option**:
- `--cleanup`: Remove courses from Redis on exit
- `--no-cleanup` (default): Keep courses for next run

**Implementation**:
```python
class CourseQACLI:
    def __init__(self, cleanup_on_exit: bool = False):
        self.cleanup_on_exit = cleanup_on_exit
        
        if cleanup_on_exit:
            atexit.register(self._cleanup)
    
    def _cleanup(self):
        if self.course_manager and self.cleanup_on_exit:
            asyncio.run(cleanup_courses(self.course_manager))
```

### 5. Debug Tools

Created `debug_search.py` to test course search functionality:

**Tests**:
1. Get all courses from Redis
2. Direct CourseManager search with various queries
3. Search with different similarity thresholds
4. Test the agent tool search
5. Inspect course content and embeddings
6. Try different query formats

**Usage**:
```bash
python debug_search.py
```

## Testing Results

### Successful Test Run

```bash
$ python cli.py "What machine learning courses are available?"

✅ Found 50 existing courses in Redis
✅ Workflow created successfully
💾 Courses will persist in Redis after exit

📝 Answer:
Found relevant courses:

Course 1:
CS002: Machine Learning
Department: Computer Science
Credits: 4
Level: advanced
Format: in_person
Instructor: Lisa Dunlap
Description: Introduction to machine learning algorithms and applications...

Course 2:
CS009: Machine Learning
Department: Computer Science
Credits: 4
Level: advanced
Format: hybrid
Instructor: Katelyn Jones
Prerequisites: CS001
Description: Introduction to machine learning algorithms and applications...

[... more courses ...]

📊 Performance:
   Total Time: 2140.56ms
   Sub-questions: 1
   Questions Researched: 1
   Execution: decomposed → cache_checked → researched → quality_evaluated → researched → quality_evaluated → synthesized
```

### Debug Search Results

```bash
$ python debug_search.py

Test 2: Direct CourseManager Search
🔍 Query: 'machine learning'
   Results: 3 courses found
   1. CS002: Machine Learning
   2. CS009: Machine Learning
   3. MATH029: Linear Algebra

🔍 Query: 'database'
   Results: 3 courses found
   1. CS005: Database Systems
   2. CS001: Database Systems
   3. CS004: Data Structures and Algorithms

✅ All tests passed!
```

## Architecture Decisions

### Why Simplify from ReAct Agent?

1. **Educational Clarity**: Students can see exactly what's happening without nested agent loops
2. **Reliability**: No recursion limit errors
3. **Performance**: Fewer LLM calls (1 embedding call vs multiple ReAct iterations)
4. **Debugging**: Easier to trace execution flow
5. **Cost**: Lower API costs with fewer LLM calls

### Why Keep LangGraph?

1. **State Management**: Clean, observable state transitions
2. **Conditional Routing**: Quality evaluation loop works perfectly
3. **Modularity**: Easy to add/remove nodes (e.g., caching, memory)
4. **Visualization**: Can generate workflow diagrams
5. **Industry Standard**: Students learn a real-world framework

### Why Use nest_asyncio?

1. **Compatibility**: Allows async CourseManager in sync LangGraph nodes
2. **Simplicity**: No need to rewrite CourseManager as sync
3. **Flexibility**: Can still use async version in other contexts
4. **Standard Solution**: Common pattern for nested event loops

## Next Steps

### Stage 1 & 2 (Backward Deconstruction)

Create simplified versions by removing features:

**Stage 1 - Baseline RAG**:
- Remove query decomposition (single question only)
- Remove quality evaluation loop
- Remove context engineering (use raw JSON)
- Keep basic semantic search

**Stage 2 - Context-Engineered RAG**:
- Add context engineering (transform_course_to_text, optimize_course_text)
- Still single question (no decomposition)
- Still no quality loop
- Show improvement over Stage 1

### Stage 4 - Memory Integration

Add Redis Agent Memory Server:
- Working memory (conversation history)
- Long-term memory (user preferences, past queries)
- Memory tools for agent to use
- Demonstrate memory-augmented RAG

## Files Modified/Created

### Created
- `cli.py` - Interactive CLI with 3 modes
- `debug_search.py` - Debug tool for testing search
- `agent/setup.py` - Initialization and course loading
- `agent/state.py` - Workflow state definitions
- `agent/tools.py` - Course search tools
- `agent/nodes.py` - LangGraph workflow nodes
- `agent/edges.py` - Routing logic
- `agent/workflow.py` - Workflow builder
- `agent/__init__.py` - Package exports
- `README.md` - Comprehensive documentation
- `IMPLEMENTATION_NOTES.md` - This file

### Key Dependencies
- `langgraph` - Workflow orchestration
- `langchain` - LLM integration
- `redis` - Vector storage
- `redisvl` - Redis vector library
- `nest_asyncio` - Nested event loop support
- `python-dotenv` - Environment variable loading

## Lessons Learned

1. **Simplicity > Complexity**: Direct search works better than ReAct agent for this use case
2. **Async/Sync Bridge**: nest_asyncio is essential for mixing async and sync code
3. **Auto-loading**: Automatic data loading greatly improves UX
4. **Debug Tools**: Separate debug scripts are invaluable for troubleshooting
5. **Documentation**: Clear README with diagrams helps students understand the system

