def lis(arr):
    ends = {}
    longest = 0

    for i, val in enumerate(arr):

        # Find all prefix lengths where the last elements are less than the current value
        prefix_lengths = [j for j in range(1, longest + 1) if arr[ends[j]] < val]

        # Determine the length of the longest increasing subsequence up to this point
        length = max(prefix_lengths) if prefix_lengths else 0

        # Update ends for the current value if we can extend the longest subsequence
        if length == longest or (length + 1 not in ends) or val < arr[ends[length + 1]]:
            ends[length + 1] = i
        longest = max(longest, length + 1)  # update the longest subsequence length

    return longest


"""
Longest Increasing Subsequence
longest-increasing-subsequence


Input:
    arr: A sequence of ints

Precondition:
    The ints in arr are unique

Output:
    The length of the longest monotonically increasing subsequence of arr

Example:
    >>> lis([4, 1, 5, 3, 7, 6, 2])
    3
"""