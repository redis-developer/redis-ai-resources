# Logging and Intent Classification Updates

## Overview

Applied two important updates across all progressive agent stages:

1. **Suppressed httpx INFO logs** - Cleaner console output
2. **Improved intent classification** - Default to summary for general questions

---

## 1. Suppressed httpx Logs

### Problem
The httpx library was logging every HTTP request to OpenAI API:
```
22:44:50 httpx INFO   HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
```

This cluttered the console output and made it harder to see the agent's actual workflow.

### Solution
Added logging configuration to suppress httpx INFO logs in all stages:

```python
# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)
```

### Files Modified
- `stage1_baseline_rag/agent/nodes.py`
- `stage2_context_engineered/agent/nodes.py`
- `stage3_full_agent_without_memory/agent/nodes.py`
- `stage4_hybrid_search_with_ner/agent/nodes.py`

### Result
Console output now shows only relevant workflow logs:
```
🎯 Classifying intent for: 'What is CS002?'
🎯 Intent: COURSE_OVERVIEW, Detail Level: summary
🔍 Extracting entities from query...
✅ Extracted entities: course_codes=['CS002']
```

---

## 2. Improved Intent Classification

### Problem
Queries like "What is CS002?" or "Tell me about CS002" were sometimes classified as COURSE_DETAILS with full detail level, returning complete syllabi when users just wanted a summary.

### Solution
Updated the intent classification prompt to explicitly handle "What is X?" questions and default to summary level unless specific details are requested.

### Changes to Intent Classification Prompt

**Before:**
```
Intent Categories:
- COURSE_OVERVIEW: Asking about what courses exist, course listings, general course information
- COURSE_DETAILS: Asking for specific details like syllabus, assignments, schedule, grading policy

Detail Levels:
- summary: Course summaries only (overview questions)
- full: Full course details with syllabi (specific detail requests)
```

**After:**
```
Intent Categories:
- COURSE_OVERVIEW: Asking about what courses exist, course listings, general course information, or "What is <course>?"
- COURSE_DETAILS: Asking for SPECIFIC details like syllabus, assignments, schedule, grading policy, or explicitly asking to "learn more"

Detail Levels:
- summary: Course summaries only (overview questions, "What is X?" questions, general inquiries)
- full: Full course details with syllabi (ONLY when explicitly requesting syllabus, assignments, grading, schedule, or "learn more")

IMPORTANT: 
- "What is CS002?" or "Tell me about CS002" → COURSE_OVERVIEW with summary level
- "Show me the syllabus for CS002" → COURSE_DETAILS with full level
- "What are the assignments for CS002?" → COURSE_DETAILS with full level
- Default to summary unless explicitly requesting detailed information
```

### Files Modified
- `stage3_full_agent_without_memory/agent/nodes.py`
- `stage4_hybrid_search_with_ner/agent/nodes.py`

(Stage 1 and 2 don't have intent classification)

### Examples

**Query: "What is CS002?"**
- **Before**: Might return COURSE_DETAILS with full syllabus (~700 tokens)
- **After**: Returns COURSE_OVERVIEW with summary only (~100 tokens)

**Query: "Tell me about machine learning courses"**
- **Before**: Might return full details for all courses
- **After**: Returns summaries only (~400 tokens)

**Query: "Show me the syllabus for CS002"**
- **Before**: Returns full details (~700 tokens)
- **After**: Returns full details (~700 tokens) - CORRECT, user explicitly asked for syllabus

**Query: "What are the assignments for CS002?"**
- **Before**: Returns full details (~700 tokens)
- **After**: Returns full details (~700 tokens) - CORRECT, user explicitly asked for assignments
  - In Stage 4: Also filters to show ONLY assignments (~150 tokens)

---

## Benefits

### 1. Cleaner Console Output
- No more httpx request logs cluttering the output
- Easier to follow the agent's workflow
- Better debugging experience

### 2. Better User Experience
- General questions get concise summaries
- Users aren't overwhelmed with information
- Detailed information only when explicitly requested

### 3. Token Efficiency
- "What is X?" queries use ~85% fewer tokens
- Reduces API costs
- Faster response times

### 4. Progressive Disclosure
- Users see summaries first
- Can ask for more details if interested
- Natural conversation flow

---

## Testing

### Test Scenarios

**1. General Question (Should Return Summary)**
```bash
python cli.py "What is CS002?"
```
Expected: COURSE_OVERVIEW, summary level, ~100 tokens

**2. Specific Detail Request (Should Return Full)**
```bash
python cli.py "Show me the syllabus for CS002"
```
Expected: COURSE_DETAILS, full level, ~700 tokens

**3. Assignment Request (Should Return Full, Filtered in Stage 4)**
```bash
python cli.py "What are the assignments for CS002?"
```
Expected: COURSE_DETAILS, full level
- Stage 3: ~700 tokens (full details)
- Stage 4: ~150 tokens (assignments only)

**4. Topic Exploration (Should Return Summary)**
```bash
python cli.py "What machine learning courses are available?"
```
Expected: COURSE_OVERVIEW, summary level, ~400 tokens

**5. Greeting (Should Skip Course Search)**
```bash
python cli.py "hello"
```
Expected: GREETING, none level, ~50 tokens

---

## Implementation Notes

### Logging Configuration
The httpx logging suppression must be placed **after** the logging import but **before** any HTTP requests are made. In all stages, it's placed near the top of `nodes.py` after the imports.

### Intent Classification
The improved prompt is in the `classify_intent_node()` function in both Stage 3 and Stage 4. The key is the explicit examples and the "IMPORTANT" section that guides the LLM to default to summary.

### Backward Compatibility
These changes are backward compatible:
- Existing queries that requested details still get details
- Existing queries that requested summaries still get summaries
- Only ambiguous queries like "What is X?" are now handled better

---

---

## 3. Added Debug Mode to CLI

### Problem
Error tracebacks were always shown in the CLI, cluttering the output for end users. Detailed stack traces are useful for developers but confusing for regular users.

### Solution
Added a `--debug` flag to all CLI files that controls whether detailed error messages and tracebacks are shown.

**Default behavior (no --debug):**
```
❌ Error: Connection failed
```

**With --debug flag:**
```
❌ Error: Connection failed
Traceback (most recent call last):
  File "cli.py", line 162, in interactive_mode
    result = self.ask_question(query)
  ...
```

### Files Modified
- `stage1_baseline_rag/cli.py`
- `stage2_context_engineered/cli.py`
- `stage3_full_agent_without_memory/cli.py`
- `stage4_hybrid_search_with_ner/cli.py`

### Changes Made

**1. Added debug parameter to CLI class:**
```python
def __init__(self, cleanup_on_exit: bool = False, debug: bool = False):
    self.debug = debug
```

**2. Conditional traceback printing:**
```python
except Exception as e:
    logger.error(f"Error: {e}")
    if self.debug:
        import traceback
        traceback.print_exc()
```

**3. Added --debug argument:**
```python
parser.add_argument(
    "--debug",
    action="store_true",
    help="Show detailed error messages and tracebacks"
)
```

**4. Pass debug flag to CLI:**
```python
cli = CourseQACLI(cleanup_on_exit=cleanup, debug=args.debug)
```

### Usage

**Normal mode (clean errors):**
```bash
python cli.py "What courses are available?"
```

**Debug mode (detailed errors):**
```bash
python cli.py --debug "What courses are available?"
```

**Interactive mode with debug:**
```bash
python cli.py --debug
```

### Benefits

1. **Cleaner User Experience**: End users see simple error messages
2. **Developer-Friendly**: Developers can enable debug mode for troubleshooting
3. **Professional Output**: Production-like behavior by default
4. **Easy Debugging**: One flag to see all details when needed

---

## Summary

✅ **Suppressed httpx logs** in all 4 stages for cleaner output
✅ **Improved intent classification** in Stage 3 and 4 to default to summary
✅ **Added debug mode** to all 4 CLI files for conditional error tracebacks
✅ **Better user experience** with progressive disclosure
✅ **Token efficiency** improved by ~85% for general questions
✅ **Backward compatible** with existing query patterns

These changes make the agents more production-ready and demonstrate best practices for:
- Clean logging and observability
- Intent understanding and classification
- Progressive disclosure patterns
- Token efficiency and cost optimization
- User-friendly error handling

