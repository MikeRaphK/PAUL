from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from subprocess import run
from typing import Annotated, Literal, Sequence, TypedDict

import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(SCRIPT_DIR, "resources")
GRAPH_PNG_PATH = os.path.join(RESOURCES_DIR, "graph.png")
PATCHER_SYSTEM_MESSAGE_PATH = os.path.join(RESOURCES_DIR, "patcher_system_message.txt")
VERIFIER_SYSTEM_MESSAGE_PATH = os.path.join(
    RESOURCES_DIR, "verifier_system_message.txt"
)


class PaulState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    llm: Runnable
    tests: list[str]
    tests_pass: bool = False


def invoke_llm(state: PaulState) -> PaulState:
    """
    Invokes LLM using its chat history.

    Args:
        state (PaulState): The current graph state.

    Returns:
        PaulState: The updated state with 'messages' updated.
    """
    chat_history = state["messages"]
    llm = state["llm"]
    new_message = llm.invoke(chat_history)
    return {**state, "messages": [new_message]}


def need_tool(state: PaulState) -> Literal["Need tool", "Done patching"]:
    """
    Determines whether LLM needs to call a tool or not.

    Args:
        state (PaulState): The current state.

    Returns:
        str: "Need tool" if the agent requested a tool, otherwise "Done patching".
    """
    chat_history = state["messages"]
    last_message = chat_history[-1]
    if last_message.tool_calls:
        return "Need tool"
    print("Done patching!\n")
    return "Done patching"


def verify_patch(state: PaulState) -> PaulState:
    """
    Determines whether tests pass or fail.

    Args:
        state (PaulState): The current graph state containing verifier chat history.

    Returns:
        PaulState: The updated state with 'tests_pass' updated.
    """
    print("Verifying patch...\n")
    tests = state["tests"]
    if not tests:
        print("No tests provided, skipping verification.\n")
        return {**state, "tests_pass": True}
    
    tests_pass = True
    for test in tests:
        print(f"Running test: {test}")
        result = run(["pytest", test, "-vvvv"], capture_output=True, text=True)
        if result.returncode != 0:
            error_text = f"Test '{test}' failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n"
            state["messages"].append(HumanMessage(content=error_text))
            print(error_text)
            tests_pass = False
        else:
            print(f"Test '{test}' passed.\n")
    return {**state, "tests_pass": tests_pass}


def tests_passed(state: PaulState) -> Literal["Fail", "Pass"]:
    """
    Checks if the tests passed.

    Args:
        state (PaulState): The current graph state.

    Returns:
        str: "Pass" if tests passed, otherwise "Fail".
    """
    if not state["tests_pass"]:
        print("Returning to patcher...\n")
        return "Fail"
    print("Done verifying!\n")
    return "Pass"


def build_paul_graph(toolkit: list[BaseTool]) -> CompiledStateGraph:
    graph = StateGraph(PaulState)

    # Patcher
    graph.add_node("Patcher", invoke_llm)
    graph.set_entry_point("Patcher")
    graph.add_node(
        "Patcher Toolkit",
        ToolNode(toolkit)
    )
    graph.add_edge("Patcher Toolkit", "Patcher")
    graph.add_conditional_edges(
        "Patcher",
        need_tool,
        {"Need tool": "Patcher Toolkit", "Done patching": "Verifier"}
    )

    # Verifier
    graph.add_node("Verifier", verify_patch)
    graph.add_conditional_edges(
        "Verifier",
        tests_passed,
        {"Fail": "Patcher", "Pass": END}
    )

    # Compile graph and write png
    PAUL = graph.compile()
    PAUL.get_graph().draw_mermaid_png(output_file_path=GRAPH_PNG_PATH)
    print(f"Graph written to '{GRAPH_PNG_PATH}'\n")
    return PAUL
