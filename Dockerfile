# === Base image ===
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# === Dev image ===
FROM base AS dev

ENV ENV=development

# Install debug/reload tools
RUN pip install --no-cache-dir debugpy watchdog

CMD ["watchmedo", "auto-restart", "--directory=src/", "--pattern=*.py", "--recursive", "--", "python", "-m", "src.main"]

# === Production image ===
FROM base AS prod
COPY src/ src/
ENV ENV=production
CMD ["python", "src/main.py"]
