from dotenv import load_dotenv
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_core.messages import BaseMessage
from typing import Tuple, Dict, List

import argparse
import json
import os
import re



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
        epilog="Example: python3 %(prog)s github --owner MikeRaphK --repo PAUL --issue 13 --model gpt-4o"
    )
    subparsers = parser.add_subparsers(dest="mode", required=True, title="modes", metavar="<mode>", description="Choose one of PAUL's available modes of operation")

    # GitHub Actions mode
    parser_github = subparsers.add_parser(
        'github',
        help='Run in GitHub Actions mode',
        usage="python3 %(prog)s --owner <repo owner username> --repo <repo name> --issue <issue number> --model <openai model>",
        description="Run PAUL in GitHub Actions mode.",
        epilog="Example: python3 %(prog)s --owner MikeRaphK --repo PAUL --issue 13 --model gpt-4o"
    )
    parser_github.add_argument('--owner', required=True, help='GitHub repository owner username', metavar='<username>')
    parser_github.add_argument('--repo', required=True, help='Repository name', metavar='<repo name>')
    parser_github.add_argument('--issue', required=True, type=int, help='Issue number (int)', metavar='<number>')
    parser_github.add_argument('--model', default="gpt-4o-mini", help='OpenAI model to use (optional, default: gpt-4o-mini)', metavar='<model>')

    # Local mode
    parser_local = subparsers.add_parser(
        'local',
        help='Run locally on a cloned repository',
        usage="python3 %(prog)s --path <repo path> --issue <issue desc> --output <output file path> --model <openai model>",
        description="Run PAUL locally on a cloned repository.",
        epilog="Example: python3 %(prog)s --path ./repos/my_repo_1 --issue ./issues/my_issue_13.txt --output ./patch.txt --model gpt-4o"
    )
    parser_local.add_argument('--path', required=True, help='Path to locally cloned repository', metavar='<repo path>')
    parser_local.add_argument('--issue', required=True, help='File containing issue description', metavar='<issue desc>')
    parser_local.add_argument('--output', required=True, help='Output file path containing patch and PR info', metavar='<out file>')
    parser_local.add_argument('--model', default="gpt-4o-mini", help='OpenAI model to use (optional, default: gpt-4o-mini)', metavar='<model>')

    # SWE-bench Lite mode
    parser_swebench_lite = subparsers.add_parser(
        'swebench',
        help='Run on SWE-bench Lite',
        usage="python3 %(prog)s --split <split> --id <instance id> --model <openai model>",
        description="Run PAUL on SWE-bench Lite benchmark.",
        epilog="Example: python3 %(prog)s --split test --id sympy__sympy-20590 --model gpt-4o"
    )
    parser_swebench_lite.add_argument('--split', required=True, help='The split of SWE-bench Lite', metavar='<split>')
    parser_swebench_lite.add_argument('--id', required=True, help='The instance id of a benchmark instance', metavar='<instance id>')
    parser_swebench_lite.add_argument('--model', default="gpt-4o-mini", help='OpenAI model to use (optional, default: gpt-4o-mini)', metavar='<model>')

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
    if mode == 'github' and not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set.")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    return GITHUB_TOKEN, OPENAI_API_KEY



def parse_paul_response(chat_history: List[BaseMessage], issue_number: int, token_logger: OpenAICallbackHandler) -> Dict[str, str]:
    """
    Parse JSON response from PAUL.

    Args:
        chat_history (List[BaseMessage]): The conversation history with the LLM, where the last message contains the JSON response.
        issue_number (int): The GitHub issue number for reference in the PR body.
        token_logger (OpenAICallbackHandler): The callback object containing LLM usage statistics.

    Returns:
        Dict[str, str]: The enriched JSON object containing PR details and additional metadata.
    """
    # Remove leading and trailing fences
    last_message_content = chat_history[-1].content.strip()
    if last_message_content.startswith("```"):
        last_message_content = re.sub(r"^```(?:json)?\s*", "", last_message_content)
        last_message_content = re.sub(r"\s*```$", "", last_message_content)
    paul_response = json.loads(last_message_content)

    # Add starting note
    paul_response["pr_body"] =  "> **Note:** This message was automatically generated by PAUL. Please review the proposed changes carefully before merging.\n\n" + paul_response["pr_body"] + "\n\n"

    # Add tool usage info
    paul_response["pr_body"] += f"Tools Used:\n"
    tool_str = ""
    for message in chat_history:
        tool_calls = getattr(message, "additional_kwargs", {}).get("tool_calls", [])
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_arguments = tool_call["function"]["arguments"]
            tool_str += f"- `{tool_name}` with arguments `{tool_arguments}`\n"
    if tool_str:
        paul_response["pr_body"] += f"{tool_str}\n"
    else:
        paul_response["pr_body"] += "None\n\n"

    # Add token usage info
    paul_response["pr_body"] += f"Tokens Used: {token_logger.total_tokens}\n"
    paul_response["pr_body"] += f"Successful Requests: {token_logger.successful_requests}\n"
    paul_response["pr_body"] += f"Total Cost (USD): {token_logger.total_cost:.6f}\n\n"

    # Add ending note
    paul_response["pr_body"] += f"Related to #{issue_number}\n"

    return paul_response
