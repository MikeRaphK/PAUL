from ..workflow import run_paul_workflow
from ..utils import write_paul_response
from typing import Tuple
import os



def parse_issue_file(issue_path: str) -> Tuple[str, int, str]:
    """
    Checks if the given file exists and parses its contents.
    The first line becomes the issue_title, the second line the issue_number (int) and the rest the issue_body.

    Args:
        issue_path (str): Path to the issue description file.

    Returns:
        Tuple[str, int, str]: (issue_title, issue_number, issue_body)

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file has invalid formatting.
    """
    # Check if the issue file exists
    if not os.path.isfile(issue_path):
        raise FileNotFoundError(f"Issue file not found: {issue_path}")

    # Read it
    with open(issue_path, encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) < 3:
        raise ValueError(f"Issue file must have at least 3 lines (title, number, body)")

    # Parse it
    issue_title = lines[0].strip()
    issue_number = int(lines[1].strip())
    issue_body = "".join(lines[2:]).strip()
    return issue_title, issue_number, issue_body



def run_local(repo_path: str, issue_path: str, output_path: str, model: str, OPENAI_API_KEY: str) -> None:
    print(f"Reading issue file from '{issue_path}'...\n")
    issue_title, issue_number, issue_body = parse_issue_file(issue_path)

    paul_response, _ = run_paul_workflow(model, repo_path, issue_title, issue_body, issue_number, OPENAI_API_KEY)
    write_paul_response(output_path, paul_response)