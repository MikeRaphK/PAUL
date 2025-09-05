from .graph import build_paul_graph
from .models import PaulState, PatchReport
from .tools.insert_lines_tool import insert_lines_tool
from .tools.read_numbered_tool import read_numbered_tool
from .utils import finalize_report

from langchain_community.tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticToolsParser
from langchain_openai import ChatOpenAI

import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(SCRIPT_DIR, "resources")
PATCHER_SYSTEM_MESSAGE_PATH = os.path.join(RESOURCES_DIR, "patcher_system_message.txt")
REPORTER_SYSTEM_MESSAGE_PATH = os.path.join(RESOURCES_DIR, "reporter_system_message.txt")


def run_paul_workflow(
    *,
    repo_path: str,
    issue_body: str,
    OPENAI_API_KEY: str,
    issue_title: str = None,
    issue_number: int = None,
    model: str,
    tests: list[str],
    venv: str,
    swe: bool = False
) -> PatchReport:
    """
    Executes the PAUL workflow to generate a patch for a given issue using an LLM agent.

    Args:
        repo_path (str): Path to the local repository.
        issue_body (str): Body/description of the issue to resolve.
        OPENAI_API_KEY (str): The OpenAI API key.
        issue_title (str): Title of the issue to resolve. Defaults to None.
        issue_number (int): Issue number (for response parsing). Defaults to None.
        model (str): The OpenAI model name to use.
        tests (list[str]): List of pytest targets to run.
        venv (str): Path to the Python virtual environment in which tests should be executed.
        swe (bool): Whether to run in SWE-bench compatibility mode. Defaults to False. 

    Returns:
        PatchReport: 
            The finalized structured patch report with fields:
            - 'commit_msg': Concise git commit message
            - 'title': Patch title
            - 'body': Patch description with context and changes

    Raises:
        RuntimeError: If the workflow fails due to recursion limit.
    """
    START_DIR = os.getcwd()
    os.chdir(repo_path)

    print("Testing suite:")
    if not tests:
        print("None")
    else:
        for test in tests:
            print(f"{test}")
    print()

    print(f"Building PAUL LangGraph graph...\n")
    building_start_time = time.perf_counter()
    # Default toolkit has LangChain community tools. Use custom tools for SWE-bench
    toolkit = [ListDirectoryTool(), ReadFileTool(), WriteFileTool()]
    if swe:
        toolkit = [ListDirectoryTool(), read_numbered_tool, insert_lines_tool]  
    PAUL = build_paul_graph(toolkit)

    print(f"Building patcher LLM using '{model}'...\n")
    patcher_llm = ChatOpenAI(model=model, openai_api_key=OPENAI_API_KEY)
    patcher_llm = patcher_llm.bind_tools(toolkit)
    query = ""
    if issue_title is not None:
        query += f"Issue Title: {issue_title}\n"
    query += f"Issue Body: {issue_body}"
    with open(PATCHER_SYSTEM_MESSAGE_PATH, "r") as f:
        patcher_chat_history = [SystemMessage(content=f.read()), HumanMessage(content=query)]

    print(f"Building reporter LLM using '{model}'...\n")
    reporter_llm = ChatOpenAI(model=model, openai_api_key=OPENAI_API_KEY)
    reporter_llm = reporter_llm.bind_tools([PatchReport])
    parser = PydanticToolsParser(tools=[PatchReport])
    reporter_chain = reporter_llm | parser
    with open(REPORTER_SYSTEM_MESSAGE_PATH, "r") as f:
        reporter_chat_history = [SystemMessage(content=f.read()), HumanMessage(content=query)]
    building_end_time = time.perf_counter()
    building_time = building_end_time - building_start_time
    print(f"Building complete in {building_time:.4f} seconds\n")

    print("Working on a patch...\n")
    initial_state: PaulState = {
        # Patcher
        "patcher_llm": patcher_llm,
        "patcher_chat_history": patcher_chat_history,
        "write_tool_used": False,
        "patcher_tokens": 0,
        "patcher_cost": 0.0,

        # Verifier
        "tests": tests,
        "tests_pass": False,
        "venv": venv,
        "failed_attempts": 0,

        # Reporter
        "reporter_chain": reporter_chain,
        "reporter_chat_history": reporter_chat_history,
        "reporter_tokens": 0,
        "reporter_cost": 0.0,
        "report": None
    }
    execution_start_time = time.perf_counter()
    output_state = PAUL.invoke(initial_state, config={"recursion_limit": 50})
    execution_end_time = time.perf_counter()
    execution_time = execution_end_time - execution_start_time
    print(f"PAUL has finished working with an execution time of {execution_time:.4f} seconds!\n")

    os.chdir(START_DIR)
    return finalize_report(output_state, building_time, execution_time, issue_number)
