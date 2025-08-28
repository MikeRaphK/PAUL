from langchain_core.tools import tool

@tool
def read_numbered_tool(path: str) -> str:
    """
    Return the contents of a text file with 1-based line numbers.
    Example line format: '     42: print(\"hello\")'

    Args:
        path: Path to the target file.

    Returns:
        A string with numbered lines, or an error message prefixed by 'ERROR:'.
    """
    print(f"\nPAUL is using 'read_numbered_tool' on: {path}\n")

    if not path:
        return "ERROR: No path provided"

    try:
        with open(path, "r") as f:
            lines = f.readlines()

        out_lines = []
        for i, line in enumerate(lines, start=1):
            out_lines.append(f"{i:6d}:{line.rstrip('\r\n')}")
        return "\n".join(out_lines)

    except FileNotFoundError:
        return f"ERROR: File not found: {path}"
    except Exception as e:
        return f"ERROR: {e}"
    