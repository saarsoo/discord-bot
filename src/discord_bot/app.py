import os
import discord
from discord.ext import commands

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Define the intents
intents = discord.Intents.all()
intents.message_content = True  # This enables the bot to read message content

# Create a new instance of the bot
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("hello"):
        await message.channel.send("Hello!")

    await bot.process_commands(message)


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")


# Replace 'YOUR_BOT_TOKEN' with your bot's token
bot.run(DISCORD_BOT_TOKEN)
