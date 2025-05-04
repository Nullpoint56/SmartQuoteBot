import json
import random
from io import BytesIO

import discord
from discord.ext import commands

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
            real_index = int(idx) - 1
            app_ctx.quote_manager.remove_quote(real_index)
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
            app_ctx.logger.info("Admin %s requested quote list, but it's empty.", ctx.author)
        else:
            formatted = "\n".join([f"{i + 1}. {q['text']}" for i, q in enumerate(quotes)])
            if len(formatted) > 1900:
                formatted = formatted[:1900] + "\n..."
            await ctx.send(f"Quotes:\n```{formatted}```", ephemeral=True)
            app_ctx.logger.info("Admin %s listed quotes.", ctx.author)

    @commands.command(name="downloadquotes", help="Download quotes (admin only)")
    async def download_quotes(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You need to be an admin to use this.", ephemeral=True)
            return

        quotes = app_ctx.quote_manager.list_quotes()
        if not quotes:
            await ctx.send("No quotes available.", ephemeral=True)
            return

        content = json.dumps(quotes, indent=2).encode("utf-8")
        buffer = BytesIO(content)
        buffer.name = "quotes.json"  # Required by discord.File

        await ctx.send(file=discord.File(buffer), ephemeral=True)

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
    async def on_message(self, message: discord.Message):
        # Log every incoming message (use debug level to avoid spamming production logs)
        app_ctx.logger.debug("on_message triggered with message: %s (author: %s)", message.content, message.author)

        # Skip bot messages
        if message.author.bot:
            app_ctx.logger.debug("Message is from a bot. Ignoring.")
            return

        # Skip command messages
        if any(message.content.startswith(prefix) for prefix in COMMAND_PREFIXES):
            app_ctx.logger.debug("Message starts with a command prefix. Ignoring.")
            return

        # Save the message for collection
        app_ctx.collector.save_message(message.content.strip())
        app_ctx.logger.debug("Saved message content: %s", message.content.strip())

        # Run semantic query
        ctx_text = message.content.strip()
        results = app_ctx.quote_manager.query(ctx_text, top_n=1, threshold=0.5)

        if results:
            quote = results[0]["text"]
            await message.channel.send(f"{quote}")
            app_ctx.logger.info("Triggered by '%s' -> responded with quote: %s", ctx_text, quote)
        elif self.bot.user in message.mentions:
            app_ctx.logger.debug("Bot was mentioned in message: %s", ctx_text)

            if "quote" in ctx_text.lower():
                results = app_ctx.quote_manager.query(ctx_text, top_n=1, threshold=0.0)
                if results:
                    await message.channel.send(results[0]["text"])
                else:
                    await message.channel.send("No quotes available!")
            elif "help" in ctx_text.lower():
                await message.channel.send("Try `!helpme` for a list of commands!")


async def setup(bot: commands.Bot):
    await bot.add_cog(QuoteCog(bot))