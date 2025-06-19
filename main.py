import argparse
from src.paul.runner_github import run_github
from src.paul.runner_local import run_local
from src.paul.runner_swebench_lite import run_swebench_lite
from src.paul.utils import check_env_vars

if __name__ == "__main__":
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
        usage="python3 %(prog)s --repo <repo path> --issue <issue desc> --model <openai model>",
        description="Run PAUL locally on a cloned repository.",
        epilog="Example: python3 %(prog)s --repo ./repos/my_repo_1 --issue ./issues/my_issue_13.txt --model gpt-4o"
    )
    parser_local.add_argument('--repo', required=True, help='Path to locally cloned repository', metavar='<repo path>')
    parser_local.add_argument('--issue', required=True, help='File containing issue description', metavar='<issue desc>')
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

    args = parser.parse_args()

    # Check environment variables
    GITHUB_TOKEN, OPENAI_API_KEY = check_env_vars()

    if args.mode == 'github':
        run_github(args.owner, args.repo, args.issue, GITHUB_TOKEN, OPENAI_API_KEY, args.model)
    elif args.mode == 'local':
        run_local(args.repo, args.issue, GITHUB_TOKEN, OPENAI_API_KEY, args.model)
    elif args.mode == 'swebench':
        run_swebench_lite(args.split, args.id, GITHUB_TOKEN, OPENAI_API_KEY, args.model)
    else:
        parser.error("Unknown mode selected.")


