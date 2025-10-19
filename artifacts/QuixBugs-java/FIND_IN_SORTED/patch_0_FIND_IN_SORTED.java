    public static int find_in_sorted(int[] arr, int x) {
        return binsearch(arr, x, 0, arr.length - 1); // Adjust to search in the correct range
    }