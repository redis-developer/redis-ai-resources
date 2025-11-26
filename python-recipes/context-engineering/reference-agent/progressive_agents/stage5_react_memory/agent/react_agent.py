"""
ReAct Agent for Stage 5 (Memory-Augmented with ReAct).

Implements the ReAct (Reasoning + Acting) loop pattern with:
- Working memory (conversation history)
- ONE tool: search_courses
- Explicit reasoning traces
"""

import json
import logging
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .react_parser import parse_react_output
from .react_prompts import REACT_SYSTEM_PROMPT
from .tools import search_courses_tool

logger = logging.getLogger("course-qa-workflow")


class ReActStep:
    """Represents a single step in the ReAct loop."""

    def __init__(self, thought: str, action: str, action_input: str):
        self.thought = thought
        self.action = action
        self.action_input = action_input
        self.observation = None


class ReActAgent:
    """
    ReAct agent with working memory and search_courses tool.
    
    Stage 5 demonstrates:
    - ReAct loop with explicit reasoning
    - Working memory (conversation history)
    - Single tool: search_courses
    """
    
    def __init__(self, llm: BaseChatModel, max_iterations: int = 10):
        """
        Initialize ReAct agent.
        
        Args:
            llm: Language model for reasoning and action selection
            max_iterations: Maximum number of reasoning steps
        """
        self.llm = llm
        self.max_iterations = max_iterations

        # Available tools
        self.tools = {
            "search_courses": search_courses_tool,
        }
        
    async def run(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Run the ReAct loop to answer a query.
        
        Args:
            query: User's question
            conversation_history: Previous conversation turns
            
        Returns:
            Dict with answer, reasoning_trace, and metrics
        """
        if conversation_history is None:
            conversation_history = []
            
        # Build conversation context
        history_text = self._format_history(conversation_history)
        
        # Initialize messages
        messages = [
            SystemMessage(content=REACT_SYSTEM_PROMPT),
        ]
        
        # Add conversation history if present
        if history_text:
            messages.append(
                SystemMessage(content=f"CONVERSATION HISTORY:\n{history_text}")
            )
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        # Track reasoning steps
        reasoning_trace = []
        iterations = 0
        
        # ReAct loop
        while iterations < self.max_iterations:
            iterations += 1
            
            # Get LLM response
            response = await self.llm.ainvoke(messages)
            response_text = response.content

            # Parse the response
            parsed = parse_react_output(response_text)
            step = ReActStep(
                thought=parsed.get("thought", ""),
                action=parsed.get("action", ""),
                action_input=parsed.get("action_input", "")
            )
            reasoning_trace.append(step)
            
            logger.info(f"Iteration {iterations}:")
            logger.info(f"  Thought: {step.thought}")
            logger.info(f"  Action: {step.action}")
            
            # Check if finished
            if step.action == "FINISH":
                return {
                    "answer": step.action_input,
                    "reasoning_trace": reasoning_trace,
                    "iterations": iterations,
                    "success": True,
                }
            
            # Execute the action
            observation = await self._execute_action(step)
            step.observation = observation
            
            logger.info(f"  Observation: {observation[:200]}...")
            
            # Add to messages for next iteration
            messages.append(AIMessage(content=response_text))
            messages.append(
                HumanMessage(content=f"Observation: {observation}")
            )
        
        # Max iterations reached
        return {
            "answer": "I apologize, but I couldn't complete the task within the allowed steps.",
            "reasoning_trace": reasoning_trace,
            "iterations": iterations,
            "success": False,
        }
    
    async def _execute_action(self, step: ReActStep) -> str:
        """
        Execute a tool action.
        
        Args:
            step: ReActStep with action and action_input
            
        Returns:
            Observation string
        """
        action = step.action
        
        if action not in self.tools:
            return f"Error: Unknown action '{action}'. Available actions: {list(self.tools.keys())}"
        
        try:
            # Parse action input as JSON
            if isinstance(step.action_input, str):
                try:
                    action_input = json.loads(step.action_input)
                except json.JSONDecodeError:
                    return f"Error: Action input must be valid JSON. Got: {step.action_input}"
            else:
                action_input = step.action_input
            
            # Execute the tool
            tool = self.tools[action]
            result = await tool.ainvoke(action_input)
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return f"Error executing {action}: {str(e)}"
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """
        Format conversation history for context.
        
        Args:
            history: List of {role, content} dicts
            
        Returns:
            Formatted history string
        """
        if not history:
            return ""
        
        formatted = []
        for turn in history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        
        return "\n".join(formatted)


async def run_react_agent(
    query: str,
    llm: BaseChatModel,
    conversation_history: List[Dict[str, str]] = None,
    max_iterations: int = 10,
) -> Dict[str, Any]:
    """
    Convenience function to run the ReAct agent.
    
    Args:
        query: User's question
        llm: Language model
        conversation_history: Previous conversation turns
        max_iterations: Maximum reasoning steps
        
    Returns:
        Dict with answer, reasoning_trace, and metrics
    """
    agent = ReActAgent(llm=llm, max_iterations=max_iterations)
    return await agent.run(query=query, conversation_history=conversation_history)

