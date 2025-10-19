package java_programs;
import java.util.*;

public class KHEAPSORT {
    public static ArrayList<Integer> kheapsort(ArrayList<Integer> arr, int k) {
        PriorityQueue<Integer> heap = new PriorityQueue<Integer>();
        
        // Add initial part (up to k elements) to the heap
        for (Integer v : arr.subList(0, Math.min(k, arr.size()))) {
            heap.add(v);
        }

        ArrayList<Integer> output = new ArrayList<Integer>();
        
        // Start processing from the k-th element to end
        for (int i = k; i < arr.size(); i++) {
            heap.add(arr.get(i));  // Add current element to heap
            output.add(heap.poll());  // Remove the smallest element
        }

        // Empty the remaining elements in the heap to output
        while (!heap.isEmpty()) {
            output.add(heap.poll());
        }

        return output;
    }
}
