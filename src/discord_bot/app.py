import difflib
import logging
import os
import discord
from discord.ext import commands

from discord_bot.database import (
    add_profession,
    add_user,
    add_user_recipe,
    get_all_professions,
    get_all_recipes,
    get_user_professions,
    get_user_recipes,
    remove_profession,
    remove_user_recipe,
    validate_connection,
)
from discord_bot.profession import Profession
from discord_bot.alchemy import alchemy_recipes

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

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
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info("Testing db connection...")
    await validate_connection()


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
    await add_user(ctx.message.author.id, ctx.message.author.display_name)

    split = ctx.message.content.split(" ")
    if len(split) < 2:
        await ctx.send("Please provide one or more professions to register.")
        return

    profession_strs = ctx.message.content.split(" ")[1:]
    for profession_str in profession_strs:
        profession = find_prof(profession_str)
        if profession is None:
            await ctx.send(f"Profession `{profession_str}` not found.")
            continue

        guild = ctx.guild
        channel = ctx.channel
        author = ctx.message.author

        await add_profession(author.id, profession.value)

        await ctx.send(
            f"Registered profession `{profession.value}` for user `{author.display_name}`."
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

        await remove_profession(author.id, profession.value)

        await ctx.send(
            f"Removed profession `{profession.value}` for user `{author.display_name}`."
        )


@bot.command(name="list-prof")
async def list_prof(ctx):
    all_profs = await get_all_professions()

    if all_profs is None:
        await ctx.send("An error occurred.")
        return

    unique_professions = {prof["profession_name"] for prof in all_profs}

    profession_groups = {
        profession: [
            prof["user_name"]
            for prof in all_profs
            if prof["profession_name"] == profession
        ]
        for profession in unique_professions
    }

    if len(all_profs) == 0:
        await ctx.send("No professions registered.")
    else:
        prof_groups = [
            f"{profession}: {', '.join(authors)}"
            for profession, authors in profession_groups.items()
        ]
        await ctx.send("\n".join(prof_groups))


@bot.command(name="my-prof")
async def my_prof(ctx):
    user_professions = await get_user_professions(ctx.message.author.id)
    author = ctx.message.author
    if not user_professions:
        await ctx.send(f"No professions registered for user `{author.display_name}`.")
    else:
        await ctx.send(
            f"Registered professions: {', '.join([f'`{profession["profession_name"]}`' for profession in user_professions])}"
        )


@bot.command(name="add-recipe")
async def add_recipe(ctx):
    try:
        user_professions = await get_user_professions(ctx.message.author.id)

        if not user_professions:
            await ctx.send(
                "No professions registered. Add professions with `!add-prof`."
            )
            return

        user_professions = [prof["profession_name"] for prof in user_professions]

        search_recipes = [
            recipe.strip()
            for recipe in (" ".join(ctx.message.content.split(" ")[1:])).split(",")
            if recipe.strip()
        ]

        if not search_recipes:
            await ctx.send("Please provide one or more recipes to register.")
            return

        alchemy_recipe_names = [r.lower() for r in alchemy_recipes]

        alchemy_matches = await _search_recipe(search_recipes, alchemy_recipe_names)

        for key, recipes in alchemy_matches.items():
            if not recipes:
                await ctx.send(f"No recipe found for `{key}`.")
                continue
            else:
                if len(recipes) > 1:
                    await ctx.send(
                        f"`{key}` matches multiples recipes: {', '.join([f'`{match}`' for match in recipes])}.\nPlease be more specific."
                    )
                    continue
                else:
                    matched_recipe = recipes[0]
                    await add_user_recipe(ctx.message.author.id, matched_recipe)
                    await ctx.send(f"Added recipe `{matched_recipe}`.")
    except Exception as e:
        logger.info(f"An error occurred: {e}")
        await ctx.send("Failed to add recipes. (Something is broken)")


@bot.command(name="remove-recipe")
async def remove_recipe(ctx):
    split = ctx.message.content.split(" ")
    if len(split) < 2:
        await ctx.send("Please provide a recipe to remove.")
        return

    recipe_strs = ctx.message.content.split(" ")[1:]
    author = ctx.message.author
    user_recipes = await get_user_recipes(author.id)
    if not user_recipes:
        await ctx.send(f"No recipes registered for user `{author.display_name}`.")
        return

    user_recipe_names = [recipe["recipe_name"] for recipe in user_recipes]
    matches = await _search_recipe(recipe_strs, user_recipe_names)

    if not matches:
        await ctx.send(f"No recipe found for `{', '.join(recipe_strs)}`.")
        return
    else:
        for recipe_str, recipes in matches.items():
            for recipe in recipes:
                await remove_user_recipe(author.id, recipe)
                await ctx.send(
                    f"Removed recipe `{recipe}` for user `{author.display_name}`."
                )


async def _search_recipe(
    recipes: list[str], available_recipes: list[str]
) -> dict[str, list[str]]:
    result_groups = {recipe: [] for recipe in recipes}

    for recipe in recipes:
        matches = []

        all_alchemy_recipes = [r.lower() for r in available_recipes]
        if recipe in all_alchemy_recipes:
            matches = [recipe]
        else:
            matches = difflib.get_close_matches(recipe.lower(), all_alchemy_recipes)
            matches = [r for r in alchemy_recipes if recipe.lower() in r.lower()]

        if not matches:
            matches = [r for r in alchemy_recipes if recipe.lower() in r.lower()]

        if matches:
            better_matches = [
                match for match in matches if recipe.lower() in match.lower()
            ]
            if better_matches:
                matches = better_matches

            if len(matches) == 1 or matches[0].lower() == recipe.lower():
                matched_recipe = matches[0]
                result_groups[recipe].append(matched_recipe)
            else:
                result_groups[recipe].extend(matches)

    return result_groups


@bot.command(name="search-recipe")
async def search_recipe(ctx):
    recipes = [
        recipe.strip()
        for recipe in (" ".join(ctx.message.content.split(" ")[1:])).split(",")
    ]

    all_recipes = list(alchemy_recipes.keys())

    matches = await _search_recipe(recipes, all_recipes)

    if matches:
        await ctx.send(
            f"Available recipes {', '.join([f'`{match}`' for match in matches])}."
        )
    else:
        await ctx.send(f"No recipe found for `{', '.join(recipes)}`.")


@bot.command(name="who")
async def who(ctx):
    search_recipes = [
        recipe.strip()
        for recipe in (" ".join(ctx.message.content.split(" ")[1:])).split(",")
        if recipe.strip()
    ]

    if not search_recipes:
        await ctx.send("Please provide one or more recipes to search.")
        return

    user_recipes = await get_all_recipes()
    if not user_recipes:
        await ctx.send(f"No recipe found for `{', '.join(search_recipes)}`.")
        return

    user_recipe_names = [recipe["recipe_name"] for recipe in user_recipes]

    matches = await _search_recipe(search_recipes, user_recipe_names)

    # flatten the matches
    recipe_names = [match for match_list in matches.values() for match in match_list]

    user_crafters = [
        recipe for recipe in user_recipes if recipe["recipe_name"] in recipe_names
    ]

    recipe_user_craft_groups = {
        recipe_name: [
            recipe["user_name"]
            for recipe in user_crafters
            if recipe["recipe_name"] == recipe_name
        ]
        for recipe_name in {recipe["recipe_name"] for recipe in user_crafters}
    }

    if recipe_user_craft_groups:
        for recipe_name in recipe_user_craft_groups:
            await ctx.send(
                f"Users that can craft `{recipe_name}`: {', '.join([f'`{user}`' for user in recipe_user_craft_groups[recipe_name]])}"
            )
    else:
        await ctx.send(f"No recipe found for `{', '.join(search_recipes)}`.")


@bot.command(name="commands")
async def list_commands(ctx):
    await ctx.send(
        "Commands:\n"
        "`!add-prof <profession>` - Add one or more professions\n"
        "`!remove-prof <profession>` - Remove one or more professions\n"
        "`!list-prof` - List all registered professions\n"
        "`!my-prof` - List your registered professions\n"
        "`!add-recipe <recipe>` - Add one or more recipes\n"
        "`!remove-recipe <recipe>` - Remove one or more recipes\n"
        "`!search-recipe <recipe>` - Search for a recipe\n"
        # "!craft <recipe> - Display users that can craft an item\n"
        "`!who <recipe>` - Display users that can craft an item\n"
    )


bot.run(DISCORD_BOT_TOKEN)
