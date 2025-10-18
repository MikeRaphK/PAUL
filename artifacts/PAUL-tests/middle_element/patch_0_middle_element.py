def middle_element(lst):
    """Return the middle element of a non-empty list.
    If the list has even length, return the lower of the two middle elements.
    """
    idx = len(lst) // 2
    if len(lst) % 2 == 0:
        return min(lst[idx - 1], lst[idx])  # return lower of the two middles
    return lst[idx]