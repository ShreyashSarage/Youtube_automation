"""Load-test each server the same way and print a results table.

Server on CPU cores 0-1, the load generator (wrk) on cores 2-3, so they don't fight for CPU.
Usage: python3 bench.py [Rust Go Node Python] [--quick]
"""
import json, os, re, signal, socket, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
SERVERS = {
    "Rust":   (["./rust/target/release/server"], HERE),
    "Go":     (["./go/server"], HERE),
    "Node":   (["node", "server.js"], os.path.join(HERE, "node")),
    "Python": (["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8080", "--workers", "2",
                "--log-level", "warning", "--no-access-log"], os.path.join(HERE, "python")),
}
QUICK = "--quick" in sys.argv
DUR = "5s" if QUICK else "15s"
URL = "http://127.0.0.1:8080"

def rss_mb(pgid):
    total = 0
    for pid in os.listdir("/proc"):
        if not pid.isdigit(): continue
        try:
            if os.getpgid(int(pid)) != pgid: continue
            for line in open(f"/proc/{pid}/status"):
                if line.startswith("VmRSS:"): total += int(line.split()[1])
        except (ProcessLookupError, FileNotFoundError, PermissionError): pass
    return total / 1024

def wait_port(timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try: socket.create_connection(("127.0.0.1", 8080), 0.2).close(); return True
        except OSError: time.sleep(0.1)
    return False

def wrk(conns, path, script=None):
    cmd = ["taskset", "-c", "2,3", "wrk", "-t2", f"-c{conns}", f"-d{DUR}", "--latency", "--timeout", "5s"]
    if script: cmd += ["-s", os.path.join(HERE, script)]
    out = subprocess.run(cmd + [URL + path], capture_output=True, text=True).stdout
    num = lambda pat: float(re.search(pat, out).group(1)) if re.search(pat, out) else 0.0
    def ms(pat):
        m = re.search(pat + r"\s+([\d.]+)(us|ms|s)\b", out)
        if not m: return None
        return float(m.group(1)) * {"us": 0.001, "ms": 1, "s": 1000}[m.group(2)]
    errs = sum(int(x) for x in re.findall(r"(?:connect|read|write|timeout) (\d+)", out)) + int(num(r"Non-2xx or 3xx responses: (\d+)"))
    return {"rps": num(r"Requests/sec:\s+([\d.]+)"), "p50": ms("50%"), "p99": ms("99%"), "errors": errs, "raw": out}

results = {}
for name in [a for a in sys.argv[1:] if not a.startswith("--")] or list(SERVERS):
    cmd, cwd = SERVERS[name]
    p = subprocess.Popen(["taskset", "-c", "0,1"] + cmd, cwd=cwd, start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert wait_port(), f"{name} did not start"
    time.sleep(1.5)
    check = subprocess.run(["curl", "-s", URL + "/api/user/42"], capture_output=True, text=True).stdout
    idle = rss_mb(p.pid)
    peak = [idle]; stop = threading.Event()
    def sample():
        while not stop.is_set(): peak[0] = max(peak[0], rss_mb(p.pid)); time.sleep(0.25)
    threading.Thread(target=sample, daemon=True).start()
    wrk(50, "/api/user/1")                       # warm-up (JIT, caches)
    r = {"check": check, "idle_mb": round(idle, 1),
         "get": wrk(100, "/api/user/42"), "post": wrk(100, "/api/orders", "post.lua"), "c1000": wrk(1000, "/api/user/42")}
    stop.set(); r["peak_mb"] = round(peak[0], 1)
    os.killpg(p.pid, signal.SIGTERM); p.wait(timeout=10); time.sleep(1)
    results[name] = r
    g, po, c = r["get"], r["post"], r["c1000"]
    print(f"{name:<7} GET {g['rps']:>9,.0f} req/s p99 {g['p99']} ms | POST {po['rps']:>9,.0f} req/s p99 {po['p99']} ms | "
          f"1000 conns {c['rps']:>9,.0f} req/s p99 {c['p99']} ms errors {c['errors']} | RAM idle {r['idle_mb']} MB peak {r['peak_mb']} MB", flush=True)
json.dump(results, open(os.path.join(HERE, "results.json"), "w"), indent=1)
