"""Basic Langraph Q&A Agent demo."""
import os
from typing import Annotated, TypedDict
import operator

from langgraph.constants import END
from langgraph.graph import StateGraph
from openai import OpenAI

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AgentState(TypedDict):
    """State that is access by all nodes."""
    messages: Annotated[list, operator.add]  # Accumulates messages
    question: str
    answer: str
    iteration_count: int

# 2. Define Nodes - functions that do work
def ask_question(state: AgentState) -> AgentState:
    """Node that processes the question"""
    print(f"Processing question: {state['question']}")
    return {
        "messages": [f"Question received: {state['question']}"],
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def generate_answer(state: AgentState) -> AgentState:
    """Node that generates an answer using OpenAI"""
    print("Generating answer with OpenAI...")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides clear, concise answers."},
                {"role": "user", "content": state['question']}
            ],
            max_tokens=150,
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        answer = f"Error generating answer: {str(e)}"

    return {
        "answer": answer,
        "messages": [f"Answer generated: {answer}"]
    }

# 3. Define conditional logic
def should_continue(state: AgentState) -> str:
    """Decides whether to continue or end"""
    print(f"Checking if we should continue...{state['iteration_count']}")
    if state["iteration_count"] > 3:
        return "end"
    return "continue"


if __name__=="__main__":
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables!")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        exit(1)

    initial_state = {
        "question": "What is LangGraph?",
        "messages": [],
        "answer": "",
        "iteration_count": 0
    }

    # # 4. Build the Graph
    workflow = StateGraph(AgentState)
    #
    # Two nodes that are doing things
    workflow.add_node("process_question", ask_question)
    workflow.add_node("generate_answer", generate_answer)
    # #
    # # # Add edges
    workflow.set_entry_point("process_question")  # Start here

    # First, always go from process_question to generate_answer
    workflow.add_edge("process_question", "generate_answer")

    # After generating answer, check if we should continue or end
    workflow.add_conditional_edges(
        "generate_answer",  # Check after generating answer
        should_continue,
        {
            "continue": "process_question",  # If continue, loop back to process_question
            "end": END  # If end, finish
        }
    )
    #
    # # Compile the graph
    app = workflow.compile()
    result = app.invoke(initial_state)
    print("\n=== Final Result ===")
    print(f"Question: {result['question']}")
    print(f"Answer: {result['answer']}")
    print(f"Messages: {result['messages']}")
    # print(result)

