from ..paul import run_paul_workflow
from ..utils import print_patch_report


def run_local(
    repo_path: str,
    issue_path: str,
    tests: list[str],
    model: str,
    venv: str,
    OPENAI_API_KEY: str,
) -> None:
    print(f"Reading issue file from '{issue_path}'...\n")
    with open(issue_path, "r") as f:
        issue_body = f.read()

    report = run_paul_workflow(
        repo_path=repo_path,
        issue_body=issue_body,
        tests=tests,
        model=model,
        OPENAI_API_KEY=OPENAI_API_KEY,
        venv=venv,
    )
    print_patch_report(report)
