FROM rust:bookworm AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY dashboard.html ./dashboard.html
RUN cargo build --release --bin enose-cloud

FROM debian:bookworm-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/target/release/enose-cloud /app/enose-cloud
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080
CMD ["/app/enose-cloud"]
