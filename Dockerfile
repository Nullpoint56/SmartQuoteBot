# === Base image ===
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# === Dev image ===
FROM base as dev
# (Optional: install dev tools here)
# RUN pip install --no-cache-dir debugpy watchdog ipython
ENV ENV=development
CMD ["python", "-m", "src.bot"]

# === Production image ===
FROM base as prod
COPY src/ src/
ENV ENV=production
CMD ["python", "src/bot.py"]
