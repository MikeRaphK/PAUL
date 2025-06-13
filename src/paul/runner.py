from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_community.tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError

import json
import os
import re
import uuid

from . import github_utils as ghu
from .graph_builder import build_graph
from github import Github
from subprocess import run


def run_paul(owner: str, repo_name: str, issue_number: int, GITHUB_TOKEN: str, OPENAI_API_KEY: str) -> None:
    print("Starting PAUL...")
    print(f"Owner: {owner}")
    print(f"Repo: {repo_name}")
    print(f"Issue Number: {issue_number}")

    # Set up git environment
    os.chdir("/github/workspace")
    run(["git", "config", "user.email", "paul-bot@users.noreply.github.com"], check=True)
    run(["git", "config", "user.name", "paul-bot"], check=True)
    gh = Github(GITHUB_TOKEN)

    # Get issue
    repo = gh.get_repo(f"{owner}/{repo_name}")
    issue = repo.get_issue(number=issue_number)

    # Create new branch
    branch_name = f"PAUL-branch-{uuid.uuid4().hex[:8]}"
    print(f"\nBranching to '{branch_name}'...\n")
    run(["git", "checkout", "-b", branch_name], check=True)

    # Create the graph
    print("Initializing ReAct graph...\n")
    callback = OpenAICallbackHandler()
    model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, callbacks=[callback], request_timeout=15.0)
    tools = [ReadFileTool(), WriteFileTool(), ListDirectoryTool()]
    APP = build_graph(tools=tools, llm=model)

    # Initialize system message and query
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
        Issue Title: {issue['title']}
        Issue Body: {issue['body']}
        Issue Number: {issue['number']}
    """)
    chat_history.append(query)

    # Invoke the LLM
    print("Invoking LLM...\n")
    try:
        output_state = APP.invoke({"messages" : chat_history})
    except GraphRecursionError as e:
        raise RuntimeError("Failed to provide a solution due to recursion limit. Exiting...") from e
    content = output_state["messages"][-1].content
    print("LLM response received:\n")
    print(content)

    print("Creating pull request...\n")
    # Remove leading and trailing fences
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    content_json = json.loads(content)

    # Add more info to pr_body
    content_json["pr_body"] =  "> **Note:** This message was automatically generated by PAUL. Please review the proposed changes carefully before merging.\n\n" + content_json["pr_body"]
    content_json["pr_body"] += f"\n\nRelated to #{issue['number']}\n"
    content_json["pr_body"] += f"Tokens Used: {callback.total_tokens}\n"
    content_json["pr_body"] += f"Successful Requests: {callback.successful_requests}\n"
    content_json["pr_body"] += f"Total Cost (USD): {callback.total_cost:.6f}\n"

    for key, value in content_json.items():
        print(f"{key}: {value}\n")

    print("Exiting PAUL...")
    exit()
    
    ghu.create_pr(repo, content_json["commit_msg"], owner, repo_name, GITHUB_TOKEN, content_json["pr_title"], content_json["pr_body"], default_branch)
    print("\nPull request created successfully!")    