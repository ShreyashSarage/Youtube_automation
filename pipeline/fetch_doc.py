"""Print a lesson source as text. Book URLs are read from the Book's Markdown source on GitHub
(doc.rust-lang.org itself may be blocked by the network policy); Rust by Example too.
Usage: python3 fetch_doc.py https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
"""
import re, subprocess, sys, html
url = sys.argv[1]
m = re.match(r"https?://doc\.rust-lang\.org/(stable/)?book/([\w\-]+)\.html", url)
if m: url = f"https://raw.githubusercontent.com/rust-lang/book/main/src/{m.group(2)}.md"
m = re.match(r"https?://doc\.rust-lang\.org/(stable/)?rust-by-example/([\w\-/]+)\.html", url)
if m: url = f"https://raw.githubusercontent.com/rust-lang/rust-by-example/master/src/{m.group(2)}.md"
r = subprocess.run(["curl", "-sSfL", "--retry", "2", "--max-time", "30", url], capture_output=True, text=True)
if r.returncode: sys.exit(f"fetch failed ({url}): {r.stderr.strip()[:200]}. Try WebSearch / the web-fetch agent instead.")
t = r.stdout
if "<html" in t[:2000].lower():
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S); t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"[ \t]+", " ", t)
print(t[:20000])
