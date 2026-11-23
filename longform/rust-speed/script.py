"""Rust vs 5 languages: real benchmarks. Every output and every number comes from captures/cap.json (real runs)."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = json.load(open(os.path.join(HERE, "captures/cap.json")))
def out(k): return CAP[k]["out"]
def src(path): return open(os.path.join(HERE, "project", path)).read().expandtabs(4).rstrip("\n").split("\n")

# ---- official numbers: medians of 5 runs from bench.py
MED = {}; _sec = None
for line in out("bench").split("\n"):
    m = re.match(r"^--- (\w+)", line)
    if m: _sec = m.group(1); MED[_sec] = {}; continue
    m = re.match(r"^(.+?)\s+([\d.]+) s\s+([\d.]+) MB$", line)
    if m: MED[_sec][m.group(1)] = (float(m.group(2)), float(m.group(3)))
def sec(r, l): return MED[r][l][0]
def mb(r, l): return MED[r][l][1]
def real(k): return float(re.search(r"real\s+(\d+)m([\d.]+)s", out(k)).group(2)) + 60 * int(re.search(r"real\s+(\d+)m", out(k)).group(1))
def x(a, b): return a / b
def say_s(v): return f"{v:.2f}".rstrip("0").rstrip(".") if v < 10 else f"{v:.1f}"
R1, R2, R3 = "collatz", "wordfreq", "hello"
PY_X = round(x(sec(R1, "Python"), sec(R1, "Rust")))
JS_X = round(x(sec(R1, "JavaScript"), sec(R1, "Rust")))
MEM_LO = x(mb(R2, "Go"), mb(R2, "Rust")); MEM_HI = x(mb(R2, "Java"), mb(R2, "Rust"))
LOOP, ITER, PAR = real("r4_loop"), real("r4_iter"), real("r4_par")
GO_RACE = [out(f"r4_race_go{i}").split()[0] for i in (1, 2, 3)]
CPU = out("specs").split("\n")[1].split(":", 1)[1].strip()

PROJECT = "speed-test"
FIRST_CHAPTER = "The race"
PROMPT_DIR = {"home": "~", "proj": "~/speed-test"}
FILES_ON_DISK = ["Collatz.java", "Hello.java", "WordFreq.java", "bench.py", "build.sh", "collatz.c", "collatz.go", "collatz.js",
                 "collatz.py", "gen_text.py", "hello.go", "hello.js", "hello.py", "race.go", "wordfreq.go", "wordfreq.js", "wordfreq.py"]
TREE = ["rust/", "rust/collatz/", "rust/collatz/src/", "rust/collatz/src/main.rs", "rust/wordfreq/", "rust/wordfreq/src/", "rust/wordfreq/src/main.rs",
        "rust/collatz_par/", "rust/collatz_par/src/", "rust/collatz_par/src/main.rs", "rust/Cargo.toml"] + FILES_ON_DISK + ["words.txt"]
TREE_INITIAL = [p for p in TREE if p != "words.txt"]
TREE_LATER = {"words.txt": "gen"}
FILES = {f: src(f) for f in ["build.sh", "collatz.py", "collatz.js", "collatz.go", "Collatz.java", "collatz.c", "wordfreq.py", "race.go",
                             "rust/collatz/src/main.rs", "rust/wordfreq/src/main.rs", "rust/collatz_iter/src/main.rs",
                             "rust/collatz_par/src/main.rs", "rust/race/src/main.rs", "rust/Cargo.toml"]}
def line_of(f, needle): return next(i + 1 for i, l in enumerate(FILES[f]) if needle in l)

DIAGRAMS = {
 "rules": {"title": "The rules, so it's a fair fight",
   "nodes": [{"id": "a", "label": "Same algorithm", "sub": "the same loop in every language", "x": 120, "y": 60, "w": 640, "h": 150, "color": "orange"},
             {"id": "b", "label": "Optimized builds", "sub": "cargo --release · clang/gcc -O2 · go build", "x": 900, "y": 60, "w": 640, "h": 150, "color": "blue"},
             {"id": "c", "label": "Same machine", "sub": "4 cores · " + CPU.replace("Intel(R) ", "").replace("(R)", ""), "x": 120, "y": 300, "w": 640, "h": 150, "color": "green"},
             {"id": "d", "label": "Median of 5 runs", "sub": "and a live run of each on screen", "x": 900, "y": 300, "w": 640, "h": 150, "color": "purple"}],
   "edges": [],
   "notes": [{"text": "Normal, idiomatic code: what a regular developer would write", "x": 800, "y": 560, "color": "gray", "size": 30},
             {"text": "All the code is linked in the description", "x": 800, "y": 640, "color": "orange", "size": 30}]},
 "collatz": {"title": "Round 1: the Collatz problem (pure number crunching)",
   "nodes": [{"id": "n", "label": "take a number n", "sub": "start: 1 … 999,999", "x": 40, "y": 220, "w": 400, "h": 150, "color": "gray"},
             {"id": "even", "label": "even?  n / 2", "x": 600, "y": 80, "w": 400, "h": 130, "color": "blue"},
             {"id": "odd", "label": "odd?  3n + 1", "x": 600, "y": 380, "w": 400, "h": 130, "color": "orange"},
             {"id": "one", "label": "until n = 1", "sub": "count the steps", "x": 1160, "y": 220, "w": 440, "h": 150, "color": "green"}],
   "edges": [{"src": "n", "dst": "even", "color": "gray"}, {"src": "n", "dst": "odd", "color": "gray"},
             {"src": "even", "dst": "one", "color": "gray"}, {"src": "odd", "dst": "one", "color": "gray"}],
   "notes": [{"text": "6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1", "x": 800, "y": 600, "color": "purple", "size": 34, "mono": True},
             {"text": "Longest chain below one million?  ≈ 131 million steps of + × ÷ %", "x": 800, "y": 690, "color": "gray", "size": 30}]},
 "why1": {"title": "Why such a big gap? How each language runs your loop",
   "nodes": [{"id": "py", "label": "Python", "sub": "bytecode → interpreter, step by step", "x": 20, "y": 60, "w": 500, "h": 150, "color": "blue"},
             {"id": "jit", "label": "JavaScript · Java", "sub": "JIT: compiles hot code while running", "x": 20, "y": 290, "w": 500, "h": 150, "color": "purple"},
             {"id": "aot", "label": "Rust · C · Go", "sub": "compiled to machine code beforehand", "x": 20, "y": 520, "w": 500, "h": 150, "color": "orange"},
             {"id": "cpu", "label": "CPU", "sub": "runs machine code", "x": 1180, "y": 290, "w": 420, "h": 150, "color": "green"}],
   "edges": [{"src": "py", "dst": "cpu", "label": "many instructions per +", "color": "blue"},
             {"src": "jit", "dst": "cpu", "label": "after warm-up", "color": "purple"},
             {"src": "aot", "dst": "cpu", "label": "directly", "color": "orange"}],
   "notes": [{"text": "Rust = C with clang: both use the LLVM optimizer", "x": 800, "y": 790, "color": "orange", "size": 30}]},
 "words": {"title": "Round 2: count the words in a 96 MB file",
   "nodes": [{"id": "f", "label": "words.txt", "sub": "96 MB · 14 million words", "x": 0, "y": 230, "w": 360, "h": 150, "color": "gray"},
             {"id": "s", "label": "split", "sub": "on spaces & newlines", "x": 430, "y": 230, "w": 340, "h": 150, "color": "blue"},
             {"id": "m", "label": "hash map", "sub": "word → count", "x": 840, "y": 230, "w": 340, "h": 150, "color": "orange"},
             {"id": "t", "label": "sort", "sub": "print the top 10", "x": 1250, "y": 230, "w": 380, "h": 150, "color": "green"}],
   "edges": [{"src": "f", "dst": "s", "color": "gray"}, {"src": "s", "dst": "m", "color": "gray"}, {"src": "m", "dst": "t", "color": "gray"}],
   "notes": [{"text": "Strings, memory allocation, hashing: what real programs do all day", "x": 800, "y": 560, "color": "gray", "size": 30},
             {"text": "49,514 different random words, made by gen_text.py", "x": 800, "y": 640, "color": "purple", "size": 28}]},
 "memory": {"title": f"Why Rust used {MEM_LO:.0f} to {MEM_HI:.0f}x less memory",
   "nodes": [{"id": "txt", "label": "the file in memory", "sub": "one 96 MB string", "x": 560, "y": 20, "w": 560, "h": 130, "color": "gray"},
             {"id": "list", "label": "Python · Java · JS", "sub": "a list of 14 million word objects", "x": 0, "y": 300, "w": 520, "h": 150, "color": "blue"},
             {"id": "go", "label": "Go", "sub": "a list of 14 million slices", "x": 580, "y": 300, "w": 520, "h": 150, "color": "purple"},
             {"id": "rs", "label": "Rust", "sub": "no list: an iterator + &str keys", "x": 1160, "y": 300, "w": 520, "h": 150, "color": "orange"}],
   "edges": [{"src": "txt", "dst": "list", "label": "copies", "color": "blue"}, {"src": "txt", "dst": "go", "label": "points into", "color": "purple"},
             {"src": "txt", "dst": "rs", "label": "borrows", "color": "orange"}],
   "notes": [{"text": "Python's split and Counter are written in C: that's why it beat Java and JavaScript here", "x": 840, "y": 620, "color": "blue", "size": 28},
             {"text": "The JVM also grows its heap freely while RAM is available", "x": 840, "y": 700, "color": "gray", "size": 26}]},
 "why": {"title": "Why Rust is fast: 5 reasons we just measured",
   "nodes": [{"id": "a", "label": "Native code", "sub": "compiled ahead of time by LLVM", "x": 0, "y": 40, "w": 520, "h": 150, "color": "orange"},
             {"id": "b", "label": "No garbage collector", "sub": "memory freed at known points", "x": 580, "y": 40, "w": 520, "h": 150, "color": "blue"},
             {"id": "c", "label": "Borrow, don't copy", "sub": "&str slices instead of copies", "x": 1160, "y": 40, "w": 520, "h": 150, "color": "green"},
             {"id": "d", "label": "Zero-cost abstractions", "sub": "iterator chain = hand-written loop", "x": 290, "y": 300, "w": 520, "h": 150, "color": "purple"},
             {"id": "e", "label": "Fearless parallelism", "sub": "data races are compile errors", "x": 870, "y": 300, "w": 520, "h": 150, "color": "red"}],
   "edges": [],
   "notes": [{"text": "Speed of C, with memory safety checked by the compiler", "x": 840, "y": 600, "color": "orange", "size": 34}]},
 "notfaster": {"title": "Where Rust is NOT faster (be honest)",
   "nodes": [{"id": "a", "label": "Waiting on I/O", "sub": "a 50 ms database call is 50 ms in any language", "x": 0, "y": 40, "w": 800, "h": 140, "color": "gray"},
             {"id": "b", "label": "Libraries written in C", "sub": "numpy, pandas, Counter: Python is quick there", "x": 860, "y": 40, "w": 800, "h": 140, "color": "blue"},
             {"id": "c", "label": "Compile time", "sub": "release builds take seconds to minutes", "x": 0, "y": 260, "w": 800, "h": 140, "color": "purple"},
             {"id": "d", "label": "Time to learn", "sub": "ownership and borrowing take practice", "x": 860, "y": 260, "w": 800, "h": 140, "color": "orange"}],
   "edges": [],
   "notes": [{"text": "Rust: CPU-heavy work, low memory, servers, tools, reliability", "x": 830, "y": 540, "color": "orange", "size": 30},
             {"text": "Python: scripts, data science, quick prototypes", "x": 830, "y": 610, "color": "blue", "size": 30},
             {"text": "Go & Java: great for services too. Pick the tool for the job", "x": 830, "y": 680, "color": "gray", "size": 30}]},
}

def T(cmd, out="", term=1, d="proj", speed=None, pause=0.6, **kw):
    return dict(kind="cmd", cmd=cmd, out=out, term=term, dir=d, speed=speed, pause=pause, **kw)
def C(k, **kw): return T(CAP[k]["cmd"], out(k), **kw)

def bars(r, labels, mem=False):
    bs = []
    for l in labels:
        b = {"label": l, "value": mb(r, l) if mem else sec(r, l)}
        if mem and l != "Rust":
            k = mb(r, l) / mb(r, "Rust"); b["note"] = f"{k:.1f}x more" if k >= 1.15 else (f"{1 / k:.1f}x less" if k <= 0.85 else "≈ same")
        bs.append(b)
    return bs
R1_LANGS = ["Rust", "C (clang)", "C (gcc)", "Go", "Java", "JavaScript", "Python"]
R2_LANGS = ["Rust", "Go", "Python", "Java", "JavaScript"]
R3_LANGS = ["Rust", "Go", "Python", "Java", "JavaScript"]

SHOTS = [
 dict(id="cold_open", scene="chart", chart={"title": "Same algorithm. Same machine. Seven programs.", "sub": "Longest Collatz chain below 1,000,000  ·  real time",
      "bars": bars(R1, R1_LANGS), "mode": "race", "fmt": "{:.2f} s"},
   say=f"Same algorithm, same machine, seven programs. Rust is done in {say_s(sec(R1, 'Rust'))} seconds. C is right there with it. Then Go, then Java. JavaScript needs almost {round(sec(R1, 'JavaScript'))} seconds. And Python? Still going. Still going. {round(sec(R1, 'Python'))} seconds. That's {PY_X} times slower than Rust, for the exact same loop. In this video we'll run four real benchmarks, find out why Rust is this fast, and I'll also show you where Rust is not faster."),
 dict(id="intro", scene="title", title="Rust vs 5 Languages", subtitle="Real benchmarks  ·  real code  ·  no tricks", chips=["Rust", "C", "Go", "Java", "JavaScript", "Python"],
   say="Hey everyone. Everybody says Rust is fast, but how fast, compared to the languages most developers actually use? Today we put Rust against C, Go, Java, JavaScript and Python, in four rounds: pure number crunching, real world text processing, startup and memory, and finally using every CPU core."),
 dict(id="rules", scene="diagram", diagram="rules", chapter="The rules",
   say="First, the rules, so it's a fair fight. Every language runs the same algorithm, written the normal, idiomatic way. Every program is built with its usual optimized settings. Everything runs on the same machine, a four core Xeon. And the official numbers are the median of five runs, but you'll also see a live run of every program on screen."),
 dict(id="setup", scene="terminal", chapter="The setup", actions=[C("specs"), C("versions"), C("ls", pause=1.0)],
   say="Here's the machine: four cores. And the versions: Rust one point ninety seven, Go one point twenty four, Java twenty one, Node twenty two, Python three point thirteen, and clang eighteen for C. In the folder there's one program per language and round, plus a rust folder with the Rust versions."),
 dict(id="buildsh", scene="editor", file="build.sh", show=True, highlight=[4, 5, 6, 8, 10],
   say="This build script compiles everything the way you would for production. Cargo build dash dash release for Rust. Clang and GCC with dash O two for C. Go build for Go. And javac for Java, which then compiles to machine code at run time, with its JIT compiler. Python and JavaScript don't need a build step."),
 dict(id="gen", scene="terminal", actions=[T("clear", pause=0.2), C("gen"), C("build", pause=1.0)],
   say="One more thing: a test file for round two. This little Python script writes ninety six megabytes of random words, always the same ones, thanks to a fixed seed. Then we run the build script. All built. Let's race."),

 # ---------------- round 1
 dict(id="collatz", scene="diagram", diagram="collatz", chapter="Round 1 · Pure CPU",
   say="Round one is pure number crunching: the Collatz problem. Take a number. If it's even, halve it. If it's odd, triple it and add one. Repeat until you reach one, and count the steps. Six takes nine numbers to get there. Our job: find the start below one million with the longest chain. That's about a hundred and thirty one million steps of plain arithmetic, no libraries, nothing to hide behind."),
 dict(id="r1_code", scene="codes", files=["collatz.py", "collatz.js", "collatz.go", "Collatz.java", "collatz.c", "rust/collatz/src/main.rs"], cols=3,
   say="Here's the same program in all six languages: Python, JavaScript, Go, Java, C and Rust. Same two nested loops, same if else, same variables. No tricks like caching results, which would make it much faster in every language."),
 dict(id="r1_rust", scene="editor", file="rust/collatz/src/main.rs", show=True, highlight=[line_of("rust/collatz/src/main.rs", "while n != 1"), line_of("rust/collatz/src/main.rs", "n = if")],
   say="And here's the Rust version up close. A constant N, a for loop over the range one to N, and inside, a while loop. Notice there's not a single type written for n or steps: Rust infers them, starting from the u64 constant. If else is an expression, so it directly gives the new value of n."),
 dict(id="r1_run1", scene="terminal", actions=[T("clear", pause=0.2), C("r1_rust"), C("r1_clang"), C("r1_gcc", pause=1.0)],
   say=f"Let's run it with time in front. Rust: {say_s(real('r1_rust'))} seconds, and the answer, eight three seven seven nine nine, with five hundred and twenty five steps. C compiled with clang: basically identical. C with GCC: a bit slower, {say_s(real('r1_gcc'))} on this run."),
 dict(id="r1_run2", scene="terminal", actions=[T("clear", pause=0.2), C("r1_go"), C("r1_java"), C("r1_js", pause=1.0)],
   say=f"Go: {say_s(real('r1_go'))} seconds. Java: {say_s(real('r1_java'))}, and that includes starting the Java virtual machine. Node with JavaScript: {say_s(real('r1_js'))} seconds. Every language finds the same answer, which proves they all did the same work."),
 dict(id="r1_run3", scene="terminal", actions=[T("clear", pause=0.2), C("r1_py", wait=5.0, wait_badge=f"▶▶ {real('r1_py'):.1f} s real time, sped up", pause=1.2)],
   say=f"And Python. I've sped this part up, because the real run took {real('r1_py'):.1f} seconds. Same answer, same steps, about a hundred times longer."),
 dict(id="r1_chart", scene="chart", chart={"title": "Round 1 · Pure CPU", "sub": "Collatz below 1,000,000  ·  median of 5 runs  ·  lower is better",
      "bars": bars(R1, R1_LANGS), "fmt": "{:.2f} s", "base": "Rust", "foot": "Same algorithm in every language"},
   say=f"Here are the official medians. Rust {say_s(sec(R1, 'Rust'))} seconds, C with clang {say_s(sec(R1, 'C (clang)'))}: that's a tie, within measurement noise. GCC is {x(sec(R1, 'C (gcc)'), sec(R1, 'Rust')):.1f} times slower, Go {x(sec(R1, 'Go'), sec(R1, 'Rust')):.1f}, Java {x(sec(R1, 'Java'), sec(R1, 'Rust')):.1f}. JavaScript is {JS_X} times slower, and Python {PY_X} times."),
 dict(id="why1", scene="diagram", diagram="why1",
   say="Why such a huge gap? It's about how your loop reaches the CPU. Python compiles to bytecode, and an interpreter runs it one step at a time. Every plus and every modulo means checking types and handling number objects, which costs many CPU instructions. JavaScript and Java use a JIT compiler that turns hot loops into machine code while the program runs, so they get close after a warm up. Rust, C and Go are compiled to machine code before the program ever starts. And here's the nice detail: Rust and C with clang tie, because both use the same optimizer, LLVM. Rust really is C speed."),

 # ---------------- round 2
 dict(id="words", scene="diagram", diagram="words", chapter="Round 2 · Real-world data",
   say="But real programs aren't just arithmetic. They read files, split strings, use hash maps. So round two: read a ninety six megabyte text file, split it into its fourteen million words, count each word in a hash map, and print the ten most common. This tests memory allocation, hashing and strings, the stuff real apps do all day."),
 dict(id="r2_code", scene="codes", files=["wordfreq.py", "rust/wordfreq/src/main.rs"], cols=2, max_font=24,
   say="Python can do it in a few lines with Counter. The Rust version is a bit longer, but just as readable. Read the file to a string, split on whitespace, and count with the entry API."),
 dict(id="r2_rust", scene="editor", file="rust/wordfreq/src/main.rs", show=True, highlight=[line_of("rust/wordfreq/src/main.rs", "HashMap<&str"), line_of("rust/wordfreq/src/main.rs", "split_ascii_whitespace")],
   say="One line matters a lot here: the hash map's keys are ampersand str. Those are borrowed slices that point straight into the text we read. Rust never copies a single word. And split ascii whitespace is an iterator: it hands us one word at a time, so there's never a list of fourteen million words in memory. The borrow checker guarantees the text lives longer than the map, so this is completely safe."),
 dict(id="r2_run1", scene="terminal", actions=[T("clear", pause=0.2), C("r2_rust_out", pause=0.8), C("r2_rust", pause=1.0)],
   say=f"Let's run it. Here's the top ten. Now with slash user slash bin slash time, which shows the time and the peak memory: {say_s(real_v := float(out('r2_rust').split()[0]))} seconds, and about {round(int(out('r2_rust').split()[2]) / 1024)} megabytes. Remember, the file alone is ninety six megabytes."),
 dict(id="r2_run2", scene="terminal", actions=[T("clear", pause=0.2), C("r2_go"), C("r2_java"), C("r2_js"), C("r2_py", pause=1.2)],
   say=f"Go: {out('r2_go').split()[0]} seconds and {round(int(out('r2_go').split()[2]) / 1024)} megabytes. Java: {out('r2_java').split()[0]} seconds and almost one and a half gigabytes. JavaScript: {out('r2_js').split()[0]} seconds and a gigabyte. And Python: {out('r2_py').split()[0]} seconds. Wait. Python beat Java and JavaScript?"),
 dict(id="r2_chart", scene="chart", chart={"title": "Round 2 · Time", "sub": "Top 10 words in a 96 MB file  ·  median of 5 runs  ·  lower is better",
      "bars": bars(R2, R2_LANGS), "fmt": "{:.2f} s", "base": "Rust"},
   say=f"Yes, and that's real. Official medians: Rust {say_s(sec(R2, 'Rust'))} seconds, Go {say_s(sec(R2, 'Go'))}, Python {say_s(sec(R2, 'Python'))}, Java {say_s(sec(R2, 'Java'))}, JavaScript {say_s(sec(R2, 'JavaScript'))}. Rust is still the fastest, but the gap to Python shrank from {PY_X} times to under {int(x(sec(R2, 'Python'), sec(R2, 'Rust'))) + 1}."),
 dict(id="r2_mem", scene="chart", chart={"title": "Round 2 · Peak memory", "sub": "Same task  ·  lower is better", "bars": bars(R2, R2_LANGS, mem=True), "fmt": "{:.0f} MB"},
   say=f"Memory is where it gets dramatic. Rust peaks at {round(mb(R2, 'Rust'))} megabytes, basically just the file. Go needs {MEM_LO:.0f} times more. Python, JavaScript and Java need between nine and {MEM_HI:.0f} times more, up to almost one and a half gigabytes."),
 dict(id="memory", scene="diagram", diagram="memory",
   say="Here's why. Python, Java and JavaScript first build a list with fourteen million separate word objects, each with its own header and memory, and a garbage collector has to track all of them. Go is smarter: its strings can point into the original text, but it still builds a list of fourteen million slices. Rust builds no list at all. It borrows. And Python's surprise win? Its split and Counter are written in C, so the hot loop isn't really Python. To be fair to Java, the JVM also grows its heap freely while memory is available."),

 # ---------------- round 3
 dict(id="r3_run", scene="terminal", chapter="Round 3 · Startup & memory", actions=[T("clear", pause=0.2), C("r3_rust"), C("r3_go"), C("r3_java"), C("r3_js"), C("r3_py"), C("r3_size", pause=1.2)],
   say="Round three is quick: just printing hello. This measures what a language costs before your code even runs. Rust and Go start instantly, with about two megabytes. Python needs eleven megabytes for its interpreter. Java and Node need around forty megabytes and a few hundredths of a second, to start a virtual machine. And the Rust binary is just four hundred and thirty five kilobytes, with nothing to install on the target machine."),
 dict(id="r3_chart", scene="chart", chart={"title": "Round 3 · Memory to print \"hello\"", "sub": "Peak memory  ·  median of 5 runs  ·  lower is better",
      "bars": bars(R3, R3_LANGS, mem=True), "fmt": "{:.1f} MB", "foot": "Matters for CLIs, serverless functions and containers"},
   say="Why care about a few megabytes? Command line tools start thousands of times a day. Serverless functions pay for cold starts. And if you run a hundred small containers, forty megabytes each adds up fast. No runtime and no garbage collector means Rust starts like C."),

 # ---------------- round 4
 dict(id="r4_code", scene="codes", chapter="Round 4 · All CPU cores",
      files=[{"file": "rust/collatz_iter/src/main.rs", "title": "collatz_iter: one core", "hl": [line_of("rust/collatz_iter/src/main.rs", "into_iter")]},
             {"file": "rust/collatz_par/src/main.rs", "title": "collatz_par: every core (rayon)", "hl": [line_of("rust/collatz_par/src/main.rs", "use rayon"), line_of("rust/collatz_par/src/main.rs", "into_par_iter")]}], cols=2, max_font=24,
   say="So far everything used one CPU core. But this machine has four. Round four: the Collatz problem again, now up to ten million. On the left, the same work written as an iterator chain: map each number to its chain length, and take the max. On the right, the parallel version with the rayon crate. The only change: into iter becomes into par iter."),
 dict(id="r4_run", scene="terminal", actions=[T("clear", pause=0.2), C("r4_loop"), C("r4_iter"), C("r4_par", pause=1.2)],
   say=f"First the plain for loop version: {say_s(LOOP)} seconds. The iterator version: {say_s(ITER)}. The same speed, because Rust's iterators compile down to the same machine code as the hand written loop. That's what zero cost abstraction means. And now rayon: {say_s(PAR)} seconds. Look at user time: {say_s(float(re.search(r'user\s+0m([\d.]+)s', out('r4_par')).group(1)))} seconds of CPU work, split across four cores."),
 dict(id="r4_chart", scene="chart", chart={"title": "Round 4 · One core vs four", "sub": "Rust, Collatz below 10,000,000  ·  lower is better",
      "bars": [{"label": "for loop", "value": LOOP, "color": (150, 150, 165)}, {"label": "iterator", "value": ITER, "color": (200, 150, 110), "note": "same speed: zero cost"},
               {"label": "rayon", "value": PAR, "color": (222, 105, 50), "note": f"{LOOP / PAR:.1f}x faster"}], "fmt": "{:.2f} s"},
   say=f"{LOOP / PAR:.1f} times faster from one word. Now, to be fair, Go has goroutines and Java has parallel streams, so they can use every core too. What's special in Rust is what happens when you get it wrong."),
 dict(id="r4_race_code", scene="codes",
      files=[{"file": "rust/race/src/main.rs", "title": "race (Rust)", "hl": [line_of("rust/race/src/main.rs", "count += 1")]},
             {"file": "race.go", "title": "race.go (Go)", "hl": [line_of("race.go", "count++")]}], cols=2, max_font=24,
   say="Here's a classic bug. We count the multiples of seven below ten million on every core, but every thread adds to the same shared counter, with no lock. That's a data race. Two threads read the same old value, both add one, and one of the updates is lost. The left is Rust with rayon, the right is the same thing in Go, with four goroutines."),
 dict(id="r4_race", scene="split", actions=[C("r4_race_rs", term=1, pause=1.0), C("r4_race_go1", term=2), C("r4_race_go2", term=2), C("r4_race_go3", term=2, pause=1.2)],
   say=f"Rust refuses to compile it. Error E zero five nine four: cannot assign to count, it's a captured variable in an F n closure. In other words, many threads might touch this at once, so fix it first. Go compiles it happily. We run it: {GO_RACE[0]}. Again: {GO_RACE[1]}. And again: {GO_RACE[2]}. The right answer is one million, four hundred twenty eight thousand, five hundred seventy two. A different wrong answer every time, and in a real app this would be a bug you might never reproduce. Go does have a race detector, but you have to remember to run it, and it only finds races that actually happen during that run. Rust checks every single build."),

 # ---------------- why / not faster
 dict(id="why", scene="diagram", diagram="why", chapter="Why Rust is fast",
   say="So, why is Rust fast? Five reasons, and we've just measured every one of them. One: native code, compiled ahead of time by LLVM, the same optimizer as clang. Two: no garbage collector. Memory is freed at points the compiler knows, so there are no pauses and no extra heap. Three: borrow, don't copy, like the ampersand str keys that saved a gigabyte. Four: zero cost abstractions. The iterator ran exactly as fast as the loop. And five: fearless parallelism. The compiler turns data races into compile errors."),
 dict(id="notfaster", scene="diagram", diagram="notfaster", chapter="Where Rust is NOT faster",
   say="But let's be honest about where Rust doesn't win. If your app spends its time waiting on a database or the network, a fifty millisecond query takes fifty milliseconds in any language. When Python calls libraries written in C, like numpy, pandas, or that Counter from round two, it can be quick. Rust's compile times are real; big projects take minutes to build. And ownership and borrowing take some practice to learn. So: Rust for CPU heavy work, low memory, servers, tools and reliability. Python for scripts, data science and prototypes. Go and Java are great for services too. Pick the tool for the job."),
 dict(id="outro", scene="title", title="Rust: C speed, memory safe", subtitle=f"= C on CPU  ·  {PY_X}x faster than Python  ·  up to {MEM_HI:.0f}x less memory", outro=True,
   say=f"So, is Rust faster? On pure CPU work it matched C, and beat Python by {PY_X} times. On real text processing it was fastest, with up to {MEM_HI:.0f} times less memory. It starts instantly, and it caught a data race at compile time. All the code is linked in the description, so run it on your machine and tell me your numbers in the comments. If you want to learn Rust from zero, follow my daily Rust shorts. Subscribe for more, and see you in the next one!"),
]
