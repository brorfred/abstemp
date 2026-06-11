# Use Case 1 — bundled data (less downloads)
#
# Build (from the project root):
#   podman build -t abstemp .
#
# Run (mount the data dir and figs output):
#   podman run --rm \
#     -v "$(pwd)/src/abstemp/data:/app/src/abstemp/data:ro" \
#     -v "$(pwd)/figs:/app/figs" \
#     abstemp

FROM debian:bookworm-slim

# ── System packages ──────────────────────────────────────────────────────────
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ── Pixi ─────────────────────────────────────────────────────────────────────
ENV PIXI_HOME=/usr/local/pixi
RUN curl -fsSL https://pixi.sh/install.sh | PIXI_HOME=/usr/local/pixi sh
ENV PATH="/usr/local/pixi/bin:$PATH"

# ── Project ───────────────────────────────────────────────────────────────────
WORKDIR /app
COPY . .

# Figure output directory
RUN mkdir -p figs

# Install the pixi environment (reproducible via pixi.lock)
RUN pixi install --locked

# ── Runtime ───────────────────────────────────────────────────────────────────
# Use the non-interactive matplotlib backend (no display needed in the container)
ENV MPLBACKEND=Agg
# Disable Python output buffering so progress is visible in container logs
ENV PYTHONUNBUFFERED=1

#ENTRYPOINT ["pixi", "run", "python", "docker/run_figures.py"]
