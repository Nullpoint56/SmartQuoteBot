# === Base image ===
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies needed for psycopg (esp. binary wheels)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# === Dev image ===
FROM base AS dev
COPY src/ src/
ENV ENV=development
CMD ["python", "-m", "src.bot"]

# === Production image ===
FROM base AS prod
COPY src/ src/
ENV ENV=production
CMD ["python", "src/bot.py"]
