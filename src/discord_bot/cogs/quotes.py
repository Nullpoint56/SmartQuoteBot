import json
import random
from io import BytesIO

from discord import Message, File
from discord.ext import commands

from src.discord_bot.cogs.utils import clean_message_from_mentions
from src.discord_bot.ui import QuotePaginator
from src.startup import app_ctx

COMMAND_PREFIXES = ("!quote", "!addquote", "!removequote", "!listquotes", "!downloadquotes", "!helpme")


class QuoteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        app_ctx.logger.info("QuoteCog loaded. Quotes loaded: %d", app_ctx.quote_manager.count_quotes())

    @commands.command(name="quote", help="Get a random quote")
    async def quote(self, ctx: commands.Context):
        quotes = app_ctx.quote_manager.list_quotes()
        if not quotes:
            await ctx.send("No quotes available!")
            app_ctx.logger.info("User %s tried to get a quote but none exist.", ctx.author)
        else:
            quote = random.choice(quotes)["text"]
            await ctx.send(quote)
            app_ctx.logger.info("User %s retrieved quote: %s", ctx.author, quote)

    @commands.command(name="addquote", help="Add a quote")
    async def add_quote(self, ctx: commands.Context, *, quote: str):
        app_ctx.quote_manager.add_quote(text=quote)
        await ctx.send(f"Added quote: '{quote}'", ephemeral=True)
        app_ctx.logger.info("User %s added quote: %s", ctx.author, quote)

    @commands.command(name="removequote", help="Remove a quote (admin only)")
    async def remove_quote(self, ctx: commands.Context, idx: str):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You need to be an admin to use this.", ephemeral=True)
            return

        if not idx.isdigit():
            await ctx.send("Please provide a valid index number.", ephemeral=True)
            return

        try:
            app_ctx.quote_manager.remove_quote_by_id(idx)
            await ctx.send(f"🗑Removed quote at index {idx}.", ephemeral=True)
            app_ctx.logger.info("Admin %s removed quote at index: %s", ctx.author, idx)
        except Exception as e:
            await ctx.send("Failed to remove quote: " + str(e), ephemeral=True)
            app_ctx.logger.warning("Admin %s failed to remove quote: %s", ctx.author, e)

    @commands.command(name="listquotes", help="List all quotes (admin only)")
    async def list_quotes(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You need to be an admin to use this.", ephemeral=True)
            return

        quotes = app_ctx.quote_manager.list_quotes()
        if not quotes:
            await ctx.send("No quotes yet.", ephemeral=True)
            return

        paginator = QuotePaginator(quotes, per_page=10)
        view = paginator if paginator.max_page() > 1 else None
        await ctx.send(paginator.format_page(), view=view, ephemeral=True)

    @commands.command(name="downloadquotes", help="Download quotes (admin only)")
    async def download_quotes(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You need to be an admin to use this.", ephemeral=True)
            return

        quotes = app_ctx.quote_manager.list_quotes()
        if not quotes:
            await ctx.send("No quotes available.", ephemeral=True)
            return

        content = json.dumps(quotes, indent=2, ensure_ascii=False).encode("utf-8")
        buffer = BytesIO(content)
        buffer.name = "quotes.json"

        await ctx.send(file=File(buffer), ephemeral=True)

    @commands.command(name="helpme", help="Show help info for RodofBot")
    async def rodof_help(self, ctx: commands.Context):
        is_admin = ctx.author.guild_permissions.administrator
        text = [
            "**📜 Rodof Bot Help**",
            "",
            "🗣️ Public commands:",
            "`!quote` — Get a random quote",
            "`!addquote <quote>` — Add a new quote",
        ]
        if is_admin:
            text += [
                "",
                "🔐 Admin-only commands:",
                "`!removequote <index>` — Remove a quote by index",
                "`!listquotes` — List all quotes",
                "`!downloadquotes` — Download quotes.json",
            ]
        await ctx.send("\n".join(text), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        content = message.content.strip()
        author = message.author

        app_ctx.logger.debug("on_message triggered with message: %s (author: %s)", content, author)

        if author.bot:
            app_ctx.logger.debug("Message is from a bot. Ignoring.")
            return

        if any(content.startswith(prefix) for prefix in COMMAND_PREFIXES):
            app_ctx.logger.debug("Message starts with a command prefix. Ignoring.")
            return

        try:
            content = clean_message_from_mentions(message)
            app_ctx.logger.debug("Running similarity search for: %s", content)
            results = app_ctx.quote_manager.query(content, top_n=1, threshold=0.5, metric="cosine")
            app_ctx.logger.debug("Similarity search results: %s", results)
        except Exception as e:
            app_ctx.logger.exception("Error during quote_manager query: %s", e)
            return

        if results:
            quote = results[0]["text"]
            await message.channel.send(quote)
            app_ctx.logger.debug("Responded to '%s' with quote: %s", content, quote)
        elif self.bot.user in message.mentions:
            app_ctx.logger.debug("Bot was mentioned in message: %s", content)

            if "quote" in content.lower():
                results = app_ctx.quote_manager.query(content, top_n=1, threshold=0.0)
                if results:
                    await message.channel.send(results[0]["text"])
                else:
                    await message.channel.send("No quotes available!")

            elif "help" in content.lower():
                await message.channel.send("Try `!helpme` for a list of commands!")


async def setup(bot: commands.Bot):
    await bot.add_cog(QuoteCog(bot))
