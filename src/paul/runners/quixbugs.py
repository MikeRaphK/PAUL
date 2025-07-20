from ..utils import print_paul_response
from ..workflow import run_paul_workflow
import os


def run_quixbugs(
    repo_path: str, file: str, model: str, OPENAI_API_KEY: str
) -> None:
    print(f"Running PAUL on QuixBugs file '{file}'...\n")
    issue_title = f"QuixBugs Issue: {file}"
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PAUL_DIR = os.path.dirname(CURRENT_DIR)
    QUIXBUGS_TEMPLATE_PATH = os.path.join(
        PAUL_DIR, "resources/quixbugs_issue_template.txt"
    )
    with open(QUIXBUGS_TEMPLATE_PATH, "r") as f:
        issue_body = f.read().format(
            file_path=f"python_programs/{file}",
            test_path=f"python_testcases/test_{file}",
        )

    paul_response = run_paul_workflow(
        repo_path=repo_path,
        issue_title=issue_title,
        issue_body=issue_body,
        OPENAI_API_KEY=OPENAI_API_KEY,
        model=model,
    )

    print_paul_response(paul_response)
