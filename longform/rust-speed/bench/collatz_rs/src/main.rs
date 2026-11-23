// Longest Collatz chain for a starting number below N
const N: u64 = 1_000_000;

fn main() {
    let (mut best_n, mut best_len) = (1, 1);
    for start in 1..N {
        let (mut n, mut steps) = (start, 1);
        while n != 1 {
            n = if n % 2 == 0 { n / 2 } else { 3 * n + 1 };
            steps += 1;
        }
        if steps > best_len {
            (best_n, best_len) = (start, steps);
        }
    }
    println!("{best_n} ({best_len} steps)");
}
