    public static ArrayList<Integer> sieve(Integer max) {
        ArrayList<Integer> primes = new ArrayList<Integer>();
        for (int n=2; n<max+1; n++) {
            // Check if all previous primes do not divide n
            if (all(list_comp(n, primes))) {
                primes.add(n);
            }
        }
        return primes;
    }