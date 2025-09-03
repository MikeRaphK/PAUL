from .models import PaulState

from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from subprocess import run
from typing import Literal

import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(SCRIPT_DIR, "resources")
GRAPH_PNG_PATH = os.path.join(RESOURCES_DIR, "graph.png")


def invoke_patcher(state: PaulState) -> PaulState:
    """
    Invokes patcher LLM using its chat history.

    Args:
        state (PaulState): The current graph state.

    Returns:
        PaulState: 
            A new state object with:
            - Updated 'patcher_chat_history' containing the new message
            - Incremented 'patcher_tokens' and 'patcher_cost' fields
    """
    llm = state["patcher_llm"]
    chat_history = state["patcher_chat_history"]
    with get_openai_callback() as cb:
        new_message = llm.invoke(chat_history)
        return {**state, "patcher_chat_history": [new_message], "patcher_tokens": state["patcher_tokens"] + cb.total_tokens, "patcher_cost": state["patcher_cost"] + cb.total_cost}


def get_tool_used(state: PaulState) -> Literal["Read tool used", "Write tool used"]:
    """
    Checks what kind of tool LLM used.

    Args:
        state (PaulState): The current state.

    Returns:
        str: "Read tool used" for read/ls tool, otherwise "Write tool used".
    """
    chat_history = state["patcher_chat_history"]

    # Search backwards through chat history to find the most recent AI message
    ai_message = None
    for i in range(len(chat_history) - 1, -1, -1):
        message = chat_history[i]
        if hasattr(message, 'tool_calls') and message.tool_calls:
            ai_message = message
            break
    if ai_message is None:
        raise ValueError("No AI message with tool calls found in chat history.")

    # Check all tool calls and print them
    write_tool_found = False
    write_tools = ["write_file", "insert_lines_tool"]
    for tool_call in ai_message.tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        print(f"Using {tool_name} with the following args: {tool_args}\n")
        
        # Check if this is a write tool
        if tool_name in write_tools:
            write_tool_found = True
    
    if not write_tool_found:
        return "Read tool used"
    return "Write tool used"


def verify_patch(state: PaulState) -> PaulState:
    """
    Determines whether tests pass or fail.

    Args:
        state (PaulState): The current graph state containing verifier chat history.

    Returns:
        PaulState: The updated state with 'tests_pass' updated.
    """
    print("Patch provided. Verifying...\n")

    # Check if tests are given
    tests = state["tests"]
    if not tests:
        print("No tests provided, skipping verification.\n")
        return {**state, "tests_pass": True}

    # Check if venv is given
    pytest_path = "pytest"
    if state["venv"]:
        pytest_path = os.path.join(state["venv"], "bin", "pytest")

    tests_pass = True
    failed_attempts = state["failed_attempts"]
    for test in tests:
        test_txt = f"{pytest_path} {test}"
        output_text = f"{test_txt} passed!\n"

        # Run pytest
        print(f"Running '{test_txt}'...")
        result = run([pytest_path, test, "-vvvv"], capture_output=True, text=True)

        # Pytest failed
        if result.returncode != 0:
            output_text = f"{test_txt} failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n"
            state["patcher_chat_history"].append(HumanMessage(content=output_text))
            tests_pass = False
            failed_attempts += 1

        print(output_text)

    return {**state, "tests_pass": tests_pass, "failed_attempts": failed_attempts}


def get_tests_status(state: PaulState) -> Literal["Fail", "Pass"]:
    """
    Checks if the tests passed.

    Args:
        state (PaulState): The current graph state.

    Returns:
        str: "Pass" if tests passed, otherwise "Fail".
    """
    if not state["tests_pass"]:
        print("Verification failed. Returning to patcher...\n")
        return "Fail"
    
    print("Verification passed!\n")
    return "Pass"


def invoke_reporter(state: PaulState) -> PaulState:
    """
    Invokes reporter LLM using its chat history.

    Args:
        state (PaulState): The current graph state.

    Returns:
        PaulState: 
            A new state object with:
            - Incremented 'reporter_tokens' and 'reporter_cost' fields
            - Updated 'report' containing the final patch report
    """
    print("Creating report...\n")
    chain = state["reporter_chain"]
    chat_history = state["reporter_chat_history"]
    chat_history.append(HumanMessage(content=f"Patch: {state["patcher_chat_history"][-2]}"))
    
    with get_openai_callback() as cb:
        output = chain.invoke(chat_history)
        report = output[0]
        return {**state, "reporter_tokens": cb.total_tokens, "reporter_cost": cb.total_cost, "report": report}


def build_paul_graph(toolkit: list[BaseTool]) -> CompiledStateGraph:
    """
    Build and compile the PAUL workflow LangGraph graph.

    Args:
        toolkit (list[BaseTool]): 
            A list of tools for the Toolkit node.

    Returns:
        CompiledStateGraph: 
            The compiled PAUL workflow state graph ready for execution.
    """
    graph = StateGraph(PaulState)

    # Nodes
    graph.add_node("Patcher", invoke_patcher)
    graph.add_node("Toolkit", ToolNode(tools=toolkit, messages_key="patcher_chat_history"))
    graph.add_node("Verifier", verify_patch)
    graph.add_node("Reporter", invoke_reporter)

    # Patcher
    graph.set_entry_point("Patcher")
    graph.add_edge("Patcher", "Toolkit")

    # Toolkit
    graph.add_conditional_edges(
        "Toolkit",
        get_tool_used,
        {"Read tool used": "Patcher", "Write tool used": "Verifier"},
    )

    # Verifier
    graph.add_conditional_edges(
        "Verifier",
        get_tests_status,
        {"Fail": "Patcher", "Pass": "Reporter"}
    )

    # Reporter
    graph.add_edge("Reporter", END)

    # Compile graph and write png
    PAUL = graph.compile()
    PAUL.get_graph().draw_mermaid_png(output_file_path=GRAPH_PNG_PATH)
    print(f"Graph written to '{GRAPH_PNG_PATH}'\n")
    return PAUL
