def sieve(max):
    primes = []
    for n in range(2, max + 1):
        # Check if n is not divisible by any of the previously found primes
        if all(n % p != 0 for p in primes):
            primes.append(n)  # Append n if it's a prime
    return primes

"""
Sieve of Eratosthenes
prime-sieve

Input:
    max: A positive int representing an upper bound.

Output:
    A list containing all primes up to and including max
"""