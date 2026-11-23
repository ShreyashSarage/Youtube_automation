# Longest Collatz chain for a starting number below N
N = 1_000_000

best_n, best_len = 1, 1
for start in range(1, N):
    n, steps = start, 1
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    if steps > best_len:
        best_n, best_len = start, steps

print(f"{best_n} ({best_len} steps)")
