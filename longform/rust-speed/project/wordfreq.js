// Top 10 most common words in words.txt
const fs = require("fs");

const text = fs.readFileSync("words.txt", "utf8");
const counts = new Map();
for (const word of text.split(/\s+/)) {
  if (word) counts.set(word, (counts.get(word) || 0) + 1);
}

const top = [...counts].sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1)).slice(0, 10);
for (const [word, n] of top) console.log(word, n);
