from ..workflow import run_paul_workflow
from ..utils import print_paul_response



def run_local(repo_path: str, issue_path: str, model: str, OPENAI_API_KEY: str) -> None:
    print(f"Reading issue file from '{issue_path}'...\n")
    with open(issue_path, "r") as f:
        issue_body = f.read()
    paul_response = run_paul_workflow(repo_path=repo_path, issue_body=issue_body, OPENAI_API_KEY=OPENAI_API_KEY, model=model)
    print_paul_response(paul_response)