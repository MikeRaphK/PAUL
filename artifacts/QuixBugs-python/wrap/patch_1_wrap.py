def wrap(text, cols):
    lines = []
    while len(text) > cols:
        end = text.rfind(' ', 0, cols + 1)
        if end == -1:  # No space found
            end = cols  # Force split at columns
        line, text = text[:end].rstrip(), text[end:]  # Remove unnecessary space (if any) at the end
        lines.append(line)

    if text:  # Append any remaining text
        lines.append(text)

    return lines
