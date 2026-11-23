#!/bin/bash
# Build every program with its normal optimized settings
set -e
(cd rust && cargo build --release -q)          # Rust (release mode)
clang -O2 -o collatz_clang collatz.c           # C with clang (LLVM, like Rust)
gcc -O2 -o collatz_gcc collatz.c               # C with gcc
for p in collatz wordfreq hello race; do
    go build -o ${p}_go $p.go                  # Go
done
javac Collatz.java WordFreq.java Hello.java    # Java (JIT-compiled at run time)
echo "all built"
