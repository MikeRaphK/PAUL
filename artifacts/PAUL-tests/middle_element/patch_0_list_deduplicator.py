def deduplicate(items):
    """Remove duplicates but preserve original order."""
    seen = set()
    result = []
    for i in range(len(items)):
        if items[i] not in seen:
            seen.add(items[i])  # Corrected from seen.add(i) to seen.add(items[i]) to track the actual item
            result.append(items[i])
    return result
