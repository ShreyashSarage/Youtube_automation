// Top 10 most common words in words.txt
use std::collections::HashMap;
use std::fs;

fn main() {
    let text = fs::read_to_string("words.txt").expect("read words.txt");
    let mut counts: HashMap<&str, u32> = HashMap::new();
    for word in text.split_ascii_whitespace() {
        *counts.entry(word).or_insert(0) += 1;
    }

    let mut top: Vec<(&str, u32)> = counts.into_iter().collect();
    top.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(b.0)));
    for (word, n) in top.iter().take(10) {
        println!("{word} {n}");
    }
}
