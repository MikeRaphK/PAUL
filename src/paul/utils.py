from dotenv import load_dotenv
from typing import Tuple

import argparse
import os
import shutil


def parse_args() -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    """
    Parses command-line arguments for PAUL's modes of operation.

    Returns:
        Tuple[argparse.ArgumentParser, argparse.Namespace]: A tuple containing:
            - The configured ArgumentParser instance.
            - The parsed arguments namespace.

        The contents of the parsed arguments depend on the selected mode:
            - For 'github': contains 'owner', 'repo', 'issue', 'model'
            - For 'local': contains 'repo', 'issue', 'model'
            - For 'swebench': contains 'split', 'id', 'model'
    """

    # Main parser
    parser = argparse.ArgumentParser(
        description="PAUL - Patch Automation Using LLMs: LLM agent that automatically detects and patches GitHub issues.",
        epilog="Example: paul local --path ./local/PAUL-tests/ --issue ./local/PAUL-tests/issues/is_anagram_issue.txt --model gpt-4o",
    )
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
        help="Run in GitHub Actions mode",
        usage="paul github --owner <repo owner username> --repo <repo name> --issue <issue number> --model <openai model>",
        description="Run PAUL in GitHub Actions mode.",
        epilog="Example: paul github --owner MikeRaphK --repo PAUL --issue 13 --model gpt-4o",
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
    parser_github.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (optional, default: gpt-4o-mini)",
        metavar="<model>",
    )

    # Local mode
    parser_local = subparsers.add_parser(
        "local",
        help="Run locally on a cloned repository",
        usage="paul local --path <repo path> --issue <issue desc> --model <openai model>",
        description="Run PAUL locally on a cloned repository.",
        epilog="Example: paul local --path PAUL-tests/ --issue PAUL-tests/issues/is_anagram_issue.txt --model gpt-4o",
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
    parser_local.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (optional, default: gpt-4o-mini)",
        metavar="<model>",
    )

    # SWE-bench Lite mode
    parser_swebench_lite = subparsers.add_parser(
        "swebench",
        help="Run on SWE-bench Lite",
        usage="paul swebench --path <repo path> --split <split> --id <instance id> --test <test> --model <openai model>",
        description="Run PAUL on SWE-bench Lite benchmark.",
        epilog="Example: paul swebench --path ./local/sympy --split test --id sympy__sympy-20590 --test sympy/core/tests/test_basic.py::test_immutable --model gpt-4o",
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
    parser_swebench_lite.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (optional, default: gpt-4o-mini)",
        metavar="<model>",
    )

    return parser, parser.parse_args()


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
