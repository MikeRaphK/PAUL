package java_programs;
import java.util.*;

/**
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author derricklin
 */
public class FIND_FIRST_IN_SORTED {

    public static int find_first_in_sorted(int[] arr, int x) {
        int lo = 0;
        int hi = arr.length; // Keep hi as arr.length for range to accommodate last index

        while (lo < hi) { // Continue to search while lo < hi
            int mid = (lo + hi) / 2;

            if (x == arr[mid]) {
                // Check if it's the first occurrence
                if (mid == 0 || arr[mid - 1] != x) {
                    return mid;
                } else {
                    hi = mid; // Keep searching in the left half
                }
            } else if (x < arr[mid]) {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        }

        return -1;
    }

}