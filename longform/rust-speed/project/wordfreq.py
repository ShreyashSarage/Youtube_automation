# Top 10 most common words in words.txt
from collections import Counter

with open("words.txt") as f:
    counts = Counter(f.read().split())

top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
for word, n in top:
    print(word, n)
