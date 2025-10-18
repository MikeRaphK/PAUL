def reverse_string(s):
    """Return the reverse of the input string s."""
    if s is None:
        return None  # Fix: Handle None input
    if s:
        return s[::-1]
    return ''  # Handle empty string explicitly#  Added handling for None type input and explicitly returning '' for empty strings.