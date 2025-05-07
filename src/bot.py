import asyncio
import discord
from discord.ext import commands

from src.startup import app_ctx

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=app_ctx.config.bot.command_prefix, intents=intents)


async def load_extensions():
    try:
        await bot.load_extension("src.discord_bot.cogs.quotes")
        app_ctx.logger.info("Loaded extension: cogs.quotes")
    except Exception:
        app_ctx.logger.exception("Failed to load extension: cogs.quotes")


def get_user_display(bot):
    return str(bot.user)


@bot.event
async def on_ready():
    app_ctx.logger.info(f"Logged in as {get_user_display(bot)}")
    app_ctx.logger.info(f"Bot is ready (prefix: {app_ctx.config.bot.command_prefix})")

    for cmd in bot.commands:
        app_ctx.logger.info(f"Command loaded: !{cmd.name} — {cmd.help}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Quietly ignore unknown commands
        app_ctx.logger.debug("Ignored unknown command: %s", ctx.message.content)
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You're missing some required input.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You don’t have permission to use this command.")
    else:
        # Unexpected error from a valid command
        app_ctx.logger.exception("Unhandled command error: %s", error)
        await ctx.send("An error occurred while processing the command.")



async def main():
    app_ctx.boot()
    try:
        async with bot:
            await load_extensions()
            await bot.start(app_ctx.config.bot.token)
    except Exception:
        app_ctx.logger.exception("Bot startup failed:")
    finally:
        app_ctx.shutdown()


asyncio.run(main())
