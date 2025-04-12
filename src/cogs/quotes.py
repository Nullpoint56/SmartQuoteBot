import random
import discord
from discord.ext import commands
from discord import app_commands, Interaction, File

from paths import QUOTES_FILE
from utils.storage import load_quotes, save_quotes
from startup import app_ctx


def is_admin():
    async def predicate(interaction: Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    return app_commands.check(predicate)


class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes = load_quotes()
        app_ctx.logger.info("QuoteCog loaded. Quotes loaded: %d", len(self.quotes))

    # --- Slash Commands ---

    @app_commands.command(name="quote", description="Get a random quote")
    async def quote(self, interaction: Interaction):
        if not self.quotes:
            await interaction.response.send_message("No quotes available!", ephemeral=True)
            app_ctx.logger.info("User %s tried to get a quote but none exist.", interaction.user)
        else:
            quote = random.choice(self.quotes)
            await interaction.response.send_message(f"{quote}")
            app_ctx.logger.info("User %s retrieved quote: %s", interaction.user, quote)

    @app_commands.command(name="rodof-add", description="Add a quote")
    async def add_quote(self, interaction: Interaction, quote: str):
        self.quotes.append(quote)
        save_quotes(self.quotes)
        await interaction.response.send_message(f"Added quote: '{quote}'")
        app_ctx.logger.info("User %s added quote: %s", interaction.user, quote)

    @app_commands.command(name="rodof-remove", description="Remove a quote (admin only)")
    @is_admin()
    async def remove_quote(self, interaction: Interaction, quote: str):
        try:
            self.quotes.remove(quote)
            save_quotes(self.quotes)
            await interaction.response.send_message(f"Removed: '{quote}'")
            app_ctx.logger.info("Admin %s removed quote: %s", interaction.user, quote)
        except ValueError:
            await interaction.response.send_message("Quote not found.")
            app_ctx.logger.warning("Admin %s tried to remove non-existent quote: %s", interaction.user, quote)

    @app_commands.command(name="rodof-list", description="List all quotes (admin only)")
    @is_admin()
    async def list_quotes(self, interaction: Interaction):
        if not self.quotes:
            await interaction.response.send_message("No quotes yet.")
            app_ctx.logger.info("Admin %s requested quote list, but it's empty.", interaction.user)
        else:
            formatted = "\n".join([f"{i + 1}. {q}" for i, q in enumerate(self.quotes)])
            # If too long, paginate or truncate — Discord has limits
            if len(formatted) > 1900:
                formatted = formatted[:1900] + "\n..."
            await interaction.response.send_message(f"Quotes:\n```{formatted}```")
            app_ctx.logger.info("Admin %s listed quotes.", interaction.user)

    @app_commands.command(name="rodof-download", description="Download the current quotes (admin only)")
    @is_admin()
    async def download_quotes(self, interaction: discord.Interaction):
        if not QUOTES_FILE.exists():
            await interaction.response.send_message("No quotes file found to download.")
            app_ctx.logger.warning("Admin %s tried to download quotes but file was missing.", interaction.user)
            return

        await interaction.response.send_message("Downloading quotes...", ephemeral=True)
        try:
            await interaction.followup.send(
                file=File(QUOTES_FILE, filename="quotes.json"),
                ephemeral=True  # only visible to the admin
            )
            app_ctx.logger.info("Admin %s downloaded the quotes file.", interaction.user)
        except Exception:
            app_ctx.logger.exception("Failed to send quotes.json to admin:")
            await interaction.followup.send("Failed to send quotes file.")

    @app_commands.command(name="help", description="Show help info")
    async def help(self, interaction: discord.Interaction):
        is_admin = interaction.user.guild_permissions.administrator

        text = [
            "**📜 Rodof Bot Help**",
            "",
            "🗣️ Public commands:",
            "`/quote` — Get a random quote",
            "`/rodof-add <quote>` — Add a new quote",
        ]

        if is_admin:
            text += [
                "",
                "🔐 Admin-only commands:",
                "`/rodof-remove <quote>` — Remove a quote",
                "`/rodof-list` — List all quotes",
                "`/rodof-download` — Download quotes.json",
            ]

        await interaction.response.send_message("\n".join(text), ephemeral=True)

    # --- Mention Listener ---

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions and "quote" in message.content.lower():
            if not self.quotes:
                await message.channel.send("No quotes available!")
                app_ctx.logger.info("User %s mentioned bot but no quotes exist.", message.author)
            else:
                quote = random.choice(self.quotes)
                await message.channel.send(f"{quote}")
                app_ctx.logger.info("User %s retrieved quote via mention: %s", message.author, quote)

        if self.bot.user in message.mentions and "help" in message.content.lower():
            await message.channel.send("Try `/help` for a full list of available commands!")


async def setup(bot: commands.Bot):
    await bot.add_cog(QuoteCog(bot))
