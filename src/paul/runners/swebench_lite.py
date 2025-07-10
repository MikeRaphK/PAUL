from ..utils import print_paul_response
from ..workflow import run_paul_workflow
from datasets import load_dataset

import os


def run_swebench_lite(
    repo_path: str, split: str, id: str, test: str, model: str, OPENAI_API_KEY: str
) -> None:
    print(f"Loading SWE-bench Lite dataset from split '{split}'...\n")
    swebench_lite = load_dataset("princeton-nlp/SWE-bench_Lite", split=split)

    print(f"Searching for benchmark with ID '{id}' in split '{split}'...\n")
    benchmark = None
    for row in swebench_lite:
        if row["instance_id"] == id:
            benchmark = row
            break
    if benchmark is None:
        raise ValueError(f"Benchmark with ID {id} not found in split {split}.")

    issue_title = f"SWE-bench Lite: {id}"
    SWEBENCH_TEMPLATE_PATH = os.path.join(
        os.getcwd(), "src/paul/swebench_issue_template.txt"
    )
    with open(SWEBENCH_TEMPLATE_PATH, "r") as f:
        issue_body = f.read().format(
            problem_statement=benchmark["problem_statement"],
            hints_text=benchmark["hints_text"],
            test=test,
        )
    paul_response = run_paul_workflow(
        repo_path=repo_path,
        issue_title=issue_title,
        issue_body=issue_body,
        OPENAI_API_KEY=OPENAI_API_KEY,
        model=model,
    )
    print_paul_response(paul_response)
