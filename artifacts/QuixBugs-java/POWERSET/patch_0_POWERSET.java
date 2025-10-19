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
public class POWERSET {
    public static ArrayList<ArrayList> powerset(ArrayList arr) {
        // Base case: if the array is empty, return a list containing the empty set
        if (arr.isEmpty()) {
            ArrayList<ArrayList> empty_set = new ArrayList<ArrayList>();
            empty_set.add(new ArrayList());
            return empty_set;
        }

        Object first = arr.get(0);
        // Create a new list for the rest of the elements without modifying the original
        ArrayList rest = new ArrayList(arr.subList(1, arr.size()));
        ArrayList<ArrayList> rest_subsets = powerset(rest);

        // Prepare output list to hold all subsets
        ArrayList<ArrayList> output = new ArrayList<ArrayList>();

        // Add all subsets without the first element
        output.addAll(rest_subsets);

        // Create new subsets that include the first element
        for (ArrayList subset : rest_subsets) {
            ArrayList new_subset = new ArrayList();
            new_subset.add(first);
            new_subset.addAll(subset);
            output.add(new_subset);
        }

        return output;
    }
}