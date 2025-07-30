from ..workflow import run_paul_workflow
from github import Github
from github.Repository import Repository
from subprocess import run
from typing import Dict

import os
import re
import uuid


def setup_git_environment(CHECKOUT_DIR: str) -> None:
    """
    Set up the local Git environment for safe repository operations in a Docker-based GitHub Action.

    Args:
        CHECKOUT_DIR (str): Name of the repository to set up.

    Raises:
        subprocess.CalledProcessError: If any git command fails.
        AssertionError: If the .git directory does not exist in /github/workspace.
    """
    os.environ["GIT_DIR"] = os.path.join(CHECKOUT_DIR, ".git")
    os.environ["GIT_WORK_TREE"] = CHECKOUT_DIR
    run(
        ["git", "config", "user.email", "paul-bot@users.noreply.github.com"], check=True
    )
    run(["git", "config", "user.name", "paul-bot"], check=True)
    run(["git", "config", "--global", "--add", "safe.directory", CHECKOUT_DIR])


def get_tests(issue_body: str) -> list[str]:
    """
    Parses a ```tests code block from the issue body and returns a list of test paths.

    Args:
        issue_body (str): The full issue description text.

    Returns:
        list[str]: List of test paths (lines) inside the ```tests block.
                   Returns an empty list if no block is found.
    """
    # Match the ```tests fenced code block
    match = re.search(r"```tests\s*\n(.*?)```", issue_body, re.DOTALL)
    
    if not match:
        return []

    # Extract and clean each line inside the block
    block_content = match.group(1)
    lines = [line.strip() for line in block_content.strip().splitlines()]
    
    return [line for line in lines if line]


def create_pull_request(
    paul_response: Dict[str, str], branch_name: str, repo: Repository
) -> str:
    """
    Commit local changes and create a pull request on GitHub.

    Args:
        paul_response (Dict[str, str]): Dictionary containing the commit message, PR title, and PR body.
        branch_name (str): Name of the branch to push and use as the PR head.
        repo (Repository): PyGithub Repository object for the target repo.

    Returns:
        str: The created GitHub pull request URL.
    """

    # Commit and push
    run(["git", "add", "."], check=True)
    run(["git", "commit", "-m", paul_response["commit_msg"]], check=True)
    run(["git", "push", "--set-upstream", "origin", branch_name], check=True)

    # Create pull request
    pr = repo.create_pull(
        title=paul_response["pr_title"],
        body=paul_response["pr_body"],
        head=branch_name,
        base=repo.default_branch,
        draft=False,
    )
    return pr.html_url


def run_github(
    owner: str,
    repo_name: str,
    issue_number: int,
    model: str,
    GITHUB_TOKEN: str,
    OPENAI_API_KEY: str,
) -> None:
    print("Setting up GitHub environment...\n")
    CHECKOUT_DIR = f"/__w/{repo_name}/{repo_name}"
    setup_git_environment(CHECKOUT_DIR)

    print(f"Getting issue #{issue_number}...\n")
    gh = Github(GITHUB_TOKEN)
    repo = gh.get_repo(f"{owner}/{repo_name}")
    issue = repo.get_issue(number=issue_number)
    label_names = [label.name for label in issue.labels]
    if "PAUL" not in label_names:
        print("No 'PAUL' label found. Exiting...")
        return

    branch_name = f"PAUL-branch-{uuid.uuid4().hex[:8]}"
    run(["git", "checkout", "-b", branch_name], check=True)
    print()
    
    print("Getting tests from issue body...\n")
    tests = get_tests(issue.body)
    print(f"Found tests: {tests}\n")

    paul_response = run_paul_workflow(
        repo_path=CHECKOUT_DIR,
        issue_title=issue.title,
        issue_body=issue.body,
        issue_number=issue_number,
        OPENAI_API_KEY=OPENAI_API_KEY,
        model=model,
        tests=[]
    )

    print("Creating pull request...\n")
    url = create_pull_request(paul_response, branch_name, repo)
    print(f"Pull request successfully created: {url}")
