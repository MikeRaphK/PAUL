    public static int binsearch(int[] arr, int x, int start, int end) {
        if (start > end) { // Correct condition to check for the valid range
            return -1;
        }
        int mid = start + (end - start) / 2; // check this is floor division
        if (x < arr[mid]) {
            return binsearch(arr, x, start, mid - 1); // Exclusive of mid element while searching left
        } else if (x > arr[mid]) {
            return binsearch(arr, x, mid + 1, end); // Exclusive of mid element while searching right
        } else {
            return mid;
        }
    }