# Search Parameters Across All Stages

## Overview

This document details the similarity thresholds, k values, and search parameters used across all progressive agent stages.

---

## Key Parameters

### 1. **top_k (Number of Results)**

**Default:** `5` courses

**Where Used:**
- All stages (1, 2, 3, 4)
- Configurable in `search_courses_sync()` function

**Purpose:** Controls how many courses are returned from semantic search

**Trade-offs:**
- **Higher k (e.g., 10)**: More options, but more tokens and potential noise
- **Lower k (e.g., 3)**: Fewer options, more focused, but might miss relevant courses
- **Current value (5)**: Balanced - enough options without overwhelming

---

### 2. **similarity_threshold (Distance Threshold)**

The similarity threshold determines how similar a course must be to the query to be included in results.

#### Stage 1 & 2: Baseline
```python
similarity_threshold=0.5
```

#### Stage 3: Hierarchical Retrieval
```python
similarity_threshold=0.5  # Semantic search
```

#### Stage 4: Hybrid Search with NER

**Exact Match Strategy:**
```python
similarity_threshold=0.9  # Very high - only exact matches
```

**Hybrid Strategy:**
```python
# Exact matches for course codes
similarity_threshold=0.9

# Semantic search for topics/names
similarity_threshold=0.5
```

**Semantic Only Strategy:**
```python
similarity_threshold=0.5  # Standard semantic search
```

---

## Detailed Breakdown by Stage

### Stage 1: Baseline RAG

**File:** `stage1_baseline_rag/agent/nodes.py`

```python
basic_courses = await course_manager.search_courses(
    query=query,
    limit=5,
    similarity_threshold=0.5
)
```

**Characteristics:**
- Returns top 5 courses
- Threshold: 0.5 (moderate similarity required)
- Returns FULL details for ALL 5 courses (information overload)

---

### Stage 2: Context Engineered

**File:** `stage2_context_engineered/agent/nodes.py`

```python
basic_courses = await course_manager.search_courses(
    query=query,
    limit=5,
    similarity_threshold=0.5
)
```

**Characteristics:**
- Same search parameters as Stage 1
- Returns top 5 courses
- Threshold: 0.5
- Applies context engineering (cleaned format)
- Still returns same detail level for all courses

---

### Stage 3: Hierarchical Retrieval

**File:** `stage3_full_agent_without_memory/agent/tools.py`

```python
basic_results = await course_manager.search_courses(
    query=query,
    filters=None,
    limit=top_k,  # Default: 5
    similarity_threshold=0.5
)
```

**Characteristics:**
- Returns top 5 courses
- Threshold: 0.5
- **NEW:** Hierarchical retrieval
  - Summaries for ALL 5 courses
  - Full details (with syllabi) for top 2-3 only
- Adaptive detail level based on intent

---

### Stage 4: Hybrid Search with NER

**File:** `stage4_hybrid_search_with_ner/agent/tools.py`

#### Exact Match Strategy
```python
# For course codes (CS101, MATH202, etc.)
results = await course_manager.search_courses(
    query=course_code,
    filters=None,
    limit=1,  # Only need one exact match
    similarity_threshold=0.9  # Very high - exact match only
)
```

#### Hybrid Strategy
```python
# Step 1: Exact matches for course codes
results = await course_manager.search_courses(
    query=course_code,
    filters=None,
    limit=1,
    similarity_threshold=0.9
)

# Step 2: Semantic search with filters
semantic_results = await course_manager.search_courses(
    query=semantic_query,
    filters=metadata_filters,
    limit=top_k - len(basic_results),  # Fill remaining slots
    similarity_threshold=0.5
)
```

#### Semantic Only Strategy
```python
basic_results = await course_manager.search_courses(
    query=query,
    filters=metadata_filters,
    limit=top_k,  # Default: 5
    similarity_threshold=0.5
)
```

**Characteristics:**
- Adaptive k: 1 for exact matches, 5 for semantic
- Adaptive threshold: 0.9 for exact, 0.5 for semantic
- Combines multiple search strategies
- Deduplicates results by course code

---

## Similarity Threshold Explained

### What is Similarity Threshold?

The similarity threshold is the minimum cosine similarity score (0.0 to 1.0) required for a course to be included in results.

**Cosine Similarity Scale:**
- **1.0**: Identical vectors (perfect match)
- **0.9-1.0**: Very high similarity (exact or near-exact match)
- **0.7-0.9**: High similarity (strong match)
- **0.5-0.7**: Moderate similarity (relevant match)
- **0.3-0.5**: Low similarity (weak match)
- **0.0-0.3**: Very low similarity (likely irrelevant)

### Threshold Values Used

| Threshold | Use Case | Stage | Purpose |
|-----------|----------|-------|---------|
| **0.9** | Exact match | Stage 4 | Course code lookup (CS101, MATH202) |
| **0.5** | Semantic search | All stages | General topic/keyword search |
| **0.3** | Debug/testing | Debug scripts | Testing with very low threshold |

### Why 0.5 for Semantic Search?

**Rationale:**
- **Too high (0.7+)**: Misses relevant courses with different wording
- **Too low (0.3-)**: Returns too many irrelevant courses
- **0.5 (current)**: Balanced - captures relevant courses while filtering noise

**Example:**
```
Query: "machine learning courses"

Course: "Introduction to Machine Learning" → Similarity: 0.85 ✅
Course: "Advanced ML Algorithms" → Similarity: 0.72 ✅
Course: "Data Science Fundamentals" → Similarity: 0.58 ✅
Course: "Python Programming" → Similarity: 0.42 ❌
Course: "Database Systems" → Similarity: 0.28 ❌
```

### Why 0.9 for Exact Match?

**Rationale:**
- Course codes should match exactly or very closely
- Prevents false positives (CS101 vs CS102)
- Ensures precision for specific course requests

**Example:**
```
Query: "CS101"

Course: "CS101: Intro to Programming" → Similarity: 0.95 ✅
Course: "CS102: Data Structures" → Similarity: 0.78 ❌
Course: "CS201: Algorithms" → Similarity: 0.65 ❌
```

---

## Top-K Values

### Default: k=5

**Rationale:**
- Provides enough options for comparison
- Not overwhelming (unlike k=10 or k=20)
- Fits within reasonable token budget
- Allows for hierarchical disclosure (summaries for 5, details for 2-3)

### Adaptive K in Stage 4

**Exact Match:** k=1
- Only need one exact match per course code
- No need for multiple results

**Semantic Search:** k=5
- Standard exploratory search
- Multiple options for user to choose from

**Hybrid:** k=5 total
- Exact matches + semantic results
- Deduplicates to avoid showing same course twice

---

## Metadata Filters

### Available Filters

Stage 4 supports metadata filtering extracted from NER:

```python
metadata_filters = {
    "department": ["Computer Science", "Mathematics"],
    "difficulty_level": ["beginner", "intermediate"],
    "format": ["online", "in_person", "hybrid"],
    "semester": ["fall", "spring", "summer"],
    "credits": [3, 4]
}
```

### How Filters Work

Filters are applied **in addition to** similarity threshold:

```python
results = await course_manager.search_courses(
    query="machine learning",
    filters={"department": ["Computer Science"], "difficulty_level": ["beginner"]},
    limit=5,
    similarity_threshold=0.5
)
```

**Result:** Top 5 courses that:
1. Match "machine learning" with similarity ≥ 0.5
2. Are in Computer Science department
3. Are beginner level

---

## Recommendations

### When to Adjust Threshold

**Increase threshold (0.6-0.7):**
- Very specific queries (exact course names)
- High precision required
- Willing to sacrifice recall

**Decrease threshold (0.3-0.4):**
- Exploratory queries
- Broad topic searches
- High recall required
- Willing to accept some noise

### When to Adjust K

**Increase k (7-10):**
- Exploratory queries ("show me all ML courses")
- User wants comprehensive overview
- Have token budget for more results

**Decrease k (2-3):**
- Specific queries ("best intro course")
- Limited token budget
- User wants focused recommendations

---

## Summary

| Parameter | Stage 1-3 | Stage 4 (Exact) | Stage 4 (Hybrid) | Stage 4 (Semantic) |
|-----------|-----------|-----------------|------------------|-------------------|
| **top_k** | 5 | 1 | 5 | 5 |
| **threshold** | 0.5 | 0.9 | 0.9 + 0.5 | 0.5 |
| **filters** | None | None | Yes | Yes |
| **strategy** | Semantic only | Exact match | Multi-strategy | Semantic only |

**Key Insight:** Stage 4's adaptive approach uses different parameters based on query type, optimizing for both precision (exact match) and recall (semantic search).

