# Stage 5 Implementation Summary: Approach 1 (LLM Does Everything)

## What Was Implemented

Stage 5 has been updated from a **scripted workflow** to an **agentic workflow** using **Approach 1: Complex Tool with Full LLM Control**.

### Architecture Change

**Before (Scripted):**
```
load_memory → classify_intent → extract_entities → decompose_query
    → check_cache → research → evaluate_quality → synthesize → save_memory
```
- Hardcoded function calls
- LLM just processes data
- No decision-making

**After (Agentic):**
```
load_memory → classify_intent → agent → save_memory
```
- LLM decides when to search
- LLM determines all parameters
- Full agentic behavior

---

## The Tool

### Tool Definition

```python
@tool("search_courses", args_schema=SearchCoursesInput)
async def search_courses_tool(
    query: str,
    intent: str = "GENERAL",
    search_strategy: str = "hybrid",
    course_codes: List[str] = [],
    information_type: List[str] = [],
    departments: List[str] = [],
    difficulty_level: Optional[str] = None,
) -> str:
```

### What the LLM Controls

1. **When to search**: LLM decides if search is needed
2. **Intent**: GENERAL, PREREQUISITES, SYLLABUS_OBJECTIVES, ASSIGNMENTS
3. **Search strategy**: exact_match, hybrid, semantic_only
4. **Entities**: course_codes, departments, information_type
5. **Filters**: difficulty_level, departments

---

## Test Results

### Test 1: Course Code Queries (Exact Match)

| Query | Intent | Strategy | Course Codes | Result |
|-------|--------|----------|--------------|--------|
| "What is CS004?" | GENERAL | exact_match | ["CS004"] | ✅ Summary only |
| "Prerequisites for CS004?" | PREREQUISITES | exact_match | ["CS004"] | ✅ Prerequisite details |
| "Syllabus for CS004?" | SYLLABUS_OBJECTIVES | exact_match | ["CS004"] | ✅ Syllabus details |
| "Assignments for CS004?" | ASSIGNMENTS | exact_match | ["CS004"] | ✅ Assignment details |

**Key Insight:** LLM correctly uses `exact_match` for course codes (no vector search needed).

---

### Test 2: Topic Queries (Vector Search)

| Query | Intent | Strategy | Course Codes | Result |
|-------|--------|----------|--------------|--------|
| "I'm interested in linear algebra" | GENERAL | semantic_only | [] | ✅ Found 3 LA courses |
| "Prerequisites for linear algebra?" | PREREQUISITES | semantic_only | [] | ✅ Prerequisites for 3 courses |
| "Topics for linear algebra?" | SYLLABUS_OBJECTIVES | semantic_only | [] | ✅ Syllabus for MATH028 |
| "Assignments for linear algebra?" | ASSIGNMENTS | semantic_only | [] | ✅ Assignments for MATH028 |

**Key Insight:** LLM correctly uses `semantic_only` for topics (vector search to find relevant courses).

---

## How It Works

### 1. LLM Receives System Prompt

```
You are a helpful course advisor assistant. Your job is to help students find and learn about courses.

You have access to a search_courses tool that can search the course catalog. Use this tool to find relevant courses to answer the user's question.

When using the search_courses tool, you need to determine:

1. **intent**: What type of information does the user want?
   - "GENERAL": Just course summaries/overviews
   - "PREREQUISITES": Detailed prerequisite information
   - "SYLLABUS_OBJECTIVES": Syllabus and learning objectives
   - "ASSIGNMENTS": Assignment details

2. **search_strategy**: How should we search?
   - "exact_match": When user mentions specific course codes (e.g., "CS004", "MATH301")
   - "hybrid": Combine exact matching + semantic search (best for most queries)
   - "semantic_only": Pure semantic search (when no specific codes mentioned)

3. **course_codes**: Extract any specific course codes mentioned (e.g., ["CS004"])

4. **information_type**: What specific info is needed? (e.g., ["prerequisites"], ["syllabus"], ["assignments"])

5. **departments**: Filter by department if mentioned (e.g., ["Computer Science"])

Examples:
- "What is CS004?" → intent="GENERAL", search_strategy="exact_match", course_codes=["CS004"]
- "What are the prerequisites for CS004?" → intent="PREREQUISITES", search_strategy="exact_match", course_codes=["CS004"], information_type=["prerequisites"]
- "Show me machine learning courses" → intent="GENERAL", search_strategy="hybrid", query="machine learning"
- "What's the syllabus for CS004?" → intent="SYLLABUS_OBJECTIVES", search_strategy="exact_match", course_codes=["CS004"], information_type=["syllabus"]

After calling the tool and getting results, provide a clear, helpful answer to the user.
```

### 2. LLM Analyzes Query

**Example: "What are the prerequisites for CS004?"**

LLM reasoning:
- User wants prerequisites → `intent="PREREQUISITES"`
- User mentioned "CS004" → `course_codes=["CS004"]`
- Course code mentioned → `search_strategy="exact_match"`
- Specific info needed → `information_type=["prerequisites"]`

### 3. LLM Calls Tool

```python
{
    'query': 'CS004',
    'intent': 'PREREQUISITES',
    'search_strategy': 'exact_match',
    'course_codes': ['CS004'],
    'information_type': ['prerequisites'],
    'departments': []
}
```

### 4. Tool Executes Search

```python
# Build extracted_entities from tool parameters
extracted_entities = {
    "course_codes": ["CS004"],
    "information_type": ["prerequisites"],
    "departments": []
}

# Call existing search function
result = search_courses_sync(
    query="CS004",
    top_k=5,
    intent="PREREQUISITES",
    search_strategy="exact_match",
    extracted_entities=extracted_entities,
    metadata_filters={}
)
```

### 5. Search Process

**For exact_match:**
```
1. Extract course code: "CS004"
2. Direct lookup: course_details:CS004
3. Filter details to show only prerequisites
4. Return: ~881 tokens (summary + prerequisite details)
```

**For semantic_only:**
```
1. Generate embedding for "linear algebra"
2. Vector search in course_summaries index
3. Find top 5 semantically similar courses
4. Retrieve full details for top 1-2
5. Filter details based on intent
6. Return: ~950 tokens (summaries + filtered details)
```

### 6. LLM Synthesizes Response

Tool returns raw course data → LLM formats into helpful answer:

```
The course CS004, titled "Computer Vision," is an advanced-level course offered by the Computer Science department. Here are the prerequisites for CS004:

- **Prerequisites**: The course requires a solid understanding of basic programming and data structures. Familiarity with linear algebra, probability, and statistics is also recommended.
```

---

## Progressive Disclosure

The tool implements **hierarchical retrieval** with **intent-based filtering**:

### Tier 1: Summaries (Always Included)
- ~87 tokens per course
- Basic info: code, title, department, instructor, credits, level, format, description

### Tier 2: Filtered Details (Based on Intent)
- **GENERAL**: No details (summary only)
- **PREREQUISITES**: Summary + prerequisites (~881 tokens)
- **SYLLABUS_OBJECTIVES**: Summary + syllabus + learning objectives (~950 tokens)
- **ASSIGNMENTS**: Summary + assignments (~995 tokens)

This optimizes token usage while providing exactly the information the user needs.

---

## Advantages of Approach 1

### ✅ Flexibility
- LLM can handle any query pattern
- No need to hardcode entity extraction rules
- Adapts to new query types automatically

### ✅ Intelligence
- LLM understands context and intent
- Correctly distinguishes course codes from topics
- Chooses appropriate search strategy

### ✅ Simplicity
- Single tool instead of multiple specialized tools
- No complex routing logic needed
- Clean workflow: load → classify → agent → save

### ✅ Educational Value
- Demonstrates full LLM capability
- Shows how to design complex tools
- Illustrates agentic vs scripted workflows

---

## Potential Challenges

### ⚠️ LLM Mistakes
- LLM might choose wrong intent
- LLM might extract entities incorrectly
- LLM might use wrong search strategy

**Mitigation:**
- Clear system prompt with examples
- Well-designed tool schema with descriptions
- Testing with diverse queries

### ⚠️ Token Cost
- Two LLM calls per query (tool call + synthesis)
- More expensive than scripted approach

**Mitigation:**
- Use cheaper model for agent (gpt-4o-mini)
- Cache common queries
- Progressive disclosure reduces context size

### ⚠️ Latency
- LLM reasoning adds latency
- Tool execution adds latency

**Mitigation:**
- Async execution
- Parallel tool calls (if multiple tools)
- Fast Redis lookups

---

## Comparison with Other Approaches

### Approach 2: Hybrid (Nodes + Simple Tool)
```
load_memory → classify_intent → extract_entities → decompose_query → agent → save_memory
```
- Nodes determine intent/entities
- Tool just executes search
- LLM decides WHEN to search

**Pros:** More reliable entity extraction, lower LLM cognitive load
**Cons:** Less flexible, more complex workflow

### Approach 3: Multiple Specialized Tools
```python
@tool
async def search_courses(query: str) -> str:
    """Search for courses by topic."""

@tool
async def get_prerequisites(course_code: str) -> str:
    """Get prerequisites for a course."""

@tool
async def get_syllabus(course_code: str) -> str:
    """Get syllabus for a course."""
```

**Pros:** Clear tool purposes, easier for LLM
**Cons:** More tools to manage, routing complexity

---

## Conclusion

**Approach 1 (LLM Does Everything) is working successfully!**

The implementation demonstrates:
- ✅ LLM can handle complex tool parameters
- ✅ LLM correctly chooses search strategies
- ✅ LLM accurately extracts entities
- ✅ Intent-based filtering works across strategies
- ✅ Progressive disclosure optimizes token usage
- ✅ Vector search works for topic queries
- ✅ Exact match works for course code queries

This validates that a well-designed complex tool with clear instructions can give the LLM full control while maintaining accuracy and reliability.

