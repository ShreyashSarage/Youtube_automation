use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

const DB: &str = "todos.json";

/// A tiny todo list for your terminal
#[derive(Parser)]
#[command(name = "todo", version, about)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Add a new task
    Add { text: String },
    /// Show all tasks
    List,
    /// Mark a task as done
    Done { id: usize },
    /// Delete a task
    Remove { id: usize },
}

#[derive(Serialize, Deserialize)]
struct Task {
    id: usize,
    text: String,
    done: bool,
}

fn load() -> Vec<Task> {
    if !Path::new(DB).exists() {
        return Vec::new();
    }
    let data = fs::read_to_string(DB).expect("could not read todos.json");
    serde_json::from_str(&data).expect("todos.json is not valid JSON")
}

fn save(tasks: &[Task]) {
    let data = serde_json::to_string_pretty(tasks).expect("could not serialize");
    fs::write(DB, data).expect("could not write todos.json");
}

fn main() {
    let cli = Cli::parse();
    let mut tasks = load();

    match cli.command {
        Command::Add { text } => {
            let id = tasks.iter().map(|t| t.id).max().unwrap_or(0) + 1;
            println!("Added #{id}: {text}");
            tasks.push(Task { id, text, done: false });
        }
        Command::List => {
            if tasks.is_empty() {
                println!("Nothing to do!");
            }
            for t in &tasks {
                let mark = if t.done { "x" } else { " " };
                println!("[{mark}] {}: {}", t.id, t.text);
            }
        }
        Command::Done { id } => match tasks.iter_mut().find(|t| t.id == id) {
            Some(t) => {
                t.done = true;
                println!("Completed #{id}");
            }
            None => eprintln!("No task with id {id}"),
        },
        Command::Remove { id } => {
            let before = tasks.len();
            tasks.retain(|t| t.id != id);
            if tasks.len() < before {
                println!("Removed #{id}");
            } else {
                eprintln!("No task with id {id}");
            }
        }
    }
    save(&tasks);
}
