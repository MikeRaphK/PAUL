from ..utils import print_paul_response
from ..workflow import run_paul_workflow
from datasets import load_dataset, Dataset

import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PAUL_DIR = os.path.dirname(CURRENT_DIR)
SWE_CACHE_PATH = os.path.join(PAUL_DIR, "resources/swebench_cache/")
SWEBENCH_TEMPLATE_PATH = os.path.join(PAUL_DIR, "resources/swebench_issue_template.txt")


def run_swebench_lite(
    repo_path: str,
    id: str,
    tests: list[str],
    model: str,
    venv: str,
    OPENAI_API_KEY: str,
) -> None:
    # Load SWE-bench Lite dataset (from cache if available)
    if os.path.exists(SWE_CACHE_PATH):
        print(f"Loading SWE-bench Lite test split from cache at {SWE_CACHE_PATH}...\n")
        swebench_lite = Dataset.load_from_disk(SWE_CACHE_PATH)
    else:
        print(f"Cache not found. Downloading SWE-bench Lite test split...\n")
        swebench_lite = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
        print(f"Saving dataset to {SWE_CACHE_PATH}...\n")
        swebench_lite.save_to_disk(SWE_CACHE_PATH)

    # Search for the benchmark with the given ID
    print(f"Searching for benchmark with ID '{id}'...\n")
    benchmark = None
    for row in swebench_lite:
        if row["instance_id"] == id:
            benchmark = row
            break
    if benchmark is None:
        raise ValueError(f"Benchmark with ID {id} not found in test split.")

    # Read issue template and format with benchmark details
    issue_title = f"SWE-bench Lite: {id}"
    with open(SWEBENCH_TEMPLATE_PATH, "r") as f:
        issue_body = f.read().format(
            problem_statement=benchmark["problem_statement"],
            hints_text=benchmark["hints_text"],
            tests=tests,
        )

    # Run PAUL workflow
    paul_response = run_paul_workflow(
        repo_path=repo_path,
        issue_title=issue_title,
        issue_body=issue_body,
        OPENAI_API_KEY=OPENAI_API_KEY,
        model=model,
        tests=tests,
        venv=venv,
        swe=True
    )
    print_paul_response(paul_response)
