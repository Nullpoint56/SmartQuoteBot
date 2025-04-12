import discord
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from cogs.quotes import QuoteCog
from discord import File
from discord.ext import commands

@pytest.fixture
def bot():
    intents = discord.Intents.default()
    intents.message_content = True  # If your commands require message content
    return commands.Bot(command_prefix="/", intents=intents)

@pytest.fixture
def cog(bot):
    cog = QuoteCog(bot)
    cog.quotes = ["test quote"]
    return cog

@pytest.fixture
def mock_interaction():
    user = MagicMock()
    user.guild_permissions.administrator = True
    return MagicMock(user=user, response=AsyncMock(), followup=AsyncMock())

@pytest.mark.asyncio
async def test_quote_returns_quote(cog, mock_interaction):
    await cog.quote.callback(cog, mock_interaction)
    mock_interaction.response.send_message.assert_called_with("📜 test quote")

@pytest.mark.asyncio
async def test_quote_empty_list(cog, mock_interaction):
    cog.quotes = []
    await cog.quote.callback(cog, mock_interaction)
    mock_interaction.response.send_message.assert_called_with("No quotes available!", ephemeral=True)

@pytest.mark.asyncio
async def test_add_quote(cog, mock_interaction):
    with patch("cogs.quotes.save_quotes") as mock_save:
        await cog.add_quote.callback(cog, mock_interaction, "new quote")
        assert "new quote" in cog.quotes
        mock_save.assert_called_once()
        mock_interaction.response.send_message.assert_called_with("✅ Added quote: 'new quote'")

@pytest.mark.asyncio
async def test_remove_quote_success(cog, mock_interaction):
    with patch("cogs.quotes.save_quotes") as mock_save:
        await cog.remove_quote.callback(cog, mock_interaction, "test quote")
        assert "test quote" not in cog.quotes
        mock_interaction.response.send_message.assert_called_with("🗑️ Removed: 'test quote'")

@pytest.mark.asyncio
async def test_remove_quote_failure(cog, mock_interaction):
    await cog.remove_quote.callback(cog, mock_interaction, "not found")
    mock_interaction.response.send_message.assert_called_with("❌ Quote not found.")

@pytest.mark.asyncio
async def test_list_quotes(cog, mock_interaction):
    await cog.list_quotes.callback(cog, mock_interaction)
    assert mock_interaction.response.send_message.call_args[0][0].startswith("📋 Quotes:")

@pytest.mark.asyncio
async def test_download_quotes_file_exists(cog, mock_interaction, tmp_path):
    file = tmp_path / "quotes.json"
    file.write_text('["hello"]', encoding="utf-8")

    with patch("cogs.quotes.QUOTES_FILE", file):
        await cog.download_quotes.callback(cog, mock_interaction)
        mock_interaction.followup.send.assert_called()
        args, kwargs = mock_interaction.followup.send.call_args
        assert isinstance(kwargs["file"], File)

@pytest.mark.asyncio
async def test_download_quotes_missing_file(cog, mock_interaction, tmp_path):
    with patch("cogs.quotes.QUOTES_FILE", tmp_path / "missing.json"):
        await cog.download_quotes.callback(cog, mock_interaction)
        mock_interaction.response.send_message.assert_called_with("❌ No quotes file found to download.")

@pytest.mark.asyncio
async def test_help_admin(cog, mock_interaction):
    await cog.help.callback(cog, mock_interaction)
    sent = "\n".join(call[0][0] for call in mock_interaction.response.send_message.call_args_list)
    assert "Admin-only" in sent

@pytest.mark.asyncio
async def test_mention_quote():
    mock_user = MagicMock()
    mock_bot = MagicMock()
    mock_bot.user = mock_user

    cog = QuoteCog(mock_bot)
    cog.quotes = ["sample quote"]

    msg = MagicMock()
    msg.author.bot = False
    msg.content = "@Bot quote"
    msg.mentions = [mock_user]
    msg.channel.send = AsyncMock()

    await cog.on_message(msg)
    msg.channel.send.assert_called_once()


@pytest.mark.asyncio
async def test_mention_help():
    mock_user = MagicMock()
    mock_bot = MagicMock()
    mock_bot.user = mock_user

    cog = QuoteCog(mock_bot)

    msg = MagicMock()
    msg.author.bot = False
    msg.content = "@Bot help"
    msg.mentions = [mock_user]
    msg.channel.send = AsyncMock()

    await cog.on_message(msg)
    msg.channel.send.assert_called_with("Try `/help` for a full list of available commands!")
