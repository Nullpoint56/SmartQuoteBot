import discord
from discord.ext import commands
from config import TOKEN, COMMAND_PREFIX
from startup import app_ctx

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

async def load_extensions():
    await bot.load_extension("cogs.quotes")

def get_user_display(bot):
    return str(bot.user)

@bot.event
async def on_ready():
    app_ctx.logger.info(f"Logged in as {get_user_display(bot)}")

async def main():
    app_ctx.boot()
    try:
        async with bot:
            await load_extensions()
            await bot.start(TOKEN)
    except Exception as e:
        app_ctx.logger.exception("Bot startup failed:")
    finally:
        app_ctx.shutdown()

import asyncio
asyncio.run(main())
