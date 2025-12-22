import discord
from discord import app_commands
from discord.ext import commands
from langdetect import detect, LangDetectException
import datetime

# Replace with your bot token
TOKEN = 'YOUR_BOT_TOKEN_HERE'

# Channel IDs (replace with your actual channel IDs)
ENGLISH_CHANNEL_ID = 123456789012345678  # English chat channel
HINDI_CHANNEL_ID = 987654321098765432    # Hindi chat channel

# Timeout duration in seconds (e.g., 300 = 5 minutes)
TIMEOUT_DURATION = 300

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot is ready as {bot.user}')

@bot.tree.command(name="help", description="Shows information about the bot's commands and features.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Language Enforcement Bot Help",
        description="This bot enforces language rules: only English in the English channel (timeouts for Hindi), strictly Hindi in the Hindi channel (timeouts for any non-Hindi).",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Features",
        value=(
            "- **English Channel**: Timeouts users for Hindi messages (5 minutes).\n"
            "- **Hindi Channel**: Timeouts users for any non-Hindi messages (5 minutes).\n"
            "- Uses language detection to identify violations.\n"
            "- Timeouts are temporary mutes applied by the bot."
        ),
        inline=False
    )
    embed.add_field(
        name="Commands",
        value="- `/help`: Displays this help message.",
        inline=False
    )
    embed.set_footer(text="Bot created with discord.py. Contact an admin if you have issues.")
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"Message received in channel {message.channel.id}: '{message.content}'")  # Debug: logs all messages

    if message.channel.id == ENGLISH_CHANNEL_ID:
        try:
            lang = detect(message.content)
            print(f"Detected language in English channel: {lang} for message: '{message.content}'")
            if lang == 'hi':
                print(f"Attempting to timeout {message.author} for Hindi in English channel.")
                await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=TIMEOUT_DURATION))
                await message.channel.send(f'{message.author.mention}, you were timed out for 5 minutes for speaking Hindi in the English channel.')
                print("Timeout applied successfully.")
        except LangDetectException:
            print("Language detection failed in English channel.")
        except discord.Forbidden:
            print("Forbidden: Bot lacks permissions to timeout in English channel.")

    elif message.channel.id == HINDI_CHANNEL_ID:
        try:
            lang = detect(message.content)
            print(f"Detected language in Hindi channel: {lang} for message: '{message.content}'")
            if lang != 'hi':  # Strict: Timeout for any non-Hindi
                print(f"Attempting to timeout {message.author} for non-Hindi ({lang}) in Hindi channel.")
                await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=TIMEOUT_DURATION))
                await message.channel.send(f'{message.author.mention}, you were timed out for 5 minutes for speaking non-Hindi in the Hindi channel.')
                print("Timeout applied successfully.")
        except LangDetectException:
            print("Language detection failed in Hindi channel (skipping timeout).")
        except discord.Forbidden:
            print("Forbidden: Bot lacks permissions to timeout in Hindi channel.")

    await bot.process_commands(message)

bot.run(TOKEN)