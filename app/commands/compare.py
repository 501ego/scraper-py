import discord
from discord import app_commands
from app.config import CHANNEL_ID, GUILD_ID, SOURCES, PARIS_LABELS, FALABELLA_LABELS
from app.services.scraper import ParisScraper, FalabellaScraper
from app.utils.price_comparer import create_embed_for_url
from app.services.database import get_urls_by_source
from app.services.logger import get_logger
import asyncio

logger = get_logger("compare_command")


@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.command(
    name="compare",
    description="Compare prices for all stored URLs and notify if price has changed."
)
async def compare(interaction: discord.Interaction):
    if int(interaction.channel_id) != int(CHANNEL_ID):
        await interaction.response.send_message(
            "This command can only be used in the designated channel.",
            ephemeral=True
        )
        return

    await interaction.response.send_message("Comparing prices, this may take a moment...")

    scraper_mapping = {
        "paris": (ParisScraper(), PARIS_LABELS),
        "falabella": (FalabellaScraper(), FALABELLA_LABELS)
    }

    channel = interaction.channel
    tasks = []

    for source in SOURCES:
        scraper, labels = scraper_mapping[source.lower()]
        urls = get_urls_by_source(source)

        for url in urls:
            tasks.append(create_embed_for_url(
                source, url, scraper, labels, interaction.client))

    embeds = await asyncio.gather(*tasks, return_exceptions=True)

    total_sent = 0
    for embed in embeds:
        if isinstance(embed, discord.Embed):
            await channel.send(embed=embed)
            total_sent += 1
            await asyncio.sleep(0.2)

    if total_sent == 0:
        await channel.send("No URLs to compare or no changes detected.")
