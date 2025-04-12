import json
import logging
import pytest
from unittest.mock import patch, MagicMock
from startup import AppContext
import startup

@pytest.fixture
def ctx():
    return AppContext()

@pytest.mark.parametrize("env", ["development", "production"])
def test_boot_calls_all(monkeypatch, env):
    monkeypatch.setattr(startup, "ENV", env)
    ctx = AppContext()
    monkeypatch.setattr(ctx, "_init_logging", MagicMock())
    monkeypatch.setattr(ctx, "_init_sentry", MagicMock())
    monkeypatch.setattr(ctx, "_bootstrap_data", MagicMock())
    ctx.logger = MagicMock()

    ctx.boot()

    ctx._init_logging.assert_called_once()
    ctx._init_sentry.assert_called_once()
    ctx._bootstrap_data.assert_called_once()
    ctx.logger.info.assert_any_call(f"🚀 Rodof Bot starting in {env.upper()} mode")

def test_logging_setup_sets_handlers(tmp_path, monkeypatch):
    monkeypatch.setattr(startup, "LOGS_DIR", tmp_path)
    ctx = AppContext()

    logger = logging.getLogger("rodof")
    logger.handlers.clear()  # Clear old handlers

    ctx._init_logging()

    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    assert any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers)


@patch("sentry_sdk.init")
def test_sentry_skipped_when_not_production(mock_init, monkeypatch):
    monkeypatch.setattr(startup, "ENV", "development")
    ctx = AppContext()
    ctx.logger = MagicMock()
    ctx._init_sentry()
    mock_init.assert_not_called()
    ctx.logger.info.assert_called_with("ℹ️ Sentry not enabled (ENV=development)")

@patch("sentry_sdk.init")
def test_sentry_initialized_when_production(mock_init, monkeypatch):
    monkeypatch.setattr(startup, "ENV", "production")
    monkeypatch.setattr(startup, "SENTRY_DSN", "abc")
    ctx = AppContext()
    ctx.logger = MagicMock()
    ctx._init_sentry()
    mock_init.assert_called_once()
    ctx.logger.info.assert_called_with("✅ Sentry initialized")

def test_bootstrap_creates_files(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    quotes_file = data_dir / "quotes.json"
    monkeypatch.setattr(startup, "DATA_DIR", data_dir)
    monkeypatch.setattr(startup, "QUOTES_FILE", quotes_file)
    ctx = AppContext()
    ctx.logger = MagicMock()
    ctx._bootstrap_data()

    assert quotes_file.exists()
    assert json.loads(quotes_file.read_text()) == []

@pytest.mark.parametrize("env", ["development", "production"])
def test_bootstrap_reads_existing_file(monkeypatch, tmp_path, env):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    quotes_file = data_dir / "quotes.json"
    quotes_file.write_text(json.dumps(["a", "b", "c"]))

    monkeypatch.setattr(startup, "DATA_DIR", data_dir)
    monkeypatch.setattr(startup, "QUOTES_FILE", quotes_file)
    monkeypatch.setattr(startup, "ENV", env)

    ctx = AppContext()
    ctx.logger = MagicMock()
    ctx._bootstrap_data()

    ctx.logger.info.assert_any_call("📖 quotes.json exists. Loaded %d quotes.", 3)
    if env == "development":
        ctx.logger.debug.assert_called_with("📝 Preview: %s", ["a", "b", "c"])
    else:
        ctx.logger.debug.assert_not_called()

def test_bootstrap_handles_bad_json(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    quotes_file = data_dir / "quotes.json"
    quotes_file.write_text("invalid json")

    monkeypatch.setattr(startup, "DATA_DIR", data_dir)
    monkeypatch.setattr(startup, "QUOTES_FILE", quotes_file)

    ctx = AppContext()
    ctx.logger = MagicMock()
    ctx._bootstrap_data()

    ctx.logger.exception.assert_called_with("💥 Failed to inspect existing quotes.json:")
