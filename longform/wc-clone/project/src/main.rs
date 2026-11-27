use clap::Parser;
use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::path::PathBuf;

/// Count lines, words and bytes, like the Unix `wc` tool
#[derive(Parser)]
#[command(name = "rwc", version, about)]
struct Args {
    /// Files to read (none, or "-", means standard input)
    files: Vec<PathBuf>,

    /// Print the line count
    #[arg(short, long)]
    lines: bool,

    /// Print the word count
    #[arg(short, long)]
    words: bool,

    /// Print the byte count
    #[arg(short = 'c', long)]
    bytes: bool,
}

#[derive(Debug, Default, PartialEq)]
struct Counts {
    lines: usize,
    words: usize,
    bytes: usize,
}

/// Count everything in one pass over the input, one line at a time
fn count<R: BufRead>(mut reader: R) -> io::Result<Counts> {
    let mut c = Counts::default();
    let mut line = Vec::new();
    while reader.read_until(b'\n', &mut line)? > 0 {
        c.bytes += line.len();
        if line.ends_with(b"\n") {
            c.lines += 1;
        }
        c.words += line
            .split(|b| b.is_ascii_whitespace())
            .filter(|word| !word.is_empty())
            .count();
        line.clear();
    }
    Ok(c)
}

/// Open a file, or standard input for "-"
fn count_input(path: &PathBuf) -> io::Result<Counts> {
    if path.as_os_str() == "-" {
        count(io::stdin().lock())
    } else {
        count(BufReader::new(File::open(path)?))
    }
}

fn main() {
    let args = Args::parse();
    // no flags means: show all three, like wc
    let all = !(args.lines || args.words || args.bytes);
    let show = [all || args.lines, all || args.words, all || args.bytes];
    let inputs = if args.files.is_empty() {
        vec![PathBuf::from("-")]
    } else {
        args.files.clone()
    };

    let mut rows = Vec::new();
    let mut total = Counts::default();
    let mut failed = false;
    for path in &inputs {
        match count_input(path) {
            Ok(c) => {
                total.lines += c.lines;
                total.words += c.words;
                total.bytes += c.bytes;
                rows.push((c, path.display().to_string()));
            }
            Err(e) => {
                eprintln!("rwc: {}: {e}", path.display());
                failed = true;
            }
        }
    }
    if inputs.len() > 1 {
        rows.push((total, "total".to_string()));
    }

    // line the columns up the way wc does: one column needs no padding,
    // standard input gets width 7, files get the width of the biggest count
    let reads_stdin = inputs.iter().any(|p| p.as_os_str() == "-");
    let width = if show.iter().filter(|&&s| s).count() == 1 {
        1
    } else if reads_stdin {
        7
    } else {
        rows.iter().map(|(c, _)| c.bytes.to_string().len()).max().unwrap_or(1)
    };
    for (c, name) in &rows {
        let nums = [c.lines, c.words, c.bytes];
        let cols: Vec<String> = (0..3)
            .filter(|&i| show[i])
            .map(|i| format!("{:>width$}", nums[i]))
            .collect();
        if name == "-" {
            println!("{}", cols.join(" "));
        } else {
            println!("{} {name}", cols.join(" "));
        }
    }
    if failed {
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn counts(text: &str) -> Counts {
        count(text.as_bytes()).unwrap()
    }

    #[test]
    fn empty_input_is_all_zeros() {
        assert_eq!(counts(""), Counts::default());
    }

    #[test]
    fn counts_lines_words_and_bytes() {
        let c = counts("hello world\nbye\n");
        assert_eq!(c, Counts { lines: 2, words: 3, bytes: 16 });
    }

    #[test]
    fn extra_spaces_are_not_words() {
        assert_eq!(counts("  one   two  \n").words, 2);
    }

    #[test]
    fn last_line_without_newline() {
        let c = counts("one\ntwo");
        assert_eq!((c.lines, c.words), (1, 2));
    }

    #[test]
    fn emoji_is_four_bytes() {
        assert_eq!(counts("🦀\n").bytes, 5);
    }
}
