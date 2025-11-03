# Agent Test Plan

## 🧪 Comprehensive Testing Guide

This document outlines how to test the Redis University Class Agent to ensure it works correctly after the recent fixes.

## 🚀 Setup

1. **Start the Redis Agent Memory Server:**
   ```bash
   docker-compose up
   ```

2. **Start the agent:**
   ```bash
   redis-class-agent --student-id test_user_$(date +%s)
   ```

## 📋 Test Cases

### 1. User Knowledge Summary Tool

**Test:** User profile queries
```
You: What do you know about me?
Expected: Should call `summarize_user_knowledge_tool`
Expected Response: "I don't have any stored information about you yet..."

You: Show me my profile
Expected: Should call `summarize_user_knowledge_tool`

You: What do you remember about me?
Expected: Should call `summarize_user_knowledge_tool`
```

### 2. Interest Expression & Recommendations

**Test:** User expresses interests
```
You: I like math
Expected: Should call `get_recommendations_tool` and `_store_memory_tool`
Expected Response: Personalized math course recommendations

You: I'm interested in programming
Expected: Should call `get_recommendations_tool` and `_store_memory_tool`
Expected Response: Programming course recommendations

You: Suggest courses for me
Expected: Should call `get_recommendations_tool`
Expected Response: Recommendations based on stored interests
```

### 3. Specific Course Searches

**Test:** Specific course requests
```
You: Show me CS courses
Expected: Should call `search_courses_tool`
Expected Response: List of computer science courses

You: Find programming classes
Expected: Should call `search_courses_tool`
Expected Response: Programming-related courses

You: What math courses are available?
Expected: Should call `search_courses_tool`
Expected Response: Mathematics courses
```

### 4. Major Information

**Test:** Major/program queries
```
You: What majors are available?
Expected: Should call `list_majors_tool`
Expected Response: List of all available majors

You: List all programs
Expected: Should call `list_majors_tool`
Expected Response: All degree programs
```

### 5. Memory Management

**Test:** Memory clearing/reset
```
You: Clear my profile
Expected: Should call `clear_user_memories_tool`
Expected Response: Confirmation of reset

You: Ignore all that
Expected: Should call `clear_user_memories_tool`
Expected Response: Reset confirmation

You: Reset what you know about me
Expected: Should call `clear_user_memories_tool`
Expected Response: Reset confirmation
```

### 6. Memory Persistence Test

**Test:** Information storage and retrieval
```
1. You: I prefer online courses
   Expected: Should call `_store_memory_tool`

2. You: My goal is to become a data scientist
   Expected: Should call `_store_memory_tool`

3. You: What do you know about me?
   Expected: Should call `summarize_user_knowledge_tool`
   Expected Response: Should include preferences and goals from steps 1-2
```

### 7. Sequential Interaction Test

**Test:** Complete user journey
```
1. You: Hi
   Expected: Greeting, no tools called

2. You: I like math and science
   Expected: `get_recommendations_tool` + `_store_memory_tool`

3. You: What do you know about me?
   Expected: `summarize_user_knowledge_tool` with math/science interests

4. You: Suggest more courses
   Expected: `get_recommendations_tool` based on stored interests

5. You: Show me specific calculus courses
   Expected: `search_courses_tool` for calculus

6. You: Clear my preferences
   Expected: `clear_user_memories_tool`

7. You: What do you know about me?
   Expected: `summarize_user_knowledge_tool` showing reset state
```

## ✅ Success Criteria

For each test case, verify:

1. **Correct Tool Selection**: The agent calls the expected tool (check the HTTP logs)
2. **Appropriate Response**: The response matches the expected behavior
3. **Memory Persistence**: Information is stored and retrieved correctly
4. **Error Handling**: Graceful fallbacks when tools fail

## 🚨 Common Issues to Watch For

1. **Wrong Tool Called**: Agent calls `search_courses_tool` for everything
2. **No Tool Called**: Agent responds without using any tools
3. **Memory Not Stored**: User interests/preferences not saved
4. **Memory Not Retrieved**: Stored information not shown in summaries
5. **Tool Errors**: Tools fail with validation or execution errors

## 📊 Expected Tool Usage Patterns

- **User Knowledge Queries** → `summarize_user_knowledge_tool`
- **Interest Expression** → `get_recommendations_tool` + `_store_memory_tool`
- **Course Suggestions** → `get_recommendations_tool`
- **Specific Course Search** → `search_courses_tool`
- **Major Information** → `list_majors_tool`
- **Memory Management** → `clear_user_memories_tool`

## 🔧 Debugging Tips

1. **Check HTTP Logs**: Look for tool calls in the request logs
2. **Verify Tool Names**: Ensure the agent is calling the correct tool names
3. **Test Memory Server**: Verify the Redis memory server is running and accessible
4. **Check API Keys**: Ensure OpenAI API key is valid for LLM calls

## 📝 Test Results Template

```
Test Case: [Description]
User Input: "[Input]"
Expected Tool: [tool_name]
Actual Tool: [tool_name]
Response Quality: [Good/Poor/Error]
Memory Stored: [Yes/No/N/A]
Status: [✅ Pass / ❌ Fail]
Notes: [Any observations]
```

Run through all test cases and document the results to verify the agent is working correctly!
