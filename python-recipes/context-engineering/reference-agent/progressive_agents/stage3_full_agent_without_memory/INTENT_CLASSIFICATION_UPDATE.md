# Intent Classification and Adaptive Detail Levels - Stage 3 Update

## Problem Statement

The original Stage 3 agent had a critical issue: it performed full course searches with detailed syllabi for **every query**, including:
- Simple greetings ("hello", "hi", "thanks")
- Course overview questions ("What ML courses are available?")
- Specific detail requests ("Show me the syllabus for CS101")

This resulted in:
- **Wasted tokens** (~3,800+ tokens for greetings)
- **Poor user experience** (overwhelming information for simple queries)
- **Inefficient retrieval** (always returning full syllabi even when not needed)

## Solution: Intent Classification + Adaptive Detail Levels

### Architecture

```
User Query
    ↓
[1. Classify Intent] ← NEW!
    ↓
    ├─→ GREETING → [Handle Greeting] → END
    ├─→ COURSE_OVERVIEW → [Decompose] → [Research with detail_level=summary]
    └─→ COURSE_DETAILS → [Decompose] → [Research with detail_level=full]
```

### Components Added

#### 1. Intent Classification Node (`classify_intent_node`)

Classifies queries into:
- **GREETING**: Social interactions, pleasantries
- **COURSE_OVERVIEW**: "What courses exist?", "Show me ML courses"
- **COURSE_DETAILS**: "Show me the syllabus", "What are the assignments?"
- **GENERAL_QUESTION**: Other course-related questions

Determines detail level:
- **none**: No course data needed (greetings)
- **summary**: Course summaries only (overview questions)
- **full**: Full details with syllabi (specific requests)

#### 2. Greeting Handler Node (`handle_greeting_node`)

Handles non-course queries without triggering course search:
- Responds naturally to greetings
- Introduces the agent's capabilities
- Skips all course retrieval logic

#### 3. Adaptive Detail Levels in Research

Updated `search_courses_sync()` to accept `detail_level` parameter:
- **summary**: Returns ONLY course summaries (~300-400 tokens)
- **full**: Returns summaries + full syllabi for top 2-3 (~700 tokens)

#### 4. Summary-Only Context Assembly

Added `assemble_summary_only_context()` to `HierarchicalContextAssembler`:
- Returns course overviews without syllabi
- Perfect for "what courses exist?" queries
- Much more concise than full hierarchical context

### State Updates

Added to `WorkflowState`:
```python
query_intent: Optional[str]  # "greeting", "course_overview", "course_details", "general_question"
detail_level: Optional[str]  # "none", "summary", "full"
```

### Workflow Updates

New workflow flow:
1. **classify_intent** (NEW entry point)
2. Route based on intent:
   - GREETING → **handle_greeting** → END
   - Others → **decompose_query** → ... (existing flow)
3. Research respects `detail_level` from classification

## Results

### Before (Original Stage 3)

| Query Type | Behavior | Tokens | Issue |
|------------|----------|--------|-------|
| "hello" | Full course search + syllabi | ~3,800 | Wasteful |
| "What ML courses?" | Full course search + syllabi | ~2,600 | Too verbose |
| "Show syllabus for CS101" | Full course search + syllabi | ~3,900 | Appropriate |

### After (With Intent Classification)

| Query Type | Intent | Detail Level | Tokens | Improvement |
|------------|--------|--------------|--------|-------------|
| "hello" | GREETING | none | ~50 | ✅ 99% reduction |
| "What ML courses?" | COURSE_OVERVIEW | summary | ~400 | ✅ 85% reduction |
| "Show syllabus for CS101" | COURSE_DETAILS | full | ~3,900 | ✅ Appropriate |

## Example Outputs

### Greeting Query: "hello"

**Before**: 3,800 tokens of course data with full syllabi for 3 courses

**After**:
```
Hello! It's great to hear from you. I'm a course advisor agent here to help you 
find courses, view syllabi, check prerequisites, and more. How can I assist you today?
```
**Tokens**: ~50 (99% reduction)

---

### Overview Query: "What machine learning courses are available?"

**Before**: 2,600 tokens with full syllabi for top 3 courses

**After**:
```
Found 5 relevant courses:

1. CS002: Deep Learning and Neural Networks
   Department: Computer Science
   Instructor: Abigail Shaffer
   Credits: 4 | Level: Graduate
   Format: Hybrid
   Description: Advanced neural network architectures...
   Tags: deep learning, neural networks, transformers

2. CS009: Computer Vision
   ...
```
**Tokens**: ~400 (85% reduction, summaries only)

---

### Detail Query: "Show me the syllabus for CS002"

**Before**: 3,900 tokens with full syllabi

**After**: Same behavior (3,900 tokens with full syllabi)
**Tokens**: ~3,900 (appropriate - user asked for details)

## Educational Value

This update demonstrates:

### 1. Query Understanding
- Not all queries need the same level of detail
- Intent classification is crucial for efficient retrieval
- Context engineering includes understanding user needs

### 2. Adaptive Retrieval
- Match retrieval depth to query intent
- Progressive disclosure based on what's actually needed
- Token budget management through smart routing

### 3. User Experience
- Don't overwhelm users with unnecessary information
- Respond appropriately to different query types
- Balance efficiency with information quality

### 4. Production Patterns
- Intent classification is a real-world requirement
- Adaptive detail levels improve both cost and UX
- Routing logic prevents wasteful operations

## Implementation Details

### Files Modified

1. **`agent/state.py`**
   - Added `query_intent` and `detail_level` fields

2. **`agent/nodes.py`**
   - Added `classify_intent_node()` - LLM-based intent classification
   - Added `handle_greeting_node()` - Non-course query handler
   - Updated `research_node()` - Respects detail_level

3. **`agent/workflow.py`**
   - Changed entry point to `classify_intent`
   - Added routing logic based on intent
   - Added greeting handler to workflow

4. **`agent/tools.py`**
   - Updated `search_courses_sync()` - Accepts `detail_level` parameter
   - Implements summary vs full retrieval logic

5. **`redis_context_course/hierarchical_context.py`**
   - Added `assemble_summary_only_context()` method
   - Supports summary-only context assembly

### Key Design Decisions

#### Why LLM-based Intent Classification?

- **Flexibility**: Handles natural language variations
- **Accuracy**: Better than regex/keyword matching
- **Extensibility**: Easy to add new intent categories
- **Cost**: Minimal (~50 tokens per classification)

#### Why Three Detail Levels?

- **none**: Greetings, off-topic (no retrieval needed)
- **summary**: Overview questions (broad awareness)
- **full**: Specific requests (deep information)

This covers the spectrum of user needs without over-complicating.

#### Why Route at Workflow Level?

- **Efficiency**: Skip unnecessary nodes for greetings
- **Clarity**: Explicit routing makes flow obvious
- **Maintainability**: Easy to add new routes

## Testing

### Test Cases

```bash
# Greeting (should NOT search courses)
python cli.py "hello"
python cli.py "thanks"
python cli.py "how are you"

# Overview (should return summaries only)
python cli.py "What machine learning courses are available?"
python cli.py "Show me all computer science courses"
python cli.py "What courses can I take?"

# Details (should return full syllabi)
python cli.py "Show me the syllabus for CS101"
python cli.py "What are the assignments in CS202?"
python cli.py "Tell me about the grading policy for MATH301"
```

### Expected Behavior

| Query | Intent | Detail | Course Search | Syllabi |
|-------|--------|--------|---------------|---------|
| "hello" | GREETING | none | ❌ No | ❌ No |
| "What ML courses?" | COURSE_OVERVIEW | summary | ✅ Yes | ❌ No |
| "Show syllabus CS101" | COURSE_DETAILS | full | ✅ Yes | ✅ Yes (top 2-3) |

## Future Enhancements

### 1. More Granular Intent Categories
- PREREQUISITE_CHECK
- INSTRUCTOR_INFO
- SCHEDULE_QUERY
- ENROLLMENT_INFO

### 2. Dynamic Detail Level Adjustment
- Start with summary, offer to show more
- "Would you like to see the full syllabus?"
- Progressive disclosure through conversation

### 3. Intent-Specific Tools
- Different tools for different intents
- Specialized retrievers per query type
- Optimized context assembly per intent

### 4. Confidence Thresholds
- Handle ambiguous queries
- Ask clarifying questions
- Multi-intent queries

## Conclusion

This update transforms Stage 3 from a "one-size-fits-all" retrieval system into an **intelligent, adaptive agent** that:

✅ Understands user intent
✅ Adapts retrieval depth to query needs
✅ Minimizes token waste
✅ Improves user experience
✅ Demonstrates production-ready patterns

The agent now exhibits true intelligence: knowing **when** to retrieve, **what** to retrieve, and **how much detail** to provide.

