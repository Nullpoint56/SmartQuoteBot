# tests/unit_tests/test_bot_startup.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import bot  # your actual module name

@pytest.mark.asyncio
async def test_load_extensions():
    bot.bot.load_extension = AsyncMock()
    await bot.load_extensions()
    bot.bot.load_extension.assert_called_once_with("cogs.quotes")

@pytest.mark.asyncio
async def test_on_ready_logs(monkeypatch):
    fake_logger = MagicMock()

    # Patch app_ctx.logger
    monkeypatch.setattr("bot.app_ctx", type("FakeCtx", (), {"logger": fake_logger}))

    # ✅ Patch get_user_display instead of messing with .user
    with patch("bot.get_user_display", return_value="RodofBot#1234"):
        await bot.on_ready()

    fake_logger.info.assert_called_with("✅ Logged in as RodofBot#1234")
