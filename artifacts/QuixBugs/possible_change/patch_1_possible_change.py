def possible_change(coins, total):
    if total == 0:
        return 1
    if total < 0 or not coins:
        return 0

    first, *rest = coins
    # Recursive call by including the first coin and then skipping it
    return possible_change(coins, total - first) + possible_change(rest, total)