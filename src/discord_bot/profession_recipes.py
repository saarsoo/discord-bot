from discord_bot.alchemy import alchemy_recipes
from discord_bot.blacksmith import blacksmith_recipes
from discord_bot.profession import Profession

profession_recipes = {
    Profession.alchemy: alchemy_recipes,
    Profession.blacksmithing: blacksmith_recipes,
}
