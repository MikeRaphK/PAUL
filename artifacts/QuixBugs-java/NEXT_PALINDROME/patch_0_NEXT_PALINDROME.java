package java_programs;
import java.util.*;
import java.lang.Math.*;
/**
 *
 * @author derricklin
 */
public class NEXT_PALINDROME {
    public static String next_palindrome(int[] digit_list) {
        int n = digit_list.length;
        
        // mirror left to right
        for (int i = 0; i < n / 2; i++) {
            digit_list[n - 1 - i] = digit_list[i];
        }

        // Check if the number is already a palindrome or less than the palindrome formed
        boolean needsIncrement = false;
        for (int i = 0; i < n; i++) {
            if (digit_list[i] < digit_list[n - 1 - i]) {
                needsIncrement = false;
                break;
            }
            if (digit_list[i] > digit_list[n - 1 - i]) {
                needsIncrement = true;
                break;
            }
        }

        // If still the same or not palindrome, increment the middle
        if (!needsIncrement) {
            int left = (n - 1) / 2;
            digit_list[left]++;
            int carry = digit_list[left] / 10;
            digit_list[left] %= 10;

            // Propagate the carry if necessary
            int right = n / 2;
            while (carry > 0 && left >= 0) {
                digit_list[left--] = (digit_list[left] + carry) % 10;
                carry = (digit_list[left + 1] == 0) ? 1 : 0;
            }

            // Mirror again in case of increment
            for (int i = 0; i < n / 2; i++) {
                digit_list[n - 1 - i] = digit_list[i];
            }
        }

        // If there's still a carry, we need an extra digit (e.g., 999 -> 1001)
        if (digit_list[0] == 0) {
            int[] newNumber = new int[n + 1];
            newNumber[0] = 1;
            newNumber[n] = 1;
            return Arrays.toString(newNumber);
        }

        return Arrays.toString(digit_list);
    }
}
