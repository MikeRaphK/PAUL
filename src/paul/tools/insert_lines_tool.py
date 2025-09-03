from langchain_core.tools import tool

@tool
def insert_lines_tool(path: str, index: int, content: str) -> str:
    """
    Insert one or more lines into a text file BEFORE the given 1-based line index.
    - Uses 1-based indexing (like editors/tracebacks).
    - If index > number of lines, appends at EOF.

    Args:
        path: Path to the target file.
        index: 1-based line number to insert BEFORE.
        content: The text to insert. Can contain multiple lines.

    Returns:
        A status string with details, or an error message prefixed by 'ERROR:'.
    """
    print(f"PAUL is using 'insert_lines_tool' on: {path} at index: {index}\n")

    if not path:
        return "ERROR: No path provided"
    if not isinstance(index, int):
        return "ERROR: index must be an integer (1-based)"
    if index < 1:
        return f"ERROR: index must be >= 1 (got {index})"

    try:
        with open(path, "r") as f:
            lines = f.readlines()

        # If index is beyond EOF, append
        if index > len(lines):
            lines.extend([content if content.endswith("\n") else content + "\n"])
        else:
            insert_lines = content.splitlines(keepends=True)
            if not insert_lines[-1].endswith("\n"):
                insert_lines[-1] += "\n"
            lines[index - 1:index - 1] = insert_lines

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return f"OK: Inserted content at index {index} in '{path}'"

    except FileNotFoundError:
        return f"ERROR: File not found: {path}"
    except Exception as e:
        return f"ERROR: {e}"
