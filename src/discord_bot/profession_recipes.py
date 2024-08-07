from discord_bot.alchemy import alchemy_recipes
from discord_bot.blacksmith import blacksmith_recipes
from discord_bot.cooking import cooking_recipes
from discord_bot.enchanting import enchanting_recipes
from discord_bot.engineering import engineering_recipes
from discord_bot.first_aid import first_aid_recipes
from discord_bot.fishing import fishing_recipes
from discord_bot.herbalism import herbalism_recipes
from discord_bot.leatherworking import leatherworking_recipes
from discord_bot.mining import mining_recipes
from discord_bot.rogue_poisons import rogue_poisons_recipes
from discord_bot.tailoring import tailoring_recipes
from discord_bot.profession import Profession

profession_recipes = {
    Profession.alchemy: alchemy_recipes,
    Profession.blacksmithing: blacksmith_recipes,
    Profession.cooking: cooking_recipes,
    Profession.enchanting: enchanting_recipes,
    Profession.engineering: engineering_recipes,
    Profession.first_aid: first_aid_recipes,
    Profession.fishing: fishing_recipes,
    Profession.herbalism: herbalism_recipes,
    Profession.leatherworking: leatherworking_recipes,
    Profession.mining: mining_recipes,
    Profession.rogue_poisons: rogue_poisons_recipes,
    Profession.tailoring: tailoring_recipes,
}
