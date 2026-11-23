// Count long chains on every core, with a shared counter (a data race!)
use rayon::prelude::*;

fn main() {
    let mut long_chains = 0;
    (1..10_000_000u64).into_par_iter().for_each(|n| {
        if n % 7 == 0 {
            long_chains += 1;
        }
    });
    println!("{long_chains}");
}
