from .models import PaulState

from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from shutil import copy2
from subprocess import run
from typing import Literal

import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PATCHES_DIR = os.path.join(SCRIPT_DIR, "patches")
RESOURCES_DIR = os.path.join(SCRIPT_DIR, "resources")
GRAPH_PNG_PATH = os.path.join(RESOURCES_DIR, "graph.png")
WRITE_TOOLS = ["write_file", "insert_lines_tool"]


def invoke_patcher(state: PaulState) -> PaulState:
    """
    Invokes patcher LLM using its chat history. Also makes sure LLM calls a tool.

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
    
    # Invoke until a tool call is made
    result = []
    with get_openai_callback() as cb:
        while True:
            new_message = llm.invoke(chat_history + result)
            result.append(new_message)
            if getattr(new_message, "tool_calls", None):
                break
            print("LLM did not call a tool. Re-invoking...\n")
            retry_message = HumanMessage(content="Please use one of the available tools to help solve the problem. You must call a tool to proceed. Choose the most appropriate tool based on what you need to do.")
            result.append(retry_message)

    # Check if any write tool was used
    write_tool_used = False
    file_modified = None
    for tool_call in new_message.tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call.get("args", {})
        print(f"Using '{tool_name}' tool with args: {tool_args}")
        if tool_name in WRITE_TOOLS:
            write_tool_used = True
            file_modified = tool_args['file_path']
    return {**state, "patcher_chat_history": result, "write_tool_used": write_tool_used, "file_modified": file_modified, "patcher_tokens": state["patcher_tokens"] + cb.total_tokens, "patcher_cost": state["patcher_cost"] + cb.total_cost}


def get_tool_used(state: PaulState) -> Literal["Read tool used", "Write tool used"]:
    """
    Checks what kind of tool LLM used.

    Args:
        state (PaulState): The current state.

    Returns:
        str: "Read tool used" for read/ls tool, otherwise "Write tool used".
    """
    if not state["write_tool_used"]:
        print("Read tool used. Returning to patcher...\n")
        return "Read tool used"
    
    print("Write tool used. Proceeding to verifier...\n")
    # Save patch
    attempt_number = state["failed_attempts"]
    modified_file_path = state["file_modified"]
    modified_file_name = os.path.basename(modified_file_path)
    os.makedirs(PATCHES_DIR, exist_ok=True)
    destination = os.path.join(PATCHES_DIR, f"patch_{attempt_number}_{modified_file_name}")
    print(f"Saving modified file to '{destination}'\n")
    copy2(modified_file_path, destination)
    return "Write tool used"


def verify_patch(state: PaulState) -> PaulState:
    """
    Determines whether tests pass or fail.

    Args:
        state (PaulState): The current graph state containing verifier chat history.

    Returns:
        PaulState: The updated state with 'tests_pass' updated.
    """
    print("Verifying...\n")

    # Check if tests are given
    tests = state["tests"]
    verify_cmd = state["quixbugs_verify_cmd"]
    if not tests and not verify_cmd:
        print("No tests provided, skipping verification.\n")
        return {**state, "tests_pass": True}

    # Setup for QuixBugs
    cmd_prefix = ""
    if verify_cmd:
        tests = [verify_cmd]
    # Setup for pytest
    else:
        cmd_prefix = "pytest"
        if state["venv"]:
            cmd_prefix = os.path.join(state["venv"], "bin", "pytest")
        cmd_prefix = cmd_prefix + " -vvvv"

    tests_pass = True
    failed_attempts = state["failed_attempts"]
    for test in tests:
        cmd = f"{cmd_prefix} {test}".strip()
        output = f"{cmd} passed!\n"

        # Run pytest
        print(f"Running '{cmd}'...")
        result = run(cmd.split(), capture_output=True, text=True)

        # Pytest failed
        if result.returncode != 0:
            output = f"{cmd} failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n"
            state["patcher_chat_history"].append(HumanMessage(content=output))
            tests_pass = False
            failed_attempts += 1

        print(output)

    if state["swe"] and not tests_pass:
        print(f"Reverting changes...")
        run(["git", "reset", "--hard", "HEAD"], capture_output=True, text=True)
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
    
    print("Verification passed! Moving to reporter...\n")
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
    print("Report finished!\n")
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
