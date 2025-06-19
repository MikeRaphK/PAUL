def run_local(repo: str, issue: str, GITHUB_TOKEN: str, OPENAI_API_KEY: str, model: str) -> None:
    print("Running PAUL in local mode...")
    print(f"Repository path: {repo}")
    print(f"Issue description file: {issue}")
    print(f"OpenAI model: {model}")