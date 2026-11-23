"""Pre-publish gate for a daily Rust Short: the RUNBOOK rules that check_spec.py does not enforce.
Usage: python3 .claude/skills/rust-short-preflight/preflight.py episodes/YYYY-MM-DD [--date YYYY-MM-DD] [--recheck]
Exit 0 = OK to build/publish, 1 = blocking problems (printed), warnings never block.
"""
import json, re, sys, datetime, pathlib

args = sys.argv[1:]
if not args: sys.exit(__doc__)
ep = pathlib.Path(args[0]); root = pathlib.Path(__file__).resolve().parents[3]
today = args[args.index("--date") + 1] if "--date" in args else \
    datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).date().isoformat()  # Asia/Kolkata
spec = json.loads((ep / "spec.json").read_text())
hist = json.loads((root / "state/history.json").read_text())["posted"]
cur = json.loads((root / "state/curriculum.json").read_text())["lessons"]
errs, warns = [], []

day = spec.get("day")
if not isinstance(day, int): sys.exit(f"FAIL  {ep}/spec.json has no integer 'day': not a curriculum Short")
recheck = "--recheck" in args  # re-check an already-posted episode's content; skips the history gates

# 1. never post twice in a day, never repeat a day
if not recheck and any(h.get("date") == today for h in hist): errs.append(f"history.json already has a post dated {today}: stop, do not publish")
done = {h["day"] for h in hist}
if not recheck and day in done: errs.append(f"day {day} is already in history.json")
nxt = next((l for l in cur if l["day"] not in done), None)
if not recheck and nxt and day != nxt["day"]: errs.append(f"spec is day {day} but the next unposted lesson is day {nxt['day']} ({nxt['title']})")
lesson = next((l for l in cur if l["day"] == day), None)

# 2. theme parity: odd -> ocean, even -> matrix
want = "ocean" if day % 2 else "matrix"
if spec.get("theme") != want: errs.append(f"day {day} is {'odd' if day % 2 else 'even'}: theme must be '{want}', not '{spec.get('theme')}'")

# 3. brand, sources
if spec.get("brand", "").replace(" ", "") != f"RUST·DAY{day}": warns.append(f"brand is '{spec.get('brand')}', expected 'RUST  ·  DAY {day}'")
if lesson and lesson["source"] not in spec.get("sources", []): errs.append(f"sources must include the lesson source {lesson['source']}")

# 4. YouTube text: no < or > anywhere (check_spec only checks the title)
yt = spec.get("youtube", {}); desc = yt.get("description", "")
if "<" in desc or ">" in desc: errs.append("description contains < or > (YouTube rejects them; write -> as →)")
n_tags = len(re.findall(r"#\w", desc))
if not 10 <= n_tags <= 15: warns.append(f"description has {n_tags} hashtags; the template wants 10-13")

# 5. tomorrow teaser matches the following lesson
after = next((l for l in cur if l["day"] == day + 1), None)
if after:
    key = re.sub(r"[^a-z]", "", after["title"].lower())[:10]
    cta = " ".join(sum(([s.get("say", "")] + s.get("question", []) for s in spec.get("scenes", []) if s.get("type") == "cta"), []))
    if key and key not in re.sub(r"[^a-z]", "", cta.lower()): warns.append(f"cta doesn't tease tomorrow's lesson '{after['title']}'")
    if key and key not in re.sub(r"[^a-z]", "", desc.lower()): warns.append(f"description's 'Tomorrow:' line doesn't mention '{after['title']}'")

# 6. scene shape from the runbook
sc = spec.get("scenes", []); types = [s.get("type") for s in sc]
if not 8 <= len(sc) <= 10: warns.append(f"{len(sc)} scenes; the runbook asks for 8-10")
if types[:1] != ["hook"]: errs.append("first scene must be the hook")
if types[-1:] != ["cta"]: errs.append("last scene must be the cta")
if not any(s.get("expect_error") for s in sc): warns.append("no 'expect_error' mistake scene (classic beginner error)")
if "thumbnail" not in spec: errs.append("missing 'thumbnail' block")
else:
    for ln in spec["thumbnail"].get("lines", []):
        if len(ln) > 11: errs.append(f"thumbnail line '{ln}' is {len(ln)} chars; keep it <= 11")
        elif ln != ln.upper() and not re.search(r"\b[iuf]\d+\b|\b[a-z_]+!|::", ln): warns.append(f"thumbnail line '{ln}' isn't CAPS (fine only for code like i32, vec!)")

print(f"preflight {ep} (day {day}, today {today} IST)")
for w in warns: print("  WARN ", w)
for e in errs: print("  FAIL ", e)
print("  OK" if not errs else f"  {len(errs)} blocking problem(s)")
sys.exit(1 if errs else 0)
