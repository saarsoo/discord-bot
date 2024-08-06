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
from discord_bot.profession import Profession, profession_aliases
from discord_bot.profession_recipes import profession_recipes

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]


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


async def _add_professions(ctx, raw_professions):
    for raw_profession in raw_professions:
        profession = find_prof(raw_profession)
        if profession is None:
            await ctx.send(f"Profession `{raw_profession}` not found.")
            continue

        author = ctx.message.author

        await add_profession(author.id, profession.value)

        await ctx.send(
            f"Registered profession `{profession.value}` for user `{author.display_name}`."
        )


@bot.command(name="remove-prof")
async def remove_prof(ctx, *raw_professions):
    if len(raw_professions) == 0:
        await ctx.send("Please provide a profession to register.")
        return

    for raw_profession in raw_professions:
        profession = find_prof(raw_profession)
        if profession is None:
            await ctx.send(f'Profession "{raw_profession}" not found.')
            continue

        author = ctx.message.author

        await remove_profession(author.id, profession.value)

        await ctx.send(
            f"Removed profession `{profession.value}` for user `{author.display_name}`."
        )


@bot.command(name="prof")
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
            f"`{profession}`: {', '.join([f"`{author}`" for author in authors])}"
            for profession, authors in profession_groups.items()
        ]
        await ctx.send("\n".join(prof_groups))


@bot.command(name="my-prof")
async def my_prof(ctx, *raw_professions):
    await add_user(ctx.message.author.id, ctx.message.author.display_name)

    if len(raw_professions) > 0:
        await _add_professions(ctx, raw_professions)
        return

    user_professions = await get_user_professions(ctx.message.author.id)
    author = ctx.message.author
    if not user_professions:
        await ctx.send(f"No professions registered for user `{author.display_name}`.")
    else:
        await ctx.send(
            f"Registered professions: {', '.join([f'`{profession["profession_name"]}`' for profession in user_professions])}"
        )


@bot.command(name="add-recipe")
async def add_recipe(ctx, *search_recipes):
    try:
        user_professions = await get_user_professions(ctx.message.author.id)

        if not user_professions:
            await ctx.send(
                "No professions registered. Add professions with `!prof <prof>`."
            )
            return

        user_professions = [Profession(prof["profession_name"]) for prof in user_professions]

        if not search_recipes:
            await ctx.send("Please provide one or more recipes to register.")
            return

        all_recipe_names = [
            recipe_name
            for profession, recipes in profession_recipes.items()
            if profession in user_professions
            for recipe_name in list(recipes.keys())
        ]

        matches = await _search_recipe(search_recipes, all_recipe_names)

        for key, recipes in matches.items():
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
async def remove_recipe(ctx, *recipe_strs):
    if len(recipe_strs) == 0:
        await ctx.send("Please provide a recipe to remove.")
        return

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
    search_recipes: list[str], available_recipes: list[str]
) -> dict[str, list[str]]:
    result_groups = {recipe: [] for recipe in search_recipes}

    for search_recipe in search_recipes:
        matches = []

        available_recipe_names = [r.lower() for r in available_recipes]
        if search_recipe in available_recipe_names:
            matches = [
                r for r in available_recipes if search_recipe.lower() == r.lower()
            ]
        else:
            matches = difflib.get_close_matches(
                search_recipe.lower(), available_recipe_names
            )
            matches = [
                r for r in available_recipes if search_recipe.lower() in r.lower()
            ]

        if not matches:
            matches = [
                r for r in available_recipes if search_recipe.lower() in r.lower()
            ]

        if matches:
            better_matches = [
                match for match in matches if search_recipe.lower() in match.lower()
            ]
            if better_matches:
                matches = better_matches

            if len(matches) == 1 or matches[0].lower() == search_recipe.lower():
                matched_recipe = matches[0]
                result_groups[search_recipe].append(matched_recipe)
            else:
                result_groups[search_recipe].extend(matches)

    return result_groups


@bot.command(name="search")
async def search_recipe(ctx, *recipes):
    all_recipe_names = [
        recipe_name
        for profession, recipes in profession_recipes.items()
        for recipe_name in list(recipes.keys())
    ]

    matches = await _search_recipe(recipes, all_recipe_names)

    if matches:
        recipe_names = [
            recipe_name
            for recipe_names in matches.values()
            for recipe_name in recipe_names
        ]
        await ctx.send(
            f"Available recipes {', '.join([f'`{recipe_name}`' for recipe_name in recipe_names])}."
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
        await ctx.send("Please provide one or more recipes to search for.")
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


@bot.command(name="my-recipes")
async def list_recipes(ctx):
    user_recipes = await get_user_recipes(ctx.message.author.id)

    if not user_recipes:
        await ctx.send(
            f"No recipes registered for user `{ctx.message.author.display_name}`."
        )
        return

    user_recipe_names: list[str] = [recipe["recipe_name"] for recipe in user_recipes]

    user_professions = await get_user_professions(ctx.message.author.id)
    if not user_professions:
        await ctx.send(
            f"No professions registered for user `{ctx.message.author.display_name}`."
        )
        return

    user_professions = [
        Profession(prof["profession_name"]) for prof in user_professions
    ]

    recipe_groups = {
        profession.value: [
            user_recipe_name
            for user_recipe_name in user_recipe_names
            if profession in profession_recipes and user_recipe_name in profession_recipes[profession]
        ]
        for profession in user_professions
    }

    for profession, recipes_names in recipe_groups.items():
        if recipes_names:
            await ctx.send(
                f"`{profession}`: {', '.join([f'`{recipe_name}`' for recipe_name in recipes_names])}"
            )


@bot.command(name="commands")
async def list_commands(ctx):
    await ctx.send(
        "Commands:\n"
        "`!who <recipe>` - Display users that can craft an item\n"
        "`!search <recipe>` - Search for a recipe\n"
        "`!prof` - List all user professions\n"
        "`!my-prof` - List or register your professions\n"
        "`!remove-prof <profession>` - Remove one or more professions\n"
        "`!my-recipes` - List recipes that you can craft\n"
        "`!add-recipe <recipe>` - Add one or more recipes\n"
        "`!remove-recipe <recipe>` - Remove one or more recipes\n"
    )


bot.run(DISCORD_BOT_TOKEN)
