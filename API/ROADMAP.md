# Roadmap — From Zero to Portfolio-Grade in 6 Weeks

> Honest framing: "mastery" in 6 weeks means **strong working proficiency + a portfolio that proves it**.
> We get there by ruthlessly applying 80/20: learn the 20% of concepts that appear in 80% of real work,
> then spend most of your time building, breaking, and securing real systems.

## The 80/20 core (if you learn nothing else, learn these)
| Area | The vital 20% |
|---|---|
| APIs | HTTP request/response anatomy, methods + idempotency, status codes, REST resource design, JSON, auth headers |
| Rust APIs | `async`/Tokio, Axum routers + extractors + shared state, `serde`, error handling with `Result` + `?`, SQLx + Postgres, integration tests |
| Scaling | Stateless services, caching, connection pooling, DB indexes, pagination, rate limiting, horizontal scaling behind a load balancer, measuring (load tests + metrics) |
| Security | AuthN vs AuthZ, JWT done right, TLS/mTLS, input validation, OWASP API Top 10 (esp. BOLA), secrets handling, least privilege |
| IoT Security | Device→Gateway→Cloud architecture, MQTT, device identity (certs), OWASP IoT Top 10, threat modeling (STRIDE), secure firmware/OTA updates |

## Module map (order matters — each builds on the last)

```
M1 API Foundations ─► M2 Rust for APIs ─► M3 Building APIs in Rust (Axum)
                                               │
                     ┌─────────────────────────┴───────────┐
                     ▼                                     ▼
             M4 API Security                        M5 API Scaling
                     └──────────────┬──────────────────────┘
                                    ▼
                         M6 IoT Cybersecurity
                                    ▼
                      M7 Capstone: Secure IoT Platform
```

### Week 1 (Nov 19–25) — M1 API Foundations + M2 Rust for APIs (start)
| # | Lesson | Hands-on deliverable |
|---|---|---|
| 1 | How machines talk: HTTP & APIs | Drive real APIs with `curl`; read raw HTTP |
| 2 | REST design & status codes | Design a full API spec for a "smart home" service |
| 3 | JSON, OpenAPI, API types (REST vs gRPC vs GraphQL vs WebSocket vs MQTT) | Write an OpenAPI file; compare protocols |
| 4 | Rust crash-course for API devs: ownership, structs, enums, `Result`, `?` | 10 kata exercises |
| 5 | Async Rust & Tokio | Concurrent HTTP fetcher with `reqwest` |
| ✅ | **Checkpoint quiz 1** | — |

### Week 2 (Nov 26–Dec 2) — M3 Building APIs in Rust
| # | Lesson | Hands-on deliverable |
|---|---|---|
| 6 | Axum: routing, handlers, extractors | Hello-API with 5 endpoints |
| 7 | State, `serde`, validation, error types | Typed errors → correct status codes |
| 8 | Postgres with SQLx: migrations, queries, pooling | CRUD backed by a real DB (Docker) |
| 9 | Testing APIs: unit, integration, contract | Test suite with ≥ 80% handler coverage |
| 10 | Middleware with Tower: logging, timeouts, CORS, tracing | Request-ID + structured logs |
| 🛠 | **Project 1: "DeviceRegistry API"** — CRUD for IoT devices in Axum + Postgres, tested, documented | |

### Week 3 (Dec 3–9) — M4 API Security
| # | Lesson | Hands-on deliverable |
|---|---|---|
| 11 | AuthN vs AuthZ, password hashing (Argon2), sessions vs tokens | Signup/login endpoints |
| 12 | JWT deep-dive + common JWT attacks (`alg:none`, weak secrets) | Break a vulnerable JWT API, then fix yours |
| 13 | OWASP API Security Top 10 (BOLA, mass assignment, SSRF…) | Exploit a deliberately vulnerable API, write findings |
| 14 | TLS, mTLS, secrets, CORS, security headers | Enable TLS with `rustls`; mTLS client certs |
| 15 | Rate limiting & abuse prevention | Token-bucket limiter as Tower middleware |
| 🛠 | **Project 2: Harden DeviceRegistry** + a mini pentest report on it | |

### Week 4 (Dec 10–16) — M5 API Scaling
| # | Lesson | Hands-on deliverable |
|---|---|---|
| 16 | Measuring first: latency percentiles, throughput, load testing (`oha`/`k6`) | Baseline report: p50/p95/p99 |
| 17 | DB scaling: indexes, `EXPLAIN`, N+1, pooling, pagination (cursor vs offset) | 10× faster list endpoint |
| 18 | Caching with Redis: cache-aside, TTLs, invalidation, stampedes | Cached reads + measured gain |
| 19 | Horizontal scaling: statelessness, load balancers (Nginx), Docker Compose replicas | 3 replicas behind Nginx |
| 20 | Async work & backpressure: queues, idempotency keys, retries, circuit breakers | Background job worker |
| 21 | Observability: metrics (Prometheus), tracing, dashboards (Grafana) | Live dashboard of your API |
| 🛠 | **Project 3: Scale DeviceRegistry** to a target (e.g. 5k req/s p99 < 50 ms locally) with a before/after report | |

### Week 5 (Dec 17–23) — M6 IoT Cybersecurity
| # | Lesson | Hands-on deliverable |
|---|---|---|
| 22 | IoT architecture & attack surface (device, network, gateway, cloud, mobile app) | Attack-surface map of a smart lock |
| 23 | MQTT & CoAP: how devices talk | Mosquitto broker + Rust publisher/subscriber (`rumqttc`) |
| 24 | Attacking IoT protocols: open brokers, sniffing, topic injection | Exploit an unauthenticated broker in a lab; capture with Wireshark |
| 25 | Device identity: PKI, X.509, mTLS for MQTT, provisioning | Build a mini CA; per-device certs |
| 26 | Firmware security: secure boot, signed OTA updates, extraction (binwalk) | Sign & verify firmware updates in Rust (`ed25519`) |
| 27 | Threat modeling (STRIDE) + OWASP IoT Top 10 | Full threat model for your capstone |

### Week 6 (Dec 24–Jan 1) — M7 Capstone + Mastery Exam
🛠 **Capstone: "SentinelIoT" — a secure, scalable IoT telemetry platform in Rust**
- Simulated devices (Rust) publish telemetry over **MQTT with mTLS** and per-device certs
- Rust **ingestion gateway** validates, rate-limits, and writes to Postgres/Timescale
- **Axum API** with JWT auth, RBAC, BOLA-proof object access, cursor pagination, Redis cache
- **Signed OTA update** endpoint (Ed25519)
- Prometheus metrics + Grafana dashboard; load-tested with documented p99
- **Threat model + self-pentest report** (what you attacked, what you fixed)
- Deliverables: GitHub repo, README with architecture diagram, 5-min demo video

Dec 30–31: **Final mastery exam** (theory + live build + live debugging + security review).

## Mastery checklist (you're "done" when you can…)
- [ ] Explain any HTTP exchange byte-by-byte and pick the right status code without thinking
- [ ] Build a tested, documented Axum + Postgres API from scratch in < 2 hours
- [ ] Find and fix BOLA, broken auth, and mass-assignment bugs in someone else's API
- [ ] Load test an API, find the bottleneck, and prove a fix with numbers
- [ ] Secure an MQTT fleet with mTLS and explain why each control exists
- [ ] Produce a STRIDE threat model for an IoT product in 30 minutes

## Tools you'll install (as needed, not all on day 1)
`curl`, `jq`, Rust (`rustup`), Docker, Postgres, Redis, Mosquitto, `oha` or `k6`, Wireshark, Postman/Bruno (optional).
