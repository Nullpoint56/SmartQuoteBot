# === Builder: install dependencies with uv ===
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Copy lockfile and project config
COPY pyproject.toml uv.lock ./

# Install dependencies only (without app code), use cache mount for speed
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy application source and install it
COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# === Final image ===
FROM python:3.11-slim-bookworm AS final

WORKDIR /app

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy just the source code
COPY src/ src/

CMD ["python", "src/bot.py"]
