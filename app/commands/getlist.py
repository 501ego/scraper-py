import discord
from discord import app_commands
from app.config import CHANNEL_ID, GUILD_ID
from app.services.database import get_all_urls


@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.command(name="list", description="Retrieve the complete list of URLs mapped by source.")
async def getlist(interaction: discord.Interaction):
    """Slash command to retrieve the list of URLs by source."""
    if int(interaction.channel_id) != int(CHANNEL_ID):
        await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
        return
    docs = get_all_urls()
    description = ""
    for doc in docs:
        source = doc.get("source", "Unknown")
        urls = doc.get("urls", [])
        description += f"**{source}:**\n" + "\n".join(urls) + "\n\n"
    embed = discord.Embed(
        title="Scraper URL Repository", description=description or "No URLs found.", color=0x0000ff)
    embed.set_footer(
        text=f"Generated by {interaction.client.user.name}", icon_url=interaction.client.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)
