"""Run a long-form project's commands for real and save their exact output.

Usage: python3 longform/engine/capture.py PROJECT_DIR
Reads PROJECT_DIR/capture.json, a list of steps run in order inside a fresh fake home (/home/dev in outputs):
  {"id": "new", "cmd": "cargo new todo-cli", "cwd": "home"}
  {"id": "build", "cmd": "cargo build", "cwd": "proj", "write": ["src/main.rs"]}   # copy files from PROJECT_DIR/project/ first
  {"id": "server", "cmd": "cargo run -q", "cwd": "proj", "background": true, "wait": 3}
  {"kill": "server"}
cwd: "home" (the fake home) or "proj" (home/<PROJECT>, set by "project" at the top of capture.json's first step or
the "project" key of a step). Writes PROJECT_DIR/captures/cap.json: {id: {"cmd", "out", "code"}}.
"""
import json, os, shutil, signal, subprocess, sys, tempfile, time

PD = os.path.abspath(sys.argv[1]); steps = json.load(open(os.path.join(PD, "capture.json")))
proj = next((s["project"] for s in steps if "project" in s), "project")
root = tempfile.mkdtemp(prefix="lf-"); home = os.path.join(root, "dev"); os.makedirs(home)
env = dict(os.environ, CARGO_TERM_COLOR="never", NO_COLOR="1", COLUMNS="100"); env.pop("JAVA_TOOL_OPTIONS", None)  # sandbox-only JVM noise
out, bg = {}, {}
def clean(t): return t.replace(home, "/home/dev").replace(root, "/tmp")
for st in steps:
    if "kill" in st:
        p = bg.pop(st["kill"]); p.send_signal(signal.SIGINT)
        try: o, _ = p.communicate(timeout=10)
        except subprocess.TimeoutExpired: p.kill(); o, _ = p.communicate()
        out[st["kill"]]["out"] = clean(o); out[st["kill"]]["code"] = p.returncode; continue
    if "sleep" in st: time.sleep(st["sleep"]); continue
    cwd = home if st.get("cwd", "proj") == "home" else os.path.join(home, proj)
    for f in st.get("write", []):
        dst = os.path.join(home, proj, f); os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(os.path.join(PD, "project", f), dst)
    for f in st.get("delete", []): os.remove(os.path.join(home, proj, f))
    if st.get("background"):
        p = subprocess.Popen(st["cmd"], shell=True, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, executable="/bin/bash")
        bg[st["id"]] = p; out[st["id"]] = {"cmd": st.get("shown", st["cmd"]), "out": "", "code": None}; time.sleep(st.get("wait", 2)); continue
    t0 = time.time()
    r = subprocess.run(st["cmd"], shell=True, cwd=cwd, env=env, capture_output=True, text=True, timeout=st.get("timeout", 900), executable="/bin/bash")
    o = clean(r.stderr + r.stdout) if st.get("stderr_first", True) else clean(r.stdout + r.stderr)
    out[st["id"]] = {"cmd": st.get("shown", st["cmd"]), "out": o.rstrip("\n"), "code": r.returncode, "secs": round(time.time() - t0, 1)}
    print(f"$ {out[st['id']]['cmd']}  [{r.returncode}, {time.time() - t0:.1f}s]\n{o.rstrip()[-600:]}\n")
    if r.returncode != 0 and not st.get("may_fail"):
        sys.exit(f"step {st['id']} failed (exit {r.returncode}); fix the project or mark the step may_fail")
for k, p in bg.items(): p.kill()
os.makedirs(os.path.join(PD, "captures"), exist_ok=True)
json.dump(out, open(os.path.join(PD, "captures", "cap.json"), "w"), indent=1)
shutil.rmtree(root, ignore_errors=True)
print("captured", len(out), "steps ->", os.path.join(PD, "captures", "cap.json"))
