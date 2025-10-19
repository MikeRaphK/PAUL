package java_programs;
import java.util.*;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author derricklin
 */
public class QUICKSORT {
    public static ArrayList<Integer> quicksort(ArrayList<Integer> arr) {
        if (arr.isEmpty()) {
            return new ArrayList<Integer>();
        }

        Integer pivot = arr.get(0);
        ArrayList<Integer> lesser = new ArrayList<Integer>();
        ArrayList<Integer> middle = new ArrayList<Integer>(); // for duplicates
        ArrayList<Integer> greater = new ArrayList<Integer>();
        
        for (Integer x : arr) {
            if (x < pivot) {
                lesser.add(x);
            } else if (x > pivot) {
                greater.add(x);
            } else {
                middle.add(x); // Handle duplicates here
            }
        }

        // Combine results to maintain order
        ArrayList<Integer> sorted = new ArrayList<>();
        sorted.addAll(quicksort(lesser));  // Sort lesser
        sorted.addAll(middle);              // Middle has the pivot and duplicates
        sorted.addAll(quicksort(greater));  // Sort greater
        return sorted;
    }
}