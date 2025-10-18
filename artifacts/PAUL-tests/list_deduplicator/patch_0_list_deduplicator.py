def is_anagram(s1, s2):
    """Check if two strings are anagrams, ignoring spaces and case."""
    s1 = s1.replace(' ', '').lower()  # Remove spaces and convert to lowercase
    s2 = s2.replace(' ', '').lower()  # Remove spaces and convert to lowercase
    return sorted(s1) == sorted(s2)