import discord
from discord.ext import commands
from app.config import DISCORD_BOT_TOKEN, GUILD_ID, service_name
from app.services.logger import get_logger
from app.commands.add import add as add_command
from app.commands.getlist import getlist as getlist_command
from app.commands.compare import compare as compare_command


class DiscordBot(commands.Bot):
    """Discord bot for handling slash commands and sending formatted messages."""

    def __init__(self, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.logger = get_logger(service_name)

    async def setup_hook(self):
        self.tree.add_command(add_command)
        self.tree.add_command(getlist_command)
        self.tree.add_command(compare_command)
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

    async def on_ready(self):
        """Handles the event when the bot is ready."""
        print(f'Logged in as {self.user}')


def run_bot():
    """Starts the Discord bot."""
    intents = discord.Intents.default()
    intents.message_content = True
    bot = DiscordBot(command_prefix='!', intents=intents)
    bot.run(DISCORD_BOT_TOKEN)
