from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_community.tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError

from .graph_builder import build_graph
from .tool_logger import ToolLogger
from .utils import setup_git_environment, parse_paul_response, create_pull_request
from github import Github
from subprocess import run

import uuid


def run_paul(owner: str, repo_name: str, issue_number: int, GITHUB_TOKEN: str, OPENAI_API_KEY: str) -> None:
    print("Waking PAUL up...\n")
    setup_git_environment()
    gh = Github(GITHUB_TOKEN)

    print(f"Getting issue #{issue_number}...")
    repo = gh.get_repo(f"{owner}/{repo_name}")
    issue = repo.get_issue(number=issue_number)

    branch_name = f"PAUL-branch-{uuid.uuid4().hex[:8]}"
    print(f"Branching to '{branch_name}'...\n")
    run(["git", "checkout", "-b", branch_name], check=True)

    print("Initializing ReAct graph...\n")
    token_logger = OpenAICallbackHandler()
    tool_logger = ToolLogger()
    model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, callbacks=[token_logger])
    tools = [ReadFileTool(), WriteFileTool(), ListDirectoryTool()]
    APP = build_graph(tools=tools, llm=model, callbacks=[tool_logger])

    print("Initializing chat history...\n")
    chat_history = []
    system_message = SystemMessage(content="""
    You are PAUL, an AI-powered GitHub developer assistant.
    Your job is to automatically resolve issues in a local repository that has already been cloned to /github/workspace.

    Given the following:
    - The full GitHub issue (including number, title, and body)
    - Complete read/write access to the repository files and standard developer tools

    Follow this workflow:
    1. **Understand the Issue:** Carefully read the issue title, body, and number to determine what needs to be fixed or implemented.
    2. **Locate Relevant Code:** Identify which file(s) in the codebase are related to the issue and require modification.
    3. **Apply the Patch:** Make only the changes necessary to address the issue. Ensure your code is clear, correct, and matches the project’s coding style.
    4. **Test:** If possible, verify that your fix works (e.g., run tests, add a minimal test if relevant, or explain what you did to verify).
    5. **Prepare the Commit:** Write a concise, informative commit message describing the change. The message should be suitable for inclusion in the main branch’s history.
    6. **Draft a Pull Request:** Write a clear pull request title and body. The title should summarize the fix; the body should explain what was changed and why. Do **not** include the issue number in the body.

    **Constraints:**
    - Make the minimal necessary change to resolve the issue—avoid unrelated edits.
    - Maintain or improve code readability and safety.
    - Only use developer tools (such as code editing, git operations, etc.) when required.
    - Output must be in the required JSON format, with all fields present.

    **Your response must be a JSON object with these fields:**
    - `modified_files`: List of modified file paths (relative to the repo root).
    - `commit_msg`: A clear, concise commit message.
    - `pr_title`: The pull request title.
    - `pr_body`: The pull request body (do not mention the issue number in the body).

    Example response:
    ```json
    {
    "modified_files": ["src/app.py"],
    "commit_msg": "Fix division by zero error in app.py",
    "pr_title": "Fix division by zero in app calculation",
    "pr_body": "This PR fixes a bug in app.py that could cause a division by zero when processing empty input. A conditional check was added to prevent the error."
    }
    ```
                                   
    Do not include any explanation or extra commentary outside the JSON. Only output the JSON object.
    """)
    chat_history.append(system_message)
    query = HumanMessage(content=f"""
        Issue Title: {issue.title}
        Issue Body: {issue.body}
        Issue Number: {issue_number}
    """)
    chat_history.append(query)

    print("Invoking LLM...\n")
    try:
        output_state = APP.invoke({"messages" : chat_history})
    except GraphRecursionError as e:
        raise RuntimeError("Failed to provide a solution due to recursion limit. Exiting...") from e
    content = output_state["messages"][-1].content
    
    print("Creating pull request...\n")
    content_json = parse_paul_response(content, issue_number, token_logger, tool_logger)
    pr = create_pull_request(content_json, branch_name, repo)
    
    print(f"Pull request successfully created: {pr.html_url}")