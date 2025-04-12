# Base image
FROM python:3.12-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app


# Pre-copy requirements and install deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ src/
COPY .env .env

# Optional: Create persistent folders (can be managed via volume too)
RUN mkdir -p data logs

# Preload with initial data if exists
COPY data/ data/

# Entrypoint
CMD ["python", "src/bot.py"]
