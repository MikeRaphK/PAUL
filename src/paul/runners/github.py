from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from typing import Dict

import os

from ..workflow import run_paul_workflow

def setup_git_environment() -> None:
    """
    Set up the local Git environment for safe repository operations in a Docker-based GitHub Action.

    Raises:
        subprocess.CalledProcessError: If any git command fails.
        AssertionError: If the .git directory does not exist in /github/workspace.
    """
    os.chdir("/github/workspace")
    os.environ["GIT_DIR"] = os.path.abspath(".git")
    os.environ["GIT_WORK_TREE"] = os.getcwd()
    run(["git", "config", "user.email", "paul-bot@users.noreply.github.com"], check=True)
    run(["git", "config", "user.name", "paul-bot"], check=True)
    run(["git", "config", "--global", "--add", "safe.directory", os.getcwd()])



def create_pull_request(paul_response: Dict[str, str], branch_name: str, repo: Repository) -> PullRequest:
    """
    Commit local changes and create a pull request on GitHub.

    Args:
        paul_response (Dict[str, str]): Dictionary containing the commit message, PR title, and PR body.
        branch_name (str): Name of the branch to push and use as the PR head.
        repo (Repository): PyGithub Repository object for the target repo.

    Returns:
        PullRequest: The created GitHub PullRequest object.
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
        draft=False
    )
    return pr

def run(owner: str, repo_name: str, issue_number: int, model: str, GITHUB_TOKEN: str, OPENAI_API_KEY: str) -> None:
    print("Setting up GitHub environment...\n")
    setup_git_environment()
    gh = Github(GITHUB_TOKEN)

    print(f"Getting issue #{issue_number}...")
    repo = gh.get_repo(f"{owner}/{repo_name}")
    issue = repo.get_issue(number=issue_number)
    label_names = [label.name for label in issue.labels]
    if 'PAUL' not in label_names:
        print("No 'PAUL' label found. Exiting...")
        return

    paul_response, branch_name = run_paul_workflow(model, "/github/workspace", issue.title, issue.body, issue_number, OPENAI_API_KEY)

    print("Creating pull request...\n")
    pr = create_pull_request(paul_response, branch_name, repo)
    
    print(f"Pull request successfully created: {pr.html_url}")