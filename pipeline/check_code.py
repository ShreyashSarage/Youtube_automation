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
if errs: print("CODE ERRORS:\n  " + "\n  ".join(errs)); sys.exit(1)
print(f"code ok: {n} code scene(s) compiled")
