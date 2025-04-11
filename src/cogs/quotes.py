from discord.ext import commands
import random
from utils.storage import load_quotes, save_quotes
from startup import app_ctx

class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes = load_quotes()
        app_ctx.logger.info("QuoteCog loaded. Quotes loaded: %d", len(self.quotes))

    @commands.command(name="rodof-quote")
    async def rodof_quote(self, ctx):
        if not self.quotes:
            await ctx.send("No quotes available!")
            app_ctx.logger.info("User %s tried to get a quote but none exist.", ctx.author)
        else:
            quote = random.choice(self.quotes)
            await ctx.send(f"📜 {quote}")
            app_ctx.logger.info("User %s retrieved quote: %s", ctx.author, quote)

    @commands.command(name="rodof-add")
    async def rodof_add(self, ctx, *, quote: str):
        self.quotes.append(quote)
        save_quotes(self.quotes)
        await ctx.send(f"✅ Added quote: '{quote}'")
        app_ctx.logger.info("User %s added quote: %s", ctx.author, quote)

    @commands.command(name="rodof-remove")
    async def rodof_remove(self, ctx, *, quote: str):
        try:
            self.quotes.remove(quote)
            save_quotes(self.quotes)
            await ctx.send(f"🗑️ Removed: '{quote}'")
            app_ctx.logger.info("User %s removed quote: %s", ctx.author, quote)
        except ValueError:
            await ctx.send("❌ Quote not found.")
            app_ctx.logger.warning("User %s tried to remove non-existent quote: %s", ctx.author, quote)

    @commands.command(name="rodof-list")
    async def rodof_list(self, ctx):
        if not self.quotes:
            await ctx.send("No quotes yet.")
            app_ctx.logger.info("User %s requested quote list, but it's empty.", ctx.author)
        else:
            formatted = "\n".join([f"{i+1}. {q}" for i, q in enumerate(self.quotes)])
            await ctx.send(f"📋 Quotes:\n```{formatted}```")
            app_ctx.logger.info("User %s listed quotes.", ctx.author)

async def setup(bot):
    await bot.add_cog(QuoteCog(bot))
