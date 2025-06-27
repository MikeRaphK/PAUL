from src.paul.runners.github import run_github
from src.paul.runners.local import run_local
from src.paul.runners.swebench_lite import run_swebench_lite
from src.paul.utils import parse_args, check_env_vars

if __name__ == "__main__":
    # Parse arguements and check environment variables
    parser, args = parse_args()
    GITHUB_TOKEN, OPENAI_API_KEY = check_env_vars(args.mode)

    # Run PAUL based on the selected mode
    if args.mode == 'github':
        run_github(args.owner, args.repo, args.issue, args.model, GITHUB_TOKEN, OPENAI_API_KEY)
    elif args.mode == 'local':
        run_local(args.path, args.issue, args.output, args.model, OPENAI_API_KEY)
    elif args.mode == 'swebench':
        run_swebench_lite(args.path, args.split, args.id, args.test, args.output, args.model, OPENAI_API_KEY)
    else:
        parser.error("Unknown mode selected.")
