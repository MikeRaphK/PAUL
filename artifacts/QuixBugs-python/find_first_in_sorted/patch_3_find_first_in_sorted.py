def find_first_in_sorted(arr, x):
    lo = 0
    hi = len(arr) - 1  # Maintain hi as the last index of the array

    while lo <= hi:  # Maintain the condition to include the last element
        mid = (lo + hi) // 2

        if arr[mid] == x:
            # Check if it's the first occurrence of the target value
            if mid == 0 or arr[mid - 1] != x:
                return mid
            hi = mid - 1  # Move to search in the left half

        elif x < arr[mid]:  # When x is less, search the left side
            hi = mid - 1

        else:
            lo = mid + 1  # Move to the right side

    return -1


"""
Fancy Binary Search
fancy-binsearch


Input:
    arr: A sorted list of ints
    x: A value to find

Output:
    The lowest index i such that arr[i] == x, or -1 if x not in arr

Example:
    >>> find_first_in_sorted([3, 4, 5, 5, 5, 5, 6], 5)
    2
"""