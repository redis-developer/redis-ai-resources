"""
Scenario 2: Agent with Tool Calling
====================================
Learning Goal: Enable the agent to use external tools/functions

Question: "What year was Oregon founded?"
Expected Answer: Tool returns "1859", LLM uses this in response
Type: tool-required
"""
import operator
import os
from typing import TypedDict, Annotated, Literal

from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    """
    The state that flows through our agent graph.

    messages: List of conversation messages (accumulates over time)
    """
    messages: Annotated[list, operator.add]  # operator.add means append to list

@tool
def get_oregon_facts(query: str):
    """Tool that returns facts about Oregon"""
    facts = {
        "founding": "Oregon became a state on February 14, 1859",
        "founding year": "1859",
        "population": "4.2 million as of 2023",
        "capital": "Salem",
        "largest city": "Portland",
        "state flower": "Oregon grape"
    }
    # Simple keyword matching
    query_lower = query.lower()
    for key, value in facts.items():
        if key in query_lower:
            return value

    return "Fact not found. Available topics: founding year, population, capital, largest city, state flower"

# os.environ["OPENAI_API_KEY"] =
tools = [get_oregon_facts]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools=llm.bind_tools(tools)

def call_llm(state=AgentState) -> AgentState:
    """Node that calls the LLM"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


def execute_tools(state: AgentState) -> AgentState:
    """
    Execute any tool calls requested by the LLM.

    This node:
    1. Looks at the last message from the LLM
    2. If it contains tool calls, executes them
    3. Adds ToolMessages with the results
    """
    print("Executing tools...")
    messages = state["messages"]
    last_message = messages[-1]

    # Extract tool calls from the last AI message
    tool_calls = last_message.tool_calls

    # Execute each tool call
    tool_messages = []
    for tool_call in tool_calls:
        # Find the matching tool
        selected_tool = {tool.name: tool for tool in tools}[tool_call["name"]]
        print(f"Executing tool {selected_tool.name} with args {tool_call['args']}")
        # Execute the tool
        tool_output = selected_tool.invoke(tool_call["args"])

        # Create a ToolMessage with the result
        tool_messages.append(
            ToolMessage(
                content=str(tool_output),
                tool_call_id=tool_call["id"]
            )
        )

    return {"messages": tool_messages}


def should_continue(state: AgentState) -> Literal["execute_tools", "end"]:
    """
    Decide whether to execute tools or end.

    Returns:
        "execute_tools" if the LLM made tool calls
        "end" if the LLM provided a final answer
    """
    print("Checking if we should continue...")
    last_message = state["messages"][-1]

    # If there are tool calls, we need to execute them
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "execute_tools"

    # Otherwise, we're done
    return "end"


def create_tool_agent():
    """
    Creates an agent that can use tools.

    Flow:
    START -> call_llm -> [conditional]
                            ├─> execute_tools -> call_llm (loop)
                            └─> END
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("execute_tools", execute_tools)

    # Set entry point
    workflow.set_entry_point("call_llm")

    # Add conditional edge from call_llm
    workflow.add_conditional_edges(
        "call_llm",
        should_continue,
        {
            "execute_tools": "execute_tools",
            "end": END
        }
    )

    # After executing tools, go back to call_llm
    workflow.add_edge("execute_tools", "call_llm")

    return workflow.compile()

    return app

if __name__ == "__main__":
    app = create_tool_agent()
    # question="Who is the best manager of Arsenal Women's and Mens'?"
    question = "What year was Oregon founded?"
    initial_state = {
        "messages": [HumanMessage(content=question)]
    }

    print(f"Question: {question}\n")
    print("Executing agent...\n")

    result = app.invoke(initial_state)

    # Print the conversation flow
    print("=== Conversation Flow ===")
    for msg in result["messages"]:
        if isinstance(msg, HumanMessage):
            print(f"Human: {msg.content}")
        elif isinstance(msg, AIMessage):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"AI: [Calling tools: {[tc['name'] for tc in msg.tool_calls]}]")
            else:
                print(f"AI: {msg.content}")
        elif isinstance(msg, ToolMessage):
            print(f"Tool: {msg.content}")

    print("\n" + "=" * 50)
    print("✅ Scenario 2 Complete!")
    print("=" * 50)

    print("\nGraph Structure:")
    print("START -> call_llm -> [should_continue?]")
    print("                        ├─> execute_tools -> call_llm (loop)")
    print("                        └─> END")
