from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_community.tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError
from subprocess import run
from typing import Tuple, Dict

from .pytest_tool import pytest_tool
from .react_graph import build_react_graph
from .utils import parse_paul_response

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
    
    print("Waking PAUL up...\n")

    branch_name = f"PAUL-branch-{uuid.uuid4().hex[:8]}"
    run(["git", "checkout", "-b", branch_name], check=True)

    print("Initializing ReAct graph...\n")
    token_logger = OpenAICallbackHandler()
    llm = ChatOpenAI(model=model, openai_api_key=OPENAI_API_KEY, callbacks=[token_logger])
    tools = [ReadFileTool(), WriteFileTool(), ListDirectoryTool(), pytest_tool]
    APP = build_react_graph(tools=tools, llm=llm)

    print("Initializing chat history...\n")
    chat_history = []
    system_message = SystemMessage(content=f"""
    You are PAUL, an AI-powered GitHub developer assistant.
    Your job is to automatically resolve issues in a local repository that has already been cloned to {repo_path}.

    Given the following:
    - The full GitHub issue (including title and body)
    - Complete read/write access to the repository files and standard developer tools

    Follow this workflow:
    1. **Understand the Issue:** Carefully read the issue title and body to determine what needs to be fixed or implemented.
    2. **Locate Relevant Code:** Identify which file(s) in the codebase are related to the issue and require modification.
    3. **Apply the Patch:** Make only the changes necessary to address the issue. Ensure your code is clear, correct, and matches the project’s coding style.
    4. **Test:** If possible, verify that your fix works (e.g., run tests or explain what you did to verify).
    5. **Prepare the Commit:** Write a concise, informative commit message describing the change. The message should be suitable for inclusion in the main branch’s history.
    6. **Draft a Pull Request:** Write a clear pull request title and body. The title should summarize the fix; the body should explain what was changed and why.

    **Constraints:**
    - Make the minimal necessary change to resolve the issue—avoid unrelated edits.
    - Maintain or improve code readability and safety.
    - Only use developer tools (such as code editing, git operations, etc.) when required.
    - Output must be in the required JSON format, with all fields present.

    **Your response must be a JSON object with these fields:**
    - `commit_msg`: A clear, concise commit message.
    - `pr_title`: The pull request title.
    - `pr_body`: The pull request body (do not mention the issue number in the body).

    Example response:
    ```json
    {
    "commit_msg": "Fix division by zero error in app.py",
    "pr_title": "Fix division by zero in app calculation",
    "pr_body": "This PR fixes a bug in app.py that could cause a division by zero when processing empty input. A conditional check was added to prevent the error."
    }
    ```
                                   
    Do not include any explanation or extra commentary outside the JSON. Only output the JSON object.
    """)
    chat_history.append(system_message)
    query = HumanMessage(content=f"""
        Issue Title: {issue_title}
        Issue Body: {issue_body}
    """)
    chat_history.append(query)

    print("Invoking PAUL...\n")
    try:
        output_state = APP.invoke({"messages" : chat_history})
    except GraphRecursionError as e:
        raise RuntimeError("Failed to provide a solution due to recursion limit. Exiting...") from e
    
    print("PAUL has finished working!\n")
    return parse_paul_response(output_state["messages"], issue_number, token_logger), branch_name