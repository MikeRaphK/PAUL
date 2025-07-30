from .runners.github import run_github
from .runners.local import run_local
from .runners.swebench_lite import run_swebench_lite
from .runners.quixbugs import run_quixbugs
from .utils import parse_args, check_env_vars

def main():
    # Parse arguements and check environment variables
    args = parse_args()
    GITHUB_TOKEN, OPENAI_API_KEY = check_env_vars(args.mode)

    # Run PAUL based on the selected mode
    if args.mode == "github":
        run_github(
            args.owner, args.repo, args.issue, args.model, GITHUB_TOKEN, OPENAI_API_KEY
        )
    elif args.mode == "local":
        run_local(args.path, args.issue, args.tests, args.model, OPENAI_API_KEY)
    elif args.mode == "swebench":
        run_swebench_lite(
            args.path, args.split, args.id, args.test, args.model, OPENAI_API_KEY
        )
    elif args.mode == "quixbugs":
        run_quixbugs(args.path, args.file, args.model, OPENAI_API_KEY)
    else:
        print("Unknown mode selected.")
        exit(1)

if __name__ == "__main__":
    main()