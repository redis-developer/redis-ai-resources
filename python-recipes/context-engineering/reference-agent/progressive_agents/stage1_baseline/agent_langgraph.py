"""
Stage 1: Baseline RAG Agent (LangGraph Version)

This is a deliberately simple RAG implementation using LangGraph that demonstrates:
- Basic semantic search retrieval
- Raw JSON context formatting (inefficient)
- LangGraph StateGraph workflow orchestration
- Linear node execution (retrieve → format → generate)

Educational Purpose:
Students learn:
- How to structure a RAG agent with LangGraph
- State management with AgentState
- Node-based workflow design
- Why raw JSON is inefficient (~2,500 tokens for 5 courses)

This sets the stage for improvements in Stage 2 and Stage 3.
"""

import json
from typing import Annotated, Any, Dict, List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from redis_context_course import Course, CourseManager


class AgentState(BaseModel):
    """
    State for the baseline RAG agent.
    
    Fields:
        messages: Conversation history (managed by add_messages)
        query: Current user query
        retrieved_courses: Courses from semantic search
        context: Formatted context string (raw JSON)
        metadata: Additional tracking info (token counts, etc.)
    """
    messages: Annotated[List[BaseMessage], add_messages]
    query: str = ""
    retrieved_courses: List[Course] = []
    context: str = ""
    metadata: Dict[str, Any] = {}


class BaselineRAGAgent:
    """
    Stage 1: Baseline RAG Agent (LangGraph Version)
    
    A simple RAG agent using LangGraph StateGraph:
    1. retrieve_courses - Semantic search for relevant courses
    2. format_context - Convert to raw JSON (inefficient)
    3. generate_response - LLM generates answer
    
    Workflow:
        START → retrieve_courses → format_context → generate_response → END
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the baseline agent with LangGraph workflow."""
        self.model_name = model_name
        self.course_manager = CourseManager()
        self.llm = ChatOpenAI(model=model_name, temperature=0.0)
        
        # Build the graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Nodes:
            - retrieve_courses: Fetch relevant courses via semantic search
            - format_context: Format as raw JSON (deliberately inefficient)
            - generate_response: LLM generates answer
            
        Edges:
            Linear flow: retrieve → format → generate → END
        """
        # Create workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve_courses", self.retrieve_courses_node)
        workflow.add_node("format_context", self.format_context_node)
        workflow.add_node("generate_response", self.generate_response_node)
        
        # Define edges (linear flow)
        workflow.set_entry_point("retrieve_courses")
        workflow.add_edge("retrieve_courses", "format_context")
        workflow.add_edge("format_context", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # Compile
        return workflow.compile()
    
    # ========== Node Functions ==========
    
    async def retrieve_courses_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Retrieve relevant courses using semantic search.
        
        Takes the user query and searches the course catalog.
        Stores results in state.retrieved_courses.
        """
        # Extract query from latest message
        if state.messages:
            last_message = state.messages[-1]
            if isinstance(last_message, HumanMessage):
                state.query = last_message.content
        
        # Semantic search
        courses = await self.course_manager.search_courses(
            query=state.query,
            limit=5
        )
        
        state.retrieved_courses = courses
        state.metadata["num_courses_retrieved"] = len(courses)
        
        return state
    
    def format_context_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Format courses as raw JSON (deliberately inefficient).
        
        This is the NAIVE approach that many developers start with:
        - Includes ALL fields (id, timestamps, enrollment data)
        - Uses verbose JSON structure
        - Results in ~500 tokens per course
        
        Educational note: This inefficiency motivates Stage 2 optimizations.
        """
        course_dicts = []
        for course in state.retrieved_courses:
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
                    {"course_code": p.course_code, "course_title": p.course_title}
                    for p in course.prerequisites
                ] if course.prerequisites else [],
                "created_at": str(course.created_at),
                "updated_at": str(course.updated_at),
            }
            course_dicts.append(course_dict)
        
        # Format as JSON with indentation (adds even more tokens!)
        state.context = json.dumps(course_dicts, indent=2)
        
        # Track token count (approximate)
        state.metadata["context_length"] = len(state.context)
        state.metadata["estimated_tokens"] = len(state.context) // 4  # Rough estimate
        
        return state
    
    async def generate_response_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Generate response using LLM.
        
        Builds system prompt with raw JSON context and gets LLM response.
        """
        # Build system prompt
        system_prompt = f"""You are a helpful Redis University course advisor.

Your role is to help students find courses, understand prerequisites, and plan their learning path.

Here are the relevant courses (in JSON format):

{state.context}

Instructions:
- Answer questions about courses based on the provided data
- Be helpful and concise
- If a course isn't in the data, say you don't have information about it
"""
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state.query)
        ]
        
        # Get LLM response
        response = await self.llm.ainvoke(messages)
        
        # Add to state messages
        state.messages.append(response)
        
        return state
    
    # ========== Public Interface ==========
    
    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return a response.
        
        Args:
            user_message: User's question
            
        Returns:
            Agent's response string
        """
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=user_message)],
            query=user_message
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract response
        last_message = final_state["messages"][-1]
        return last_message.content
    
    async def get_metrics(self, query: str) -> dict:
        """
        Get metrics about the context for a given query.
        
        Useful for demonstrating inefficiency of raw JSON approach.
        """
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            query=query
        )
        
        # Run through retrieve and format nodes only
        state = await self.retrieve_courses_node(initial_state)
        state = self.format_context_node(state)
        
        # Calculate metrics
        token_count = state.metadata.get("estimated_tokens", 0)
        
        return {
            "token_count": token_count,
            "character_count": state.metadata.get("context_length", 0),
            "num_courses": state.metadata.get("num_courses_retrieved", 0),
            "format": "raw_json",
            "estimated_cost_per_1k_queries": self._estimate_cost(token_count)
        }
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost per 1,000 queries."""
        # gpt-4o-mini pricing
        input_cost_per_1m = 0.150  # $0.150 per 1M input tokens
        output_cost_per_1m = 0.600  # $0.600 per 1M output tokens
        avg_output_tokens = 200  # Estimated average response length
        
        input_cost = (tokens / 1_000_000) * input_cost_per_1m * 1000
        output_cost = (avg_output_tokens / 1_000_000) * output_cost_per_1m * 1000
        
        return round(input_cost + output_cost, 2)
    
    def get_graph_diagram(self) -> str:
        """
        Get Mermaid diagram of the LangGraph workflow.
        
        Returns:
            Mermaid diagram as string
        """
        return """```mermaid
graph LR
    START([START]) --> A[retrieve_courses]
    A --> B[format_context]
    B --> C[generate_response]
    C --> END([END])
    
    style A fill:#ff6b6b
    style B fill:#ff6b6b
    style C fill:#4ecdc4
    
    classDef inefficient fill:#ff6b6b,stroke:#c92a2a
    classDef llm fill:#4ecdc4,stroke:#1098ad
```

**Node Descriptions:**
- **retrieve_courses** (red): Semantic search - retrieves 5 courses
- **format_context** (red): Raw JSON formatting - INEFFICIENT (~2,500 tokens)
- **generate_response** (blue): LLM generates answer
"""

