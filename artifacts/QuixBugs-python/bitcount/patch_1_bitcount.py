def bitcount(n):
    count = 0
    # Handle the case where n is 0
    if n == 0:
        return 0
    while n > 0:
        count += n & 1  # Increment count if the last bit is 1
        n >>= 1  # Right shift n to process the next bit
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