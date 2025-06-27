from langchain_core.tools import tool
from subprocess import run


@tool
def pytest_tool(target: str = "", test_function: str = "") -> dict:
    """
    Runs pytest in the current environment.
    - If called with no arguments, runs all tests (pytest).
    - If target is a directory, runs tests in that directory.
    - If target is a file, runs tests in that file.
    - If target file and test_function are both specified, runs only that test function found in target file.
    Args:
        target: The file or directory to test (optional).
        test_function: The test function to run inside the target file (optional, file only).
    Returns:
        A dict with:
            - command: The pytest command run
            - stdout: Standard output of the command
            - stderr: Standard error output
            - returncode: Exit code from pytest
    """
    # Build command
    command = ["pytest"]
    if target:
        if test_function:
            command.append(f"{target}::{test_function}")
        else:
            command.append(target)
    command.append("-vvvv")

    # Try to run pytest
    try:
        result = run(command, capture_output=True, text=True, check=False)
        return f"Command: {' '.join(command)}\n\nOutput:\n{result.stdout}\nReturn code: {result.returncode}"
    except Exception as e:
        return f"Error running pytest: {e}"
