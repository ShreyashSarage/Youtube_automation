"""Compile (and run) every code scene so no broken Rust ever reaches the channel.

Per code scene in spec.json:
  "code"   what is shown on screen (short lines)
  "check"  optional full program that contains/extends the shown code (used instead of "code")
  "expect" optional exact stdout the program must print
  "expect_error": "E0384"  the program must FAIL to compile with this error code (for "common mistake" scenes)
Usage: python3 check_code.py EPISODE_DIR
"""
import json, os, subprocess, sys, tempfile, shutil

EP = sys.argv[1]; spec = json.load(open(os.path.join(EP, "spec.json"))); errs = []; n = 0
if not shutil.which("rustc"):
    print("check_code: rustc not found; install with: curl -sSf https://sh.rustup.rs | sh -s -- -y"); sys.exit(1)
for i, sc in enumerate(spec["scenes"]):
    if sc.get("type") != "code": continue
    n += 1; src = sc.get("check") or sc["code"]
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, "main.rs"); open(f, "w").write(src); exe = os.path.join(td, "main")
        r = subprocess.run(["rustc", "--edition", "2021", "-A", "warnings", "-o", exe, f], capture_output=True, text=True)
        want_err = sc.get("expect_error")
        if want_err:
            if r.returncode == 0: errs.append(f"scene {i}: expected compile error {want_err}, but it compiled")
            elif want_err not in r.stderr: errs.append(f"scene {i}: compile failed but not with {want_err}:\n{r.stderr[:600]}")
            continue
        if r.returncode != 0:
            errs.append(f"scene {i}: does not compile (add a full program in \"check\" if the shown code is a snippet):\n{r.stderr[:800]}"); continue
        if "expect" in sc:
            out = subprocess.run([exe], capture_output=True, text=True, timeout=10).stdout
            if out.strip() != sc["expect"].strip(): errs.append(f"scene {i}: output {out.strip()!r} != expected {sc['expect'].strip()!r}")
# ---- "run" scenes: real `cargo run` output (or the real compiler error) for the video
runs = {}
for i, sc in enumerate(spec["scenes"]):
    if sc.get("type") != "run": continue
    j = sc.get("from_code")
    if j is None or j >= len(spec["scenes"]) or spec["scenes"][j].get("type") != "code":
        errs.append(f"scene {i} (run): from_code must point at a code scene"); continue
    src_sc = spec["scenes"][j]; crate = spec.get("crate", "demo")
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["cargo", "new", "-q", "--vcs", "none", crate], cwd=td, check=True)
        pd = os.path.join(td, crate); open(os.path.join(pd, "src", "main.rs"), "w").write(src_sc.get("check") or src_sc["code"])
        r = subprocess.run(["cargo", "run", "-q" if sc.get("quiet") else "--color=never"] + ([] if sc.get("quiet") else []), cwd=pd,
                           capture_output=True, text=True, timeout=300, env=dict(os.environ, CARGO_TERM_COLOR="never"))
        text = (r.stderr + r.stdout).replace(td, "~")
    lines = [l.rstrip() for l in text.split("\n")]
    cut = next((k for k, l in enumerate(lines) if l.startswith("error: could not compile") or l.startswith("For more information")), len(lines))
    lines = lines[:cut]
    while lines and not lines[-1].strip(): lines.pop()
    if len(lines) > 14: errs.append(f"scene {i} (run): output is {len(lines)} lines; keep the example small (max 14)")
    if src_sc.get("expect_error") and r.returncode == 0: errs.append(f"scene {i} (run): expected a compile error")
    runs[str(j)] = {"cmd": "cargo run", "lines": lines[:14], "ok": r.returncode == 0}
os.makedirs(os.path.join(EP, "build"), exist_ok=True)
json.dump({str(i): runs[str(sc["from_code"])] for i, sc in enumerate(spec["scenes"]) if sc.get("type") == "run" and str(sc.get("from_code")) in runs},
          open(os.path.join(EP, "build", "code_runs.json"), "w"), indent=1)
if errs: print("CODE ERRORS:\n  " + "\n  ".join(errs)); sys.exit(1)
print(f"code ok: {n} code scene(s) compiled")
