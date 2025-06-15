# === Base image with uv and Python on the TARGET platform ===
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS final

WORKDIR /app

# Set environment early for consistent installs
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy only files needed to install dependencies first (enables better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies and project (on target architecture)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Remove dist-info and __pycache__ to reduce image size
RUN rm -rf /app/.venv/lib/python*/site-packages/**/*.dist-info \
    && rm -rf /app/.venv/lib/python*/site-packages/**/__pycache__ \
    && find /app/.venv -name '*.pyc' -delete

# Copy source code
COPY src/ src/

CMD ["python", "-m", "smartquotebot.bot"]
