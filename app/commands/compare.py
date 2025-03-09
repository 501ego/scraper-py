import discord
from discord import app_commands
from app.config import CHANNEL_ID, GUILD_ID
from app.utils.price_comparer import get_comparison_embeds


@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.command(
    name="compare",
    description="Compare prices for all stored URLs and notify if price has changed."
)
async def compare(interaction: discord.Interaction):
    "Slash command to compare prices for all stored URLs and send individual embeds for each product."
    if int(interaction.channel_id) != int(CHANNEL_ID):
        await interaction.response.send_message(
            "This command can only be used in the designated channel.",
            ephemeral=True
        )
        return
    await interaction.response.defer()
    embeds = get_comparison_embeds(bot=interaction.client)
    if embeds:
        await interaction.followup.send(embeds=embeds)
    else:
        await interaction.followup.send("No URLs to compare.")
