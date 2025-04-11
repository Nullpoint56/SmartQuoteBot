# src/paths.py

from pathlib import Path

# /app or project root
BASE_DIR = Path(__file__).resolve().parents[1]

# Runtime data
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
QUOTES_FILE = DATA_DIR / "quotes.json"
