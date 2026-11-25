"""How many requests can Rust handle? Rust vs Go vs Node vs Python web servers.
Terminal output comes from captures/cap.json (real runs); charts use the medians of project/results/run1-3.json."""
import json, os, re, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = json.load(open(os.path.join(HERE, "captures/cap.json")))
RUNS = [json.load(open(os.path.join(HERE, f"project/results/run{i}.json"))) for i in (1, 2, 3)]
def out(k): return CAP[k]["out"]
def src(path): return open(os.path.join(HERE, "project", path)).read().expandtabs(4).rstrip("\n").split("\n")

LANGS = ["Rust", "Go", "Node", "Python"]
def med(lang, test, key): return st.median(r[lang][test][key] for r in RUNS)
def mem(lang, key): return st.median(r[lang][key] for r in RUNS)
GET = {l: med(l, "get", "rps") for l in LANGS}
GET99 = {l: med(l, "get", "p99") for l in LANGS}
POST = {l: med(l, "post", "rps") for l in LANGS}
C1K = {l: med(l, "c1000", "rps") for l in LANGS}
C1K99 = {l: med(l, "c1000", "p99") for l in LANGS}
C1KERR = {l: med(l, "c1000", "errors") for l in LANGS}
IDLE = {l: mem(l, "idle_mb") for l in LANGS}
PEAK = {l: mem(l, "peak_mb") for l in LANGS}
def live_rps(k): return float(re.search(r"Requests/sec:\s+([\d.]+)", out(k)).group(1))
def k(v): return f"{v / 1000:.0f} thousand"
X_NODE = GET["Rust"] / GET["Node"]; X_PY = GET["Rust"] / GET["Python"]; X_GO = GET["Rust"] / GET["Go"]

PROJECT = "web-bench"
FIRST_CHAPTER = "The race"
PROMPT_DIR = {"home": "~", "proj": "~/web-bench"}
TREE = ["go/", "go/go.mod", "go/main.go", "node/", "node/package.json", "node/server.js", "python/", "python/app.py", "python/app_sync.py",
        "rust/", "rust/src/", "rust/src/main.rs", "rust/Cargo.toml", "bench.py", "post.lua"]
TREE_INITIAL = TREE
FILES = {f: src(f) for f in ["rust/src/main.rs", "go/main.go", "node/server.js", "python/app.py", "python/app_sync.py", "post.lua", "rust/Cargo.toml"]}
def line_of(f, needle): return next(i + 1 for i, l in enumerate(FILES[f]) if needle in l)

DIAGRAMS = {
 "setup": {"title": "A fair fight: the same machine, split in two",
   "nodes": [{"id": "wrk", "label": "wrk (load generator)", "sub": "CPU cores 2 and 3", "x": 20, "y": 200, "w": 520, "h": 160, "color": "gray"},
             {"id": "srv", "label": "the server under test", "sub": "CPU cores 0 and 1", "x": 1100, "y": 200, "w": 540, "h": 160, "color": "orange"},
             {"id": "e1", "label": "GET /api/user/42", "sub": "build a user, send JSON", "mono": False, "x": 560, "y": 480, "w": 520, "h": 120, "color": "blue"},
             {"id": "e2", "label": "POST /api/orders", "sub": "parse 10 items, send the total", "x": 560, "y": 640, "w": 520, "h": 120, "color": "green"}],
   "edges": [{"src": "wrk", "dst": "srv", "label": "HTTP on localhost", "color": "gray"}],
   "notes": [{"text": "Warm-up first · 15 s per test · 3 full runs · we use the median", "x": 830, "y": 60, "color": "purple", "size": 30}]},
 "why": {"title": "Why Rust (and Go) pull ahead here",
   "nodes": [{"id": "a", "label": "Compiled to machine code", "sub": "Rust & Go: no interpreter, no warm-up", "x": 0, "y": 40, "w": 800, "h": 140, "color": "orange"},
             {"id": "b", "label": "No garbage collector", "sub": "Rust: no GC pauses, tiny memory", "x": 860, "y": 40, "w": 800, "h": 140, "color": "blue"},
             {"id": "c", "label": "Every core, every request", "sub": "tokio & goroutines share all threads", "x": 0, "y": 250, "w": 800, "h": 140, "color": "green"},
             {"id": "d", "label": "Node & Python: one process per core", "sub": "a full runtime copy in each worker", "x": 860, "y": 250, "w": 800, "h": 140, "color": "purple"}],
   "edges": [],
   "notes": [{"text": "Go's lower tail latency at 1000 connections: most likely its fair, preemptive scheduler", "x": 830, "y": 520, "color": "gray", "size": 26}]},
 "reality": {"title": "Does this matter for YOUR app?",
   "nodes": [{"id": "fw", "label": "framework overhead", "sub": "microseconds per request", "x": 40, "y": 80, "w": 700, "h": 140, "color": "orange"},
             {"id": "db", "label": "database query", "sub": "often milliseconds", "x": 920, "y": 80, "w": 700, "h": 140, "color": "blue"},
             {"id": "y", "label": "Rust pays off when…", "sub": "huge traffic · many servers · low memory · steady latency", "x": 40, "y": 330, "w": 1580, "h": 140, "color": "green"}],
   "edges": [],
   "notes": [{"text": "For a small CRUD app, the database is usually the bottleneck. Pick what your team ships fastest.", "x": 830, "y": 600, "color": "gray", "size": 28}]},
}

def T(cmd, out="", term=1, d="proj", speed=None, pause=0.6, **kw):
    return dict(kind="cmd", cmd=cmd, out=out, term=term, dir=d, speed=speed, pause=pause, **kw)
def C(k_, **kw): return T(CAP[k_]["cmd"], out(k_), **kw)
def WRK(k_, **kw): return C(k_, wait=4.0, wait_badge="▶▶ 15 s load test, sped up", speed=30, **kw)
COL = {"Rust": (222, 105, 50), "Go": (60, 175, 200), "Node": (120, 190, 90), "Python": (70, 120, 200)}
def bars(d, unit, more=True, extra=None):
    bs = []
    for l in LANGS:
        b = {"label": l, "value": d[l], "color": COL[l]}
        if l != "Rust":
            r = d["Rust"] / d[l] if more else d[l] / d["Rust"]
            b["note"] = (f"Rust: {r:.1f}x more" if more else f"{r:.1f}x more") if r >= 1.1 else (f"{1 / r:.1f}x {'more than Rust' if more else 'less'}" if r <= 0.9 else "≈ same")
        if extra: b["note"] = extra(l, b.get("note"))
        bs.append(b)
    return bs

SHOTS = [
 dict(id="cold_open", scene="chart", chart={"title": "Requests served in 10 seconds", "sub": "Same API, same machine, 100 users hammering it  ·  median of 3 runs",
      "bars": [{"label": l, "value": GET[l], "color": COL[l]} for l in LANGS], "mode": "rate", "seconds": 10, "fmt": "{:,.0f}"},
   say=f"Same API, same machine, a hundred users hammering it for ten seconds. Rust serves one point six million requests. Go, about a million. Node and Python? Around one hundred seventy thousand. That's {X_NODE:.0f} times fewer. Today: a real load test of Rust, Go, Node and Python web servers, and the one test where Rust did not win."),
 dict(id="intro", scene="title", title="How Many Requests Can Rust Handle?", subtitle="Rust vs Go vs Node vs Python  ·  real load test", chips=["Rust · Axum", "Go", "Node · Express", "Python · FastAPI"],
   say="Hey everyone. My last video benchmarked Rust against five languages on raw number crunching, and lots of you asked: what about web servers, where most of us actually work? So I built the same tiny API in Rust, Go, Node and Python, and hit each one with up to a thousand simultaneous connections."),
 dict(id="setup", scene="diagram", diagram="setup", chapter="The fair setup",
   say="Here's how to make it fair. This machine has four CPU cores. The server gets two of them, and the load generator, a tool called wrk, gets the other two, so they never fight over the CPU. Every server has the same two endpoints: a GET that builds a user and returns JSON, and a POST that parses an order with ten items and returns the total. Every test starts with a warm-up, runs for fifteen seconds, and the whole benchmark ran three times. The charts show the median."),
 dict(id="specs", scene="terminal", actions=[C("specs"), C("versions"), C("ls", pause=1.0)],
   say="The setup: four cores and wrk four point one. Rust one point ninety seven with Axum, Go one point twenty four with its standard library, Node twenty two with Express five, and Python with FastAPI on uvicorn. One folder per language."),
 dict(id="code_all", scene="codes", chapter="The four servers", files=[{"file": "rust/src/main.rs", "title": "Rust · Axum"}, {"file": "go/main.go", "title": "Go · net/http"},
      {"file": "node/server.js", "title": "Node · Express 5"}, {"file": "python/app.py", "title": "Python · FastAPI"}], cols=2, max_font=20,
   say="Here are all four, side by side. Same routes, same JSON. Each one is written the way that framework's docs recommend. And because Node and Python run one process per CPU core, they get one worker per core: Node through its cluster module, Python through uvicorn's workers flag. Rust and Go use every core from a single process."),
 dict(id="code_rust", scene="editor", file="rust/src/main.rs", show=True, highlight=[line_of("rust/src/main.rs", "async fn user"), line_of("rust/src/main.rs", ".route(\"/api/user")],
   say="The Rust version up close. Serde derives turn the structs into JSON and back. Each handler is an async function, and Axum's extractors, Path and Json, parse the request for us, with types checked at compile time. The router maps the two routes, and tokio runs it all on every core."),
 dict(id="builds", scene="terminal", actions=[T("clear", pause=0.2), C("build_rust", speed=20), C("build_go"), C("build_node", pause=1.0)],
   say="Build everything. Rust in release mode, Go with go build, and npm install for Express. Python needs no build step."),

 # ---- round 1: GET
 dict(id="run_rust", scene="terminal", chapter="Round 1 · GET JSON", actions=[T("clear", pause=0.2), C("rust_start"), C("rust_curl"), C("rust_warm"), WRK("rust_get", pause=1.2)],
   say="Round one. Start the Rust server, pinned to cores zero and one. A quick curl shows the JSON. Warm up for five seconds, and then the real test: a hundred connections, for fifteen seconds.",
   say2=f"{live_rps('rust_get') / 1000:.0f} thousand requests per second. And ninety nine percent of requests were answered within about a millisecond and a half."),
 dict(id="run_go", scene="terminal", actions=[T("clear", pause=0.2), C("go_start"), C("go_warm"), WRK("go_get", pause=1.2)],
   say="Next, Go, with nothing but its standard library. Same warm-up, same test.",
   say2=f"{live_rps('go_get') / 1000:.0f} thousand requests per second. Very fast too."),
 dict(id="run_node", scene="terminal", actions=[T("clear", pause=0.2), C("node_start"), C("node_warm"), WRK("node_get", pause=1.2)],
   say="Node, with Express and one worker per core.",
   say2=f"{live_rps('node_get') / 1000:.0f} thousand requests per second."),
 dict(id="run_py", scene="terminal", actions=[T("clear", pause=0.2), C("python_start"), C("python_warm"), WRK("python_get", pause=1.2)],
   say="And Python: FastAPI, with two uvicorn workers.",
   say2=f"{live_rps('python_get') / 1000:.0f} thousand. Basically tied with Node."),
 dict(id="chart_get", scene="chart", chart={"title": "Round 1 · GET /api/user/42", "sub": "Requests per second  ·  100 connections  ·  median of 3 runs  ·  higher is better",
      "bars": bars(GET, "req/s"), "fmt": "{:,.0f}"},
   say=f"The official medians. Rust: {k(GET['Rust'])} requests per second. Go: {k(GET['Go'])}. Node: {k(GET['Node'])}, and Python: {k(GET['Python'])}. So Rust handled {X_GO:.1f} times more than Go, and about {X_NODE:.0f} times more than Node or Python, on the same two CPU cores."),
 dict(id="chart_get99", scene="chart", chart={"title": "Round 1 · Slowest 1% of requests (p99)", "sub": "Milliseconds  ·  lower is better",
      "bars": [{"label": l, "value": GET99[l], "color": COL[l]} for l in LANGS], "fmt": "{:.1f} ms"},
   say=f"Speed isn't just throughput, it's also how long your slowest users wait. P ninety nine means ninety nine percent of requests finished faster than this. Rust: {GET99['Rust']:.1f} milliseconds. Go: {GET99['Go']:.1f}. Python: {GET99['Python']:.0f}, and Node: {GET99['Node']:.0f}."),

 # ---- round 2: POST
 dict(id="post_lua", scene="editor", file="post.lua", show=True, highlight=[2, 6], chapter="Round 2 · POST + parsing",
   say="Round two sends real work the other way. This small wrk script turns every request into a POST with a JSON order of ten items. The server has to parse the JSON into typed objects, validate it, add up the prices, and send back the total."),
 dict(id="chart_post", scene="chart", chart={"title": "Round 2 · POST /api/orders", "sub": "Parse 10 items, return the total  ·  requests per second  ·  higher is better",
      "bars": bars(POST, "req/s"), "fmt": "{:,.0f}"},
   say=f"Parsing costs everyone something. Rust still handles {k(POST['Rust'])} requests per second, Go {k(POST['Go'])}, and Node and Python around {k((POST['Node'] + POST['Python']) / 2)}. Rust's lead over Go actually grows here, to {POST['Rust'] / POST['Go']:.1f} times, because serde parses JSON straight into the struct with no runtime reflection."),

 # ---- round 3: 1000 connections
 dict(id="c1000_rust", scene="terminal", chapter="Round 3 · 1000 users at once", actions=[T("clear", pause=0.2), C("rust_start"), C("rust_warm"), WRK("rust_c1000", pause=1.2)],
   say="Round three: a traffic spike. A thousand connections at the same time, starting with Rust.",
   say2="Rust keeps going at the same rate, and its slowest one percent take around forty milliseconds."),
 dict(id="c1000_node", scene="terminal", actions=[T("clear", pause=0.2), C("node_start"), C("node_warm"), WRK("node_c1000", pause=1.2)],
   say="Now Node, with the same thousand connections.",
   say2=f"Median latency is fine, but the slowest one percent waited over two and a half seconds. And look at the red line: {re.search(r'timeout (\d+)', out('node_c1000')).group(1)} requests timed out after five seconds. Those users saw an error."),
 dict(id="chart_c1000", scene="chart", chart={"title": "Round 3 · 1000 connections", "sub": "Requests per second  ·  higher is better",
      "bars": bars(C1K, "req/s", extra=lambda l, n: (n or "") + (f"  ·  ~{C1KERR[l]:.0f} timeouts" + (" (2 of 3 runs)" if l == "Python" else "") if C1KERR[l] else "")), "fmt": "{:,.0f}"},
   say=f"Throughput at a thousand connections: Rust {k(C1K['Rust'])}, Go {k(C1K['Go'])}, Node {k(C1K['Node'])}, Python {k(C1K['Python'])}. Rust and Go had zero timeouts in every run. Node dropped about four hundred requests in every run, and Python a few hundred in two of the three runs."),
 dict(id="chart_c1000_99", scene="chart", chart={"title": "Round 3 · p99 latency at 1000 connections", "sub": "Milliseconds  ·  lower is better",
      "bars": [{"label": l, "value": C1K99[l], "color": COL[l], **({"note": "lowest!"} if l == "Go" else {})} for l in LANGS], "fmt": "{:,.0f} ms"},
   say=f"And here's the test Rust didn't win. With a thousand connections, Go's slowest one percent took about {C1K99['Go']:.0f} milliseconds, and Rust's about {C1K99['Rust']:.0f}. Rust did far more work per second, but Go's scheduler shares time between connections more evenly. Both are excellent. Node and Python were above two seconds."),

 # ---- round 4: memory
 dict(id="chart_mem", scene="chart", chapter="Round 4 · Memory", chart={"title": "Round 4 · Peak memory under load", "sub": "All processes of the server  ·  lower is better",
      "bars": [{"label": l, "value": PEAK[l], "color": COL[l], "note": f"idle {IDLE[l]:.1f} MB"} for l in LANGS], "fmt": "{:.0f} MB"},
   say=f"Round four: memory. Rust started at {IDLE['Rust']:.1f} megabytes and peaked at about {PEAK['Rust']:.0f}, during the thousand connection test. Go peaked at {PEAK['Go']:.0f}. Python at {PEAK['Python']:.0f}, and Node at almost {PEAK['Node']:.0f} megabytes, about {PEAK['Node'] / PEAK['Rust']:.0f} times Rust. If you run many containers or pay per gigabyte, that's real money."),

 # ---- the Python fix
 dict(id="py_fix_code", scene="codes", chapter="Configure it right (the Python fix)",
      files=[{"file": "python/app_sync.py", "title": "app_sync.py: plain def", "hl": [line_of("python/app_sync.py", "def user"), line_of("python/app_sync.py", "def order")]},
             {"file": "python/app.py", "title": "app.py: async def", "hl": [line_of("python/app.py", "async def user"), line_of("python/app.py", "async def order")]}], cols=2, max_font=22,
   say="Now a confession. My first Python run was terrible, and it was my fault. On the left, the handlers are plain def functions, so FastAPI runs each one in a thread pool. And I had installed plain uvicorn, without the fast event loop. On the right: async def, and uvicorn with its standard extras, uvloop and httptools. That's what FastAPI's docs recommend."),
 dict(id="py_fix_run", scene="terminal", actions=[T("clear", pause=0.2), C("slow_start"), WRK("slow_get", pause=1.2)],
   say="Here is the slow setup, for real.",
   say2=f"{live_rps('slow_get'):,.0f} requests per second, with almost fifty milliseconds per request."),
 dict(id="py_fix_chart", scene="chart", chart={"title": "Same FastAPI app, two setups", "sub": "GET requests per second  ·  higher is better",
      "bars": [{"label": "plain def", "value": live_rps("slow_get"), "color": (110, 110, 130)},
               {"label": "async def", "value": live_rps("python_get"), "color": COL["Python"], "note": f"{live_rps('python_get') / live_rps('slow_get'):.0f}x faster"}], "fmt": "{:,.0f}"},
   say=f"And the recommended setup: {live_rps('python_get'):,.0f}. That's {live_rps('python_get') / live_rps('slow_get'):.0f} times faster from two small changes. So before you rewrite anything in Rust, make sure your current stack is configured properly."),

 # ---- why + reality
 dict(id="why", scene="diagram", diagram="why", chapter="Why Rust wins (and when it doesn't matter)",
   say="So why do Rust and Go pull so far ahead? Both compile to machine code, so there's no interpreter and no warm-up. Rust has no garbage collector, which keeps memory tiny and avoids pauses. And both share every core across all requests from one process, while Node and Python run a full copy of their runtime in each worker. Go's lower tail latency most likely comes from its scheduler, which preempts goroutines to share time fairly between connections."),
 dict(id="reality", scene="diagram", diagram="reality",
   say="But be realistic. Rust spends a few microseconds of framework time per request. A database query often takes milliseconds. So for a small CRUD app, your database is the bottleneck, and the best choice is whatever your team ships fastest. Rust pays off with huge traffic, when you run many servers, when memory is tight, or when latency must stay steady under spikes."),
 dict(id="outro", scene="title", title="Rust: 9x more requests than Node", subtitle=f"{k(GET['Rust'])} req/s  ·  {PEAK['Rust']:.0f} MB peak  ·  Go won tail latency", outro=True,
   say="So, how many requests can Rust handle? On two CPU cores, about a hundred and sixty thousand per second, with twenty six megabytes of memory. Go came close and won on tail latency, and a well configured FastAPI matched Express. All the code is in the description, so run it on your machine and post your numbers in the comments. Want Rust versus C plus plus or Zig next? Tell me. Subscribe, and see you in the next one!"),
]
