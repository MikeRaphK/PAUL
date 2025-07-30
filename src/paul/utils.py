from dotenv import load_dotenv
from typing import Tuple

import argparse
import os
import shutil

def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments for PAUL's modes of operation.

    Returns:
        argparse.Namespace: Parsed arguments. The fields depend on the selected mode:
            - local:
                --path: Path to local repository (str)
                --issue: Path to issue description file (str)
                --model: (optional) LLM model name (str)
                --tests: (optional) List of pytest targets (list[str])
            - github:
                --owner: GitHub repo owner (str)
                --repo: Repository name (str)
                --issue: Issue number (int)
                --model: (optional) LLM model name (str)
                --tests: (optional) List of pytest targets (list[str])
            - swebench:
                --path: Repository path (str)
                --split: Benchmark split (str)
                --id: Benchmark instance ID (str)
                --test: Pytest target (str)
                --model: (optional) LLM model name (str)
                --tests: (optional) List of pytest targets (list[str])
            - quixbugs:
                --path: Repository path (str)
                --file: Python filename to patch (str)
                --model: (optional) LLM model name (str)
                --tests: (optional) List of pytest targets (list[str])
    """

    # Main parser
    parser = argparse.ArgumentParser(
        usage="paul <mode> <mode args>",
        description="PAUL - Patch Automation Using LLMs: LLM agent that automatically detects and patches GitHub issues.",
        epilog="For more information on a specific mode, run: paul <mode> --help"
    )

    # Parent parser for shared arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (optional, default: gpt-4o-mini)",
        metavar="<model>",
    )
    parent_parser.add_argument(
        "--tests",
        default=[],
        nargs="+",
        help="Optional list of test targets to run with pytest",
        metavar="<tests>",
    )

    # Subparsers for different modes
    subparsers = parser.add_subparsers(
        dest="mode",
        required=True,
        title="modes",
        metavar="<mode>",
        description="Choose one of PAUL's available modes of operation",
    )

    # GitHub Actions mode
    parser_github = subparsers.add_parser(
        "github",
        help="Run in GitHub Actions mode.",
        usage="paul github --owner <repo owner username> --repo <repo name> --issue <issue number>",
        description="Run PAUL in GitHub Actions mode. This mode is designed to be called automatically from a GitHub Actions workflow YAML file, not for manual CLI use.",
        epilog="Example: paul github --owner MikeRaphK --repo PAUL --issue 13",
        parents=[parent_parser]
    )
    parser_github.add_argument(
        "--owner",
        required=True,
        help="GitHub repository owner username",
        metavar="<username>",
    )
    parser_github.add_argument(
        "--repo", required=True, help="Repository name", metavar="<repo name>"
    )
    parser_github.add_argument(
        "--issue",
        required=True,
        type=int,
        help="Issue number (int)",
        metavar="<number>",
    )

    # Local mode
    parser_local = subparsers.add_parser(
        "local",
        help="Run locally on a cloned repository",
        usage="paul local --path <repo path> --issue <issue desc>",
        description="Run PAUL locally on a cloned repository.",
        epilog="Example: paul local --path ./PAUL-tests/ --issue ./PAUL-tests/issues/is_anagram_issue.txt",
        parents=[parent_parser]
    )
    parser_local.add_argument(
        "--path",
        required=True,
        help="Path to locally cloned repository",
        metavar="<repo path>",
    )
    parser_local.add_argument(
        "--issue",
        required=True,
        help="File containing issue description",
        metavar="<issue desc>",
    )

    # SWE-bench Lite mode
    parser_swebench_lite = subparsers.add_parser(
        "swebench",
        help="Run on SWE-bench Lite",
        usage="paul swebench --path <repo path> --split <split> --id <instance id> --test <test>",
        description="Run PAUL on SWE-bench Lite benchmark.",
        epilog="Example: paul swebench --path ./sympy --split test --id sympy__sympy-20590 --test sympy/core/tests/test_basic.py::test_immutable",
        parents=[parent_parser]
    )
    parser_swebench_lite.add_argument(
        "--path",
        required=True,
        help="Path to locally cloned SWE-bench Lite repository",
        metavar="<repo path>",
    )
    parser_swebench_lite.add_argument(
        "--split", required=True, help="The split of SWE-bench Lite", metavar="<split>"
    )
    parser_swebench_lite.add_argument(
        "--id",
        required=True,
        help="The instance id of a benchmark instance",
        metavar="<instance id>",
    )
    parser_swebench_lite.add_argument(
        "--test",
        required=True,
        help="The test that fails when using pytest",
        metavar="<test>",
    )

    # QuixBugs mode
    parser_quixbugs = subparsers.add_parser(
        "quixbugs",
        help="Run on QuixBugs",
        usage="paul local --path <repo path> --file <file name>",
        description="Run PAUL on QuixBugs benchmark.",
        epilog="Example: paul quixbugs --path ./QuixBugs/ --file flatten.py",
        parents=[parent_parser]
    )
    parser_quixbugs.add_argument(
        "--path",
        required=True,
        help="Path to QuixBugs repository",
        metavar="<repo path>",
    )
    parser_quixbugs.add_argument(
        "--file",
        required=True,
        help="Name of Python program to patch",
        metavar="<file name>",
    )

    return parser.parse_args()


def check_env_vars(mode: str) -> Tuple[str, str]:
    """
    Loads and validates required environment variables.

    Returns:
        Tuple[str, str]: A tuple containing the GitHub token and OpenAI API key.

    Raises:
        ValueError: If either `GITHUB_TOKEN` or `OPENAI_API_KEY` is not set.
    """
    load_dotenv(override=False)

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if mode == "github" and not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set.")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    return GITHUB_TOKEN, OPENAI_API_KEY


def center_text(text: str, pad: str = "=") -> str:
    """
    Centers 'text' in the terminal, padding with 'pad' to fit terminal width.

    Args:
        text: The string to center.
    Returns:
        The padded string.
    """
    width = shutil.get_terminal_size().columns
    if not text:
        return pad * width
    centered = f" {text.strip()} "
    return centered.center(width, pad)


def print_paul_response(paul_response: dict) -> None:
    """
    Print PAUL's JSON output in a human-readable format.

    Args:
        json_data (dict): The JSON object from PAUL.
    """
    print(center_text("Better Call PAUL!", "="))
    print(f"\nPatch Title:\t{paul_response["pr_title"]}\n")
    print(center_text("", "-"))
    print(paul_response["pr_body"])
