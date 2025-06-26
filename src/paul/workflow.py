from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_community.tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from subprocess import run
from typing import Tuple, Dict

from .pytest_tool import pytest_tool
from .react_graph import build_react_graph
from .utils import parse_paul_response

import os
import uuid



def run_paul_workflow(model: str, repo_path: str, issue_title: str, issue_body: str, issue_number: int, OPENAI_API_KEY: str) -> Tuple[Dict[str, str], str]:
    """
    Executes the PAUL workflow to generate a patch for a given issue using an LLM agent.

    Args:
        model (str): The OpenAI model name to use.
        repo_path (str): Path to the local repository.
        issue_title (str): Title of the issue to resolve.
        issue_body (str): Body/description of the issue to resolve.
        issue_number (int): Issue number (for response parsing).
        OPENAI_API_KEY (str): The OpenAI API key.

    Returns:
        Dict[str, str]: Dict with the PAUL's JSON response containing: 'commit_msg', 'pr_title', 'pr_body'.
        str: The name of the newly created git branch.

    Raises:
        RuntimeError: If the workflow fails due to recursion limit.
    """
    previous_cwd = os.getcwd()
    os.chdir(repo_path)
    
    print("Waking PAUL up...\n")

    branch_name = f"PAUL-branch-{uuid.uuid4().hex[:8]}"
    run(["git", "checkout", "-b", branch_name], check=True)

    print(f"\nInitializing ReAct graph using {model}...\n")
    token_logger = OpenAICallbackHandler()
    llm = ChatOpenAI(model=model, openai_api_key=OPENAI_API_KEY, callbacks=[token_logger])
    tools = [ReadFileTool(), WriteFileTool(), ListDirectoryTool(), pytest_tool]
    PAUL = build_react_graph(tools, llm, os.path.join(previous_cwd, "graph.png"))

    print("Invoking PAUL...\n")
    with open(os.path.join(previous_cwd, "src/paul/system_message.txt"), "r") as f:
        system_message = SystemMessage(content=f.read())
    chat_history = [system_message]
    query = HumanMessage(content=f"""
        Issue Title: {issue_title}
        Issue Body: {issue_body}
    """)
    chat_history.append(query)
    output_state = PAUL.invoke({"messages" : chat_history})
    
    print("PAUL has finished working!\n")
    os.chdir(previous_cwd)
    paul_response = parse_paul_response(output_state["messages"], issue_number, token_logger)
    return paul_response, branch_name