# Search Strategy Analysis: When Does the Agent Use Vector Search?

## Overview

The agent uses **3 different search strategies** based on the query:

1. **exact_match**: Direct lookup by course code (e.g., "CS004")
2. **hybrid**: Combines exact matching + semantic search + metadata filters
3. **semantic_only**: Pure vector search for topic-based queries

The LLM **automatically chooses** the appropriate strategy based on the query.

---

## Strategy 1: Exact Match (Course Code Queries)

### When Used
- User mentions specific course codes (e.g., "CS004", "MATH301")
- No semantic search needed - direct lookup

### Example Queries

#### Query: "What is CS004?"
```python
# LLM Tool Call
{
    'query': 'CS004',
    'intent': 'GENERAL',
    'search_strategy': 'exact_match',  # ← Direct lookup
    'course_codes': ['CS004'],         # ← Extracted course code
    'information_type': [],
    'departments': []
}
```

**Search Process:**
```
1. Extract course code: "CS004"
2. Direct lookup in Redis: course_details:CS004
3. Return: 1 exact match
4. No vector search needed
```

**Response:**
> The course **CS004** is titled **Computer Vision** and is offered by the Computer Science department. It is an advanced-level course worth 4 credits and is conducted online.

---

#### Query: "What are the prerequisites for CS004?"
```python
# LLM Tool Call
{
    'query': 'CS004',
    'intent': 'PREREQUISITES',
    'search_strategy': 'exact_match',  # ← Direct lookup
    'course_codes': ['CS004'],
    'information_type': ['prerequisites'],
    'departments': []
}
```

**Search Process:**
```
1. Extract course code: "CS004"
2. Direct lookup in Redis: course_details:CS004
3. Filter details to show only prerequisites
4. Return: Prerequisite information for CS004
```

**Response:**
> The course CS004, titled "Computer Vision," is an advanced-level course offered by the Computer Science department. Here are the prerequisites for CS004:
>
> - **Prerequisites**: The course requires a solid understanding of basic programming and data structures. Familiarity with linear algebra, probability, and statistics is also recommended.

---

## Strategy 2: Semantic Only (Topic-Based Queries)

### When Used
- User asks about topics/subjects (e.g., "linear algebra", "machine learning")
- No specific course codes mentioned
- Requires semantic understanding to find relevant courses

### Example Queries

#### Query: "I am interested in linear algebra"
```python
# LLM Tool Call
{
    'query': 'linear algebra',
    'intent': 'GENERAL',
    'search_strategy': 'semantic_only',  # ← Vector search
    'course_codes': [],                  # ← No course codes
    'information_type': [],
    'departments': []
}
```

**Search Process:**
```
1. Generate embedding for "linear algebra"
2. Vector search in Redis (course_summaries index)
3. Find semantically similar courses
4. Return: Top 5 courses related to linear algebra
```

**Courses Found:**
1. **MATH030: Linear Algebra** (Intermediate, Online)
2. **MATH029: Linear Algebra** (Intermediate)
3. **MATH028: Linear Algebra for Machine Learning** (Advanced)

**Response:**
> Here are some courses related to Linear Algebra that you might be interested in:
>
> 1. **MATH030: Linear Algebra**
>    - **Department**: Mathematics
>    - **Instructor**: Vanessa Brown
>    - **Credits**: 3
>    - **Level**: Intermediate
>    - **Format**: Online
>    - **Description**: Covers vector spaces, matrices, eigenvalues, and linear transformations. Essential for data science and engineering.
>
> 2. **MATH029: Linear Algebra**
>    - **Department**: Mathematics
>    - **Instructor**: Lauren Meyer
>    - **Credits**: 3
>    - **Level**: Intermediate

---

#### Query: "What are the prerequisites for linear algebra?"
```python
# LLM Tool Call
{
    'query': 'linear algebra',
    'intent': 'PREREQUISITES',
    'search_strategy': 'semantic_only',  # ← Vector search
    'course_codes': [],
    'information_type': ['prerequisites'],
    'departments': []
}
```

**Search Process:**
```
1. Generate embedding for "linear algebra"
2. Vector search to find linear algebra courses
3. Retrieve full details for top matches
4. Filter to show only prerequisites
5. Return: Prerequisites for multiple linear algebra courses
```

**Response:**
> Here are the prerequisites for some Linear Algebra courses:
>
> 1. **MATH030: Linear Algebra**
>    - Prerequisites: Typically requires completion of introductory calculus courses such as Calculus I (MATH022 or MATH023) or equivalent.
>
> 2. **MATH029: Linear Algebra**
>    - Prerequisites: Similar to MATH030, usually requires prior completion of introductory calculus courses.
>
> 3. **MATH028: Linear Algebra for Machine Learning**
>    - Prerequisites: Generally requires a background in calculus and basic mathematical concepts, often including Calculus I and possibly Calculus II.

---

#### Query: "What's the topics for linear algebra?"
```python
# LLM Tool Call
{
    'query': 'linear algebra',
    'intent': 'SYLLABUS_OBJECTIVES',
    'search_strategy': 'semantic_only',  # ← Vector search
    'course_codes': [],
    'information_type': ['syllabus'],
    'departments': []
}
```

**Search Process:**
```
1. Generate embedding for "linear algebra"
2. Vector search to find linear algebra courses
3. Retrieve full details for top match
4. Filter to show only syllabus/learning objectives
5. Return: Detailed syllabus for MATH028
```

**Response:**
> The course "MATH028: Linear Algebra for Machine Learning" offers a detailed syllabus covering various topics in linear algebra, particularly focusing on applications to machine learning. Here's a breakdown of the topics covered over the 14-week course:
>
> 1. **Vectors and Vector Spaces**: Introduction and exploration of vectors and vector spaces.
> 2. **Matrix Operations**: Detailed study of matrix operations.
> 3. **Linear Transformations**: Understanding and applying linear transformations.
> 4. **Matrix Decompositions**: Study of different matrix decompositions.
> 5. **Eigenvalues and Eigenvectors**: Concepts and applications of eigenvalues and eigenvectors.
> [... full syllabus ...]

---

#### Query: "What are the assignments for linear algebra course?"
```python
# LLM Tool Call
{
    'query': 'linear algebra',
    'intent': 'ASSIGNMENTS',
    'search_strategy': 'semantic_only',  # ← Vector search
    'course_codes': [],
    'information_type': ['assignments'],
    'departments': []
}
```

**Search Process:**
```
1. Generate embedding for "linear algebra"
2. Vector search to find linear algebra courses
3. Retrieve full details for top match
4. Filter to show only assignments
5. Return: Assignment breakdown for MATH028
```

**Response:**
> For the Linear Algebra course, specifically "MATH028: Linear Algebra for Machine Learning," here are the assignments:
>
> ### Assignments (10 total, 1250 points)
>
> **Exams** (1):
> - **Week 7**: Midterm Exam (200 points)
>
> **Homeworks** (6):
> - **Week 2**: Homework 1 (100 points)
> - **Week 4**: Homework 2 (100 points)
> - **Week 6**: Homework 3 (100 points)
> - **Week 8**: Homework 4 (100 points)
> - **Week 10**: Homework 5 (100 points)
> - **Week 12**: Homework 6 (100 points)

---

## Strategy 3: Hybrid (Not Yet Demonstrated)

### When Used
- Combines exact matching + semantic search + metadata filters
- Best for queries like: "Show me advanced Computer Science courses about machine learning"

### Example (Hypothetical)
```python
{
    'query': 'advanced machine learning courses in Computer Science',
    'intent': 'GENERAL',
    'search_strategy': 'hybrid',
    'course_codes': [],
    'information_type': [],
    'departments': ['Computer Science']
}
```

**Search Process:**
```
1. Check for exact course code matches (none in this case)
2. Generate embedding for "advanced machine learning courses"
3. Apply metadata filters: department="Computer Science", difficulty="advanced"
4. Combine results
5. Return: Advanced CS courses about machine learning
```

---

## Summary Table

| Query Type | Example | Strategy | Uses Vector Search? | Course Codes Extracted? |
|------------|---------|----------|---------------------|------------------------|
| **Course Code** | "What is CS004?" | `exact_match` | ❌ No | ✅ Yes: ["CS004"] |
| **Course Code + Intent** | "Prerequisites for CS004?" | `exact_match` | ❌ No | ✅ Yes: ["CS004"] |
| **Topic** | "I'm interested in linear algebra" | `semantic_only` | ✅ Yes | ❌ No: [] |
| **Topic + Intent** | "Prerequisites for linear algebra?" | `semantic_only` | ✅ Yes | ❌ No: [] |
| **Topic + Filters** | "Advanced ML courses in CS" | `hybrid` | ✅ Yes | ❌ No: [] |

---

## Key Insights

### 1. LLM Correctly Distinguishes Course Codes from Topics

**Course Code (CS004):**
- Strategy: `exact_match`
- No vector search
- Direct lookup

**Topic (linear algebra):**
- Strategy: `semantic_only`
- Vector search
- Finds multiple related courses

### 2. Intent Works Across Both Strategies

Whether using exact match or semantic search, the **intent** determines what information is returned:

- **GENERAL**: Summaries only (~87 tokens)
- **PREREQUISITES**: Summaries + prerequisite details (~881 tokens)
- **SYLLABUS_OBJECTIVES**: Summaries + syllabus details (~950 tokens)
- **ASSIGNMENTS**: Summaries + assignment details (~995 tokens)

### 3. Progressive Disclosure Works for Both

**Exact Match (CS004):**
- Tier 1: Summary for CS004
- Tier 2: Full details for CS004 (filtered by intent)

**Semantic Search (linear algebra):**
- Tier 1: Summaries for top 5 linear algebra courses
- Tier 2: Full details for top 1-2 courses (filtered by intent)

---

## Conclusion

The agent **intelligently chooses** between exact match and vector search:

✅ **Exact Match** when user mentions course codes (fast, precise)
✅ **Vector Search** when user asks about topics (semantic understanding)
✅ **Intent-based filtering** works for both strategies
✅ **Progressive disclosure** optimizes token usage in both cases

This demonstrates that **Approach 1 (LLM Does Everything)** successfully handles both structured queries (course codes) and unstructured queries (topics) with appropriate search strategies.

