"""Rust Projects #3: a wc clone with tests. Every output comes from captures/cap.json (real run). Clean style."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = json.load(open(os.path.join(HERE, "captures/cap.json")))
def out(k): return CAP[k]["out"]
def src(path): return open(os.path.join(HERE, "project", path)).read().rstrip("\n").split("\n")
def real(k): return float(re.search(r"real\s+\d+m([\d.]+)s", out(k)).group(1))

STYLE = "clean"
PROJECT = "rwc"
FIRST_CHAPTER = "What we're building"
PROMPT_DIR = {"home": "~", "proj": "~/rwc"}
TREE = ["samples/", "samples/notes.txt", "samples/poem.txt", "src/", "src/main.rs", ".gitignore", "Cargo.lock", "Cargo.toml"]
TREE_INITIAL = ["src/", "src/main.rs", ".gitignore", "Cargo.toml"]
TREE_LATER = {"samples/": "samples", "samples/notes.txt": "samples", "samples/poem.txt": "samples", "Cargo.lock": "build_test"}
FILES = {"Cargo.toml": out("cat_toml").split("\n"), "src/main.rs": src("src/main.rs")}
L = lambda needle: next(i + 1 for i, l in enumerate(FILES["src/main.rs"]) if needle in l)
RWC, WC = real("time_rwc"), real("time_wc")

DIAGRAMS = {
 "plan": {"title": "What rwc does",
   "nodes": [{"id": "in", "label": "files or stdin", "sub": "poem.txt · notes.txt · a pipe", "x": 0, "y": 230, "w": 380, "h": 150, "color": "gray"},
             {"id": "read", "label": "read a line", "sub": "read_until(b'\\n')", "mono": True, "x": 440, "y": 230, "w": 360, "h": 150, "color": "blue"},
             {"id": "count", "label": "count", "sub": "lines · words · bytes", "x": 860, "y": 230, "w": 360, "h": 150, "color": "orange"},
             {"id": "out", "label": "print like wc", "sub": "aligned columns + total", "x": 1280, "y": 230, "w": 380, "h": 150, "color": "green"},
             {"id": "tests", "label": "unit tests", "sub": "cargo test checks the counting", "x": 640, "y": 520, "w": 420, "h": 140, "color": "purple"}],
   "edges": [{"src": "in", "dst": "read", "color": "gray"}, {"src": "read", "dst": "count", "color": "gray"}, {"src": "count", "dst": "out", "color": "gray"},
             {"src": "tests", "dst": "count", "label": "verify", "color": "purple"}],
   "notes": [{"text": "Goal: exactly the same output as the real wc", "x": 830, "y": 760, "color": "orange", "size": 30}]},
 "words": {"title": "How words are counted",
   "nodes": [{"id": "line", "label": "\"  one   two  \\n\"", "mono": True, "x": 0, "y": 200, "w": 520, "h": 130, "color": "gray"},
             {"id": "split", "label": "split on whitespace", "sub": "[\"\", \"\", \"one\", \"\", \"\", \"two\", \"\", \"\", \"\"]", "x": 580, "y": 200, "w": 560, "h": 130, "color": "blue"},
             {"id": "keep", "label": "drop the empty pieces", "sub": "[\"one\", \"two\"]  →  2 words", "x": 1200, "y": 200, "w": 460, "h": 130, "color": "green"}],
   "edges": [{"src": "line", "dst": "split", "color": "gray"}, {"src": "split", "dst": "keep", "color": "gray"}],
   "notes": [{"text": "Bytes = the line's length · Lines = how many newline characters", "x": 830, "y": 470, "color": "orange", "size": 30},
             {"text": "We work on raw bytes, so any file works, even if it isn't valid UTF-8", "x": 830, "y": 550, "color": "gray", "size": 26}]},
}

def T(cmd, out="", term=1, d="proj", speed=None, pause=0.6, **kw):
    return dict(kind="cmd", cmd=cmd, out=out, term=term, dir=d, speed=speed, pause=pause, **kw)
def C(k, **kw): return T(CAP[k]["cmd"], out(k), **kw)

SHOTS = [
 dict(id="cold_open", scene="split", actions=[C("wc_both", term=1, pause=1.0), C("run_both", term=2, pause=1.5)],
   say="On the left, wc, the classic Unix tool that counts lines, words and bytes. On the right, our own version, written in Rust in about a hundred lines. Same numbers, same columns, same total. And it comes with tests that prove the counting is right."),
 dict(id="intro", scene="title", title="Rewrite wc in Rust", subtitle="Rust Projects #3  ·  files, stdin, iterators and tests", chips=["Rust", "CLI", "clap", "cargo test"],
   say="Welcome to Rust projects number three. Rebuilding a tool you already know is one of the best ways to learn, because you can check every answer against the original. Today you'll learn to read files and standard input, count with iterators, and write unit tests with cargo test."),
 dict(id="plan", scene="diagram", diagram="plan", chapter="The plan",
   say="Here's the plan. rwc takes files, or standard input from a pipe. It reads one line at a time, counts lines, words and bytes, and prints them in columns exactly like wc. Unit tests check the counting part on its own."),
 dict(id="new", scene="terminal", chapter="Step 1 · Project & clap", actions=[T("clear", d="home", pause=0.2), C("new", d="home"), T("cd rwc", d="home", pause=0.3), C("add_clap", speed=30)],
   say="cargo new rwc, cd into it, and add clap with the derive feature for the command line flags, like in the last two projects."),
 dict(id="samples", scene="terminal", chapter="Step 2 · Test files", actions=[T("clear", pause=0.2), C("samples"), C("notes_a", pause=1.2)],
   say="We need some text to count. A short poem, and a notes file with tricky cases: extra spaces between words, an empty line, and a last line with no newline at the end. cat dash capital A shows a dollar sign at every line end, and you can see the last line has none. Real files look like this all the time."),
 dict(id="code_imports", scene="editor", file="src/main.rs", type=(0, 4), chapter="Step 3 · Arguments",
   say="Now main dot r s. We import Parser from clap, File, and from io: BufRead and BufReader for reading line by line, plus PathBuf for file names."),
 dict(id="code_args", scene="editor", file="src/main.rs", type=(5, 24),
   say="The arguments. files is a vector of paths, so you can pass any number of them. If there are none, we'll read standard input. Then three flags, just like wc: dash l for lines, dash w for words, and dash c for bytes. Each doc comment becomes the help text."),
 dict(id="code_counts", scene="editor", file="src/main.rs", type=(25, 31), chapter="Step 4 · Counting",
   say="A small struct holds the three numbers. Deriving Default gives us all zeros for free, and PartialEq and Debug let our tests compare two Counts and print them if they don't match."),
 dict(id="code_count", scene="editor", file="src/main.rs", type=(32, 49),
   say="This is the heart of the program. count takes any type that implements BufRead, so the same function works for a file, for standard input, and for a plain string in our tests. read until reads up to the next newline into a byte buffer. The bytes are just the line's length. If the line ends with a newline, that's one more line, which is exactly how wc counts. And words: split on whitespace, drop the empty pieces, and count what's left. Then clear the buffer and read the next line."),
 dict(id="words", scene="diagram", diagram="words",
   say="Here's the word trick. Splitting a line with extra spaces gives lots of empty pieces. Filtering out the empty ones leaves the real words. Two spaces in a row never count as an extra word."),
 dict(id="code_input", scene="editor", file="src/main.rs", type=(50, 58), chapter="Step 5 · Files and standard input",
   say="count input picks the source. A dash means standard input, which we lock for fast reading. Anything else is opened as a file and wrapped in a BufReader. The question mark passes any error, like a missing file, back to the caller."),
 dict(id="code_main1", scene="editor", file="src/main.rs", type=(59, 69),
   say="In main, if no flag was given, we show all three columns, like wc. And if no files were given, the input list is just a dash: standard input."),
 dict(id="code_main2", scene="editor", file="src/main.rs", type=(70, 90),
   say="Then the loop. Count each input. On success, add it to the total and keep a row for printing. On error, print a message to standard error, remember that something failed, and keep going with the other files, just like wc does. With more than one input, a total row goes at the end."),
 dict(id="code_print", scene="editor", file="src/main.rs", type=(91, 101), chapter="Step 6 · Printing like wc",
   say="Getting the output identical took a bit of detective work. wc pads every column to the width of the biggest number. When it reads standard input, it uses a width of seven. And with only one column, there's no padding at all."),
 dict(id="code_print2", scene="editor", file="src/main.rs", type=(101, 117),
   say="Then each row is printed. We keep only the columns that should be shown, and the format macro's width dollar sign syntax pads each number to that width. Standard input gets no file name. And if any file failed, we exit with code one."),
 dict(id="code_tests", scene="editor", file="src/main.rs", type=(118, 136), chapter="Step 7 · Unit tests",
   say="And the tests. The cfg test attribute means this module is only compiled for cargo test, never into your program. A tiny helper turns a string into Counts, because a byte slice also implements BufRead. Each test is marked with hash test, and assert eq fails the test if the two values differ. Empty input must be all zeros, and a normal case must give two lines, three words and sixteen bytes."),
 dict(id="code_tests2", scene="editor", file="src/main.rs", type=(136, 153),
   say="Three more tests for the tricky cases: extra spaces are not words, a last line without a newline still counts its words but isn't a line, and an emoji is four bytes in UTF-8."),
 dict(id="build_test", scene="terminal", actions=[T("clear", pause=0.2), C("build", speed=40), T("clear", pause=0.2), C("test", speed=20, pause=1.2)],
   say="Build it, then run cargo test. Five tests, five passed. Now if you change the counting code later, these tests tell you right away if you broke something."),
 dict(id="run_cmp", scene="split", chapter="Step 8 · Compare with the real wc", actions=[T("clear", term=1, pause=0.2), T("clear", term=2, pause=0.2), C("run_poem", term=1), C("run_l", term=1), C("run_stdin", term=1, pause=0.8), C("wc_poem", term=2), C("wc_l", term=2), C("wc_stdin", term=2, pause=1.5)],
   say="Now the real check, rwc on the left and wc on the right. One file: four lines, twenty eight words, a hundred and forty three bytes, on both sides. Only the line count with dash l: four, no padding. And from a pipe, with the wider columns and no file name. Identical every time."),
 dict(id="run_err", scene="terminal", actions=[T("clear", pause=0.2), C("help"), C("run_err", pause=1.2)],
   say="The help screen comes from our struct. And with a file that doesn't exist, rwc prints a clear error for that file, still counts the others, and exits with code one."),
 dict(id="speed", scene="terminal", chapter="Step 9 · Release build & speed", actions=[T("clear", pause=0.2), C("release", speed=40), T("clear", pause=0.2), C("big"), C("time_rwc"), C("time_wc"), C("diff", pause=1.2)],
   say=f"Let's try something bigger. A release build, and a sixty nine megabyte file with two million lines. rwc counts it in {RWC:.2f} seconds. GNU wc takes {WC:.2f}. And diff confirms both give exactly the same output for every file. To be fair, wc also understands Unicode space characters, and ours only splits on ASCII whitespace, so for normal text files the results match."),
 dict(id="install", scene="terminal", actions=[T("clear", pause=0.2), C("install"), C("global", d="home", pause=1.2)],
   say="Finally, cargo install dash dash path dot, and rwc works from anywhere, like any other command."),
 dict(id="outro", scene="title", title="You rebuilt a Unix tool!", subtitle="BufRead  ·  iterators  ·  clap  ·  cargo test", outro=True,
   say="And that's it: a real Unix tool, rebuilt in Rust, tested, and checked against the original. As practice, add a dash m flag that counts characters instead of bytes, and write a test for it first. All the code is in the description. Subscribe for the next Rust project, and see you in the next one!"),
]
