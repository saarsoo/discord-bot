from enum import Enum


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
    rogue_poisons = "Rogue Poisons"


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
    Profession.rogue_poisons: ["poison"],
}
