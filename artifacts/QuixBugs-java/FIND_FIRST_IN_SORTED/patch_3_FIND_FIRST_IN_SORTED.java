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
        int hi = arr.length; // Change hi back to arr.length so that the condition is valid

        while (lo < hi) { // Change condition to < instead of <=
            int mid = (lo + hi) / 2;

            if (x == arr[mid] && (mid == 0 || x != arr[mid-1])) {
                return mid;
            } else if (x < arr[mid]) {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        }

        return -1;
    }

}