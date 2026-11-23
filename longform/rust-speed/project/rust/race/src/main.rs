// Count multiples of 7 on every core, with a shared counter (a data race!)
use rayon::prelude::*;

fn main() {
    let mut count = 0;
    (1..10_000_000u64).into_par_iter().for_each(|n| {
        if n % 7 == 0 {
            count += 1;
        }
    });
    println!("{count}");
}
