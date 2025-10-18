def bitcount(n):
    count = 0
    # Handle the case where n is 0
    if n == 0:
        return 0
    while n:
        n ^= n - 1
        count += 1
    return count


"""
Bitcount
bitcount


Input:
    n: a nonnegative int

Output:
    The number of 1-bits in the binary encoding of n

Examples:
    >>> bitcount(127)
    7
    >>> bitcount(128)
    1
"""