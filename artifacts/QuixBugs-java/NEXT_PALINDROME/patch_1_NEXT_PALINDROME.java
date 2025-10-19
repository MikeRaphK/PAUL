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
        
        int[] original = digit_list.clone();
        // mirror left to right
        for (int i = 0; i < n / 2; i++) {
            digit_list[n - 1 - i] = digit_list[i];
        }

        // Check if the mirrored is not greater than original
        boolean isGreater = false;
        for (int i = 0; i < n; i++) {
            if (digit_list[i] > original[i]) {
                isGreater = true;
                break;
            } else if (digit_list[i] < original[i]) {
                break;
            }
        }

        // If mirrored number is less than or equal to original, increment the palindrome
        if (!isGreater) {
            int carry = 1;
            int mid = n / 2;
            while (mid >= 0 && carry > 0) {
                digit_list[mid] = (digit_list[mid] + carry) % 10;
                carry = (digit_list[mid] == 0) ? 1 : 0;
                if (mid != n - 1 - mid) {
                    // ensure we mirror the increment
                    digit_list[n - 1 - mid] = digit_list[mid];
                }
                mid--;
            }
        }

        // Handle the case where all digits were 9
        if (digit_list[0] == 0) {
            int[] newNumber = new int[n + 1];
            newNumber[0] = 1;
            newNumber[n] = 1;
            return Arrays.toString(newNumber);
        }

        return Arrays.toString(digit_list);
    }
}
