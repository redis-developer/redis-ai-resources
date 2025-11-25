"""
Stage 1: Baseline RAG Agent

This is a deliberately simple RAG implementation that demonstrates:
- Basic semantic search retrieval
- Raw JSON context formatting (inefficient)
- No context optimization
- No memory integration
- Simple question-answering flow

Educational Purpose:
Students see that basic RAG works but has clear inefficiencies:
- High token usage (raw JSON with all fields)
- Poor context formatting (JSON harder for LLM to parse)
- No personalization (stateless)
- Verbose output with unnecessary metadata

This sets the stage for improvements in Stage 2 and Stage 3.
"""

import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from redis_context_course import CourseManager, Course


@dataclass
class BaselineAgentConfig:
    """Configuration for the baseline agent."""
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_retrieval_results: int = 5
    

class BaselineRAGAgent:
    """
    Stage 1: Baseline RAG Agent
    
    A simple question-answering agent that:
    1. Takes a user query
    2. Retrieves relevant courses via semantic search
    3. Formats context as raw JSON (deliberately inefficient)
    4. Sends to LLM for answer generation
    
    No optimization, no memory, no advanced features.
    """
    
    def __init__(self, config: Optional[BaselineAgentConfig] = None):
        """Initialize the baseline agent."""
        self.config = config or BaselineAgentConfig()
        self.course_manager = CourseManager()
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature
        )
        
    async def retrieve_courses(self, query: str) -> List[Course]:
        """
        Retrieve relevant courses using semantic search.
        
        Args:
            query: User's question or search query
            
        Returns:
            List of relevant Course objects
        """
        results = await self.course_manager.search_courses(
            query=query,
            limit=self.config.max_retrieval_results
        )
        return results
    
    def format_context_as_json(self, courses: List[Course]) -> str:
        """
        Format courses as raw JSON (deliberately inefficient).
        
        This is the NAIVE approach that many developers start with:
        - Includes ALL fields (even internal ones like id, timestamps)
        - Uses JSON formatting (verbose, harder for LLM to parse)
        - No optimization or cleaning
        
        Educational note: This will use 2-3x more tokens than optimized formats.
        
        Args:
            courses: List of Course objects
            
        Returns:
            JSON string with all course data
        """
        # Convert Course objects to dicts with ALL fields
        course_dicts = []
        for course in courses:
            course_dict = {
                "id": course.id,
                "course_code": course.course_code,
                "title": course.title,
                "description": course.description,
                "department": course.department,
                "credits": course.credits,
                "difficulty_level": course.difficulty_level.value,
                "format": course.format.value,
                "instructor": course.instructor,
                "semester": course.semester.value,
                "year": course.year,
                "max_enrollment": course.max_enrollment,
                "current_enrollment": course.current_enrollment,
                "tags": course.tags,
                "learning_objectives": course.learning_objectives,
                "prerequisites": [
                    {
                        "course_code": p.course_code,
                        "course_title": p.course_title,
                        "minimum_grade": p.minimum_grade
                    }
                    for p in course.prerequisites
                ] if course.prerequisites else [],
                "created_at": str(course.created_at),
                "updated_at": str(course.updated_at),
            }
            course_dicts.append(course_dict)
        
        # Return as formatted JSON (verbose but readable)
        return json.dumps(course_dicts, indent=2)
    
    def build_system_prompt(self, context: str) -> str:
        """
        Build the system prompt with retrieved context.
        
        Args:
            context: Formatted course context (JSON string)
            
        Returns:
            System prompt string
        """
        return f"""You are a helpful Redis University course advisor.

Your role is to help students find courses, understand prerequisites, and plan their learning path.

Available Courses:
{context}

Instructions:
- Answer questions about courses based on the provided data
- Be helpful and concise
- If a course isn't in the data, say you don't have information about it
- Recommend courses based on student interests and prerequisites
"""
    
    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return a response.
        
        This is the core RAG flow:
        1. Retrieve relevant courses
        2. Format as context (raw JSON)
        3. Build system prompt
        4. Send to LLM
        5. Return response
        
        Args:
            user_message: User's question or message
            
        Returns:
            Agent's response string
        """
        # Step 1: Retrieve relevant courses
        courses = await self.retrieve_courses(user_message)
        
        # Step 2: Format context (raw JSON - inefficient)
        context = self.format_context_as_json(courses)
        
        # Step 3: Build system prompt with context
        system_prompt = self.build_system_prompt(context)
        
        # Step 4: Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Step 5: Get LLM response
        response = await self.llm.ainvoke(messages)
        
        return response.content
    
    def get_metrics(self, context: str) -> Dict[str, Any]:
        """
        Get metrics about the context (for educational comparison).
        
        Args:
            context: The formatted context string
            
        Returns:
            Dictionary with token count and other metrics
        """
        import tiktoken
        
        encoding = tiktoken.encoding_for_model(self.config.model_name)
        token_count = len(encoding.encode(context))
        
        return {
            "token_count": token_count,
            "character_count": len(context),
            "format": "raw_json",
            "optimization_level": "none"
        }


# Example usage
async def main():
    """Example usage of the baseline agent."""
    agent = BaselineRAGAgent()
    
    # Test query
    query = "What machine learning courses are available?"
    
    # Get response
    response = await agent.chat(query)
    print(f"Query: {query}")
    print(f"Response: {response}")
    
    # Show metrics (for educational purposes)
    courses = await agent.retrieve_courses(query)
    context = agent.format_context_as_json(courses)
    metrics = agent.get_metrics(context)
    print(f"\nMetrics:")
    print(f"  Token count: {metrics['token_count']:,}")
    print(f"  Format: {metrics['format']}")
    print(f"  Optimization: {metrics['optimization_level']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

