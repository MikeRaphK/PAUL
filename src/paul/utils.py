from .models import PatchReport, PaulState
from dotenv import load_dotenv
from typing import Tuple

import argparse
import os
import shutil


def convert_to_abs(path):
    """
    Convert a user-provided path or list of paths to absolute paths.

    Args:
        path (str or list[str]): A file/directory path string or a list of paths.

    Returns:
        str or list[str]: The normalized absolute path(s).
    """

    def _resolve(p: str) -> str:
        return os.path.realpath(os.path.expanduser(p))

    if not path:
        return path
    elif isinstance(path, str):
        return _resolve(path)
    elif isinstance(path, list):
        return [_resolve(p) for p in path]
    else:
        raise TypeError("path must be a str or list[str]")


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
                --id: Benchmark instance ID (str)
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
        epilog="For more information on a specific mode, run: paul <mode> --help",
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
    parent_parser.add_argument(
        "--venv",
        default=None,
        help="Path to a virtual environment to use (optional)",
        metavar="<venv>",
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
        parents=[parent_parser],
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
        epilog="Example: paul local --path ./PAUL-tests/ --issue ./PAUL-tests/issues/is_anagram_issue.txt --tests ./PAUL-tests/tests/test_is_anagram.py",
        parents=[parent_parser],
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
        usage="paul swebench --path <repo path> --id <instance id>",
        description="Run PAUL on SWE-bench Lite benchmark.",
        epilog="Example: paul swebench --path ./sympy --id sympy__sympy-20590 --tests ./sympy/sympy/core/tests/test_basic.py::test_immutable",
        parents=[parent_parser],
    )
    parser_swebench_lite.add_argument(
        "--path",
        required=True,
        help="Path to locally cloned SWE-bench Lite repository",
        metavar="<repo path>",
    )
    parser_swebench_lite.add_argument(
        "--id",
        required=True,
        help="The instance id of a benchmark instance",
        metavar="<instance id>",
    )

    # QuixBugs mode
    parser_quixbugs = subparsers.add_parser(
        "quixbugs",
        help="Run on QuixBugs",
        usage="paul local --path <repo path> --file <file name>",
        description="Run PAUL on QuixBugs benchmark.",
        epilog="Example: paul quixbugs --path ./QuixBugs/ --file flatten.py --tests ./QuixBugs/python_testcases/test_flatten.py",
        parents=[parent_parser],
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


def finalize_report(output_state: PaulState, building_time: float, execution_time: float, issue_number: int = None) -> PatchReport:
    report = output_state["report"]

    # Add starting note
    report.body = "> **Note:** This message was automatically generated by PAUL. Please review the proposed changes carefully.\n\n" + report.body + "\n\n"

    # Add tool usage info
    report.body += f"Tools Used:\n"
    tool_str = ""
    for message in output_state["patcher_chat_history"]:
        tool_calls = getattr(message, "additional_kwargs", {}).get("tool_calls", [])
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_arguments = tool_call["function"]["arguments"]
            tool_str += f"- `{tool_name}` with arguments `{tool_arguments}`\n"
    if tool_str:
        report.body += f"{tool_str}\n"
    else:
        report.body += "None\n\n"

    # Add statistics
    patcher_tokens = output_state["patcher_tokens"]
    patcher_cost = output_state["patcher_cost"]
    failed_attempts = output_state["failed_attempts"]
    reporter_tokens = output_state["reporter_tokens"]
    reporter_cost = output_state["reporter_cost"]
    total_tokens = patcher_tokens + reporter_tokens
    total_cost = patcher_cost + reporter_cost
    report.body += f"Patcher:\n"
    report.body += f"\tTokens Used: {patcher_tokens}\n"
    report.body += f"\tTotal Cost (USD): {patcher_cost:.6f}\n"
    report.body += f"Verifier:\n"
    report.body += f"\tFailed Attempts: {failed_attempts}\n"
    report.body += f"Reporter:\n"
    report.body += f"\tTokens Used: {reporter_tokens}\n"
    report.body += f"\tTotal Cost (USD): {reporter_cost:.6f}\n"
    report.body += f"Total Tokens Used: {total_tokens}\n"
    report.body += f"Total Cost (USD): {total_cost:.6f}\n"
    report.body += f"Building Time: {building_time:.4f} seconds\n"
    report.body += f"Execution Time: {execution_time:.4f} seconds\n"

    # Add ending note
    if issue_number is not None:
        report.body += f"\nRelated to #{issue_number}\n"

    return report


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


def print_patch_report(report: PatchReport) -> None:
    """
    Print PAUL's JSON output in a human-readable format.

    Args:
        json_data (dict): The JSON object from PAUL.
    """
    print(center_text("Better Call PAUL!", "="))
    print(f"\nPatch Title:\t{report.title}\n")
    print(center_text("", "-"))
    print(report.body)
    print(center_text("", "="))
