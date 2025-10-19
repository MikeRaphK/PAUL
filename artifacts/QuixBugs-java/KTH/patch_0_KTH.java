package java_programs;
import java.util.*;
/*

 */
public class KTH {
    public static Integer kth(ArrayList<Integer> arr, int k) {
        int pivot = arr.get(0);
        ArrayList<Integer> below = new ArrayList<>();
        ArrayList<Integer> above = new ArrayList<>();
        for (Integer x : arr) {
            if (x < pivot) {
                below.add(x);
            } else if (x > pivot) {
                above.add(x);
            }
        }

        // Calculate the size of the smaller part
        int num_less = below.size();
        int num_equal = arr.size() - below.size() - above.size(); // Count duplicates for correct indexing

        // Fixed condition to check for k-th index
        if (k < num_less) {
            return kth(below, k);
        } else if (k >= num_less + num_equal) {
            return kth(above, k - num_less - num_equal); // Adjust k to the new partition
        } else {
            return pivot; // pivot is the k-th largest element
        }
    }
}