"""
ReAct agent node for Stage 7.

Implements the Thought → Action → Observation loop with explicit reasoning.
"""

import json
import logging
import time
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from .react_parser import (
    extract_final_answer,
    format_observation,
    format_react_error,
    is_valid_react_output,
    parse_react_output,
    validate_action_input,
)
from .react_prompts import REACT_SYSTEM_PROMPT
from .state import WorkflowState

logger = logging.getLogger("course-qa-workflow")

# Global LLM for ReAct
_react_llm = None


def get_react_llm() -> ChatOpenAI:
    """Get the configured ReAct LLM instance (NO tool binding for ReAct)."""
    global _react_llm
    if _react_llm is None:
        # ReAct uses text-based prompting, not function calling
        _react_llm = ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=2000)
    return _react_llm


async def execute_react_tool(
    tool_name: str, tool_input: Dict[str, Any], student_id: str
) -> str:
    """
    Execute a tool based on ReAct action.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Parsed JSON input for the tool
        student_id: Student ID for memory tools

    Returns:
        Tool result as string
    """
    try:
        if tool_name == "search_courses":
            from .tools import search_courses_tool

            result = await search_courses_tool.ainvoke(tool_input)
            return result

        elif tool_name == "search_memories":
            from .tools import search_memories_tool

            # Set student_id for memory tools
            from . import tools

            tools._current_student_id = student_id

            result = await search_memories_tool.ainvoke(tool_input)
            return result

        elif tool_name == "store_memory":
            from .tools import store_memory_tool

            # Set student_id for memory tools
            from . import tools

            tools._current_student_id = student_id

            result = await store_memory_tool.ainvoke(tool_input)
            return result

        else:
            return f"Error: Unknown tool '{tool_name}'"

    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"


async def react_agent_node(state: WorkflowState) -> WorkflowState:
    """
    ReAct agent node with explicit Thought → Action → Observation loop.

    This implements the ReAct pattern where the LLM:
    1. Thinks about what to do (explicit reasoning)
    2. Acts by calling a tool or finishing
    3. Observes the result
    4. Repeats until task is complete

    Args:
        state: Current workflow state

    Returns:
        Updated workflow state with final_response and reasoning_trace
    """
    start_time = time.perf_counter()

    query = state["original_query"]
    conversation_history = state.get("conversation_history", [])
    student_id = state["student_id"]

    logger.info(f"🤖 ReAct Agent: Processing query with explicit reasoning")

    try:
        # Build conversation context
        messages = []

        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-4:]:  # Last 2 turns
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        # Add ReAct system prompt
        messages.insert(0, HumanMessage(content=REACT_SYSTEM_PROMPT))

        # Add current query
        messages.append(HumanMessage(content=f"\nUser: {query}\n"))

        # Get LLM (no tool binding for ReAct)
        llm = get_react_llm()

        # Track LLM calls and reasoning
        llm_calls = state.get("llm_calls", {}).copy()
        reasoning_trace = []

        # ReAct loop
        max_iterations = 10  # ReAct may need more iterations
        iteration = 0

        logger.info(f"   🧠 Starting ReAct loop (max {max_iterations} iterations)...")

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"   🔄 Iteration {iteration}/{max_iterations}")

            # Call LLM
            logger.info(f"      🧠 Calling LLM...")
            response = await llm.ainvoke(messages)
            llm_calls["react_llm"] = llm_calls.get("react_llm", 0) + 1

            # Parse ReAct output
            parsed = parse_react_output(response.content)

            # Log thought
            if parsed["thought"]:
                logger.info(f"      💭 Thought: {parsed['thought'][:100]}...")
                reasoning_trace.append(
                    {"type": "thought", "content": parsed["thought"], "iteration": iteration}
                )

            # Check action
            action = parsed["action"]
            if not action:
                logger.error(f"      ❌ No action found in LLM output")
                logger.error(f"      Output: {response.content[:200]}...")
                # Try to extract any useful content as final answer
                final_answer = response.content.strip()
                break

            logger.info(f"      🔧 Action: {action}")

            # Check if FINISH
            if action.upper() == "FINISH":
                final_answer = extract_final_answer(parsed["action_input"] or "")
                logger.info(f"      ✅ FINISH action - completing")
                reasoning_trace.append(
                    {
                        "type": "finish",
                        "action": "FINISH",
                        "answer": final_answer,
                        "iteration": iteration,
                    }
                )
                break

            # Validate and parse action input
            action_input_str = parsed["action_input"]
            if not action_input_str:
                observation = format_react_error("No action input provided")
                logger.error(f"      ❌ No action input")
            else:
                logger.info(f"      📝 Action Input: {action_input_str[:100]}...")

                # Parse JSON input
                action_input = validate_action_input(action_input_str)
                if not action_input:
                    observation = format_react_error(
                        f"Invalid JSON in action input: {action_input_str[:100]}"
                    )
                    logger.error(f"      ❌ Invalid JSON")
                else:
                    # Execute tool
                    tool_result = await execute_react_tool(action, action_input, student_id)
                    observation = format_observation(tool_result, max_length=500)
                    logger.info(f"      👁️  Observation: {tool_result[:100]}...")

                    # Log to reasoning trace
                    reasoning_trace.append(
                        {
                            "type": "action",
                            "action": action,
                            "input": action_input,
                            "observation": tool_result,
                            "iteration": iteration,
                        }
                    )

            # Add AI response and observation to messages
            messages.append(AIMessage(content=response.content))
            messages.append(HumanMessage(content=f"\n{observation}\n"))

            # Continue loop

        else:
            # Max iterations reached
            logger.warning(
                f"   ⚠️  Max iterations ({max_iterations}) reached, forcing completion"
            )
            # Use last response as final answer
            final_answer = response.content.strip()

        # Update state
        latency = (time.perf_counter() - start_time) * 1000

        state["final_response"] = final_answer
        state["llm_calls"] = llm_calls
        state["reasoning_trace"] = reasoning_trace
        state["react_iterations"] = iteration
        state["execution_path"].append("react_agent_completed")
        state["metrics"]["total_latency"] = latency

        logger.info(f"🤖 ReAct Agent complete in {latency:.2f}ms")
        logger.info(f"   Iterations: {iteration}")
        logger.info(f"   Reasoning steps: {len(reasoning_trace)}")
        logger.info(f"   Response: {final_answer[:100]}...")

        return state

    except Exception as e:
        logger.error(f"ReAct agent node failed: {e}")
        import traceback

        traceback.print_exc()

        state["final_response"] = f"I encountered an error: {str(e)}"
        state["execution_path"].append("react_agent_failed")
        return state

