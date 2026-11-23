// Longest Collatz chain for a starting number below N
package main

import "fmt"

const N = 1_000_000

func main() {
	bestN, bestLen := uint64(1), 1
	for start := uint64(1); start < N; start++ {
		n, steps := start, 1
		for n != 1 {
			if n%2 == 0 {
				n /= 2
			} else {
				n = 3*n + 1
			}
			steps++
		}
		if steps > bestLen {
			bestN, bestLen = start, steps
		}
	}
	fmt.Printf("%d (%d steps)\n", bestN, bestLen)
}
