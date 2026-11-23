// Longest Collatz chain below N, on every CPU core
use rayon::prelude::*;

const N: u64 = 10_000_000;

fn chain_len(start: u64) -> u32 {
    let (mut n, mut steps) = (start, 1);
    while n != 1 {
        n = if n % 2 == 0 { n / 2 } else { 3 * n + 1 };
        steps += 1;
    }
    steps
}

fn main() {
    let (best_len, best_n) = (1..N)
        .into_par_iter()
        .map(|n| (chain_len(n), n))
        .max()
        .unwrap();
    println!("{best_n} ({best_len} steps)");
}
