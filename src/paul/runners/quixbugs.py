from ..paul import run_paul_workflow
from ..utils import print_patch_report
import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PAUL_DIR = os.path.dirname(CURRENT_DIR)
QUIXBUGS_TEMPLATE_PATH = os.path.join(PAUL_DIR, "resources/quixbugs_issue_template.txt")


def run_quixbugs(
    repo_path: str,
    language: str,
    name: str,
    verify: bool,
    model: str,
    OPENAI_API_KEY: str,
) -> None:
    quixbugs_verify_cmd = None
    if language == "python":
        file_path = f"./python_programs/{name}.py"
        test_path = f"./python_testcases/test_{name}.py"
        if verify:
            quixbugs_verify_cmd = f"pytest {test_path} -vvvv"
    else:
        file_path = f"./java_programs/{name}.java"
        test_path = f"./java_testcases/junit/{name}_TEST.java"
        if verify:
            quixbugs_verify_cmd = f"gradle test --tests java_testcases.junit.{name}_TEST"

    print(f"Running PAUL on QuixBugs file '{file_path}'...\n")
    issue_title = f"QuixBugs Issue: {file_path}"
    with open(QUIXBUGS_TEMPLATE_PATH, "r") as f:
        issue_body = f.read().format(
            file_path=file_path,
            test_path=test_path,
        )

    report = run_paul_workflow(
        repo_path=repo_path,
        issue_title=issue_title,
        issue_body=issue_body,
        OPENAI_API_KEY=OPENAI_API_KEY,
        model=model,
        tests=[],
        quixbugs_verify_cmd=quixbugs_verify_cmd
    )
    print_patch_report(report)
