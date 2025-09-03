# PAUL: Patch Automation Using LLMs

**PAUL** (Patch Automation Using LLMs) is an open-source LLM-powered automation agent used for Automated Program Repair (APR). Supports a variety of modes including local repair, GitHub workflow automation, and evaluation on QuixBugs and SWE-bench Lite benchmarks.


## Dependencies
- **Python 3.12 or newer**
- [Docker](https://docs.docker.com/engine/install/) **or** [Poetry ≥2.0.0](https://python-poetry.org/docs/)  for setting up
- [OpenAI API Key](https://platform.openai.com/api-keys)
- [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens): Only for GitHub mode, must allow opening and creating pull requests


## Installation
### Using Docker
Pull the Docker image from GitHub Container Registry with dependencies pre-installed:
```bash
docker pull ghcr.io/mikeraphk/paul:latest
docker run --rm -it -e OPENAI_API_KEY=... ghcr.io/mikeraphk/paul:latest bash
``` 

### Using Poetry
Clone the repository, create a virtual environment and install dependencies using Poetry:
```bash
git clone https://github.com/MikeRaphK/PAUL.git
cd PAUL
python3.12 -m venv venv
source venv/bin/activate
poetry install
export OPENAI_API_KEY=...
```

### GitHub Actions Integration
Add the workflow found in [`.github/workflows/run-paul.yml`](.github/workflows/run-paul.yml) to your public repository. In addition to your **OpenAI API key**, you will also need a **GitHub Personal Access Token** with permissions to open and create PRs. Store both keys securely using [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) as `OPENAI_API_KEY` and `PAUL_GITHUB_TOKEN` respectively.


## Usage
Once installed, you can access the full CLI help at any time:
```bash
paul --help
```
This will show all available modes and options.

For more details and all available options for any subcommand, use:
```bash
paul <mode> --help
```

### Local mode
Point to a local repo and an issue description, and **PAUL** will attempt to produce a working patch locally. 

You can use the provided [PAUL-tests](https://github.com/MikeRaphK/PAUL-tests) repository, which contains example unit tests. These tests are continuously run using the [`.github/workflows/run-tests.yml`](.github/workflows/run-tests.yml) GitHub Actions workflow to ensure reliability and correctness across updates.

Example:
```bash
git clone https://github.com/MikeRaphK/PAUL-tests.git
paul local --path ./PAUL-tests/ --issue ./PAUL-tests/issues/is_anagram_issue.txt --tests ./PAUL-tests/tests/test_is_anagram.py
```

### GitHub mode
After adding the [run-paul.yml]((.github/workflows/run-paul.yml)) to your public GitHub repository, open or edit an issue with the `PAUL` label. **PAUL** will attempt to produce a working patch and create a pull request with the patch implementation.
> **To enable automatic test verification**, append a fenced code block at the end of the issue description using the `tests` language label. Each line should contain a test file or specific test function to run. Example:
> ````
> ```tests
> tests/test_file.py
> tests/test_file.py::test_important_case
> ```
> ````
> If no such block is provided, PAUL will skip the verification step.


## Benchmarks
**PAUL**’s effectiveness and repair rate can also be evaluated on established benchmarks like QuixBugs and SWE-bench Lite.
### QuixBugs
**PAUL** passes all QuixBugs Python test cases, reliably fixing classic programming errors out of the box. Artifacts produced during QuixBugs runs are stored in the [artifacts](artifacts_quixbugs) folder.

Example:
```bash
git clone https://github.com/jkoppel/QuixBugs.git
paul quixbugs --path ./QuixBugs/ --file flatten.py --tests ./QuixBugs/python_testcases/test_flatten.py
```

### SWE-bench Lite
**PAUL** is able to solve a subset of SWE-bench Lite tests, demonstrating its practical effectiveness on real-world Python bugs.

Example:
```bash
paul swebench --path ./sympy --id sympy__sympy-20590 --venv ./sympy/sympy_venv --tests ./sympy/sympy/core/tests/test_basic.py::test_immutable
```

## PAUL workflow
```mermaid
flowchart LR
    %% Styles
    classDef patcher fill:#1f4e2e,stroke:#8fd19e,stroke-width:2px,color:#fff;
    classDef verifier fill:#7f1d1d,stroke:#f87171,stroke-width:2px,color:#fff;
    classDef reporter fill:#4c1d95,stroke:#c084fc,stroke-width:2px,color:#fff;
    classDef tool fill:#1f2a40,stroke:#9fc3ff,stroke-width:2px,color:#fff;
    classDef optional stroke-dasharray:6 3;
    

    %% Nodes
    GitRepo[Git Repository]
    Issue[Issue]
    Model["Model Name <br/> (Optional)"]:::optional
    Patcher((Patcher)):::patcher
    Toolkit("Toolkit <br/> (ls, ReadFile, WriteFile)"):::tool
    Verifier[Verifier]:::verifier
    Venv["Venv <br/> (Optional)"]:::optional
    Tests["Tests <br/> (Optional)"]:::optional
    Reporter((Reporter)):::reporter

    %% To Patcher
    GitRepo --> Patcher;
    Issue --> Patcher;
    Model --> Patcher
    
    %% From Patcher
    Patcher --->|Need tool| Toolkit;
    linkStyle 3 stroke:#22c55e,stroke-width:2px;

    %% From Toolkit
    Toolkit -.->|Read tool used| Patcher;
    Toolkit -.->|Write tool used| Verifier;
    linkStyle 4 stroke:#3b82f6,stroke-width:2px;
    linkStyle 5 stroke:#3b82f6,stroke-width:2px;

    %% To Verifier
    Tests --> Verifier
    Venv --> Verifier;
    
    %% From Verifier
    Verifier -.->|Fail| Patcher;
    Verifier -.->|Pass| Reporter;
    linkStyle 8 stroke:#ef4444,stroke-width:2px;
    linkStyle 9 stroke:#ef4444,stroke-width:2px;
```


## License
MIT License. See [LICENSE](LICENSE) for details.


## Credits
PAUL was created by Michael-Raphael Kostagiannis as part of a BSc thesis in the Department of Informatics and Telecommunications at the National and Kapodistrian University of Athens.

Special thanks to my supervisor, [Thanassis Avgerinos](https://cgi.di.uoa.gr/~thanassis/), and [kaizen](https://github.com/ethan42/kaizen).

