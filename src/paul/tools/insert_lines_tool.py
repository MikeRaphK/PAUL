from langchain_core.tools import tool

@tool
def insert_lines_tool(
    file_path: str,
    content: str,
    line_number: int | None = None,
    operation: str = "replace_all"
) -> str:
    """
    Write or modify a text file at a specific location.
    
    Args:
        file_path: Path to the file to write/modify
        content: The content to write (can be multi-line)
        line_number: Target line number (1-based) for insert/replace operations. Required for operations other than 'replace_all'
        operation: Type of write operation. Options:
            - "replace_all": Replace entire file with content (default)
            - "insert_before": Insert content before the specified line_number
            - "insert_after": Insert content after the specified line_number
            - "replace_line": Replace the single line at line_number with content
            - "replace_lines": Replace from line_number to line_number + (number of content lines - 1)
    
    Returns:
        Success message with confirmation of changes, or error message starting with "ERROR:".
        
    Examples:
        - write_file_lines("new.py", "print('hello')") - create/overwrite file
        - write_file_lines("app.py", "import sys", 1, "insert_before") - insert at top
        - write_file_lines("app.py", "    return result", 45, "replace_line") - replace line 45
        - write_file_lines("app.py", "# TODO\\n# FIXME", 10, "insert_after") - insert multiple lines
    """
    
    VALID_OPERATIONS = {"replace_all", "insert_before", "insert_after", "replace_line", "replace_lines"}
    
    if not file_path:
        return "ERROR: file_path is required"
    
    if content is None:
        return "ERROR: content is required"
    
    if operation not in VALID_OPERATIONS:
        return f"ERROR: Invalid operation '{operation}'. Must be one of: {', '.join(VALID_OPERATIONS)}"
    
    # Validate line_number requirement
    if operation != "replace_all" and line_number is None:
        return f"ERROR: line_number is required for operation '{operation}'"
    
    if line_number is not None and line_number < 1:
        return f"ERROR: line_number must be >= 1 (got {line_number})"
    
    try:
        # Split content into lines (preserve structure)
        content_lines = content.split('\n')
        
        # Handle replace_all - simple case
        if operation == "replace_all":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"SUCCESS: Wrote {len(content_lines)} lines to '{file_path}' (entire file replaced)"
        
        # For other operations, read existing file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()
        except FileNotFoundError:
            return f"ERROR: File not found: {file_path} (use operation='replace_all' to create new file)"
        
        total_lines = len(existing_lines)
        
        # Validate line_number against file length
        if line_number > total_lines:
            if operation in {"insert_after", "insert_before"}:
                # Allow inserting after last line
                if line_number == total_lines + 1 and operation == "insert_after":
                    pass  # This is okay
                else:
                    return f"ERROR: line_number {line_number} exceeds file length ({total_lines} lines)"
            else:
                return f"ERROR: line_number {line_number} exceeds file length ({total_lines} lines)"
        
        # Ensure existing lines end with newline for proper insertion
        existing_lines = [line if line.endswith('\n') else line + '\n' for line in existing_lines]
        
        # Prepare content lines with newlines
        content_lines_with_newline = [line + '\n' for line in content_lines]
        
        # Perform the operation (convert to 0-based indexing)
        idx = line_number - 1
        
        if operation == "insert_before":
            new_lines = existing_lines[:idx] + content_lines_with_newline + existing_lines[idx:]
            action_desc = f"Inserted {len(content_lines)} line(s) before line {line_number}"
            
        elif operation == "insert_after":
            new_lines = existing_lines[:idx + 1] + content_lines_with_newline + existing_lines[idx + 1:]
            action_desc = f"Inserted {len(content_lines)} line(s) after line {line_number}"
            
        elif operation == "replace_line":
            new_lines = existing_lines[:idx] + content_lines_with_newline + existing_lines[idx + 1:]
            action_desc = f"Replaced line {line_number} with {len(content_lines)} line(s)"
            
        elif operation == "replace_lines":
            num_content_lines = len(content_lines)
            end_idx = idx + num_content_lines
            if end_idx > total_lines:
                return f"ERROR: replace_lines would extend beyond file end (trying to replace lines {line_number}-{line_number + num_content_lines - 1}, but file only has {total_lines} lines)"
            new_lines = existing_lines[:idx] + content_lines_with_newline + existing_lines[end_idx:]
            action_desc = f"Replaced lines {line_number}-{line_number + num_content_lines - 1}"
        
        # Write the modified content
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        
        new_total = len(new_lines)
        return f"SUCCESS: {action_desc} in '{file_path}'. File now has {new_total} lines (was {total_lines})."
        
    except PermissionError:
        return f"ERROR: Permission denied: {file_path}"
    except IsADirectoryError:
        return f"ERROR: Path is a directory, not a file: {file_path}"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {str(e)}"