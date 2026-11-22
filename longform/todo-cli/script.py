"""Rust Projects #1: Todo CLI app (clap + serde). Every output comes from captures/cap.json (real run)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = json.load(open(os.path.join(HERE, "captures/cap.json")))
def out(k): return CAP[k]["out"]
def src(path): return open(os.path.join(HERE, "project", path)).read().rstrip("\n").split("\n")

PROJECT = "todo-cli"
FIRST_CHAPTER = "What we're building"
PROMPT_DIR = {"home": "~", "proj": "~/todo-cli"}
TREE = ["src/", "src/main.rs", ".gitignore", "Cargo.lock", "Cargo.toml", "todos.json"]
TREE_INITIAL = ["src/", "src/main.rs", ".gitignore", "Cargo.toml"]
TREE_LATER = {"Cargo.lock": "run_basic", "todos.json": "run_basic"}
FILES = {"Cargo.toml": out("cat_toml").split("\n"), "src/main.rs": src("src/main.rs")}

DIAGRAMS = {
 "plan": {"title": "What we'll build: a todo app for your terminal",
   "nodes": [{"id": "you", "label": "You", "sub": "$ todo add \"Buy milk\"", "mono": True, "x": 40, "y": 260, "w": 380, "h": 150, "color": "gray"},
             {"id": "cli", "label": "todo CLI", "sub": "clap parses commands", "x": 560, "y": 260, "w": 380, "h": 150, "color": "orange"},
             {"id": "vec", "label": "Vec<Task>", "sub": "id · text · done", "mono": False, "x": 1100, "y": 120, "w": 400, "h": 150, "color": "blue"},
             {"id": "file", "label": "todos.json", "sub": "serde_json saves it", "x": 1100, "y": 420, "w": 400, "h": 150, "color": "green"}],
   "edges": [{"src": "you", "dst": "cli", "label": "command", "color": "gray"},
             {"src": "cli", "dst": "vec", "label": "load", "color": "blue"},
             {"src": "vec", "dst": "file", "label": "save", "color": "green"}],
   "notes": [{"text": "commands: add · list · done · remove", "x": 420, "y": 470, "color": "gray", "size": 26, "mono": True},
             {"text": "One file of Rust, ~85 lines, a 1.2 MB binary at the end", "x": 800, "y": 690, "color": "orange", "size": 30}]},
 "flow": {"title": "Every run of the program",
   "nodes": [{"id": "parse", "label": "1. Parse", "sub": "Cli::parse()", "mono": True, "x": 40, "y": 260, "w": 330, "h": 150, "color": "orange"},
             {"id": "load", "label": "2. Load", "sub": "todos.json → Vec", "x": 440, "y": 260, "w": 330, "h": 150, "color": "blue"},
             {"id": "act", "label": "3. Act", "sub": "match the command", "x": 840, "y": 260, "w": 330, "h": 150, "color": "purple"},
             {"id": "save", "label": "4. Save", "sub": "Vec → todos.json", "x": 1240, "y": 260, "w": 330, "h": 150, "color": "green"}],
   "edges": [{"src": "parse", "dst": "load", "color": "gray"}, {"src": "load", "dst": "act", "color": "gray"}, {"src": "act", "dst": "save", "color": "gray"}],
   "notes": [{"text": "No database, no server: the state lives in one JSON file", "x": 800, "y": 600, "color": "gray", "size": 28}]},
}

def T(cmd, out="", term=1, d="proj", speed=None, pause=0.6, keys=None, stream=None):
    return dict(kind="cmd", cmd=cmd, out=out, term=term, dir=d, speed=speed, pause=pause, keys=keys, stream=stream)
def C(k, **kw): return T(CAP[k]["cmd"], out(k), **kw)

SHOTS = [
 dict(id="cold_open", scene="terminal", zoom=1.2, actions=[C("list1", term=3), C("done2", term=3), C("list2", term=3)],
   say="By the end of this video, you'll have this: your own todo app that lives in your terminal. You add tasks, list them, tick them off, and it remembers everything between runs. And we'll build it from scratch in Rust, in about eighty lines of code."),
 dict(id="intro", scene="title", title="Build a Todo CLI in Rust", subtitle="Rust Projects #1  ·  clap + serde, from scratch", chips=["Rust", "CLI", "clap", "serde"],
   say="Hey everyone, welcome to the first video in my Rust projects series, where we build real, useful things step by step. Today it's a command line todo app. If you've been following my daily Rust shorts, you'll see structs, enums, match, vectors and closures all working together in a real program."),
 dict(id="plan", scene="diagram", diagram="plan", chapter="The plan",
   say="Here's the plan. You type a command like todo add, buy milk. A crate called clap turns that text into a Rust enum, so we know exactly which command you asked for. Our tasks live in a vector of Task structs, and serde saves that vector into a JSON file, so the list survives after the program exits."),
 dict(id="new", scene="terminal", chapter="Step 1 · Create the project", actions=[C("new", d="home"), T("cd todo-cli", d="home", pause=0.3)],
   say="Let's start. cargo new todo dash cli creates the project, with a Cargo dot toml and a hello world in src slash main dot r s. Then we cd into it."),
 dict(id="deps", scene="terminal", chapter="Step 2 · Add the crates", actions=[C("add_clap", speed=30), C("add_serde", speed=30), C("add_json", speed=30)],
   say="Now three dependencies. clap with the derive feature parses command line arguments for us. serde, also with derive, lets us turn our structs into data and back. And serde json is the JSON format for serde. cargo add downloads the crate index and puts the latest versions into Cargo dot toml."),
 dict(id="toml", scene="editor", file="Cargo.toml", show=True, highlight=[7, 8, 9],
   say="And here's Cargo dot toml. The three crates, with the derive features turned on. That's all the setup we need."),
 dict(id="code1", scene="editor", file="src/main.rs", type=(0, 6), chapter="Step 3 · The command line",
   say="Open main dot r s and replace everything. First the imports: Parser and Subcommand from clap, Serialize and Deserialize from serde, plus fs and Path from the standard library for files. And a constant with the file name, todos dot json."),
 dict(id="code2", scene="editor", file="src/main.rs", type=(6, 14),
   say="Now the command line itself. This struct derives Parser, and that's where the magic happens: clap reads this struct at compile time and generates the whole argument parser for us. The triple slash comment becomes the description in the help text, and version means dash dash version just works. The struct holds one field: which subcommand was used."),
 dict(id="code3", scene="editor", file="src/main.rs", type=(14, 26),
   say="The subcommands are an enum, and this is where enums really shine. Add carries the task text. List carries nothing. Done and Remove carry the id of a task, as a usize. Each doc comment becomes the help line for that command, and clap will even reject an id that isn't a number."),
 dict(id="code4", scene="editor", file="src/main.rs", type=(26, 33), chapter="Step 4 · Tasks & saving",
   say="Next, the data. A Task has an id, the text, and a done flag. Deriving Serialize and Deserialize is literally all it takes for serde to convert it to and from JSON."),
 dict(id="code5", scene="editor", file="src/main.rs", type=(33, 46),
   say="Two small helpers. load checks whether todos dot json exists. If not, we start with an empty vector. Otherwise we read the file into a string and let serde json parse it into a vector of tasks. save does the opposite: it turns the slice of tasks into pretty JSON and writes the file. I'm using expect with clear messages, so if the file is ever broken, you know exactly why."),
 dict(id="flow", scene="diagram", diagram="flow",
   say="So every time you run the program, the same four steps happen. Parse the arguments, load the tasks from the file, do whatever the command says, and save the tasks back."),
 dict(id="code6", scene="editor", file="src/main.rs", type=(46, 57), chapter="Step 5 · The logic",
   say="Here's main. Parse the command line, load the tasks into a mutable vector, and match on the command. For add, we need a new id: take the highest existing id and add one, or start at one when the list is empty. That's an iterator chain: iter, map to the ids, max, and unwrap or zero. Then we print a confirmation and push the new task."),
 dict(id="code7", scene="editor", file="src/main.rs", type=(57, 66),
   say="List is simple. If there's nothing, say so. Otherwise loop over the tasks by reference, pick an x or a space for the checkbox, and print each one."),
 dict(id="code8", scene="editor", file="src/main.rs", type=(66, 85),
   say="Done uses iter mut and find to get a mutable reference to the task with that id. If we find it, we set done to true. If not, we print an error to standard error with eprintln. Remove uses retain, which keeps every task except the one with that id, and we compare the length before and after to know whether anything was removed. And finally, whatever happened, we save."),
 dict(id="run_basic", scene="terminal", chapter="Step 6 · Run it", actions=[C("build", speed=40), T("clear", pause=0.2), C("help"), C("list_empty")],
   say="Time to run it. The first cargo build compiles clap and serde, so it takes a few seconds. Now dash dash help. Look at that: a complete help screen with every command and its description, and we never wrote any of it by hand. With an empty list, list says nothing to do."),
 dict(id="run_add", scene="terminal", actions=[T("clear", pause=0.2), C("add1"), C("add2"), C("add3"), C("list1")],
   say="Let's add a few tasks. Buy milk, learn Rust ownership, and record a YouTube video. Each one gets the next id. And list shows all three, with empty checkboxes."),
 dict(id="run_done", scene="terminal", chapter="Step 7 · Done, remove & the JSON file", actions=[C("done2"), C("list2"), C("cat_json", speed=30)],
   say="Now mark task two as done, and list again: there's the x. And here's the JSON file that serde wrote. Each task is a plain object, so you could even edit it by hand if you wanted to."),
 dict(id="run_remove", scene="terminal", actions=[T("clear", pause=0.2), C("remove1"), C("done9"), C("list3")],
   say="Remove task one. And if we try to complete a task that doesn't exist, like nine, we get a clear error instead of a crash. The list now has tasks two and three, and the ids stay the same, which is exactly what you want."),
 dict(id="release", scene="terminal", chapter="Step 8 · Release build & install", actions=[T("clear", pause=0.2), C("release", speed=40), C("ls_bin"), C("install"), C("global", d="home")],
   say="Finally, let's make it a real tool. cargo build dash dash release turns on all the optimizations. The binary is about one point two megabytes and needs nothing else to run. cargo install dash dash path dot copies it into the cargo bin folder. Cargo reminds us to put that folder on our PATH, which rustup normally does for you. And now it works from any folder."),
 dict(id="outro", scene="title", title="You built a real Rust tool!", subtitle="clap  ·  serde  ·  enums  ·  match  ·  iterators", outro=True,
   say="And that's it. In about eighty lines we built a real command line app with subcommands, help text, and storage. Try adding a priority field, or a clear command, as practice. All the code is linked in the description. If you liked this, subscribe for the next Rust project, and follow the daily Rust shorts to learn each concept on its own. See you in the next one!"),
]
