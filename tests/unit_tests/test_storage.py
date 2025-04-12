import json
import pytest
from unittest.mock import patch, MagicMock
from utils import storage

@pytest.fixture(autouse=True)
def patch_logger():
    with patch.object(storage, "app_ctx") as mock_ctx:
        yield mock_ctx

def test_load_quotes_file_not_found(tmp_path):
    with patch.object(storage, "QUOTES_FILE", tmp_path / "nonexistent.json"):
        quotes = storage.load_quotes()
        assert quotes == []

def test_load_quotes_valid_list(tmp_path):
    valid_data = ["one", "two"]
    file_path = tmp_path / "quotes.json"
    file_path.write_text(json.dumps(valid_data), encoding="utf-8")

    with patch.object(storage, "QUOTES_FILE", file_path):
        quotes = storage.load_quotes()
        assert quotes == valid_data

def test_load_quotes_not_a_list(tmp_path):
    file_path = tmp_path / "quotes.json"
    file_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

    with patch.object(storage, "QUOTES_FILE", file_path):
        quotes = storage.load_quotes()
        assert quotes == []

def test_load_quotes_non_string_items(tmp_path):
    file_path = tmp_path / "quotes.json"
    file_path.write_text(json.dumps(["good", 123, None]), encoding="utf-8")

    with patch.object(storage, "QUOTES_FILE", file_path):
        quotes = storage.load_quotes()
        assert quotes == ["good", 123, None]  # Still returns the list as-is

def test_load_quotes_invalid_json(tmp_path):
    file_path = tmp_path / "quotes.json"
    file_path.write_text("{invalid_json: true", encoding="utf-8")

    with patch.object(storage, "QUOTES_FILE", file_path):
        quotes = storage.load_quotes()
        assert quotes == []

def test_load_quotes_unexpected_exception(monkeypatch):
    # Simulate IOError or something else unexpected
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    monkeypatch.setattr(storage, "QUOTES_FILE", mock_path)
    monkeypatch.setattr("builtins.open", MagicMock(side_effect=OSError("boom")))

    quotes = storage.load_quotes()
    assert quotes == []

def test_save_quotes_creates_file_and_saves(tmp_path):
    file_path = tmp_path / "quotes.json"
    with patch.object(storage, "QUOTES_FILE", file_path):
        storage.save_quotes(["alpha", "beta"])

        assert file_path.exists()
        contents = json.loads(file_path.read_text(encoding="utf-8"))
        assert contents == ["alpha", "beta"]

def test_save_quotes_with_none(tmp_path):
    file_path = tmp_path / "quotes.json"
    with patch.object(storage, "QUOTES_FILE", file_path):
        storage.save_quotes(None)

        contents = json.loads(file_path.read_text(encoding="utf-8"))
        assert contents == []

def test_save_quotes_handles_exception(tmp_path, monkeypatch):
    file_path = tmp_path / "quotes.json"
    monkeypatch.setattr(storage, "QUOTES_FILE", file_path)
    monkeypatch.setattr("builtins.open", MagicMock(side_effect=IOError("boom")))

    # Should not raise, just logs error
    storage.save_quotes(["safe"])
