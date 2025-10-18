from langchain_core.tools import tool

def read_numbered_tool(
    file_path: str,
    start_line: int = 1,
    end_line: int | None = None
) -> str:
    """
    Read a text file and return its contents with line numbers.
    
    Args:
        file_path: Path to the file to read
        start_line: First line to read (1-based, inclusive). Default: 1
        end_line: Last line to read (1-based, inclusive). Default: read to end of file
    
    Returns:
        File contents with line numbers in format "line_number: content",
        or an error message starting with "ERROR:".
        
    Examples:
        - read_file_lines("app.py") - reads entire file
        - read_file_lines("app.py", 50, 100) - reads lines 50-100
        - read_file_lines("app.py", 200) - reads from line 200 to end
    """

    if not file_path:
        return "ERROR: No file_path provided"

    try:
        # Open file and get all lines
        with open(file_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        total_lines = len(all_lines)
        
        # Empty files check
        if total_lines == 0:
            return f"File '{file_path}' is empty (0 lines)"
        
        # Bad line range checks
        if start_line < 1:
            return f"ERROR: start_line must be >= 1 (got {start_line})"
        if start_line > total_lines:
            return f"ERROR: start_line {start_line} exceeds file length ({total_lines} lines)"
        
        # Determine end_line
        if end_line is None:
            end_line = total_lines
        else:
            if end_line < start_line:
                return f"ERROR: end_line ({end_line}) must be >= start_line ({start_line})"
            end_line = min(end_line, total_lines)

        # Extract lines (0-based indexing for Python lists)
        selected_lines = all_lines[start_line - 1 : end_line]
        numbered_lines = [
            f"{line_num}: {line.rstrip('\r\n')}"
            for line_num, line in enumerate(selected_lines, start=start_line)
        ]
        result = "\n".join(numbered_lines)

        # Add footer with context
        if start_line == 1 and end_line == total_lines:
            result += f"\n\n[Total: {total_lines} lines]"
        else:
            result += f"\n\n[Showing lines {start_line}-{end_line} of {total_lines} total]"
        
        return result
        
    except FileNotFoundError:
        return f"ERROR: File not found: {file_path}"
    except IsADirectoryError:
        return f"ERROR: Path is a directory, not a file: {file_path}"
    except PermissionError:
        return f"ERROR: Permission denied: {file_path}"
    except UnicodeDecodeError:
        return f"ERROR: Cannot read file (not a text file or encoding issue): {file_path}"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {str(e)}"
    