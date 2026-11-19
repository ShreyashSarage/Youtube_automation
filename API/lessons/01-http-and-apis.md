# Lesson 1 — How Machines Talk: HTTP & APIs

**Time:** ~2 hours · **Theory:** 20 min · **Hands-on:** 90 min · **Quiz gate:** 10 min
**Why this comes first:** every later topic (Rust APIs, scaling, IoT security) is built on HTTP. Get this solid and everything else gets easier.

---

## Part A — Theory (the 20%)

### 1. What an API actually is
**API (Application Programming Interface)** = a contract that says: *"send me a request shaped like this, and I'll send you a response shaped like that."*

> **Analogy — the restaurant.** You (the **client**) don't walk into the kitchen (the **server**/database).
> You read the **menu** (API documentation), tell the **waiter** (the API) your order in a fixed format,
> and get your food (the **response**). The kitchen can change its ovens tomorrow — as long as the menu stays the same, you never notice.
> That's the real power of APIs: **they hide implementation behind a stable contract.**

### 2. HTTP = the language most APIs speak
Every HTTP exchange is just **text** going one way, then text coming back.

**Request:**
```
POST /devices HTTP/1.1              ← method, path, version   (WHAT you want)
Host: api.example.com               ← headers                  (metadata about the request)
Content-Type: application/json
Authorization: Bearer eyJhbGc...
                                    ← blank line = headers are over
{"name": "thermostat-1"}            ← body                     (the data)
```

**Response:**
```
HTTP/1.1 201 Created                ← status line              (DID it work?)
Content-Type: application/json
Location: /devices/42

{"id": 42, "name": "thermostat-1"}
```

> **Analogy — the envelope.** Method + path = the address on the envelope. Headers = stamps and labels
> ("fragile", "from: Alice", "language: JSON"). Body = the letter inside.

### 3. The methods you'll use 95% of the time
| Method | Meaning | Safe? (no changes) | Idempotent? (repeat = same result) |
|---|---|---|---|
| `GET` | Read | ✅ | ✅ |
| `POST` | Create / trigger action | ❌ | ❌ |
| `PUT` | Replace entirely | ❌ | ✅ |
| `PATCH` | Partially update | ❌ | ❌ (usually) |
| `DELETE` | Remove | ❌ | ✅ |

> **Idempotency — the elevator button.** Pressing "Floor 5" ten times still takes you to floor 5 once. That's idempotent (`PUT`, `DELETE`).
> Ordering a pizza ten times gets you ten pizzas. Not idempotent (`POST`).
> **Why you care:** networks fail. If a request times out, can the client safely retry? Only if it's idempotent. This idea returns in Scaling (retries) and IoT (flaky device networks).

### 4. Status codes — learn the families, then the top 12
- **2xx** = it worked · **3xx** = go elsewhere · **4xx** = *you* (client) messed up · **5xx** = *I* (server) messed up

| Code | When |
|---|---|
| 200 OK | Success with body |
| 201 Created | Resource created (with `Location` header) |
| 204 No Content | Success, nothing to return (often DELETE) |
| 301/308 | Moved permanently |
| 400 Bad Request | Malformed input |
| 401 Unauthorized | **Who are you?** (not authenticated) |
| 403 Forbidden | **I know who you are — and no.** (not authorized) |
| 404 Not Found | Doesn't exist (or you're not allowed to know it does) |
| 409 Conflict | Clashes with current state (duplicate, version mismatch) |
| 422 Unprocessable | Well-formed but invalid (e.g. temperature = "banana") |
| 429 Too Many Requests | Rate limited — slow down |
| 500 / 503 | Server bug / server overloaded or down |

> **401 vs 403 — the nightclub.** 401: the bouncer says "show me your ID." 403: the bouncer read your ID and says "you're not on the list."
> Mixing these up is one of the most common interview and security-review mistakes.

### 5. Statelessness
HTTP is **stateless**: each request must carry everything the server needs (who you are, what you want). The server doesn't "remember" you between requests — that's why you send the `Authorization` header every time.
> **Why it matters later:** statelessness is *the* reason APIs can scale horizontally — any of 50 servers can answer any request. (Module 5.)

---

## Part B — Hands-on (the 80%)

**Setup:** you need a terminal with `curl` and `jq` (`sudo apt install curl jq` / `brew install curl jq` / on Windows use WSL).
Create `labs/lesson01/notes.md` and record every command + what you observed.

### Exercise 1 — See the raw conversation (15 min)
```bash
curl -v https://httpbin.org/get
```
- Lines starting `>` are what **you sent**. `<` is what **came back**. `*` is connection/TLS info.
- ✍️ Write down: the method, path, every request header, the status code, and the `Content-Type` of the response.
- ✍️ Find the line where TLS is negotiated. Which TLS version was used? (Hint: grep the `*` lines.)

### Exercise 2 — Every method (20 min)
```bash
curl -s https://httpbin.org/get?device=lamp | jq
curl -s -X POST   https://httpbin.org/post   -H 'Content-Type: application/json' -d '{"temp": 21.5}' | jq
curl -s -X PUT    https://httpbin.org/put    -H 'Content-Type: application/json' -d '{"name":"lamp","on":true}' | jq
curl -s -X PATCH  https://httpbin.org/patch  -H 'Content-Type: application/json' -d '{"on":false}' | jq
curl -s -X DELETE https://httpbin.org/delete -i
```
- ✍️ In the POST output, where does httpbin show your body? (`json` vs `data` fields — what's the difference?)
- ✍️ Repeat the POST **without** the `Content-Type` header. What changes? Why does this matter to a server?

### Exercise 3 — Provoke status codes (15 min)
```bash
for code in 200 201 204 400 401 403 404 409 422 429 500 503; do
  printf "%s -> " $code; curl -s -o /dev/null -w "%{http_code}\n" https://httpbin.org/status/$code
done
curl -i https://httpbin.org/basic-auth/alice/secret                 # no credentials
curl -i -u alice:wrong  https://httpbin.org/basic-auth/alice/secret # wrong credentials
curl -i -u alice:secret https://httpbin.org/basic-auth/alice/secret # correct
curl -i https://httpbin.org/redirect/2 ; curl -iL https://httpbin.org/redirect/2
```
- ✍️ What header comes back with the 401? (Look for `WWW-Authenticate`.) What is it telling the client?
- ✍️ What does `-L` change with redirects? Which header drives the redirect?

### Exercise 4 — Work with a "real" REST API (25 min)
JSONPlaceholder is a fake REST API that behaves like a real one.
```bash
curl -s https://jsonplaceholder.typicode.com/users | jq '.[] | {id, name, city: .address.city}'
curl -s "https://jsonplaceholder.typicode.com/posts?userId=1" | jq 'length'
curl -s https://jsonplaceholder.typicode.com/posts/1/comments | jq '.[0]'
curl -si https://jsonplaceholder.typicode.com/posts/9999 | head -1
curl -s -X POST https://jsonplaceholder.typicode.com/posts \
  -H 'Content-Type: application/json' -d '{"title":"hi","body":"x","userId":1}' -i | head -1
```
Tasks (write the command yourself):
1. Get only the **titles** of all posts by user 3.
2. Count how many todos are **completed** for user 5 (`/todos?userId=5`).
3. Update post 1's title with `PATCH`. What status comes back?
4. Notice the URL design: `/posts/1/comments`. ✍️ Explain in one sentence why nesting the URL this way is good design.

### Exercise 5 — Speak HTTP with no client at all (15 min) 🔥
Prove HTTP is just text:
```bash
printf 'GET /get HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n' | nc httpbin.org 80
```
(If `nc` isn't installed: `sudo apt install netcat-openbsd`.)
- ✍️ Remove the `Host:` line. What happens and why does the server need it?
- ✍️ This was plain HTTP on port 80. Could an attacker on the same Wi-Fi read it? What changes with HTTPS? *(Plant this seed — it's the heart of IoT security in Week 5.)*

### Stretch (optional, 15 min)
Use the browser DevTools → **Network** tab on any website. Find one `GET` that returns JSON, right-click → *Copy as cURL*, and replay it in your terminal. You've just reverse-engineered an API — an everyday skill for security testers.

---

## Part C — Quiz Gate 🔒 (answer without looking back)
Reply in chat with your answers. Need **≥ 8/10** to unlock Lesson 2.

1. In your own words (no jargon), what is an API? Give a non-restaurant analogy of your own.
2. Name the 4 parts of an HTTP request.
3. A smart lock's app sends `POST /unlock`. The network drops before the response arrives. Is it safe for the app to automatically retry? Why or why not? How could the API be redesigned to make retries safe?
4. Which is idempotent: `PUT /devices/7 {"on":true}` or `POST /devices/7/toggle`? Explain.
5. A user is logged in but tries to view another user's device. 401 or 403? (Bonus: why might some APIs return 404 instead?)
6. A client sends `{"temperature": "hot"}` to an endpoint expecting a number. Which status code fits best?
7. What does "HTTP is stateless" mean, and why does it help with scaling?
8. Your API is overloaded and rejecting some requests on purpose to protect itself from one noisy client. Which status code? Which header could tell the client when to retry?
9. What's the difference between `-d` data being sent with `Content-Type: application/json` versus without it?
10. Look at this response line: `HTTP/1.1 201 Created` with header `Location: /devices/42`. What happened, and what is the `Location` header for?

---

## Part D — Diagnostic (helps me tailor the next 6 weeks)
Rate yourself 0–5 and answer honestly — this only changes *how fast* we go, not *where* we go:
- HTTP/REST · Rust · SQL/databases · Networking (TCP/IP, DNS, TLS) · Security basics · IoT/embedded · Docker/Linux CLI
- Have you written any Rust before? Any other languages?
- How many hours per day can you realistically commit?
- What OS are you on?
