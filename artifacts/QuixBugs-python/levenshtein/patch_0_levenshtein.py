def levenshtein(source, target):
    if source == '' or target == '':
        return len(source) or len(target)

    elif source[0] == target[0]:
        return levenshtein(source[1:], target[1:])

    else:
        return 1 + min(
            levenshtein(source,     target[1:]),  # Cost of insertion
            levenshtein(source[1:], target[1:]),  # Cost of replacement
            levenshtein(source[1:], target)         # Cost of deletion
        )
