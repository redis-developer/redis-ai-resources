# Context Engineering Course - Complete Summary

## Overview

This course teaches production-ready context engineering for AI agents using Redis and the Agent Memory Server. It covers everything from fundamentals to advanced optimization techniques.

## Course Structure

### Section 1: Introduction (3 notebooks)
1. **What is Context Engineering?** - Core concepts and importance
2. **Setting Up Your Environment** - Installation and configuration
3. **Project Overview** - Understanding the reference agent

### Section 2: System Context (3 notebooks)
1. **System Instructions** - Crafting effective system prompts
2. **Defining Tools** - Giving agents capabilities
3. **Tool Selection Strategies** (Advanced) - Improving tool choice

**Key Patterns:**
- Progressive system prompt building
- Tool schema design with examples
- Clear naming conventions
- Detailed descriptions with when/when-not guidance

### Section 3: Memory (4 notebooks)
1. **Working Memory with Extraction Strategies** - Session-scoped context
2. **Long-term Memory** - Cross-session knowledge
3. **Memory Integration** - Combining working and long-term memory
4. **Memory Tools** (Advanced) - LLM control over memory

**Key Patterns:**
- Automatic memory extraction
- Semantic search for retrieval
- Memory type selection (semantic vs episodic)
- Tool-based memory management

### Section 4: Optimizations (5 notebooks)
1. **Context Window Management** - Handling token limits
2. **Retrieval Strategies** - RAG, summaries, and hybrid approaches
3. **Grounding with Memory** - Using memory to resolve references
4. **Tool Optimization** (Advanced) - Selective tool exposure
5. **Crafting Data for LLMs** (Advanced) - Creating structured views

**Key Patterns:**
- Token budget estimation
- Hybrid retrieval (summary + RAG)
- Tool filtering by intent
- Retrieve → Summarize → Stitch → Save pattern
- Structured view creation

## Reference Agent Components

### Core Modules

**`course_manager.py`**
- Course catalog management
- Vector search for courses
- Course data models

**`memory_client.py`**
- Working memory operations
- Long-term memory operations
- Integration with Agent Memory Server

**`agent.py`**
- Main agent implementation
- LangGraph workflow
- State management

### New Modules (From Course Content)

**`tools.py`** (Section 2)
- `create_course_tools()` - Search, get details, check prerequisites
- `create_memory_tools()` - Store and search memories
- `select_tools_by_keywords()` - Simple tool filtering

**`optimization_helpers.py`** (Section 4)
- `count_tokens()` - Token counting for any model
- `estimate_token_budget()` - Budget breakdown
- `hybrid_retrieval()` - Combine summary + search
- `create_summary_view()` - Structured summaries
- `create_user_profile_view()` - User profile generation
- `filter_tools_by_intent()` - Keyword-based filtering
- `classify_intent_with_llm()` - LLM-based classification
- `extract_references()` - Find grounding needs
- `format_context_for_llm()` - Combine context sources

### Examples

**`examples/advanced_agent_example.py`**
- Complete agent using all patterns
- Tool filtering enabled
- Token budget tracking
- Memory integration
- Production-ready structure

## Key Concepts by Section

### Section 2: System Context
- **System vs Retrieved Context**: Static instructions vs dynamic data
- **Tool Schemas**: Name, description, parameters
- **Tool Selection**: How LLMs choose tools
- **Best Practices**: Clear names, detailed descriptions, examples

### Section 3: Memory
- **Working Memory**: Session-scoped, conversation history
- **Long-term Memory**: User-scoped, persistent facts
- **Memory Types**: Semantic (facts), Episodic (events), Message (conversations)
- **Automatic Extraction**: Agent Memory Server extracts important facts
- **Memory Flow**: Load → Search → Process → Save → Extract

### Section 4: Optimizations
- **Token Budgets**: Allocating context window space
- **Retrieval Strategies**: Full context (bad), RAG (good), Summaries (compact), Hybrid (best)
- **Grounding**: Resolving references (pronouns, descriptions, implicit)
- **Tool Filtering**: Show only relevant tools based on intent
- **Structured Views**: Pre-computed summaries for LLM consumption

## Production Patterns

### 1. Complete Memory Flow
```python
# Load working memory
working_memory = await memory_client.get_working_memory(session_id, model_name)

# Search long-term memory
memories = await memory_client.search_memories(query, limit=5)

# Build context
system_prompt = build_prompt(instructions, memories)

# Process with LLM
response = llm.invoke(messages)

# Save working memory (triggers extraction)
await memory_client.save_working_memory(session_id, messages)
```

### 2. Hybrid Retrieval
```python
# Pre-computed summary
summary = load_catalog_summary()

# Targeted search
specific_items = await search_courses(query, limit=3)

# Combine
context = f"{summary}\n\nRelevant items:\n{specific_items}"
```

### 3. Tool Filtering
```python
# Filter tools by intent
relevant_tools = filter_tools_by_intent(query, tool_groups)

# Bind only relevant tools
llm_with_tools = llm.bind_tools(relevant_tools)
```

### 4. Token Budget Management
```python
# Estimate budget
budget = estimate_token_budget(
    system_prompt=prompt,
    working_memory_messages=10,
    long_term_memories=5,
    retrieved_context_items=3
)

# Check if within limits
if budget['total_with_response'] > 128000:
    # Trigger summarization or reduce context
```

### 5. Structured Views
```python
# Retrieve data
items = await get_all_items()

# Summarize
summary = await create_summary_view(items, group_by="category")

# Save for reuse
redis_client.set("summary_view", summary)

# Use in prompts
system_prompt = f"Overview:\n{summary}\n\nInstructions:..."
```

## Usage in Notebooks

All patterns are demonstrated in notebooks with:
- ✅ Conceptual explanations
- ✅ Bad examples (what not to do)
- ✅ Good examples (best practices)
- ✅ Runnable code
- ✅ Testing and verification
- ✅ Exercises for practice

## Importing in Your Code

```python
from redis_context_course import (
    # Core
    CourseManager,
    MemoryClient,
    
    # Tools (Section 2)
    create_course_tools,
    create_memory_tools,
    select_tools_by_keywords,
    
    # Optimizations (Section 4)
    count_tokens,
    estimate_token_budget,
    hybrid_retrieval,
    create_summary_view,
    create_user_profile_view,
    filter_tools_by_intent,
    classify_intent_with_llm,
    extract_references,
    format_context_for_llm,
)
```

## Learning Path

1. **Start with Section 1** - Understand fundamentals
2. **Work through Section 2** - Build system context and tools
3. **Master Section 3** - Implement memory management
4. **Optimize with Section 4** - Apply production patterns
5. **Study advanced_agent_example.py** - See it all together
6. **Build your own agent** - Apply to your use case

## Key Takeaways

### What Makes a Production-Ready Agent?

1. **Clear System Instructions** - Tell the agent what to do
2. **Well-Designed Tools** - Give it capabilities with clear descriptions
3. **Memory Integration** - Remember context across sessions
4. **Token Management** - Stay within limits efficiently
5. **Smart Retrieval** - Hybrid approach (summary + RAG)
6. **Tool Filtering** - Show only relevant tools
7. **Structured Views** - Pre-compute summaries for efficiency

### Common Pitfalls to Avoid

❌ **Don't:**
- Include all tools on every request
- Use vague tool descriptions
- Ignore token budgets
- Use only full context or only RAG
- Forget to save working memory
- Store everything in long-term memory

✅ **Do:**
- Filter tools by intent
- Write detailed tool descriptions with examples
- Estimate and monitor token usage
- Use hybrid retrieval (summary + targeted search)
- Save working memory to trigger extraction
- Store only important facts in long-term memory

## Next Steps

After completing this course, you can:

1. **Extend the reference agent** - Add new tools and capabilities
2. **Apply to your domain** - Adapt patterns to your use case
3. **Optimize further** - Experiment with different strategies
4. **Share your learnings** - Contribute back to the community

## Resources

- **Agent Memory Server Docs**: [Link to docs]
- **Redis Documentation**: https://redis.io/docs
- **LangChain Documentation**: https://python.langchain.com
- **Course Repository**: [Link to repo]

---

**Course Version**: 1.0  
**Last Updated**: 2024-09-30  
**Total Notebooks**: 15 (3 intro + 3 system + 4 memory + 5 optimizations)

