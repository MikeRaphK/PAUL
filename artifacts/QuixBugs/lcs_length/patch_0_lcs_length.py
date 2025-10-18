def lcs_length(s, t):
    from collections import Counter

    # Create a 2D list to store lengths of longest common suffixes
    dp = [[0] * (len(t) + 1) for _ in range(len(s) + 1)]
    max_length = 0  # Variable to store the length of longest common substring

    for i in range(1, len(s) + 1):
        for j in range(1, len(t) + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                max_length = max(max_length, dp[i][j])

    return max_length
