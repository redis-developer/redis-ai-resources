"""
Stage 3: Hybrid RAG Agent

This agent demonstrates production-ready context engineering patterns:
- Structured catalog views (hierarchical organization)
- Hybrid context assembly (overview + details)
- Query-aware context selection (smart view selection)
- Multi-strategy retrieval (semantic + metadata)

Educational Purpose:
Students see how combining multiple context engineering techniques
creates a production-ready system with optimal token usage and answer quality.

Improvements over Stage 2:
- ✅ Further token reduction (1,200 → 800)
- ✅ Better context organization (structured views)
- ✅ Query-aware optimization (smart selection)
- ✅ Scalable to large catalogs (catalog view)
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from redis_context_course import CourseManager, Course

from .structured_views import (
    hybrid_context_assembly,
    smart_context_selection,
    estimate_token_savings
)
from progressive_agents.stage2_optimized.context_utils import count_tokens


@dataclass
class HybridAgentConfig:
    """Configuration for the hybrid agent."""
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_retrieval_results: int = 5
    catalog_size: int = 50  # Number of courses for catalog view
    use_smart_selection: bool = True  # Auto-select views based on query


class HybridRAGAgent:
    """
    Stage 3: Hybrid RAG Agent
    
    Production-ready agent with advanced context engineering:
    1. Retrieves relevant courses (semantic search)
    2. Retrieves catalog overview (all courses)
    3. Intelligently selects context views based on query
    4. Assembles hybrid context (overview + details)
    5. Generates optimized response
    
    Result: ~800 tokens (vs 2,500 in Stage 1, 1,200 in Stage 2)
    """
    
    def __init__(self, config: Optional[HybridAgentConfig] = None):
        """Initialize the hybrid agent."""
        self.config = config or HybridAgentConfig()
        self.course_manager = CourseManager()
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature
        )
        self._catalog_cache = None  # Cache catalog view
        
    async def retrieve_relevant_courses(self, query: str) -> List[Course]:
        """
        Retrieve semantically relevant courses.
        
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
    
    async def retrieve_catalog_courses(self) -> List[Course]:
        """
        Retrieve courses for catalog overview.
        
        Uses caching to avoid repeated retrieval.
        
        Returns:
            List of Course objects for catalog
        """
        if self._catalog_cache is None:
            # Retrieve broader set for catalog view
            self._catalog_cache = await self.course_manager.search_courses(
                query="",  # Empty query gets diverse results
                limit=self.config.catalog_size
            )
        return self._catalog_cache
    
    async def build_hybrid_context(self, query: str) -> str:
        """
        Build hybrid context using multiple views.
        
        This is the KEY INNOVATION of Stage 3:
        1. Get relevant courses (semantic search)
        2. Get catalog courses (overview)
        3. Smart view selection (based on query)
        4. Hybrid assembly (combine views)
        
        Args:
            query: User's query
            
        Returns:
            Assembled hybrid context
        """
        # Step 1: Retrieve relevant courses
        relevant_courses = await self.retrieve_relevant_courses(query)
        
        # Step 2: Retrieve catalog courses (if needed)
        catalog_courses = await self.retrieve_catalog_courses()
        
        # Step 3: Smart view selection
        if self.config.use_smart_selection:
            views = smart_context_selection(query, relevant_courses)
        else:
            # Default: just show details
            views = {
                "include_catalog": False,
                "include_prerequisites": False,
                "include_difficulty": False
            }
        
        # Step 4: Assemble hybrid context
        context = hybrid_context_assembly(
            query=query,
            all_courses=catalog_courses,
            relevant_courses=relevant_courses,
            **views
        )
        
        return context
    
    def build_system_prompt(self, context: str) -> str:
        """
        Build the system prompt with hybrid context.
        
        Args:
            context: Assembled hybrid context
            
        Returns:
            System prompt string
        """
        return f"""You are a helpful Redis University course advisor.

Your role is to help students find courses, understand prerequisites, and plan their learning path.

{context}

Instructions:
- Answer questions about courses based on the provided data
- Use the catalog overview to give students a sense of what's available
- Use detailed course information to provide specific recommendations
- Be helpful and concise
- If a course isn't in the data, say you don't have information about it
"""
    
    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return a response.
        
        Hybrid RAG flow:
        1. Build hybrid context (overview + details)
        2. Build system prompt
        3. Send to LLM
        4. Return response
        
        Args:
            user_message: User's question or message
            
        Returns:
            Agent's response string
        """
        # Step 1: Build hybrid context
        context = await self.build_hybrid_context(user_message)
        
        # Step 2: Build system prompt
        system_prompt = self.build_system_prompt(context)
        
        # Step 3: Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Step 4: Get LLM response
        response = await self.llm.ainvoke(messages)
        
        return response.content
    
    async def get_metrics(self, query: str) -> Dict[str, Any]:
        """
        Get metrics about the hybrid context.
        
        Args:
            query: User's query
            
        Returns:
            Dictionary with token count and other metrics
        """
        context = await self.build_hybrid_context(query)
        token_count = count_tokens(context, self.config.model_name)
        
        # Get view selection info
        relevant_courses = await self.retrieve_relevant_courses(query)
        views = smart_context_selection(query, relevant_courses)
        
        return {
            "token_count": token_count,
            "character_count": len(context),
            "format": "hybrid",
            "views_included": [k for k, v in views.items() if v],
            "smart_selection": self.config.use_smart_selection,
            "estimated_cost_per_1k_queries": self._estimate_cost(token_count)
        }
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost per 1,000 queries."""
        input_cost_per_1m = 0.150
        output_cost_per_1m = 0.600
        avg_output_tokens = 200
        
        input_cost = (tokens / 1_000_000) * input_cost_per_1m * 1000
        output_cost = (avg_output_tokens / 1_000_000) * output_cost_per_1m * 1000
        
        return round(input_cost + output_cost, 2)
    
    async def compare_all_stages(self, query: str) -> Dict[str, Any]:
        """
        Compare all three stages for educational purposes.
        
        Args:
            query: Test query
            
        Returns:
            Comparison metrics across all stages
        """
        import json
        from progressive_agents.stage2_optimized.context_utils import format_courses_as_text
        
        # Get courses
        relevant_courses = await self.retrieve_relevant_courses(query)
        
        # Stage 1: Raw JSON
        stage1_context = json.dumps([
            {
                "id": c.id,
                "course_code": c.course_code,
                "title": c.title,
                "description": c.description,
                "department": c.department,
                "credits": c.credits,
                "difficulty_level": c.difficulty_level.value,
                "format": c.format.value,
                "instructor": c.instructor,
                "semester": c.semester.value,
                "year": c.year,
                "max_enrollment": c.max_enrollment,
                "current_enrollment": c.current_enrollment,
                "tags": c.tags,
                "learning_objectives": c.learning_objectives,
                "prerequisites": [
                    {"course_code": p.course_code, "course_title": p.course_title}
                    for p in c.prerequisites
                ] if c.prerequisites else [],
                "created_at": str(c.created_at),
                "updated_at": str(c.updated_at),
            }
            for c in relevant_courses
        ], indent=2)
        
        # Stage 2: Natural text
        stage2_context = format_courses_as_text(relevant_courses, optimization_level="standard")
        
        # Stage 3: Hybrid
        stage3_context = await self.build_hybrid_context(query)
        
        # Calculate tokens
        stage1_tokens = count_tokens(stage1_context)
        stage2_tokens = count_tokens(stage2_context)
        stage3_tokens = count_tokens(stage3_context)
        
        return {
            "stage1": {
                "tokens": stage1_tokens,
                "format": "Raw JSON",
                "cost_per_1k": self._estimate_cost(stage1_tokens)
            },
            "stage2": {
                "tokens": stage2_tokens,
                "format": "Natural Text",
                "cost_per_1k": self._estimate_cost(stage2_tokens),
                "vs_stage1": f"-{((stage1_tokens - stage2_tokens) / stage1_tokens * 100):.1f}%"
            },
            "stage3": {
                "tokens": stage3_tokens,
                "format": "Hybrid Views",
                "cost_per_1k": self._estimate_cost(stage3_tokens),
                "vs_stage1": f"-{((stage1_tokens - stage3_tokens) / stage1_tokens * 100):.1f}%",
                "vs_stage2": f"-{((stage2_tokens - stage3_tokens) / stage2_tokens * 100):.1f}%"
            }
        }


# Example usage
async def main():
    """Example usage of the hybrid agent."""
    agent = HybridRAGAgent()
    
    # Test query
    query = "What machine learning courses are available?"
    
    # Get response
    response = await agent.chat(query)
    print(f"Query: {query}\n")
    print(f"Response: {response}\n")
    
    # Show metrics
    metrics = await agent.get_metrics(query)
    print(f"=== Stage 3 Metrics ===")
    print(f"Token count: {metrics['token_count']:,}")
    print(f"Format: {metrics['format']}")
    print(f"Views included: {', '.join(metrics['views_included']) if metrics['views_included'] else 'details only'}")
    print(f"Est. cost per 1K queries: ${metrics['estimated_cost_per_1k_queries']}")
    
    # Compare all stages
    comparison = await agent.compare_all_stages(query)
    print(f"\n=== All Stages Comparison ===")
    for stage, data in comparison.items():
        print(f"{stage.upper()}: {data['tokens']:,} tokens ({data['format']}) - ${data['cost_per_1k']}/1K queries")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

