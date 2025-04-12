import json
from pathlib import Path

class MessageCollector:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save_message(self, text: str):
        if not text.strip():
            return
        with open(self.path, "a", encoding="utf-8") as f:
            json.dump({"text": text.strip()}, f, ensure_ascii=False)
            f.write("\n")
