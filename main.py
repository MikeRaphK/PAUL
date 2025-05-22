import sys
from src.paul.runner import run_paul

if __name__ == "__main__":
    # Read arguments
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <GitHub URL> <Issue Number>")
        sys.exit(1)
    repo_url = sys.argv[1]
    issue_number = int(sys.argv[2])

    # Ask PAUL to fix the issue
    print("Waking PAUL up...\n")
    run_paul(repo_url, issue_number)