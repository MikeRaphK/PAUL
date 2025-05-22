from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_community.tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError

import json
import re

from . import github_utils as ghu
from .graph_builder import build_graph
from .utils import check_env_vars



def run_paul(repo_url: str, issue_number: int) -> None:
    # Check environment variables
    GITHUB_TOKEN, OPENAI_API_KEY = check_env_vars()
    
    # Get repo URL and check if it is valid
    print("Checking if the GitHub URL is valid...\n")
    owner, repo_name, default_branch = ghu.parse_owner_name_default_branch(repo_url, GITHUB_TOKEN)

    # Get issue
    print(f"Getting issue #{issue_number}...\n")
    issue = ghu.get_issue(owner, repo_name, issue_number)

    # Clone repo
    repo_path = "./cloned_repo/"
    repo = ghu.clone_repo(repo_url, repo_path)

    # Create (or checkout) to the new branch
    branch_name = "PAUL-branch"
    print(f"\nBranching to '{branch_name}'...\n")
    if branch_name in [b.name for b in repo.branches]:
        repo.git.checkout(branch_name)
    else:
        repo.git.checkout("-b", branch_name)

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
        You are an AI software engineer. Your task is to automatically fix issues in a local GitHub repository located at ./cloned_repo. For each task:
            1. Read and understand the GitHub issue provided to you.
            2. Locate the relevant part(s) of the codebase inside ./cloned_repo that need to be changed.
            3. Modify the code to resolve the issue while maintaining functionality, clarity, and style.
            4. Generate a concise and informative git commit message describing the fix.
            5. Prepare a pull request summary explaining what was fixed, how it was fixed, and any tests added or run.
        Constraints:
            1. Only make changes necessary to fix the issue.
            2. Prefer minimal, safe, and testable changes.
            3. Do not introduce unrelated modifications.
            4. Assume the repository uses standard Git practices.
            5. Only use tools when strictly necessary, otherwise end the conversation.
        Respond with a JSON object containing the following fields:
            - "modified_files": The list of modified files.
            - "commit_msg": The commit message.
            - "pr_title": The pull request title.
            - "pr_body": The pull request body. Make sure to include the issue number in the body.
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
    print(f"ChatGPT response: {content}\n")
    print(f"{callback}\n")

    # Create a pull request
    print("Creating pull request...\n")
    # Remove leading and trailing fences
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    content_json = json.loads(content)
    ghu.create_pr(repo, content_json["commit_msg"], owner, repo_name, GITHUB_TOKEN, content_json["pr_title"], content_json["pr_body"], default_branch)
    print("\nPull request created successfully!")    