# Build stage: compile both binaries in release mode
FROM rust:1 AS build
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

# Run stage: a small image with just the binaries
FROM debian:bookworm-slim
COPY --from=build /app/target/release/publisher /usr/local/bin/publisher
COPY --from=build /app/target/release/subscriber /usr/local/bin/subscriber
