    public static double sqrt(double x, double epsilon) {
        if (x < 0) return Double.NaN; // Handle negative input
        double approx = x / 2d;
        while (Math.abs(x - approx * approx) > epsilon) { // Corrected condition
            approx = 0.5d * (approx + x / approx);
        }
        return approx;
    }