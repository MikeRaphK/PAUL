    factors = []
    # Fix: Store full factors list instead of returning immediately.
    while n > 1:
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                factors.append(i)
                n //= i
                break
        else:
            factors.append(n)
            break
    return factors
