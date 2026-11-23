# Run each program 5 times; report the median time and the peak memory
import statistics, subprocess, sys

ROUNDS = {
    "collatz": [("Rust", "./rust/target/release/collatz"), ("C (clang)", "./collatz_clang"),
                ("C (gcc)", "./collatz_gcc"), ("Go", "./collatz_go"), ("Java", "java Collatz"),
                ("JavaScript", "node collatz.js"), ("Python", "python3 collatz.py")],
    "wordfreq": [("Rust", "./rust/target/release/wordfreq"), ("Go", "./wordfreq_go"),
                 ("Java", "java WordFreq"), ("JavaScript", "node wordfreq.js"), ("Python", "python3 wordfreq.py")],
    "hello": [("Rust", "./rust/target/release/hello"), ("Go", "./hello_go"), ("Java", "java Hello"),
              ("JavaScript", "node hello.js"), ("Python", "python3 hello.py")],
}

for name in sys.argv[1:]:
    print(f"--- {name} (median of 5 runs) ---")
    for lang, cmd in ROUNDS[name]:
        times, mems = [], []
        for _ in range(5):
            r = subprocess.run(f"/usr/bin/time -f '%e %M' {cmd}", shell=True, capture_output=True, text=True)
            t, kb = r.stderr.strip().split("\n")[-1].split()
            times.append(float(t)); mems.append(int(kb))
        print(f"{lang:<11} {statistics.median(times):6.2f} s   {max(mems) / 1024:7.1f} MB")
