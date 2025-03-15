import discord
from discord.ext import commands
from app.config import DISCORD_BOT_TOKEN, GUILD_ID, service_name
from app.services.logger import get_logger
from app.commands.add import add as add_command
from app.commands.getlist import getlist as getlist_command
from app.commands.compare import compare as compare_command
from app.services.openvpn import connect_vpn, ensure_vpn_connection
from app.services.price_watcher import PriceWatcher
import threading
import time

logger = get_logger(service_name)


class DiscordBot(commands.Bot):
    """Discord bot for handling slash commands and sending formatted messages."""

    def __init__(self, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.logger = get_logger(service_name)
        self.price_watcher = PriceWatcher(self)

    async def setup_hook(self):
        self.tree.add_command(add_command)
        self.tree.add_command(getlist_command)
        self.tree.add_command(compare_command)
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        self.price_watcher.watch_prices.start()

    async def on_ready(self):
        """Handles the event when the bot is ready."""
        print(f'Logged in as {self.user}')


def wait_for_vpn_connection():
    """
    Blocks until a VPN connection is established.
    Repeatedly calls connect_vpn() until it succeeds.
    """
    while True:
        try:
            vpn_process = connect_vpn()
            logger.info(
                "VPN connection established. Proceeding with bot startup.")
            return vpn_process
        except Exception as e:
            logger.error("Error connecting to VPN: %s", e)
            logger.info("Retrying VPN connection in 10 seconds...")
            time.sleep(10)


def run_bot():
    """Starts the Discord bot only after the VPN connection is established."""
    wait_for_vpn_connection()
    vpn_thread = threading.Thread(target=ensure_vpn_connection, daemon=True)
    vpn_thread.start()

    intents = discord.Intents.default()
    intents.message_content = True
    bot = DiscordBot(command_prefix='!', intents=intents)
    bot.run(DISCORD_BOT_TOKEN)
