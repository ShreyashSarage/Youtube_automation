// Top 10 most common words in words.txt
package main

import (
	"fmt"
	"os"
	"sort"
	"strings"
)

func main() {
	data, err := os.ReadFile("words.txt")
	if err != nil {
		panic(err)
	}
	counts := map[string]int{}
	for _, word := range strings.Fields(string(data)) {
		counts[word]++
	}

	type kv struct {
		word string
		n    int
	}
	var all []kv
	for w, n := range counts {
		all = append(all, kv{w, n})
	}
	sort.Slice(all, func(i, j int) bool {
		if all[i].n != all[j].n {
			return all[i].n > all[j].n
		}
		return all[i].word < all[j].word
	})
	for _, e := range all[:10] {
		fmt.Println(e.word, e.n)
	}
}
