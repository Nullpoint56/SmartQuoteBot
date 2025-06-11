# === Builder: Install dependencies with uv ===
FROM --platform=$BUILDPLATFORM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Copy pyproject files
COPY pyproject.toml uv.lock ./

# Install dependencies (no project install yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy source
COPY src/ src/

# Install project and its runtime deps
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Cleanup to reduce size
RUN rm -rf /app/.venv/lib/python*/site-packages/**/*.dist-info \
    && rm -rf /app/.venv/lib/python*/site-packages/**/__pycache__ \
    && find /app/.venv -name '*.pyc' -delete \
    && uv pip cache purge

# === Final minimal image ===
FROM --platform=$TARGETPLATFORM python:3.11-slim-bookworm AS final

WORKDIR /app

# Copy virtual environment
COPY --from=builder /app/.venv /app/.venv

# Set up environment
ENV PATH="/app/.venv/bin:$PATH" \
    ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy source
COPY src/ src/

CMD ["python", "src/bot.py"]
