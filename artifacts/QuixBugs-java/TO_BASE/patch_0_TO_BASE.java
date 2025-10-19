    public static String to_base(int num, int b) {
        String result = "";
        String alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        int i;
        if (b < 2 || b > 36) return null; // Invalid base check
        while (num > 0) {
            i = num % b;
            num = num / b; // floor division?
            result = String.valueOf(alphabet.charAt(i)) + result; // Correct order of digits
        }
        return result;
    }