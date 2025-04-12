import random
import discord
from discord.ext import commands
from discord import File

from utils.storage import load_quotes, save_quotes
from startup import app_ctx


class QuoteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.quotes = load_quotes()
        self.quotes_file = app_ctx.config.quotes_file
        app_ctx.logger.info("QuoteCog loaded. Quotes loaded: %d", len(self.quotes))

    @commands.command(name="quote", help="Get a random quote")
    async def quote(self, ctx: commands.Context):
        if not self.quotes:
            await ctx.send("No quotes available!")
            app_ctx.logger.info("User %s tried to get a quote but none exist.", ctx.author)
        else:
            quote = random.choice(self.quotes)
            await ctx.send(quote)
            app_ctx.logger.info("User %s retrieved quote: %s", ctx.author, quote)

    @commands.command(name="addquote", help="Add a quote")
    async def add_quote(self, ctx: commands.Context, *, quote: str):
        self.quotes.append(quote)
        save_quotes(self.quotes)
        await ctx.send(f"Added quote: '{quote}'")
        app_ctx.logger.info("User %s added quote: %s", ctx.author, quote)

    @commands.command(name="removequote", help="Remove a quote (admin only)")
    async def remove_quote(self, ctx: commands.Context, *, quote: str):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You need to be an admin to use this.")
            return

        try:
            self.quotes.remove(quote)
            save_quotes(self.quotes)
            await ctx.send(f"🗑Removed: '{quote}'")
            app_ctx.logger.info("Admin %s removed quote: %s", ctx.author, quote)
        except ValueError:
            await ctx.send("Quote not found.")
            app_ctx.logger.warning("Admin %s tried to remove non-existent quote: %s", ctx.author, quote)

    @commands.command(name="listquotes", help="List all quotes (admin only)")
    async def list_quotes(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You need to be an admin to use this.")
            return

        if not self.quotes:
            await ctx.send("No quotes yet.")
            app_ctx.logger.info("Admin %s requested quote list, but it's empty.", ctx.author)
        else:
            formatted = "\n".join([f"{i + 1}. {q}" for i, q in enumerate(self.quotes)])
            if len(formatted) > 1900:
                formatted = formatted[:1900] + "\n..."
            await ctx.send(f"Quotes:\n```{formatted}```")
            app_ctx.logger.info("Admin %s listed quotes.", ctx.author)

    @commands.command(name="downloadquotes", help="Download quotes.json (admin only)")
    async def download_quotes(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You need to be an admin to use this.")
            return

        if not self.quotes_file.exists():
            await ctx.send("No quotes file found to download.")
            app_ctx.logger.warning("Admin %s tried to download quotes but file was missing.", ctx.author)
            return

        await ctx.send("Downloading quotes...")
        try:
            await ctx.send(file=File(self.quotes_file, filename="quotes.json"))
            app_ctx.logger.info("Admin %s downloaded the quotes file.", ctx.author)
        except Exception:
            app_ctx.logger.exception("Failed to send quotes.json to admin:")
            await ctx.send("Failed to send quotes file.")

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
                "`!removequote <quote>` — Remove a quote",
                "`!listquotes` — List all quotes",
                "`!downloadquotes` — Download quotes.json",
            ]
        await ctx.send("\n".join(text))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if self.bot.user in message.mentions:
            if "quote" in message.content.lower():
                if not self.quotes:
                    await message.channel.send("No quotes available!")
                else:
                    quote = random.choice(self.quotes)
                    await message.channel.send(quote)
            elif "help" in message.content.lower():
                await message.channel.send("Try `!helpme` for a list of commands!")


async def setup(bot: commands.Bot):
    await bot.add_cog(QuoteCog(bot))
