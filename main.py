import argparse
from src.paul.runner import run_paul
from src.paul.utils import check_env_vars

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Ask PAUL to fix a GitHub issue in a repository.",
        epilog="Example: python main.py --owner MikeRaphK --repo PAUL --issue 13",
        usage="%(prog)s --owner <repo owner username> --repo <repo name> --issue <issue number>"
    )
    parser.add_argument('--owner', required=True, help='GitHub repository owner username', metavar='USERNAME')
    parser.add_argument('--repo', required=True, help='Repository name', metavar='REPO NAME')
    parser.add_argument('--issue', required=True, type=int, help='Issue number (int)', metavar='NUMBER')
    args = parser.parse_args()

    # Check environment variables
    GITHUB_TOKEN, OPENAI_API_KEY = check_env_vars()

    # Run PAUL with the provided arguments
    run_paul(args.owner, args.repo, args.issue, GITHUB_TOKEN, OPENAI_API_KEY)