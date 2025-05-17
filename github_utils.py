import os
import re
import requests
import shutil
import subprocess
import time

from git import Repo
from requests.adapters import HTTPAdapter
from typing import Any, List, Dict, Tuple
from urllib3.util.retry import Retry

def request_with_retry(method: str, url: str, retries: int = 3, timeout: int = 5, **kwargs: Any) -> requests.Response:
    """
    Performs an HTTP request with retry and timeout logic.

    Args:
        method (str): The HTTP method to use (e.g., 'GET', 'POST', etc.).
        url (str): The URL to send the request to.
        retries (int, optional): Number of retry attempts. Defaults to 3.
        timeout (int, optional): Timeout for the request in seconds. Defaults to 5.
        **kwargs (Any): Additional keyword arguments to pass to requests.request(), such as headers, json, data, etc.

    Returns:
        requests.Response: The response object if the request succeeds.

    Raises:
        Exception: If the request fails after all retries.
    """
    retry_strategy = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=[method]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response = session.request(method=method, url=url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        msg = f"Request {method} error for {url}"
        if hasattr(e, 'response') and e.response is not None:
            msg += f": {e.response.status_code} {e.response.text}"
        raise Exception(msg) from e



def parse_owner_name_default_branch(repo_url: str, GITHUB_TOKEN: str) -> Tuple[str, str, str]:
    """
    Parse the owner, repository name, and default branch from a GitHub repository URL.

    Args:
        repo_url (str): The GitHub repository URL.

    Returns:
        Tuple[str, str, str]: A tuple containing the repository owner, name, and default branch.
        If the URL is invalid or the repo is not found, returns (None, None, None).
    """
    # Try to get the owner and repo name from the URL
    match = re.match(r'https?://github\.com/([^/]+)/([^/]+)(?:/|$)', repo_url)
    if not match:
        return None, None
    owner, repo =  match.group(1), match.group(2)

    # Try to get the default branch
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = { "Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json" }
    response = request_with_retry("GET", api_url, headers=headers)
    default_branch = response.json().get("default_branch", "main")
    return owner, repo, default_branch



def get_open_issues(owner: str, name: str) -> List[Dict[str, str]]:
    """
    Get open issues from a GitHub repository.

    Args:
        owner (str): The owner of the repository.
        name (str): The name of the repository.

    Returns:
        List[Dict[str, str]]: A list of open issues, each as a dictionary with 'title', 'body' and 'number'.
    """
    issues_url = f"https://api.github.com/repos/{owner}/{name}/issues"
    params = {'state': 'open', 'per_page': 100}
    response = request_with_retry("GET", issues_url, params=params)
    
    # Get title, body and number of each issue while ignoring pull requests
    issues = []
    for issue in response.json():
        if 'pull_request' not in issue:
            element = {"title": issue["title"], "body": issue.get("body", ""), "number": issue["number"]}
            issues.append(element)
            
    return issues



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