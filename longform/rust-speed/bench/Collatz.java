// Longest Collatz chain for a starting number below N
public class Collatz {
    static final long N = 1_000_000;

    public static void main(String[] args) {
        long bestN = 1; int bestLen = 1;
        for (long start = 1; start < N; start++) {
            long n = start; int steps = 1;
            while (n != 1) {
                n = (n % 2 == 0) ? n / 2 : 3 * n + 1;
                steps++;
            }
            if (steps > bestLen) { bestN = start; bestLen = steps; }
        }
        System.out.println(bestN + " (" + bestLen + " steps)");
    }
}
