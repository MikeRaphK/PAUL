package java_programs;
import java.util.*;

/**
 * 
 * @author derricklin
 */
public class GET_FACTORS {
    public static ArrayList<Integer> get_factors(int n) {
        if (n == 1) {
            return new ArrayList<Integer>();
        }
        int max = (int)(Math.sqrt(n) + 1.0);
        ArrayList<Integer> factors = new ArrayList<>(); // Initialize list to store factors
        for (int i=2; i < max; i++) {
            while (n % i == 0) { // Changed here to find all occurrences of each factor
                factors.add(i); // Add factor to list
                n /= i; // Divide n by the factor
            }
        }
        if (n > 1) { // Add remaining prime factor if n is greater than 1
            factors.add(n);
        }
        return factors;
    }
}