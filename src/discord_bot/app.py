import difflib
from enum import Enum
import os
import discord
from discord.ext import commands

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]


class Profession(Enum):
    alchemy = "Alchemy"
    blacksmithing = "Blacksmithing"
    enchanting = "Enchanting"
    engineering = "Engineering"
    leatherworking = "Leatherworking"
    tailoring = "Tailoring"
    herbalism = "Herbalism"
    mining = "Mining"
    skinning = "Skinning"
    cooking = "Cooking"
    fishing = "Fishing"
    first_aid = "First aid"
    lockpicking = "Lockpicking"


profession_aliases = {
    Profession.alchemy: ["alch", "alchemist"],
    Profession.blacksmithing: ["bs", "blacksmith", "hammer"],
    Profession.enchanting: ["enchant", "enchanter"],
    Profession.engineering: ["eng", "engineer", "cog"],
    Profession.leatherworking: ["lw", "leatherwork", "leatherworker"],
    Profession.tailoring: ["tailor", "cloth", "clothier"],
    Profession.herbalism: ["herb", "herbalist", "flower"],
    Profession.mining: ["mine", "miner"],
    Profession.skinning: ["skin", "skinner"],
    Profession.cooking: ["cook", "chef", "food"],
    Profession.fishing: ["fish", "fisher", "angler"],
    Profession.first_aid: ["aid", "heal", "healer", "bandage"],
    Profession.lockpicking: ["lockpick", "lockpicker", "lock", "rogue"],
}


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


all_professions: dict[discord.Member, list[Profession]] = {}


def find_prof(prof_str):
    available_professions = [prof.name for prof in Profession] + [
        alias for prof in profession_aliases for alias in profession_aliases[prof]
    ]
    matches = difflib.get_close_matches(prof_str, available_professions)
    if len(matches) == 0:
        return None
    else:
        match = matches[0]

        for prof in profession_aliases:
            if matches[0] in profession_aliases[prof]:
                match = prof.name
                break

        return Profession[match]


@bot.command(name="add-prof")
async def add_prof(ctx):
    split = ctx.message.content.split(" ")
    if len(split) < 2:
        await ctx.send("Please provide one or more professions to register.")
        return

    profession_strs = ctx.message.content.split(" ")[1:]
    for profession_str in profession_strs:
        profession = find_prof(profession_str)
        if profession is None:
            await ctx.send(f'Profession "{profession_str}" not found.')
            continue

        guild = ctx.guild
        channel = ctx.channel
        author = ctx.message.author

        if author not in all_professions:
            all_professions[author] = []

        if profession in all_professions[author]:
            await ctx.send(f'Profession "{profession.value}" already registered.')
            continue

        all_professions[author].append(profession)

        print(
            f"Registered profession {profession} by {author} ({author.id}) in {guild} in {channel}"
        )
        await ctx.send(
            f'Registered profession "{profession.value}" for user "{author.display_name}".'
        )


@bot.command(name="remove-prof")
async def remove_prof(ctx):
    split = ctx.message.content.split(" ")
    if len(split) < 2:
        await ctx.send("Please provide a profession to register.")
        return

    profession_strs = ctx.message.content.split(" ")[1:]
    for profession_str in profession_strs:
        profession = find_prof(profession_str)
        if profession is None:
            await ctx.send(f'Profession "{profession_str}" not found.')
            continue

        guild = ctx.guild
        channel = ctx.channel
        author = ctx.message.author

        if author not in all_professions:
            all_professions[author] = []

        if profession not in all_professions[author]:
            await ctx.send(f'Profession "{profession}" not found.')
            return

        all_professions[author].remove(profession)

        print(
            f"Removed profession {profession.value} by {author} ({author.id}) in {guild} in {channel}"
        )
        await ctx.send(
            f'Removed profession "{profession.value}" for user "{author.display_name}".'
        )


@bot.command(name="list-prof")
async def list_prof(ctx):
    unique_professions = {
        profession
        for author in all_professions
        for profession in all_professions[author]
    }

    profession_groups: dict[Profession, list[discord.Member]] = {
        profession: [
            author
            for author in all_professions
            if profession in all_professions[author]
        ]
        for profession in unique_professions
    }

    if len(all_professions) == 0:
        await ctx.send("No professions registered.")
    else:
        prof_groups = [
            f"{profession.value}: {', '.join([f"{author.display_name}" for author in authors])}"
            for profession, authors in profession_groups.items()
        ]
        await ctx.send("\n".join(prof_groups))


@bot.command(name="my-prof")
async def my_prof(ctx):
    author = ctx.message.author
    if author not in all_professions or len(all_professions[author]) == 0:
        await ctx.send(f'No professions registered for user "{author.display_name}".')
    else:
        await ctx.send(
            f"Registered professions: {', '.join([profession.value for profession in all_professions[author]])}"
        )


# Replace 'YOUR_BOT_TOKEN' with your bot's token
bot.run(DISCORD_BOT_TOKEN)
