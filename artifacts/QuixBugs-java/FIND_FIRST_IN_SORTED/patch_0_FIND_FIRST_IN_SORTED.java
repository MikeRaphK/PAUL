    public static int find_first_in_sorted(int[] arr, int x) {
        int lo = 0;
        int hi = arr.length - 1; // Change hi to arr.length - 1 instead of arr.length

        while (lo <= hi) {
            int mid = (lo + hi) / 2; // check if this is floor division

            if (x == arr[mid] && (mid == 0 || x != arr[mid-1])) {
                return mid;
            } else if (x < arr[mid]) { // Change <= to < for correct upper search bound
                hi = mid - 1; // Change to mid - 1 for correct search
            } else {
                lo = mid + 1;
            }
        }

        return -1;
    }