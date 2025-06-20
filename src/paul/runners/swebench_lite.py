def run(split, id, model: str, GITHUB_TOKEN: str, OPENAI_API_KEY: str) -> None:
    print("Running PAUL in SWE-bench Lite mode...")
    print(f"SWE-bench split: {split}")
    print(f"Instance id: {id}")
    print(f"OpenAI model: {model}")