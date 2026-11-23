// Count multiples of 7 on 4 goroutines, with a shared counter (a data race!)
package main

import (
	"fmt"
	"sync"
)

func main() {
	count := 0
	var wg sync.WaitGroup
	for w := 0; w < 4; w++ {
		wg.Add(1)
		go func(w int) {
			defer wg.Done()
			for n := w; n < 10_000_000; n += 4 {
				if n%7 == 0 {
					count++
				}
			}
		}(w)
	}
	wg.Wait()
	fmt.Println(count, "(expected 1428572)")
}
