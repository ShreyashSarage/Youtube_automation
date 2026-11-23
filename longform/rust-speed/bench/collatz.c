// Longest Collatz chain for a starting number below N
#include <stdio.h>
#include <stdint.h>
#define N 1000000

int main(void) {
    uint64_t best_n = 1; int best_len = 1;
    for (uint64_t start = 1; start < N; start++) {
        uint64_t n = start; int steps = 1;
        while (n != 1) {
            n = (n % 2 == 0) ? n / 2 : 3 * n + 1;
            steps++;
        }
        if (steps > best_len) { best_n = start; best_len = steps; }
    }
    printf("%lu (%d steps)\n", best_n, best_len);
    return 0;
}
