use clap::Parser;
use std::collections::{HashMap, HashSet};
use std::error::Error;
use std::fs;
use std::path::{Path, PathBuf};
use walkdir::{DirEntry, WalkDir};

/// Sort the files in a folder into subfolders by type
#[derive(Parser)]
#[command(version, about)]
struct Args {
    /// The folder to clean up, e.g. ~/Downloads
    dir: PathBuf,

    /// Only show what would happen, don't move anything
    #[arg(long)]
    dry_run: bool,

    /// Also sort the files inside subfolders
    #[arg(short, long)]
    recursive: bool,
}

const FOLDERS: [&str; 7] =
    ["Images", "Documents", "Videos", "Audio", "Archives", "Code", "Other"];

/// Which folder a file belongs in, based on its extension
fn category(path: &Path) -> &'static str {
    let ext = path
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_lowercase();
    match ext.as_str() {
        "jpg" | "jpeg" | "png" | "gif" | "webp" | "svg" => "Images",
        "pdf" | "doc" | "docx" | "txt" | "md" | "csv" | "xlsx" => "Documents",
        "mp4" | "mkv" | "mov" | "avi" | "webm" => "Videos",
        "mp3" | "wav" | "flac" | "ogg" => "Audio",
        "zip" | "tar" | "gz" | "7z" | "rar" => "Archives",
        "rs" | "py" | "js" | "html" | "json" => "Code",
        _ => "Other",
    }
}

/// A name in `dir` that isn't taken yet: notes.txt, "notes (1).txt", ...
fn free_name(dir: &Path, file: &Path, taken: &HashSet<PathBuf>) -> PathBuf {
    let stem = file.file_stem().unwrap_or_default().to_string_lossy();
    let ext = match file.extension() {
        Some(e) => format!(".{}", e.to_string_lossy()),
        None => String::new(),
    };
    let mut target = dir.join(file.file_name().unwrap_or_default());
    let mut n = 1;
    while target.exists() || taken.contains(&target) {
        target = dir.join(format!("{stem} ({n}){ext}"));
        n += 1;
    }
    target
}

/// One of our own Images/, Documents/, ... folders? Then skip it.
fn is_sorted_folder(entry: &DirEntry) -> bool {
    let name = entry.file_name().to_string_lossy();
    entry.depth() == 1
        && entry.file_type().is_dir()
        && FOLDERS.contains(&name.as_ref())
}

fn run(args: &Args) -> Result<(), Box<dyn Error>> {
    // 1. Find the files first: never move things while walking a folder
    let depth = if args.recursive { usize::MAX } else { 1 };
    let walker = WalkDir::new(&args.dir).min_depth(1).max_depth(depth);
    let mut files = Vec::new();
    for entry in walker.into_iter().filter_entry(|e| !is_sorted_folder(e)) {
        let entry = entry?; // a folder we can't read is a real error
        if entry.file_type().is_file() {
            files.push(entry.into_path());
        }
    }
    files.sort(); // same order every time, easier to read
    if files.is_empty() {
        println!("Nothing to sort in {}", args.dir.display());
        return Ok(());
    }

    // 2. Move each file into its folder (or just print the plan)
    let mut counts: HashMap<&str, usize> = HashMap::new();
    let mut taken = HashSet::new();
    for file in &files {
        let folder = category(file);
        let dest = free_name(&args.dir.join(folder), file, &taken);
        let from = file.strip_prefix(&args.dir)?;
        let to = dest.strip_prefix(&args.dir)?;
        println!("  {} -> {}", from.display(), to.display());
        if !args.dry_run {
            fs::create_dir_all(args.dir.join(folder))?;
            fs::rename(file, &dest)?;
        }
        taken.insert(dest);
        *counts.entry(folder).or_insert(0) += 1;
    }

    // 3. Summary, in a fixed order
    let verb = if args.dry_run { "Would move" } else { "Moved" };
    println!("{verb} {} files:", files.len());
    for folder in FOLDERS {
        if let Some(n) = counts.get(folder) {
            println!("  {folder:<10} {n}");
        }
    }
    Ok(())
}

fn main() {
    let args = Args::parse();
    if let Err(e) = run(&args) {
        eprintln!("error: {e}");
        std::process::exit(1);
    }
}
