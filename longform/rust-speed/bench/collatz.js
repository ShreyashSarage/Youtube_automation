// Longest Collatz chain for a starting number below N
const N = 1_000_000;

let bestN = 1, bestLen = 1;
for (let start = 1; start < N; start++) {
  let n = start, steps = 1;
  while (n !== 1) {
    n = n % 2 === 0 ? n / 2 : 3 * n + 1;
    steps++;
  }
  if (steps > bestLen) { bestN = start; bestLen = steps; }
}

console.log(`${bestN} (${bestLen} steps)`);
