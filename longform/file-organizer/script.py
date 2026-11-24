"""Rust Projects #2: File organizer (walkdir + clap). Every output comes from captures/cap.json (real run)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = json.load(open(os.path.join(HERE, "captures/cap.json")))
def out(k): return CAP[k]["out"]
def src(path): return open(os.path.join(HERE, "project", path)).read().rstrip("\n").split("\n")

PROJECT = "file-organizer"
FIRST_CHAPTER = "What we're building"
PROMPT_DIR = {"home": "~", "proj": "~/file-organizer"}
TREE = ["src/", "src/main.rs", ".gitignore", "Cargo.lock", "Cargo.toml", "make_mess.sh"]
TREE_INITIAL = ["src/", "src/main.rs", ".gitignore", "Cargo.toml"]
TREE_LATER = {"make_mess.sh": "mess", "Cargo.lock": "run_help"}
FILES = {"Cargo.toml": out("cat_toml").split("\n"), "src/main.rs": src("src/main.rs"), "make_mess.sh": src("make_mess.sh")}

DIAGRAMS = {
 "plan": {"title": "What we'll build: one command that cleans up a folder",
   "nodes": [{"id": "mess", "label": "~/Downloads", "sub": "17 files, all mixed up", "x": 20, "y": 250, "w": 400, "h": 150, "color": "gray"},
             {"id": "tool", "label": "file-organizer", "sub": "walkdir + clap", "x": 560, "y": 250, "w": 420, "h": 150, "color": "orange"},
             {"id": "img", "label": "Images/", "sub": ".jpg .png .gif", "x": 1150, "y": 30, "w": 460, "h": 120, "color": "blue"},
             {"id": "doc", "label": "Documents/", "sub": ".pdf .docx .txt", "x": 1150, "y": 200, "w": 460, "h": 120, "color": "green"},
             {"id": "vid", "label": "Videos/ · Audio/ · Archives/", "x": 1150, "y": 370, "w": 460, "h": 110, "color": "purple"},
             {"id": "oth", "label": "Code/ · Other/", "x": 1150, "y": 530, "w": 460, "h": 110, "color": "gray"}],
   "edges": [{"src": "mess", "dst": "tool", "color": "gray"}, {"src": "tool", "dst": "img", "color": "blue"}, {"src": "tool", "dst": "doc", "color": "green"},
             {"src": "tool", "dst": "vid", "color": "purple"}, {"src": "tool", "dst": "oth", "color": "gray"}],
   "notes": [{"text": "--dry-run shows the plan first · --recursive goes into subfolders", "x": 800, "y": 740, "color": "orange", "size": 28}]},
 "flow": {"title": "What happens on every run",
   "nodes": [{"id": "walk", "label": "1. Walk", "sub": "WalkDir finds files", "x": 0, "y": 200, "w": 360, "h": 150, "color": "blue"},
             {"id": "collect", "label": "2. Collect", "sub": "into a Vec, sorted", "x": 420, "y": 200, "w": 360, "h": 150, "color": "purple"},
             {"id": "decide", "label": "3. Decide", "sub": "extension → folder", "x": 840, "y": 200, "w": 360, "h": 150, "color": "orange"},
             {"id": "move", "label": "4. Move", "sub": "fs::rename (or just print)", "x": 1260, "y": 200, "w": 400, "h": 150, "color": "green"}],
   "edges": [{"src": "walk", "dst": "collect", "color": "gray"}, {"src": "collect", "dst": "decide", "color": "gray"},
             {"src": "decide", "dst": "move", "color": "gray"}],
   "notes": [{"text": "We collect first and move later: never change a folder while you're walking it", "x": 830, "y": 470, "color": "purple", "size": 28},
             {"text": "Any error travels up with ? and main prints it once", "x": 830, "y": 560, "color": "gray", "size": 28}]},
}

def T(cmd, out="", term=1, d="proj", speed=None, pause=0.6, **kw):
    return dict(kind="cmd", cmd=cmd, out=out, term=term, dir=d, speed=speed, pause=pause, **kw)
def C(k, **kw): return T(CAP[k]["cmd"], out(k), **kw)
L = lambda needle: next(i + 1 for i, l in enumerate(FILES["src/main.rs"]) if needle in l)

SHOTS = [
 dict(id="cold_open", scene="terminal", zoom=1.15, actions=[C("dry", term=3, speed=40, pause=1.0)],
   say="Is your Downloads folder a mess? Mine was. So let's build a tool in Rust that sorts every file into Images, Documents, Videos and more, with one command. It even shows you the plan before it touches anything."),
 dict(id="intro", scene="title", title="Build a File Organizer in Rust", subtitle="Rust Projects #2  ·  walkdir + clap, from scratch", chips=["Rust", "CLI", "walkdir", "clap"],
   say="Hey everyone, welcome back to Rust projects, where we build real, useful tools step by step. Today it's a file organizer. You'll learn how to work with files and paths, walk through folders, use match and hash maps, and handle errors properly with the question mark operator."),
 dict(id="plan", scene="diagram", diagram="plan", chapter="The plan",
   say="Here's the plan. You point the tool at a folder, like your Downloads. It looks at every file's extension and moves it into a folder for its type: pictures into Images, PDFs and text files into Documents, and so on. A dry run flag prints the plan without moving anything, and a recursive flag also sorts files inside subfolders."),
 dict(id="new", scene="terminal", chapter="Step 1 · Project & crates", actions=[C("new", d="home"), T("cd file-organizer", d="home", pause=0.3), C("add_clap", speed=30), C("add_walkdir", speed=30)],
   say="Let's start with cargo new file organizer, and cd into it. Then two crates. clap, with the derive feature, for the command line arguments, like in project one. And walkdir, which walks through a folder and all of its subfolders for us."),
 dict(id="toml", scene="editor", file="Cargo.toml", show=True, highlight=[7, 8],
   say="Cargo dot toml now lists both crates. That's all we need: everything else comes from Rust's standard library."),
 dict(id="mess", scene="terminal", chapter="Step 2 · A messy test folder", actions=[T("clear", pause=0.2), C("mess"), C("find1", speed=30, pause=1.0)],
   say="Before writing the organizer, we need something to organize. I'm not going to test this on my real Downloads folder, and neither should you. This little script makes a fake one with seventeen files: pictures, documents, a video, a zip file, some code, a file with no extension, and an old stuff subfolder with three more files. Notice there are two notes dot txt files. That will matter later."),
 dict(id="code1", scene="editor", file="src/main.rs", type=(0, 6), chapter="Step 3 · Arguments",
   say="Now open main dot r s. First the imports: Parser from clap, HashMap and HashSet, the Error trait, fs for file operations, Path and PathBuf for paths, and DirEntry and WalkDir from walkdir."),
 dict(id="code2", scene="editor", file="src/main.rs", type=(6, 22),
   say="The arguments struct derives Parser. dir is a PathBuf, the folder to clean up. PathBuf is like String, but for file paths, so it works on Linux, macOS and Windows. dry run and recursive are bools, so clap turns them into flags: dash dash dry dash run, and dash r or dash dash recursive. Every doc comment becomes help text."),
 dict(id="code3", scene="editor", file="src/main.rs", type=(22, 43), chapter="Step 4 · Sorting by extension",
   say="Next, the seven folder names, as a constant array. And the heart of the program: the category function. It takes the path's extension, turns it into a normal string, and lowercases it, so holiday dot JPG in capitals still counts as an image. If there's no extension, we use an empty string. Then a match with or patterns: jpg or png or gif goes to Images, pdf or docx to Documents, and so on. The underscore catches everything else, which goes to Other. The return type is ampersand static str, because these names are baked into the program."),
 dict(id="code4", scene="editor", file="src/main.rs", type=(43, 59),
   say="What if Documents already has a notes dot txt? We must never overwrite a file. free name tries the normal name first. If it exists on disk, or another file in this run already claimed it, it tries notes with one in brackets, then two, and so on, until it finds a free name. The taken set makes the dry run show exactly the same names as the real run."),
 dict(id="code5", scene="editor", file="src/main.rs", type=(59, 67),
   say="One more helper. When we walk the folder, we must skip our own Images, Documents and other folders, otherwise running the tool twice would sort the files that are already sorted. This function says yes for a folder directly inside the target folder, whose name is in our list."),
 dict(id="flow", scene="diagram", diagram="flow", chapter="Step 5 · Walk, collect, move",
   say="Now the main logic, in four steps. Walk the folder, collect the files into a vector, decide the target folder for each one, and move it. We always collect first and move later, because moving files around while you're still walking through the same folder is asking for trouble. And any error travels up with the question mark operator."),
 dict(id="code6", scene="editor", file="src/main.rs", type=(67, 84),
   say="Here's run. It returns a Result with a boxed error, so the question mark works for any kind of error. Depth one means just the folder itself, unless recursive is set. Then we walk, and filter entry skips our sorted folders, including everything inside them. Each entry is a Result, because a folder might not be readable, and the question mark passes that error up instead of ignoring it. We keep only files, sort them, and if there's nothing to do, we say so."),
 dict(id="code7", scene="editor", file="src/main.rs", type=(84, 101),
   say="Then the loop. For each file: pick its folder, find a free name, and print from, arrow, to, relative to the folder, so the output stays short. Only if this isn't a dry run do we create the folder and rename the file. fs rename moves a file without copying its contents, so it's instant. And we count how many files went into each folder, with the hash map entry API from project one."),
 dict(id="code8", scene="editor", file="src/main.rs", type=(101, 120),
   say="Last, a summary in a fixed order: Would move in a dry run, Moved otherwise. And main: parse the arguments, call run, and if it returns an error, print it nicely to standard error and exit with code one. That way the user sees a clear message, not a debug dump."),
 dict(id="run_help", scene="terminal", chapter="Step 6 · Dry run first", actions=[T("clear", pause=0.2), C("build", speed=40), T("clear", pause=0.2), C("help")],
   say="Build it. The first build compiles clap and walkdir. And here's the help screen, generated from our struct: the folder argument, dash dash dry run, and dash r for recursive."),
 dict(id="run_dry", scene="terminal", actions=[T("clear", pause=0.2), C("dry", speed=30), C("find_dry", pause=1.0)],
   say="Now the safe way: a dry run on the fake Downloads. Fourteen files, each with its target folder. Holiday dot JPG, in capitals, goes to Images. README, with no extension, goes to Other. And the old stuff folder isn't touched, because we didn't say recursive. Let's check that nothing moved: the files are all still there."),
 dict(id="run_real", scene="terminal", chapter="Step 7 · Organize for real", actions=[T("clear", pause=0.2), C("real", speed=30), C("find2", speed=30, pause=1.2)],
   say="The plan looks right, so let's do it for real. Moved fourteen files. And find shows the result: Archives, Audio, Code, Documents, Images, Other and Videos, each with the right files inside. Only old stuff is left as it was."),
 dict(id="run_again", scene="terminal", actions=[T("clear", pause=0.2), C("again"), C("rec", pause=0.8), C("docs", pause=1.2)],
   say="Run it again: nothing to sort. Our skip function works, the sorted folders are ignored. Now with recursive, it goes into old stuff too. And look: old stuff slash notes dot txt becomes notes, one in brackets, because Documents already had a notes dot txt. No file was overwritten. You can see both in the Documents folder."),
 dict(id="run_err", scene="terminal", chapter="Step 8 · Errors, release & install", actions=[T("clear", pause=0.2), C("typo", pause=1.0)],
   say="What about a typo in the folder name? Downloads, misspelled. The error from walkdir travels up through the question mark, and main prints one clear line: no such file or directory. No panic, no stack trace."),
 dict(id="release", scene="terminal", actions=[T("clear", pause=0.2), C("release", speed=40), C("size"), C("install"), C("global", d="home", pause=1.2)],
   say="Finally, a release build: an optimized binary of about one point two megabytes. cargo install dash dash path dot installs it into cargo's bin folder, which rustup normally puts on your PATH. And now file organizer works from anywhere."),
 dict(id="outro", scene="title", title="You built a real Rust tool!", subtitle="walkdir  ·  clap  ·  match  ·  PathBuf  ·  error handling with ?", outro=True,
   say="And that's it: a real file organizer in about a hundred and twenty lines. As practice, try adding an undo option, or a flag that sorts files by date instead of by type. All the code is in the description. Subscribe for the next Rust project, and follow the daily Rust shorts to learn each concept on its own. See you in the next one!"),
]
