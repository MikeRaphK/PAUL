from .runners.github import run_github
from .runners.local import run_local
from .runners.swebench_lite import run_swebench_lite
from .runners.quixbugs import run_quixbugs
from .utils import parse_args, check_env_vars, convert_to_abs


def main():
    # Parse arguements and check environment variables
    args = parse_args()
    GITHUB_TOKEN, OPENAI_API_KEY = check_env_vars(args.mode)

    # Run PAUL based on the selected mode
    if args.mode == "github":
        run_github(
            args.owner,
            args.repo,
            args.issue,
            args.model,
            convert_to_abs(args.venv),
            GITHUB_TOKEN,
            OPENAI_API_KEY,
        )
    elif args.mode == "local":
        run_local(
            convert_to_abs(args.path),
            convert_to_abs(args.issue),
            convert_to_abs(args.tests),
            args.model,
            convert_to_abs(args.venv),
            OPENAI_API_KEY,
        )
    elif args.mode == "swebench":
        run_swebench_lite(
            convert_to_abs(args.path),
            args.split,
            args.id,
            convert_to_abs(args.tests),
            args.model,
            convert_to_abs(args.venv),
            OPENAI_API_KEY,
        )
    elif args.mode == "quixbugs":
        run_quixbugs(
            convert_to_abs(args.path),
            args.file,
            convert_to_abs(args.tests),
            args.model,
            convert_to_abs(args.venv),
            OPENAI_API_KEY,
        )
    else:
        print("Unknown mode selected.")
        exit(1)


if __name__ == "__main__":
    main()
