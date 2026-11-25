// Go: standard library net/http
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
)

type User struct {
	ID    uint64   `json:"id"`
	Name  string   `json:"name"`
	Email string   `json:"email"`
	Roles []string `json:"roles"`
}

type Order struct {
	Items []struct {
		Price float64 `json:"price"`
		Qty   uint32  `json:"qty"`
	} `json:"items"`
}

func user(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.ParseUint(r.PathValue("id"), 10, 64)
	if err != nil {
		http.Error(w, "bad id", http.StatusBadRequest)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(User{id, fmt.Sprintf("user%d", id),
		fmt.Sprintf("user%d@example.com", id), []string{"reader", "writer"}})
}

func order(w http.ResponseWriter, r *http.Request) {
	var o Order
	if err := json.NewDecoder(r.Body).Decode(&o); err != nil {
		http.Error(w, "bad json", http.StatusBadRequest)
		return
	}
	total := 0.0
	for _, i := range o.Items {
		total += i.Price * float64(i.Qty)
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]any{"items": len(o.Items), "total": total})
}

func main() {
	http.HandleFunc("GET /api/user/{id}", user)
	http.HandleFunc("POST /api/orders", order)
	http.ListenAndServe("127.0.0.1:8080", nil)
}
