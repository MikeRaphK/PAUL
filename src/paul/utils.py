from dotenv import load_dotenv
from typing import Tuple

import argparse
import concurrent.futures
import os
import shutil
import time

def parse_args() -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    """
    Parses command-line arguments for PAUL's modes of operation.

    Returns:
        Tuple[argparse.ArgumentParser, argparse.Namespace]: A tuple containing:
            - The configured ArgumentParser instance.
            - The parsed arguments namespace.

        The contents of the parsed arguments depend on the selected mode:
            - For 'github': contains 'owner', 'repo', 'issue', 'model'
            - For 'local': contains 'path', 'issue', 'model'
            - For 'swebench': contains 'path', 'split', 'id', 'test', 'model'
            - For 'quixbugs': contains 'path', 'file', 'model'
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

    # QuixBugs mode
    parser_quixbugs = subparsers.add_parser(
        "quixbugs",
        help="Run on QuixBugs",
        usage="paul local --path <repo path> --file <file name> --model <openai model>",
        description="Run PAUL on QuixBugs benchmark.",
        epilog="Example: paul quixbugs --path ./local/QuixBugs/ --file flatten.py --model gpt-4o",
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
    parser_quixbugs.add_argument(
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

def call_with_timeout(func, args=(), kwargs=None, timeout=60, max_retries=2, retry_delay=2):
    """
    Calls a function with a timeout and auto-retries if it fails due to timeout.

    Args:
        func: The function to call.
        args: Positional arguments as tuple.
        kwargs: Keyword arguments as dict.
        timeout: Timeout per attempt, in seconds.
        max_retries: How many retries (total attempts = max_retries + 1).
        retry_delay: Seconds to wait between retries.

    Returns:
        The function's return value if successful.

    Raises:
        RuntimeError if all retries fail.
    """
    if kwargs is None:
        kwargs = {}
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(func, *args, **kwargs)
                return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print(f"Attempt {attempt+1}: timed out after {timeout} seconds.")
            last_exc = RuntimeError(f"Timeout after {timeout} seconds on attempt {attempt+1}")
            if attempt < max_retries:
                print(f"Retrying after {retry_delay} seconds...")
                time.sleep(retry_delay)
        except Exception as e:
            print(f"Attempt {attempt+1}: failed with exception: {e}")
            last_exc = e
            break  # Only retry on timeout
    raise last_exc