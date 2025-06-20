def run(path: str, issue: str, model: str, GITHUB_TOKEN: str, OPENAI_API_KEY: str) -> None:
    print("Running PAUL in local mode...")
    print(f"Repository path: {path}")
    print(f"Issue description file: {issue}")
    print(f"OpenAI model: {model}")