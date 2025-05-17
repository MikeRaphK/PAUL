# PAUL – Patch Automation Using LLMs

**PAUL** (Patch Automation Using LLMs) is a developer tool that leverages Large Language Models to automatically address GitHub issues by reading, understanding, and patching codebases. With a single command, PAUL clones a GitHub repository, analyzes a given issue, and generates a targeted code fix, complete with a commit message and pull request.


## Setup

1. Clone the repository:
```bash
git clone https://github.com/MikeRaphK/PAUL.git
cd PAUL
```

2. Create a `.env` file and add your credentials:
```bash
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py <GitHub Repository URL> <Issue Number>
```

Example:
```bash
python main.py https://github.com/yourusername/myproject 17
```


## License
MIT License