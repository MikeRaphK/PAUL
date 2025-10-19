    // Fix the bug by using counts instead of arr for iteration
        for (int i = 0; i < counts.size(); i++) {
            sorted_arr.addAll(Collections.nCopies(counts.get(i), i));
        }

        return sorted_arr;
    }