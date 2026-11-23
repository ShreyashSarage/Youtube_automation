# Make a ~100 MB English-like text file (same seed = same file every time)
import itertools, random

random.seed(42)
letters = "etaoinshrdlcumwfgypbvkjxqz"
weights = [12, 9, 8, 8, 7, 7, 6, 6, 6, 4, 4, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1]
vocab = sorted({"".join(random.choices(letters, weights, k=random.randint(2, 9))) for _ in range(60000)})
random.shuffle(vocab)
zipf = [1 / (r + 1) for r in range(len(vocab))]  # a few words are very common, most are rare
cum = list(itertools.accumulate(zipf))

with open("words.txt", "w") as f:
    size = 0
    while size < 100_000_000:
        line = " ".join(random.choices(vocab, cum_weights=cum, k=12)) + "\n"
        f.write(line); size += len(line)
