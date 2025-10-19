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
        ArrayList<Integer> greater = new ArrayList<Integer>();

        for (Integer x : arr.subList(1, arr.size())) {
            if (x < pivot) {
                lesser.add(x);
            } else if (x > pivot) {
                greater.add(x);
            }
        }
        ArrayList<Integer> middle = new ArrayList<Integer>();
        middle.add(pivot);
        lesser = quicksort(lesser);
        greater = quicksort(greater);
        middle.addAll(greater);
        // Correcting the return statement to return the sorted array in the proper order
        return new ArrayList<>(lesser.size() + middle.size() + greater.size()).addAll(lesser); 
        middle.addAll(greater);
        return middle;
    }
}