import discord
from discord.ext import commands
import asyncio
import webserver
import os
TOKEN = os.environ['discordkey']
intents = discord.Intents.default()
intents.message_content = True  # REQUIRED

bot = commands.Bot(command_prefix="!", intents=intents)

audio_delete_enabled = False
AUDIO_EXTENSIONS = (".mp3", ".wav")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(
    name="toggleaudiodelete",
    description="Enable or disable auto-deletion of .mp3 and .wav files after 1 minute"
)
@discord.app_commands.checks.has_permissions(administrator=True)
async def toggle_audio_delete(interaction: discord.Interaction):
    global audio_delete_enabled
    audio_delete_enabled = not audio_delete_enabled

    status = "ENABLED" if audio_delete_enabled else "DISABLED"
    await interaction.response.send_message(
        f"🔊 Auto-deletion of `.mp3` and `.wav` files is now **{status}**.",
        ephemeral=True
    )

# Error handler for missing permissions
@toggle_audio_delete.error
async def toggle_audio_delete_error(
    interaction: discord.Interaction,
    error: discord.app_commands.AppCommandError
):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ You must be an **administrator** to use this command.",
            ephemeral=True
        )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if not audio_delete_enabled:
        return

    if not message.attachments:
        return

    for attachment in message.attachments:
        if attachment.filename.lower().endswith(AUDIO_EXTENSIONS):
            await asyncio.sleep(60)
            try:
                await message.delete()
            except discord.NotFound:
                pass
            except discord.Forbidden:
                print("Missing Manage Messages permission")
            break

    await bot.process_commands(message)

webserver.keep_alive
bot.run("TOKEN")

