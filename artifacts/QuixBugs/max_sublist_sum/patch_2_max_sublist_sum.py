def max_sublist_sum(arr):
    max_ending_here = 0
    max_so_far = 0

    for x in arr:
        max_ending_here = max_ending_here + x
        # Reset max_ending_here if it drops below 0
        if max_ending_here < 0:
            max_ending_here = 0
        max_so_far = max(max_so_far, max_ending_here)

    return max_so_far
