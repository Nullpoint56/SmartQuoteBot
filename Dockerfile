FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements/prod_requirements.txt .
RUN pip install --no-cache-dir -r prod_requirements.txt

# Copy source code and assets
COPY src/ src/

# Set the working dir to source for running
WORKDIR /app/src

# Run the bot
CMD ["python", "bot.py"]
