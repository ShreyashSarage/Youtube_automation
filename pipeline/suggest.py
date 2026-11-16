"""Suggest a colour theme and topic visuals from a video title/topic.
Usage: python3 suggest.py "Docker in 2.55 ms? Meet Kiri"
The daily run uses this as a starting point, then picks the visuals that best show each scene.
"""
import re, sys

RULES = [  # (keywords, theme, visuals in priority order)
    (r"docker|container|kubernetes|k8s|podman|deploy|wasm|webassembly|cloud", "ocean", ["containers", "race", "layers", "network"]),
    (r"memory|safe|safety|borrow|ownership|lifetime|unsafe|security|cve|vulnerab|leak", "matrix", ["ownership", "shield", "compiler", "layers"]),
    (r"async|await|tokio|thread|concurren|parallel|rayon|channel|future", "neon", ["lanes", "network", "gauge", "race"]),
    (r"kernel|linux|android|windows|os\b|driver|embedded|firmware|chip", "rust", ["layers", "shield", "compiler", "containers"]),
    (r"release|1\.\d+|edition|compiler|rustc|cargo|clippy|stabiliz|rfc|feature", "gold", ["compiler", "tree", "gauge", "shield"]),
    (r"crate|librar|depend|package|ecosystem|framework|orm|serde", "rust", ["tree", "compiler", "network", "race"]),
    (r"web|http|server|api|axum|actix|network|grpc|database|db\b|postgres", "ocean", ["network", "lanes", "gauge", "race"]),
    (r"fast|faster|speed|benchmark|perf|ms\b|\d+x|slow|latency", "rust", ["race", "gauge", "compiler", "lanes"]),
]

def suggest(title):
    t = title.lower(); themes, vis = [], []
    for pat, theme, vs in RULES:
        if re.search(pat, t):
            themes.append(theme); vis += [v for v in vs if v not in vis]
    for v in ["compiler", "race", "tree", "shield"]:
        if v not in vis: vis.append(v)
    return (themes[0] if themes else "rust"), vis[:5]

if __name__ == "__main__":
    theme, vis = suggest(" ".join(sys.argv[1:]))
    print(f"theme: {theme}\nvisuals (best first): {', '.join(vis)}")
