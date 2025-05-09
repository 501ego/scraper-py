import discord
from discord import app_commands
from app.config import CHANNEL_ID, GUILD_ID, SOURCES
from app.services.database import add_url
from app.utils.url_utils import extract_source


@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.command(
    name="add",
    description="Add a URL for a given source. If source is empty, it will be extracted from the URL."
)
async def add(interaction: discord.Interaction, url: str):
    """Slash command to add a URL document to MongoDB for a given source."""
    if int(interaction.channel_id) != int(CHANNEL_ID):
        await interaction.response.send_message(
            "This command can only be used in the designated channel.",
            ephemeral=True
        )
        return

    source = extract_source(url)
    if source is None or source not in SOURCES:
        await interaction.response.send_message(
            "Invalid source provided. Please use one of the following: Falabella, Paris or SP Digital. More sources will be supported soon.",
            ephemeral=True
        )
        return

    added = add_url(source, url)
    print(f"URL Added: {added}")
    if added:
        embed = discord.Embed(
            title="URL Added",
            description=f"Source: **{source}**\nURL: **{url}**",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="Already Exists in Scraper Repository",
            description=f"Source: **{source}**\nURL: **{url}**",
            color=0xff0000
        )
    embed.set_footer(
        text=f"Generated by {interaction.client.user.name}",
        icon_url=interaction.client.user.display_avatar.url
    )
    await interaction.response.send_message(embed=embed)
