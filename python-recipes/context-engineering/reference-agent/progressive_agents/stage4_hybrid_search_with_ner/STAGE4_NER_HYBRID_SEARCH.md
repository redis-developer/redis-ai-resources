# Stage 4: Named Entity Recognition & Hybrid Search

## Overview

Stage 4 introduces **intelligent query understanding** and **hybrid search strategies** to the Course Advisor agent. Instead of treating all queries the same, the agent now:

1. **Extracts structured information** from natural language queries (NER)
2. **Selects optimal search strategies** based on extracted entities
3. **Combines multiple search approaches** for better precision and recall
4. **Targets specific information** when users request particular details

## Key Improvements Over Stage 3

| Feature | Stage 3 | Stage 4 |
|---------|---------|---------|
| **Query Understanding** | Intent classification only | Intent + NER extraction |
| **Search Strategy** | Semantic-only (vector search) | Hybrid (exact + semantic + filters) |
| **Course Code Queries** | Semantic match (imprecise) | Exact match (100% precision) |
| **Metadata Filtering** | Not used | Department, difficulty, format, etc. |
| **Information Extraction** | Full details always | Targeted (assignments, syllabus, etc.) |
| **Response Adaptation** | Generic synthesis | Context-aware (exact vs semantic) |

## Architecture

### 1. Named Entity Recognition (NER)

The `extract_entities_node` uses an LLM to extract structured information from queries:

**Extracted Entities:**
- **Course Codes**: CS101, MATH202, ENG301
- **Course Names**: "Introduction to Python", "Data Structures"
- **Departments**: Computer Science, Mathematics, Engineering
- **Instructors**: Professor names (if mentioned)
- **Topics**: machine learning, databases, calculus
- **Metadata Filters**:
  - `difficulty_level`: beginner, intermediate, advanced, graduate
  - `format`: online, in_person, hybrid
  - `semester`: fall, spring, summer
  - `credits`: number of credits
- **Information Types**: syllabus, assignments, grading_policy, textbooks, prerequisites

**Example:**
```
Query: "Show me the syllabus for CS101 and assignments for Data Structures"

Extracted Entities:
{
  "course_codes": ["CS101"],
  "course_names": ["Data Structures"],
  "departments": [],
  "topics": [],
  "metadata_filters": {},
  "information_type": ["syllabus", "assignments"]
}

Search Strategy: exact_match (course code found)
```

### 2. Search Strategy Selection

Based on extracted entities, the agent selects one of three strategies:

#### Strategy 1: Exact Match
**When**: Course codes are found in the query
**How**: Direct lookup by course code with high similarity threshold (0.9)
**Benefits**: 
- Highest precision (100% for valid codes)
- Lowest latency (no semantic search needed)
- Returns only requested courses

**Example Queries:**
- "Tell me about CS101"
- "What are the prerequisites for MATH202?"
- "Show me CS101 and CS202"

#### Strategy 2: Hybrid Search
**When**: Course names, departments, or topics are found
**How**: Combines multiple approaches:
1. Exact matches for any course codes
2. Semantic search enhanced with extracted topics
3. Metadata filtering (department, difficulty, format, etc.)
4. Deduplication of results

**Benefits**:
- Better precision than semantic-only
- Broader coverage than exact-only
- Leverages all available information

**Example Queries:**
- "What machine learning courses are available in Computer Science?"
- "Show me beginner Python courses"
- "I need an online database course"

#### Strategy 3: Semantic Only
**When**: No specific entities found (fallback)
**How**: Traditional vector search with optional metadata filters
**Benefits**:
- Handles exploratory queries
- Works for any query type
- Graceful fallback

**Example Queries:**
- "What courses should I take to learn web development?"
- "I'm interested in data science"

### 3. Targeted Information Extraction

When users request specific information (assignments, syllabus, etc.), the agent filters course details to include only what was requested.

**Implementation:**
```python
def _filter_course_details(details, info_types):
    """Extract only requested information from course details."""
    filtered_detail = CourseDetails(
        course_code=detail.course_code,
        full_description=detail.full_description if "overview" in info_types else "",
        syllabus=detail.syllabus if "syllabus" in info_types else None,
        grading_policy=detail.grading_policy if "grading" in info_types else None,
        textbooks=detail.textbooks if "textbooks" in info_types else [],
        # ... other fields
    )
```

**Benefits:**
- Reduces token usage (only relevant information)
- Improves response focus
- Better user experience (no information overload)

**Example:**
```
Query: "What are the assignments for CS101?"

Without filtering: Returns full course details (~700 tokens)
With filtering: Returns only assignments section (~150 tokens)
```

### 4. Context-Aware Synthesis

The synthesizer adapts its response based on the search strategy used:

**Exact Match Responses:**
- Direct and concise
- Focus on the specific course(s) requested
- No comparison with other courses

**Hybrid Search Responses:**
- Prioritize exact matches
- Supplement with semantically similar courses
- Explain why each course was included

**Semantic Search Responses:**
- Comprehensive overview
- Multiple options presented
- Help user explore and compare

## Workflow

```
1. User Query
   ↓
2. Intent Classification
   ↓
3. Named Entity Recognition (NEW)
   - Extract course codes, names, topics, etc.
   - Determine search strategy
   ↓
4. Query Decomposition
   ↓
5. Hybrid Search (NEW)
   - Exact match for course codes
   - Semantic search for topics
   - Metadata filtering
   ↓
6. Targeted Extraction (NEW)
   - Filter for requested information
   ↓
7. Quality Evaluation
   ↓
8. Context-Aware Synthesis (NEW)
   - Adapt response to search strategy
   ↓
9. Final Response
```

## Example Scenarios

### Scenario 1: Exact Course Code Query

**Query:** "Show me the syllabus for CS101"

**Processing:**
1. Intent: COURSE_DETAILS, detail_level: full
2. NER: course_codes=["CS101"], info_type=["syllabus"]
3. Strategy: exact_match
4. Search: Direct lookup for CS101
5. Filter: Extract only syllabus section
6. Response: Concise syllabus for CS101 only

**Token Usage:** ~200 tokens (vs ~700 without filtering)

### Scenario 2: Topic-Based Exploration

**Query:** "What machine learning courses are available?"

**Processing:**
1. Intent: COURSE_OVERVIEW, detail_level: summary
2. NER: topics=["machine learning"]
3. Strategy: hybrid
4. Search: Semantic search enhanced with "machine learning" topic
5. Filter: None (overview requested)
6. Response: Summaries of 5 ML courses

**Token Usage:** ~400 tokens

### Scenario 3: Filtered Search

**Query:** "Show me beginner Python courses in Computer Science"

**Processing:**
1. Intent: COURSE_OVERVIEW, detail_level: summary
2. NER: topics=["Python"], departments=["Computer Science"], difficulty=["beginner"]
3. Strategy: hybrid
4. Search: Semantic + metadata filters (dept=CS, difficulty=beginner)
5. Filter: None
6. Response: Summaries of beginner Python courses in CS dept

**Token Usage:** ~300 tokens (fewer results due to filtering)

### Scenario 4: Specific Information Request

**Query:** "What are the assignments for the machine learning course?"

**Processing:**
1. Intent: COURSE_DETAILS, detail_level: full
2. NER: topics=["machine learning"], info_type=["assignments"]
3. Strategy: hybrid
4. Search: Semantic search for ML courses
5. Filter: Extract only assignments from top course
6. Response: Assignments list for top ML course

**Token Usage:** ~150 tokens (vs ~700 for full details)

## Implementation Details

### State Fields (NEW in Stage 4)

```python
class WorkflowState(TypedDict):
    # ... existing fields ...
    
    # NEW in Stage 4
    extracted_entities: Optional[Dict[str, Any]]  # NER results
    search_strategy: Optional[str]  # "exact_match", "hybrid", "semantic_only"
    exact_matches: Optional[List[str]]  # Course codes that matched exactly
    metadata_filters: Optional[Dict[str, Any]]  # Filters for search
```

### Tool Updates

**search_courses_sync()** now accepts:
- `search_strategy`: Which strategy to use
- `extracted_entities`: Entities from NER
- `metadata_filters`: Filters to apply

### Node Updates

1. **extract_entities_node** (NEW): Performs NER extraction
2. **research_node**: Uses hybrid search with entities
3. **synthesize_response_node**: Adapts to search strategy

## Benefits

### 1. Precision
- Exact matches for course codes (100% precision)
- Metadata filtering reduces irrelevant results
- Targeted extraction returns only what's needed

### 2. Efficiency
- Exact match is faster than semantic search
- Filtering reduces token usage by 50-80%
- Less processing for simple queries

### 3. User Experience
- Direct answers for specific queries
- No information overload
- Relevant results for exploratory queries

### 4. Flexibility
- Handles both specific and exploratory queries
- Graceful fallback to semantic search
- Combines multiple search approaches

## Educational Value

This stage demonstrates:

1. **Query Understanding**: Moving beyond keyword matching to true understanding
2. **Hybrid Retrieval**: Combining exact, semantic, and filtered search
3. **Adaptive Systems**: Selecting strategies based on query characteristics
4. **Information Extraction**: Returning only relevant information
5. **Context Engineering**: Matching retrieval depth to user needs

## Next Steps (Future Stages)

Potential enhancements for Stage 5+:
- **Conversation History**: Use previous queries to resolve references ("the first one", "that course")
- **Multi-turn Refinement**: Allow users to drill down into results
- **Semantic Caching**: Cache NER results and search strategies
- **Learning from Feedback**: Improve entity extraction based on user corrections
- **Cross-course Queries**: "Compare CS101 and CS102"

