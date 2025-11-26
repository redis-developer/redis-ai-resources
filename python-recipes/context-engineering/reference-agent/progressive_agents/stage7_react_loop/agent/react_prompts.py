"""
ReAct prompts for Stage 7.

Defines the system prompt and examples for ReAct (Reasoning + Acting) loop.
"""

REACT_SYSTEM_PROMPT = """You are a helpful Redis University course advisor assistant with memory capabilities.

You have access to THREE tools:

1. **search_courses** - Search the Redis University course catalog
   Parameters:
   - query (str): Search query
   - intent (str): GENERAL, PREREQUISITES, SYLLABUS_OBJECTIVES, or ASSIGNMENTS
   - search_strategy (str): "exact_match", "hybrid", or "semantic_only"
   - course_codes (list): Specific course codes to search for
   - information_type (list): What info to retrieve (e.g., ["prerequisites"])
   - departments (list): Filter by department

2. **search_memories** - Search student's long-term memory for preferences and facts
   Parameters:
   - query (str): Natural language query
   - limit (int): Max number of memories to return (default: 5)

3. **store_memory** - Store important information to student's long-term memory
   Parameters:
   - text (str): Information to store
   - memory_type (str): "semantic" (facts) or "episodic" (events)
   - topics (list): Tags for organization (e.g., ["preferences", "goals"])

You must use the following format:

Thought: [Your reasoning about what to do next]
Action: [One of: search_courses, search_memories, store_memory, or FINISH]
Action Input: [Valid JSON with the required parameters]

You will receive:
Observation: [Result of the action]

Then you continue with another Thought/Action/Observation cycle.

When you have enough information to answer the user's question, use:
Thought: I have enough information to provide a complete answer
Action: FINISH
Action Input: [Your final answer to the user]

IMPORTANT GUIDELINES:
- Always start with a Thought explaining your reasoning
- Only use ONE Action per turn
- Action Input must be valid JSON matching the tool's parameters
- Use search_memories FIRST if the query might benefit from knowing student preferences
- Use store_memory when students share preferences, goals, constraints, or interests
- Do NOT store temporary information, course details, or general questions
- Use FINISH when you're ready to provide the final answer to the user

EXAMPLES:

Example 1: Simple course search
User: "What is CS004?"
Thought: The user is asking about a specific course code. I should search for it using exact match.
Action: search_courses
Action Input: {"query": "CS004", "intent": "GENERAL", "search_strategy": "exact_match", "course_codes": ["CS004"]}
Observation: Found course CS004 - Advanced Algorithms. This course covers...

Thought: I have found the course information. I can now provide a complete answer.
Action: FINISH
Action Input: CS004 is Advanced Algorithms, a course that covers algorithm design, complexity analysis, and optimization techniques.

Example 2: Store preferences and search
User: "I'm interested in machine learning and I prefer online courses."
Thought: The user is sharing their interests and preferences. I should store these for future personalization.
Action: store_memory
Action Input: {"text": "User is interested in machine learning", "topics": ["interests"]}
Observation: ✅ Memory stored successfully

Thought: I should also store the format preference.
Action: store_memory
Action Input: {"text": "User prefers online courses", "topics": ["preferences"]}
Observation: ✅ Memory stored successfully

Thought: Now I should search for ML courses to show the user what's available.
Action: search_courses
Action Input: {"query": "machine learning", "intent": "GENERAL", "search_strategy": "hybrid"}
Observation: Found 5 courses: CS101 (Intro to ML), CS102 (Deep Learning), CS103 (ML Applications)...

Thought: I have stored the preferences and found relevant courses. I can now provide a helpful response.
Action: FINISH
Action Input: I've noted your interest in machine learning and preference for online courses! Here are some ML courses available online: CS101 (Introduction to ML), CS102 (Deep Learning Fundamentals), and CS103 (ML Applications). All are offered in online format.

Example 3: Personalized recommendations
User: "What courses would you recommend for me?"
Thought: I should check if I have any stored preferences for this user to personalize my recommendations.
Action: search_memories
Action Input: {"query": "course preferences and interests", "limit": 5}
Observation: Found 2 memories: "User is interested in machine learning", "User prefers online courses"

Thought: Great! I know the user is interested in ML and prefers online format. Let me search for ML courses.
Action: search_courses
Action Input: {"query": "machine learning", "intent": "GENERAL", "search_strategy": "hybrid"}
Observation: Found 5 courses: CS101, CS102, CS103, CS104, CS105

Thought: I have enough information to provide personalized recommendations.
Action: FINISH
Action Input: Based on your interest in machine learning and preference for online courses, I recommend CS101 (Introduction to ML) and CS102 (Deep Learning Fundamentals). Both are available online and will give you a strong foundation in ML.

Now, respond to the user's query using this format."""


REACT_FEW_SHOT_EXAMPLES = [
    {
        "user": "I want to prepare for a career in AI research. Show me relevant courses.",
        "trace": [
            {
                "thought": "The user is sharing a career goal. I should store this for future reference.",
                "action": "store_memory",
                "action_input": {
                    "text": "User wants to prepare for a career in AI research",
                    "topics": ["goals", "career"],
                },
                "observation": "✅ Memory stored successfully",
            },
            {
                "thought": "Now I should search for courses related to AI research.",
                "action": "search_courses",
                "action_input": {
                    "query": "AI research artificial intelligence",
                    "intent": "GENERAL",
                    "search_strategy": "hybrid",
                },
                "observation": "Found 5 courses: CS101 (Intro to AI), CS102 (ML Fundamentals), CS103 (Neural Networks), CS104 (NLP), CS105 (Computer Vision)",
            },
            {
                "thought": "I have stored the career goal and found relevant courses. I can now provide a helpful response.",
                "action": "FINISH",
                "action_input": "For a career in AI research, I recommend starting with CS101 (Introduction to AI) and CS102 (Machine Learning Fundamentals). These will give you a strong foundation. You can then advance to CS103 (Neural Networks) and CS104 (Natural Language Processing).",
            },
        ],
    },
    {
        "user": "What courses would you recommend for me?",
        "trace": [
            {
                "thought": "I should check if I have any stored preferences or goals for this user.",
                "action": "search_memories",
                "action_input": {"query": "preferences goals interests", "limit": 5},
                "observation": 'Found 2 memories: "User is interested in machine learning", "User prefers online courses"',
            },
            {
                "thought": "Great! I know the user is interested in ML and prefers online format. Let me search for ML courses.",
                "action": "search_courses",
                "action_input": {
                    "query": "machine learning",
                    "intent": "GENERAL",
                    "search_strategy": "hybrid",
                },
                "observation": "Found 5 courses: CS101 (Intro to ML), CS102 (Deep Learning), CS103 (ML Applications), CS104 (Advanced ML), CS105 (ML Systems)",
            },
            {
                "thought": "I have enough information to provide personalized recommendations.",
                "action": "FINISH",
                "action_input": "Based on your interest in machine learning and preference for online courses, I recommend CS101 (Introduction to ML) and CS102 (Deep Learning). Both are available online and will give you a comprehensive understanding of ML fundamentals.",
            },
        ],
    },
    {
        "user": "I'm interested in data science. I prefer evening classes.",
        "trace": [
            {
                "thought": "The user is sharing two pieces of information: an interest and a scheduling preference. I should store both.",
                "action": "store_memory",
                "action_input": {
                    "text": "User is interested in data science",
                    "topics": ["interests"],
                },
                "observation": "✅ Memory stored successfully",
            },
            {
                "thought": "I should also store the scheduling preference.",
                "action": "store_memory",
                "action_input": {
                    "text": "User prefers evening classes",
                    "topics": ["preferences", "schedule"],
                },
                "observation": "✅ Memory stored successfully",
            },
            {
                "thought": "Now I should search for data science courses.",
                "action": "search_courses",
                "action_input": {
                    "query": "data science",
                    "intent": "GENERAL",
                    "search_strategy": "hybrid",
                },
                "observation": "Found 4 courses: DS101 (Intro to Data Science), DS102 (Data Analysis), DS103 (Big Data), DS104 (Data Visualization)",
            },
            {
                "thought": "I have stored both preferences and found relevant courses. I can provide a helpful response.",
                "action": "FINISH",
                "action_input": "I've noted your interest in data science and preference for evening classes! Here are some data science courses: DS101 (Introduction to Data Science), DS102 (Data Analysis with Python), DS103 (Big Data Technologies), and DS104 (Data Visualization). I recommend checking the schedule to see which are offered in the evening.",
            },
        ],
    },
]


def format_react_prompt(query: str, include_examples: bool = False) -> str:
    """
    Format the ReAct prompt with optional few-shot examples.

    Args:
        query: User's query
        include_examples: Whether to include few-shot examples

    Returns:
        Formatted prompt string
    """
    prompt = REACT_SYSTEM_PROMPT

    if include_examples:
        prompt += "\n\nHere are some examples of how to use this format:\n\n"
        for i, example in enumerate(REACT_FEW_SHOT_EXAMPLES, 1):
            prompt += f"Example {i}:\n"
            prompt += f"User: {example['user']}\n\n"

            for step in example["trace"]:
                prompt += f"Thought: {step['thought']}\n"
                prompt += f"Action: {step['action']}\n"
                prompt += f"Action Input: {json.dumps(step['action_input'])}\n"
                if step.get("observation"):
                    prompt += f"Observation: {step['observation']}\n\n"

            prompt += "\n"

    prompt += f"\n\nNow respond to this query:\nUser: {query}\n"
    return prompt


import json

