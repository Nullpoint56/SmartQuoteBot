import json
from typing import List, Union

from smartquotebot.startup import app_ctx


def load_quotes() -> List[str]:
    quotes_path = app_ctx.config.quotes_file

    if not quotes_path.exists():
        app_ctx.logger.warning("quotes.json not found at %s. Starting with empty quote list.", quotes_path)
        return []

    try:
        with open(quotes_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                app_ctx.logger.error("quotes.json is not a list. Got type: %s", type(data).__name__)
                return []
            if not all(isinstance(q, str) for q in data):
                app_ctx.logger.warning("quotes.json contains non-string items.")
            return data
    except json.JSONDecodeError as e:
        app_ctx.logger.error("Failed to parse quotes.json: %s", e)
        return []
    except Exception:
        app_ctx.logger.exception("Unexpected error while loading quotes:")
        return []


def save_quotes(quotes: Union[List[str], None]):
    quotes_path = app_ctx.config.quotes_file
    try:
        quotes_path.parent.mkdir(parents=True, exist_ok=True)
        with open(quotes_path, "w", encoding="utf-8") as f:
            json.dump(quotes or [], f, indent=2, ensure_ascii=False)
        app_ctx.logger.info("Saved %d quotes to %s", len(quotes or []), quotes_path)
    except Exception:
        app_ctx.logger.exception("Failed to save quotes:")
