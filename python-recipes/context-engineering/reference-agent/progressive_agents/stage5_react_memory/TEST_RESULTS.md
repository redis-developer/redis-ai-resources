# Stage 5 Agent Testing Results

## Overview

Stage 5 has been updated to use **Approach 1: LLM Does Everything (Complex Tool)** where the LLM has full control over:
- **When** to search (decides if search is needed)
- **What** intent to use (GENERAL, PREREQUISITES, SYLLABUS_OBJECTIVES, ASSIGNMENTS)
- **How** to search (exact_match, hybrid, semantic_only)
- **Which** entities to extract (course codes, departments, etc.)

## Architecture Changes

### Before (Scripted Workflow)
```
load_memory → classify_intent → extract_entities → decompose_query
    → check_cache → research → evaluate_quality → synthesize → save_memory
```

**Characteristics:**
- Hardcoded function calls in nodes
- LLM just processes data
- No decision-making power

### After (Agentic Workflow)
```
load_memory → classify_intent → agent → save_memory
```

**Characteristics:**
- LLM decides when to call `search_courses` tool
- LLM determines all tool parameters (intent, strategy, entities)
- Full agentic behavior with tool calling

## Tool Definition

The `search_courses` tool has the following parameters:

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

## Test Results

### Test 1: GENERAL Intent
**Question:** "What is CS004?"

**LLM Tool Call:**
```python
{
    'query': 'CS004',
    'intent': 'GENERAL',
    'search_strategy': 'exact_match',
    'course_codes': ['CS004'],
    'information_type': [],
    'departments': []
}
```

**Response:**
> The course **CS004** is titled **Computer Vision** and is offered by the Computer Science department. It is an advanced-level course worth 4 credits and is conducted online. The course covers topics such as image processing, object detection, and visual recognition systems. The instructor for this course is Kimberly Moon.

**Analysis:** ✅ PASS
- Correctly identified intent as GENERAL
- Used exact_match strategy for course code
- Returned summary-level information only
- No detailed prerequisites/syllabus/assignments

---

### Test 2: PREREQUISITES Intent
**Question:** "What are the prerequisites for CS004?"

**LLM Tool Call:**
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

**Response:**
> The course CS004, titled "Computer Vision," is an advanced-level course offered by the Computer Science department. Here are the prerequisites for CS004:
>
> - **Prerequisites**: The course requires a solid understanding of basic programming and data structures. Familiarity with linear algebra, probability, and statistics is also recommended to grasp the concepts effectively.

**Analysis:** ✅ PASS
- Correctly identified intent as PREREQUISITES
- Used exact_match strategy for course code
- Returned detailed prerequisite information
- Filtered response to focus on prerequisites

---

### Test 3: SYLLABUS_OBJECTIVES Intent
**Question:** "What's the syllabus for CS004?"

**LLM Tool Call:**
```python
{
    'query': 'CS004',
    'intent': 'SYLLABUS_OBJECTIVES',
    'search_strategy': 'exact_match',
    'course_codes': ['CS004'],
    'information_type': ['syllabus'],
    'departments': []
}
```

**Response:**
> The syllabus for CS004: Computer Vision, taught by Kimberly Moon, is structured over 14 weeks and covers a comprehensive range of topics in computer vision. Here's a detailed breakdown:
>
> ### Course Syllabus (14 weeks)
>
> **Week 1: Introduction to Computer Vision**
> - Topics: Introduction to Computer Vision - Part 1 & 2
> - Readings: Chapter 1, Research Paper 1
>
> **Week 2: Image Processing Basics**
> - Topics: Image Processing Basics - Parts 1 to 4
> - Readings: Chapter 2, Research Paper 2
> - Due: Homework 1
>
> [... full 14-week syllabus ...]

**Analysis:** ✅ PASS
- Correctly identified intent as SYLLABUS_OBJECTIVES
- Used exact_match strategy for course code
- Returned detailed syllabus information
- Filtered response to focus on syllabus/learning objectives

---

### Test 4: ASSIGNMENTS Intent
**Question:** "What are the assignments for CS004?"

**LLM Tool Call:**
```python
{
    'query': 'CS004',
    'intent': 'ASSIGNMENTS',
    'search_strategy': 'exact_match',
    'course_codes': ['CS004'],
    'information_type': ['assignments'],
    'departments': []
}
```

**Response:**
> The course CS004: Computer Vision, taught by Kimberly Moon, includes a variety of assignments throughout the semester. Here's a detailed breakdown of the assignments:
>
> ### Exams
> - **Midterm Exam**: Week 7 (200 points)
>
> ### Homeworks
> - **Homework 1**: Week 2 (100 points)
> - **Homework 2**: Week 4 (100 points)
> - **Homework 3**: Week 6 (100 points)
> - **Homework 4**: Week 8 (100 points)
> - **Homework 5**: Week 10 (100 points)
> - **Homework 6**: Week 12 (100 points)
>
> ### Projects
> - **Project Proposal**: Week 10 (50 points)
> - **Project Draft**: Week 12 (100 points)
> - **Final Project**: Week 14 (300 points)

**Analysis:** ✅ PASS
- Correctly identified intent as ASSIGNMENTS
- Used exact_match strategy for course code
- Returned detailed assignment information
- Filtered response to focus on assignments/projects/exams

---

## Summary

| Intent | Question | Tool Parameters Correct? | Response Matches Intent? | Result |
|--------|----------|-------------------------|-------------------------|--------|
| GENERAL | "What is CS004?" | ✅ Yes | ✅ Yes | ✅ PASS |
| PREREQUISITES | "What are the prerequisites for CS004?" | ✅ Yes | ✅ Yes | ✅ PASS |
| SYLLABUS_OBJECTIVES | "What's the syllabus for CS004?" | ✅ Yes | ✅ Yes | ✅ PASS |
| ASSIGNMENTS | "What are the assignments for CS004?" | ✅ Yes | ✅ Yes | ✅ PASS |

**Overall: 4/4 tests passed (100%)**

## Key Observations

1. **LLM correctly determines intent**: The LLM accurately identifies what type of information the user wants based on the question.

2. **LLM correctly chooses search strategy**: For all questions mentioning "CS004", the LLM correctly chose `exact_match` strategy.

3. **LLM correctly extracts entities**: The LLM properly extracted course codes and information types from the questions.

4. **Progressive disclosure works**: The tool returns different levels of detail based on intent:
   - GENERAL: ~87 tokens (summary only)
   - PREREQUISITES: ~881 tokens (summary + prerequisite details)
   - SYLLABUS_OBJECTIVES: ~950 tokens (summary + syllabus details)
   - ASSIGNMENTS: ~995 tokens (summary + assignment details)

5. **Responses are well-formatted**: The LLM synthesizes the tool results into clear, helpful answers.

## Conclusion

**Approach 1 (LLM Does Everything) is working successfully!**

The LLM demonstrates strong capability in:
- Understanding user intent from natural language
- Choosing appropriate search strategies
- Extracting relevant entities
- Formulating proper tool calls
- Synthesizing results into helpful responses

This validates that the complex tool approach can work well when the LLM is given clear instructions and well-designed tool schemas.

