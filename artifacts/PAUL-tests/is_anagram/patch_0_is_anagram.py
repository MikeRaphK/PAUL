def is_anagram(s1, s2):
    """Check if two strings are anagrams, ignoring spaces, case, and non-alphabetic characters."""
    # Normalize the strings: remove spaces, convert to lowercase,
    # and filter out non-alphabetic characters
    normalized_s1 = ''.join(filter(str.isalpha, s1.lower()))
    normalized_s2 = ''.join(filter(str.isalpha, s2.lower()))
    return sorted(normalized_s1) == sorted(normalized_s2)
