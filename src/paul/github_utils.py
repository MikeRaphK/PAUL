from git import Repo
from typing import Dict, Tuple

import os
import re
import shutil
import subprocess
import time

from .utils import request_with_retry



def parse_owner_name_default_branch(repo_url: str, GITHUB_TOKEN: str) -> Tuple[str, str, str]:
    """
    Parses the owner, repository name, and default branch from a GitHub repository URL.

    Args:
        repo_url (str): The full HTTPS URL of the GitHub repository (e.g., 'https://github.com/user/repo').
        GITHUB_TOKEN (str): A valid GitHub token with permission to access the repository metadata.

    Returns:
        Tuple[str, str, str]: A tuple containing:
            - owner (str): The GitHub username or organization.
            - repo (str): The repository name.
            - default_branch (str): The repository's default branch (usually 'main' or 'master').

    Raises:
        ValueError: If the given URL does not match the expected GitHub format.
        requests.RequestException: If the GitHub API request fails after retries.
    """
    # Try to get the owner and repo name from the URL
    match = re.match(r'https?://github\.com/([^/]+)/([^/]+)(?:/|$)', repo_url)
    if not match:
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    owner, repo =  match.group(1), match.group(2)

    # Try to get the default branch
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = { "Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json" }
    response = request_with_retry("GET", api_url, headers=headers)
    default_branch = response.json().get("default_branch", "main")
    return owner, repo, default_branch



def get_issue(owner: str, name: str, issue_number : int) -> Dict[str, str]:
    """
    Retrieves a specific open issue from a GitHub repository by its issue number.

    Args:
        owner (str): The GitHub username or organization that owns the repository.
        name (str): The name of the repository.
        issue_number (int): The number of the issue to retrieve.

    Returns:
        Dict[str, str]: A dictionary representing the issue.

    Raises:
        ValueError: If the specified issue number is not found among open issues.
        requests.RequestException: If the GitHub API request fails.
    """
    issues_url = f"https://api.github.com/repos/{owner}/{name}/issues"
    params = {'state': 'open', 'per_page': 100}
    response = request_with_retry("GET", issues_url, params=params)
    
    # Iterate over open issues, skipping pull requests until we find the one we want
    issue = None
    for current_issue in response.json():
        if 'pull_request' in current_issue:
            continue
        if current_issue['number'] == issue_number:
            issue = current_issue
            break

    if not issue:
        raise ValueError(f"Issue number {issue_number} not found in {owner}/{name}.")
    return issue



def clone_repo(repo_url: str, repo_path: str, timeout: float = 15.0, max_retries: int = 3, backoff: float = 5.0) -> Repo:
    """
    Clone a git repo with a per-attempt timeout and retry policy.
    
    Args:
        repo_url:     HTTPS or SSH URL of the repo to clone.
        repo_path:    Local directory to clone into.
        timeout:      Seconds to wait for each `git clone` before giving up.
        max_retries:  How many times to retry on error or timeout.
        backoff:      Seconds to sleep between attempts.
    
    Returns:
        A GitPython Repo object for the cloned repo.
    
    Raises:
        RuntimeError on final failure.
    """
    for attempt in range(0, max_retries):
        try:
            # Clean up old clone
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            
            # Attempt to clone with a timeout
            subprocess.run(["git", "clone", repo_url, repo_path], check=True, timeout=timeout)
            return Repo(repo_path)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
        except Exception as e:
            raise RuntimeError(f"Git clone unexpected error: {e!r}")
        
        # Retry policy
        if attempt < max_retries:
            time.sleep(backoff)
    # Raise an error if all attempts fail
    raise RuntimeError(f"Failed to clone {repo_url} into {repo_path} after {max_retries} attempts.")



def create_pr(repo: Repo, commit_msg:str, owner: str, repo_name: str, GITHUB_TOKEN: str, title: str, body: str, base_branch: str,
              timeout: float = 15.0, max_retries: int = 3, backoff: float = 5.0) -> None:
    """Stages all changes, commits them, pushes to the current branch, and creates a pull request on GitHub.

    The function assumes the current branch (i.e., `repo.active_branch.name`) is the source (head) of the pull request.
    It pushes the commit to the remote if needed, and then makes a GitHub API call to open a PR into the specified base branch.

    Args:
        repo (Repo): The GitPython Repo object representing the local repository.
        commit_msg (str): The commit message to use for the staged changes.
        owner (str): The GitHub username or organization that owns the repository.
        repo_name (str): The name of the target GitHub repository.
        GITHUB_TOKEN (str): A GitHub personal access token used for authentication.
        title (str): The title of the pull request.
        body (str): The body/description of the pull request.
        base_branch (str): The name of the branch to merge into (usually 'main' or 'master').
    """
    # Git add, commit, and push with retry policy
    authed_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{owner}/{repo_name}.git"
    repo.git.remote("set-url", "origin", authed_url)
    repo.git.add(".")
    repo.index.commit(commit_msg)
    branch = repo.active_branch.name
    cwd = repo.working_tree_dir
    success = False
    for attempt in range(0, max_retries):
        try:
            # Attempt to push with a timeout
            subprocess.run(["git", "push", "origin", branch], cwd=cwd, check=True, timeout=timeout)
            success = True
            break
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
        except Exception as e:
            raise RuntimeError(f"Git push unexpected error: {e!r}")

        # Retry policy
        if attempt < max_retries:
            time.sleep(backoff)
    if not success:
        raise RuntimeError(f"git push origin {branch} failed after {max_retries} attempts.")

    # Create the pull request
    pr_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    data = {
        "title": title,
        "body": body,
        "head": repo.active_branch.name,
        "base": base_branch
    }
    request_with_retry("POST", pr_url, headers=headers, json=data)