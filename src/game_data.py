# game_data.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import xmltodict
import pygame
from collections import OrderedDict
from enum import Enum
import commons
import random


class ItemTag(Enum):
    TILE = 0
    WALL = 1
    MATERIAL = 2
    WEAPON = 3
    TOOL = 4
    MELEE = 5
    RANGED = 6
    MAGICAL = 7
    AMMO = 8
    PICKAXE = 9
    AXE = 10
    HAMMER = 11
    GRAPPLE = 12
    COIN = 13


class ItemPrefixGroup(Enum):
    UNIVERSAL = 0
    COMMON = 1
    MELEE = 2
    RANGED = 3
    MAGICAL = 4


class TileTag(Enum):
    TRANSPARENT = 0
    NODRAW = 1
    NOCOLLIDE = 2
    MULTITILE = 3
    CYCLABLE = 4
    CHEST = 5
    BREAKABLE = 6
    CRAFTINGTABLE = 7
    PLATFORM = 8
    DAMAGING = 9


class TileStrengthType(Enum):
    PICKAXE = 0
    HAMMER = 1
    AXE = 2
    DAMAGE = 3


class TileMaskType(Enum):
    NONE = 0
    NOISY = 1


def make_item_tag_list(item_tags_str):
    str_list = item_tags_str.split(",")
    enum_list = []
    for string in str_list:
        for tag in ItemTag:
            if tag.name.lower() == string:
                enum_list.append(tag)
                break
    return enum_list

def make_item_prefix_list(item_prefixes_str):
    str_list = item_prefixes_str.split(",")
    enum_list = []
    for string in str_list:
        for prefix in ItemPrefixGroup:
            if prefix.name.lower() == string:
                enum_list.append(prefix)
                break
    return enum_list


def make_tile_tag_list(tile_tags_str):
    str_list = tile_tags_str.split(",")
    enum_list = []
    for string in str_list:
        for tag in TileTag:
            if tag.name.lower() == string:
                enum_list.append(tag)
                break
    return enum_list


def int_tuple_str_to_int_tuple(string):
    split_string = string.split(",")
    return int(split_string[0]), int(split_string[1])


def float_tuple_str_to_float_tuple(string):
    split_string = string.split(",")
    return float(split_string[0]), float(split_string[1])


def int_tuple_list_str_to_int_tuple_list(string):
    tuple_strs = string.split(";")
    return_list = []
    for tuple_str in tuple_strs:
        if tuple_str != "":
            return_list.append(int_tuple_str_to_int_tuple(tuple_str))
    return return_list


def float_tuple_list_str_to_float_tuple_list(string):
    tuple_strs = string.split(";")
    return_list = []
    for tuple_str in tuple_strs:
        return_list.append(float_tuple_str_to_float_tuple(tuple_str))
    return return_list


def get_tile_strength_type_from_str(strength_type_string):
    if strength_type_string == "Pickaxe":
        return TileStrengthType.PICKAXE
    elif strength_type_string == "Axe":
        return TileStrengthType.AXE
    elif strength_type_string == "Hammer":
        return TileStrengthType.HAMMER
    elif strength_type_string == "Damage":
        return TileStrengthType.DAMAGE


def get_tile_mask_type_from_str(mask_type_string):
    if mask_type_string == "None":
        return TileMaskType.NONE
    elif mask_type_string == "Noisy":
        return TileMaskType.NOISY


def find_next_char_in_string(string, char, start_index):
    for char_index in range(start_index, len(string)):
        if string[char_index] == char:
            return char_index
    return -1


# Biome Tile Information
# [[surface tile,base tile, alt tile],[wall tile, alt wall tile]]
biome_tile_vals = [[["fg.tile.grass", "fg.tile.dirt", "fg.tile.stone"], ["fg.wall.dirt", "fg.wall.stone"]],
                   [["fg.tile.snow", "fg.tile.snow", "fg.tile.ice"], ["fg.wall.snow", "fg.wall.ice"]],
                   [["fg.tile.sand", "fg.tile.sand", "fg.tile.sandstone"], ["fg.wall.sand", "fg.wall.sandstone"]]
                  ]

platform_blocks = [257]

xml_item_data = []
item_id_str_hash_table = {}
ammo_type_item_lists = {}
xml_tile_data = []
tile_id_str_hash_table = {}
tile_id_light_reduction_lookup = []
tile_id_light_emission_lookup = []
xml_wall_data = []
wall_id_str_hash_table = {}
xml_sound_data = []
sound_id_str_hash_table = {}
xml_structure_data = []
structure_id_str_hash_table = {}
xml_loot_data = []
loot_id_str_hash_table = {}

sound_volume_multiplier = 1.0
music_volume_multiplier = 1.0


#             Enemy Information
#
#             ||     Name     |  Type  |HP |Defense|KB Resist|Damage|    Blood Col   |   Item Drops   | Coin Drops ||
enemy_data = [[ "Green Slime", "Slime", 14,      0,     -0.2,     6, (10,  200,  10), [("fg.item.gel_blue", 1, 3, 100)], ( 5,  30)],
              [  "Blue Slime", "Slime", 25,      2,        0,     7, (10,   10, 200), [("fg.item.gel_blue", 1, 3, 100)], (15,  50)],
              [   "Red Slime", "Slime", 35,      4,        0,    12, (200,  10,  10), [("fg.item.gel_blue", 1, 3, 100)], (25,  75)],
              ["Purple Slime", "Slime", 40,      6,      0.1,    12, (200,  10, 200), [("fg.item.gel_blue", 1, 3, 100)], (35, 110)],
              ["Yellow Slime", "Slime", 45,      7,        0,    15, (200, 150,  10), [("fg.item.gel_blue", 1, 3, 100)], (45, 130)],
              ]


#                 Projectile Information
#
#                 ||     Name     |   Type  | Damage |Knockback|Bounces|Hitbox Size|  Trail  |  Gravity |Drag Mod|Sound ID |
projectile_data = [[  "Wooden Arrow",  "Arrow",     5,        0,      0,         13,  "arrow",       0.5,       1,       16],
                   [   "Musket Ball", "Bullet",     7,        2,      0,         10, "bullet",      0.05,     0.1,       17],
                   [   "Copper Coin", "Bullet",     1,        2,      0,         10, "bullet",      0.40,       3,       17],
                   [   "Silver Coin", "Bullet",     3,        2,      0,         10, "bullet",      0.20,       2,       17],
                   [     "Gold Coin", "Bullet",    15,        2,      0,         10, "bullet",      0.10,       1,       17],
                   [ "Platinum Coin", "Bullet",    50,        2,      0,         10, "bullet",      0.05,     0.1,       17],
                   ]


# Item Prefix Information
prefix_data = {
    ItemPrefixGroup.UNIVERSAL:
        [  # ||   Name   |Damage|Crit Chance|Knockback|Tier||
            [      "Keen",     0,       0.03,        0,   1],
            [  "Superior",   0.1,       0.03,      0.1,   2],
            [  "Forceful",     0,          0,     0.15,   1],
            [    "Broken",  -0.3,          0,     -0.2,  -2],
            [   "Damaged", -0.15,          0,        0,  -1],
            [    "Shoddy",  -0.1,          0,    -0.15,  -2],
            [   "Hurtful",   0.1,          0,        0,   1],
            [    "Strong",     0,          0,     0.15,   1],
            ["Unpleasant",  0.05,          0,     0.15,   2],
            [      "Weak",     0,          0,     -0.2,  -1],
            [  "Ruthless",  0.18,          0,     -0.1,   1],
            [     "Godly",  0.15,       0.05,     0.15,   2],
            [   "Demonic",  0.15,       0.05,        0,   2],
            [   "Zealous",     0,       0.05,        0,   1],
        ],

    ItemPrefixGroup.COMMON:
        [  # ||   Name  |Damage| Speed|Crit Chance|Knockback|Tier||
            [    "Quick",     0,   0.1,          0,        0,   1],
            [   "Deadly",   0.1,   0.1,          0,        0,   2],
            [    "Agile",     0,   0.1,       0.03,        0,   1],
            [   "Nimble",     0,  0.05,          0,        0,   1],
            ["Murderous", -0.07,  0.06,       0.03,        0,   2],
            [     "Slow",     0, -0.15,          0,        0,  -1],
            [ "Sluggish",     0,  -0.2,          0,        0,  -2],
            [     "Lazy",     0, -0.08,          0,        0,  -1],
            [ "Annoying",  -0.2, -0.15,          0,        0,  -2],
            [    "Nasty",  0.05,   0.1,       0.02,     -0.1,   1],
            [ "Quick AF",     0,     1,          0,        0,   10],
        ],

    ItemPrefixGroup.MELEE:
        [  # ||   Name  |Damage| Speed|Crit Chance| Size |Knockback|Tier||
            [    "Large",     0,     0,          0,  0.12,        0,   1],
            [  "Massive",     0,     0,          0,  0.18,        0,   1],
            ["Dangerous",  0.05,     0,       0.02,  0.05,        0,   1],
            [   "Savage",   0.1,     0,          0,   0.1,      0.1,   2],
            [    "Sharp",  0.15,     0,          0,     0,        0,   1],
            [   "Pointy",   0.1,     0,          0,     0,        0,   1],
            [     "Tiny",     0,     0,          0, -0.18,        0,  -1],
            [ "Terrible", -0.15,     0,          0, -0.13,    -0.15,  -2],
            [    "Small",     0,     0,          0,  -0.1,        0,  -1],
            [     "Dull", -0.15,     0,          0,     0,        0,  -1],
            [  "Unhappy",     0,  -0.1,          0,  -0.1,     -0.1,  -2],
            [    "Bulky",  0.05, -0.15,          0,   0.1,      0.1,   1],
            [ "Shameful",  -0.1,     0,          0,   0.1,     -0.2,  -2],
            [    "Heavy",     0,  -0.1,          0,     0,     0.15,   0],
            [    "Light",     0,  0.15,          0,     0,     -0.1,   0],
            ["Legendary",  0.15,   0.1,       0.05,   0.1,     0.15,   2],
    ["Bit O' Everything",   0.2,   0.2,        0.2,   0.2,      0.2,   5],
        ],

    ItemPrefixGroup.RANGED:
        [  # ||    Name    | Damage  |Speed|Crit Chance|Velocity|Knockback|Tier||
            [     "Sighted",      0.1,    0,       0.03,       0,        0,   1],
            [       "Rapid",        0, 0.15,          0,     0.1,        0,   2],
            [       "Hasty",        0,  0.1,          0,    0.15,        0,   2],
            ["Intimidating",        0,    0,          0,    0.05,     0.15,   2],
            [      "Deadly",      0.1, 0.05,       0.02,    0.05,     0.05,   2],
            [     "Staunch",      0.1,    0,          0,       0,     0.15,   2],
            [       "Awful",    -0.15,    0,          0,    -0.1,     -0.1,  -2],
            [   "Lethargic",        0, 0.15,          0,    -0.1,        0,  -2],
            [     "Awkward",        0, -0.1,          0,       0,     -0.2,  -2],
            [    "Powerful",     0.15, -0.1,       0.01,       0,        0,   1],
            [   "Frenzying",    -0.15, 0.15,          0,       0,        0,   0],
            [      "Unreal",     0.15,  0.1,       0.05,     0.1,     0.15,   2],
            [       "ADMIN", 99999.99, 0.85,          1,       1,        1,  11],
            [      "fucked",       -1,    0,          0,      -1,        0, -10]
        ],

    ItemPrefixGroup.MAGICAL:
        [  # ||  Name   |Damage|Speed|Crit Chance|Mana Cost|Knockback|Tier||
            [   "Mystic",   0.1,    0,          0,    -0.15,        0,   2],
            [    "Adept",     0,    0,          0,    -0.15,        0,   1],
            ["Masterful",  0.15,    0,          0,     -0.2,     0.05,   2],
            [    "Inept",     0,    0,          0,      0.1,        0,  -1],
            [ "Ignorant",  -0.1,    0,          0,      0.2,        0,  -2],
            [ "Deranged",  -0.1,    0,          0,        0,     -0.1,  -1],
            [  "Intense",   0.1,    0,          0,     0.15,        0,  -1],
            [    "Taboo",     0,  0.1,          0,      0.1,      0.1,   1],
            ["Celestial",   0.1, -0.1,          0,     -0.1,      0.1,   1],
            [  "Furious",  0.15,    0,          0,      0.2,     0.15,   1],
            [    "Manic",  -0.1,  0.1,          0,     -0.1,        0,   1],
            [ "Mythical",  0.15,  0.1,       0.05,     -0.1,     0.15,   2]
        ]
}

# (((result,((component1,amnt),(component2,amnt),etc..))#recipe)#bench type)
crafting_data = [((4, ((10, 1))),
                 (17, ((4, 10), (2, 10)))),  # inventory/no bench
                 (),
                 (),
                 (),
                ]


# Randomly chosen when the player dies

# <p> inserts the players name 
# <e> inserts the name of the enemy that killed the player
# <w> inserts the world name

death_lines = {
    "spike":
        [
            "<p> got impaled by a spike.",
            "A spike impaled the face of <p>.",
            "The spikes of <w> eradicated <p>.",
            "<p> didn't look where they were going.",
            "<p> found out that spikes are sharp.",
        ],
    "falling":
        [
            "<p> fell to their death.",
            "<p> didn't bounce.",
            "<p> fell victim of gravity.",
            "<p> face-planted the ground.",
            "<p> left a small crater.",
            "<p> was crushed into <w>.",
        ],
    "enemy":
        [
            "<p> was slain by <e>.",
            "<p> was eviscerated by <e>.",
            "<p> was murdered by <e>.",
            "<p>'s face was torn off by <e>.",
            "<p>'s entrails were ripped out by <e>.",
            "<p> was destroyed by <e>.",
            "<p>'s skull was crushed by <e>.",
            "<p> got massacred by <e>.",
            "<p> got impaled by <e>.",
            "<p> was torn in half by <e>.",
            "<p> was decapitated by <e>.",
            "<p> let their arms get torn off by <e>.",
            "<p> watched their innards become outards by <e>.",
            "<p> was brutally dissected by <e>.",
            "<p>'s extremities were detached by <e>.",
            "<p>'s body was mangled by <e>.",
            "<p>'s vital organs were ruptured by <e>.",
            "<p> was turned into a pile of flesh by <e>.",
            "<p> was removed from <w> by <e>.",
            "<p> got snapped in half by <e>.",
            "<p> was cut down the middle by <e>.",
            "<p> was chopped up by <e>.",
            "<p>'s plead for death was answered by <e>.",
            "<p>'s meat was ripped off the bone by <e>.",
            "<p>'s flailing about was finally stopped by <e>.",
            "<p> had their head removed by <e>.",
            "<e> fucked up <p> in <w>.",
            "<p> got cucked by <e>.",
            "<p> was sent to another plane by <e>",
            "The creatures of <w> took <p> to their demise.",
            "<p>'s particles were distributed across <w>."
        ]
}


# Messages displayed when a world is loading

helpful_tips = [
    "Too dark? Light things up with a lamp block",
    "1f you c4n r34d 7h15, you r34lly n33d 2 g37 l41d",
    "What do you call a thieving alligator? A Crookodile",
    "If you were a fruit, you'd be a fine-apple",
    "How do you organize a space party? You planet.",
    "What do you call a classy fish? Sofishticated.",
    "Did you hear about the guy whose whole left side was cut off? He's all right now.",
    "I wondered why the baseball was getting bigger. Then it hit me.",
    "Thanks for explaining the word 'many' to me, it means a lot.",
    "I just found out I'm colorblind. The diagnosis came completely out of the purple.",
    "The future, the present and the past walked into a bar. Things got a little tense.",
    "Claustrophobic people are more productive thinking out of the box.",
    "Atheists don't solve exponential equations, they don't believe in higher powers.",
    "I was addicted to the hokey pokey... but thankfully, I turned myself around.",
    "What do you call a cow during an earthquake? A milkshake.",
    "Did you hear about the kidnapping at school? It's okay. He woke up.",
    "Oxygen is a toxic gas. Anyone who inhales oxygen will normally die within 80 years.",
    "R.I.P boiled water. You will be mist.",
    "As a wizard, I enjoy turning objects into glass. Just wanted to make that clear.",
    "I can't believe I got fired from the calendar factory. All I did was take a day off.",
    "I wasn't originally going to get a brain transplant, but then I changed my mind.",
    "I've decided to sell my Hoover... well, it was just collecting dust.",
    "Don't spell part backwards. It's a trap.",
    "How many tickles does it take to make an octopus laugh? Ten tickles.",
    "Why did the cross-eyed teacher lose her job?  She couldn't control her pupils."
]

title_messages = [
    "Now with over 30 blocks!",
    "Now with spooky lighting!",
    "Don't ask about the original!",
    "It's back, back again, tell a friend!",
    "Watch out for slimes...",
    "Don't die! I need your business!",
    "'Oh, it's like terraria but worse'",
    "Asbestos free!",
    "Kills 99.9% of bugs!",
    "Find it on YouTube!",
]

# Messages displayed when the user presses the quit button in a world

exit_messages = [
    "Are you sure you want to exit?",
    "Leaving so soon?",
    "You'll come back someday right?",
    "So this is goodbye?",
    "Don't be gone long, k?",
    "If you quit, I'll look for you, I will find you...",
    "Running won't help, they'll still get you...",
    "You're just gonna leave your slime friends?",
    "When you quit, you're killing slimes...",
    "You're just gonna play for two seconds then leave?",
]

active_menu_buttons = [
    ["MAIN", 0, 2, 3, 4, 5, 6],
    ["SETTINGS", 0, 1, 7, 8],
    ["CREDITS", 0, 1, 9, 10, 11, 12, 13],
    ["PLAYERSELECTION", 0, 1, 14, 15],
    ["PLAYERCREATION", 0, 1, 16, 17, 18, 19, 20, 21, 22],
    ["COLOURPICKER", 0, 1],
    ["CLOTHES", 0, 1, 23, 24, 25, 26],
    ["PLAYERNAMING", 0, 1, 27],
    ["WORLDSELECTION", 0, 1, 28, 29],
    ["WORLDCREATION", 0, 1, 30, 31, 32, 33, 34],
    ["WORLDNAMING", 0, 1, 35],
    ["CHANGES", 0, 1, 36, 37, 38, 39, 40],
]

structure_tiles = [
    [  # Mine shaft hut
        [-3, -7],
        [
            [[ -2, -2], [  4,  4], [  4,  4], [  4,  4], [  4,  4], [  4,  4], [ -2, -2]], 
            [[  4,  4], [  4,  4], [  4,  4], [  4,  4], [  4,  4], [  4,  4], [  4,  4]],
            [[  4,  4], [  4,  4], [ -1,  4], [ -1,  4], [ -1,  4], [  4,  4], [  4,  4]],
            [[ -2, -2], [  1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [  1,  1], [ -2, -2]], 
            [[ -2, -2], [261,  1], [ -1,  1], [ -1, -1], [ -1,  1], [261,  1], [ -2, -2]], 
            [[ -2, -2], [271,  1], [ -1,  1], [ -1,  1], [ -1,  1], [271,  1], [ -2, -2]], 
            [[ -2, -2], [281,  1], [ -1,  1], [ -1,  1], [ -1,  1], [281,  1], [ -2, -2]], 
            [[ -2, -2], [  1,  1], [257,  4], [257,  4], [257,  4], [  1,  1], [ -2, -2]]
        ]
    ],
    [  # Mine shaft vertical
        [-2, -7],
        [
            [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
            [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]],
            [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]],
            [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
            [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
            [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
            [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
            [[  1,  1], [257,  4], [257,  4], [257,  4], [  1,  1]]
        ]
    ],
    [  # Mine shaft vertical door left
       [-2, -7],
       [
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]],
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]],
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
           [[261,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
           [[271,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
           [[281,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
           [[  1,  1], [257,  4], [257,  4], [257,  4], [  1,  1]]
       ]
    ],
    [  # Mine shaft vertical door right
       [-2, -7],
       [
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]],
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]],
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [  1,  1]], 
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [261,  1]], 
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [271,  1]], 
           [[  1,  1], [ -1,  4], [ -1,  4], [ -1,  4], [281,  1]], 
           [[  1,  1], [257,  4], [257,  4], [257,  4], [  1,  1]]
       ]
    ],
    [  # Mine shaft vertical bottom
       [-2, -7],
       [
           [[  1,  1], [ -1,  4], [ -1, -2], [ -1,  4], [  1,  1]], 
           [[  1,  1], [ -1, -2], [ -1,  4], [ -1, -2], [  1,  1]],
           [[  1,  1], [ -1,  4], [ -2,  4], [ -1,  4], [ -1,  1]],
           [[  1,  1], [ -2, -2], [ -1, -2], [ -1, -2], [  1,  1]], 
           [[  1,  1], [ -2,  4], [ -1, -2], [ -2,  4], [ -2, -2]], 
           [[ -2, -2], [ -2, -2], [ -2, -2], [ -2, -2], [  1,  1]], 
           [[  1,  1], [ -2, -2], [ -2, -2], [ -2, -2], [ -2, -2]], 
           [[ -2, -2], [ -2, -2], [ -2, -2], [ -2, -2], [ -2, -2]]
       ]
    ],
    [  # Mine shaft chest room left
       [-12, -3],
       [
           [[  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [ -2, -2], [ -2, -2], [ -2, -2]],
           [[  1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1]], 
           [[  1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [261,  1], [ -1,  1], [ -1,  1], [ -1,  1]], 
           [[  1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -3,  1], [ -2,  1], [ -1,  1], [ -1,  1], [ -1,  1], [271,  1], [ -1,  1], [ -1,  1], [ -1,  1]], 
           [[  1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -2,  1], [ -2,  1], [ -1,  1], [ -1,  1], [ -1,  1], [281,  1], [ -1,  1], [ -1,  1], [ -1,  1]], 
           [[  1,  1], [258,  1], [258,  1], [258,  1], [258,  1], [258,  1], [258,  1], [258,  1], [258,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1]], 
           [[  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [ -2, -2], [ -2, -2], [ -2, -2]],
       ]
    ],
    [  # Mine shaft chest room right
       [0, -3],
       [
           [[ -2, -2], [ -2, -2], [ -2, -2], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1]],
           [[  1,  1], [  1,  1], [  1,  1], [  1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [  1,  1]], 
           [[ -1,  1], [ -1,  1], [ -1,  1], [261,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -1,  1], [  1,  1]], 
           [[ -1,  1], [ -1,  1], [ -1,  1], [271,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -3,  1], [ -2,  1], [ -1,  1], [ -1,  1], [ -1,  1], [  1,  1]], 
           [[ -1,  1], [ -1,  1], [ -1,  1], [281,  1], [ -1,  1], [ -1,  1], [ -1,  1], [ -2,  1], [ -2,  1], [ -1,  1], [ -1,  1], [ -1,  1], [  1,  1]], 
           [[  1,  1], [  1,  1], [  1,  1], [  1,  1], [258,  1], [258,  1], [258,  1], [258,  1], [258,  1], [258,  1], [258,  1], [258,  1], [  1,  1]], 
           [[ -2, -2], [ -2, -2], [ -2, -2], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1], [  1,  1]], 
       ]
    ],
]

# Special items for loot chests
#             | Item ID | Chance | Block Depth | Random Count Range |
special_loot = [
                [       19,     0.5,            0,           [1, 1]],
                [       17,     0.5,            0,           [1, 1]],
              ]

# Misc items for loot chests
#           | Item ID | Chance | Block Depth | Random Count Range |
misc_loot = [
            [       18,   0.333,            0,            [10, 100]],
            [       20,   0.333,            0,            [10, 100]],
            [       30,   0.333,            0,              [5, 30]],
           ]


def find_prefix_data_by_name(prefix_name):
    for prefix_dat in prefix_data[ItemPrefixGroup.UNIVERSAL]:
        if prefix_dat[0] == prefix_name:
            return [ItemPrefixGroup.UNIVERSAL, prefix_dat]
    for prefix_dat in prefix_data[ItemPrefixGroup.COMMON]:
        if prefix_dat[0] == prefix_name:
            return [ItemPrefixGroup.COMMON, prefix_dat]
    for prefix_dat in prefix_data[ItemPrefixGroup.MELEE]:
        if prefix_dat[0] == prefix_name:
            return [ItemPrefixGroup.MELEE, prefix_dat]
    for prefix_dat in prefix_data[ItemPrefixGroup.RANGED]:
        if prefix_dat[0] == prefix_name:
            return [ItemPrefixGroup.RANGED, prefix_dat]
    for prefix_dat in prefix_data[ItemPrefixGroup.MAGICAL]:
        if prefix_dat[0] == prefix_name:
            return [ItemPrefixGroup.MAGICAL, prefix_dat]
    return None


def parse_item_data():
    global xml_item_data
    xml_read_file = open("res/game_data/item_data.xml", "r")
    xml_item_data = xmltodict.parse(xml_read_file.read())["items"]["item"]
    xml_read_file.close()

    xml_item_data = sorted(xml_item_data, key=lambda x: int(x["@id"]))

    for item_data in xml_item_data:
        item_data["@id"] = int(item_data["@id"])
        item_data["@tags"] = make_item_tag_list(item_data["@tags"])
        item_data["@tier"] = int(item_data["@tier"])
        item_data["@max_stack"] = int(item_data["@max_stack"])
        item_data["@buy_price"] = int(item_data["@buy_price"])
        item_data["@sell_price"] = int(item_data["@sell_price"])
        item_data["@hold_offset"] = float(item_data["@hold_offset"])
        try:
            loaded_surf = pygame.image.load(item_data["@image_path"]).convert()
            item_data["@image"] = pygame.transform.scale(loaded_surf, (loaded_surf.get_width() * 2, loaded_surf.get_height() * 2))
            item_data["@image"].set_colorkey((255, 0, 255))
            item_data["@item_slot_offset_x"] = int(24 - item_data["@image"].get_width() * 0.5)
            item_data["@item_slot_offset_y"] = int(24 - item_data["@image"].get_height() * 0.5)
        except FileNotFoundError:
            item_data["@image"] = None
        except pygame.error:
            item_data["@image"] = None

        if ItemTag.WEAPON in item_data["@tags"]:
            item_data["@attack_speed"] = int(item_data["@attack_speed"])
            item_data["@attack_damage"] = int(item_data["@attack_damage"])
            item_data["@knockback"] = int(item_data["@knockback"])
            item_data["@crit_chance"] = float(item_data["@crit_chance"])
            try:
                loaded_surf = pygame.image.load(item_data["@world_override_image_path"]).convert()
                new_size = (loaded_surf.get_width() * 2, loaded_surf.get_height() * 2)
                item_data["@world_override_image"] = pygame.Surface(new_size)
                pygame.transform.scale(loaded_surf, new_size, item_data["@world_override_image"])
                item_data["@world_override_image"].set_colorkey((255, 0, 255))
            except FileNotFoundError:
                item_data["@world_override_image"] = None
            except pygame.error:
                item_data["@world_override_image"] = None

            item_data["@prefixes"] = make_item_prefix_list(item_data["@prefixes"])

        if ItemTag.RANGED in item_data["@tags"]:
            item_data["@ranged_projectile_speed"] = float(item_data["@ranged_projectile_speed"])
            item_data["@ranged_accuracy"] = float(item_data["@ranged_accuracy"])
            item_data["@ranged_num_projectiles"] = int(item_data["@ranged_num_projectiles"])

        if ItemTag.MAGICAL in item_data["@tags"]:
            item_data["@mana_cost"] = int(item_data["@mana_cost"])

        if ItemTag.AMMO in item_data["@tags"]:
            item_data["@ammo_damage"] = float(item_data["@ammo_damage"])
            item_data["@ammo_drag"] = float(item_data["@ammo_drag"])
            item_data["@ammo_gravity_mod"] = float(item_data["@ammo_gravity_mod"])
            item_data["@ammo_knockback_mod"] = float(item_data["@ammo_knockback_mod"])
            try:
                ammo_type_item_lists[item_data["@ammo_type"]].append(int(item_data["@id"]))
            except KeyError:
                ammo_type_item_lists[item_data["@ammo_type"]] = [int(item_data["@id"])]

        if ItemTag.PICKAXE in item_data["@tags"]:
            item_data["@pickaxe_power"] = float(item_data["@pickaxe_power"])

        if ItemTag.AXE in item_data["@tags"]:
            item_data["@axe_power"] = float(item_data["@axe_power"])

        if ItemTag.HAMMER in item_data["@tags"]:
            item_data["@hammer_power"] = float(item_data["@hammer_power"])

        if ItemTag.GRAPPLE in item_data["@tags"]:
            item_data["@grapple_speed"] = float(item_data["@grapple_speed"])
            item_data["@grapple_chain_length"] = float(item_data["@grapple_chain_length"])
            item_data["@grapple_max_chains"] = int(item_data["@grapple_max_chains"])
            try:
                loaded_surf = pygame.image.load(item_data["@grapple_chain_image_path"]).convert()
                new_size = (loaded_surf.get_width() * 2, loaded_surf.get_height() * 2)
                item_data["@grapple_chain_image"] = pygame.Surface(new_size)
                pygame.transform.scale(loaded_surf, new_size, item_data["@grapple_chain_image"])
                item_data["@grapple_chain_image"].set_colorkey((255, 0, 255))
            except FileNotFoundError:
                item_data["@grapple_chain_image"] = None
            except pygame.error:
                item_data["@grapple_chain_image"] = None

            try:
                loaded_surf = pygame.image.load(item_data["@grapple_claw_image_path"]).convert()
                new_size = (loaded_surf.get_width() * 2, loaded_surf.get_height() * 2)
                item_data["@grapple_claw_image"] = pygame.Surface(new_size)
                pygame.transform.scale(loaded_surf, new_size, item_data["@grapple_claw_image"])
                item_data["@grapple_claw_image"].set_colorkey((255, 0, 255))
            except FileNotFoundError:
                item_data["@grapple_claw_image"] = None
            except pygame.error:
                item_data["@grapple_claw_image"] = None


def get_item_by_id(item_id):
    if item_id < len(xml_item_data):
        return xml_item_data[item_id]


def get_item_id_by_id_str(item_id_str):
    return item_id_str_hash_table[item_id_str]


def get_item_by_id_str(item_id_str):
    return get_item_by_id(get_item_id_by_id_str(item_id_str))


def create_item_id_str_hash_table():
    global item_id_str_hash_table
    for item_index in range(len(xml_item_data)):
        item_id_str_hash_table[xml_item_data[item_index]["@id_str"]] = item_index


def get_ammo_item_ids_for_ammo_type(ammo_type):
    ammo_item_ids = []
    for item_data in xml_item_data:
        if ItemTag.AMMO in item_data["@tags"]:
            if item_data["@ammo_type"] == ammo_type:
                ammo_item_ids.append(int(item_data["@id"]))


def parse_tile_data():
    global xml_tile_data
    xml_read_file = open("res/game_data/tile_data.xml", "r")
    xml_tile_data = xmltodict.parse(xml_read_file.read())["tiles"]["tile"]
    xml_read_file.close()

    xml_tile_data = sorted(xml_tile_data, key=lambda x: int(x["@id"]))

    for tile_data in xml_tile_data:
        tile_data["@id"] = int(tile_data["@id"])
        tile_data["@strength"] = float(tile_data["@strength"])
        tile_data["@strength_type"] = get_tile_strength_type_from_str(tile_data["@strength_type"])
        tile_data["@mask_type"] = get_tile_mask_type_from_str(tile_data["@mask_type"])
        tile_data["@mask_merge_id_strs"] = tile_data["@mask_merge_id_strs"].split(",")
        tile_data["@light_reduction"] = int(tile_data["@light_reduction"])
        tile_data["@light_emission"] = int(tile_data["@light_emission"])

        if tile_data["@average_colour"] == "auto":
            tile_data["@average_colour"] = (255, 0, 255)
            override_average_colour = True
        else:
            val_array = tile_data["@average_colour"].split(",")
            tile_data["@average_colour"] = (int(val_array[0]), int(val_array[1]), int(val_array[2]))
            override_average_colour = False

        tile_data["@tags"] = make_tile_tag_list(tile_data["@tags"])
        try:
            tile_data["@image"] = pygame.transform.scale2x(pygame.image.load(tile_data["@image_path"]).convert_alpha())  # , (commons.BLOCKSIZE, commons.BLOCKSIZE)
            if override_average_colour:
                tile_data["@average_colour"] = pygame.transform.average_color(tile_data["@image"])
        except FileNotFoundError:
            tile_data["@image"] = None
        except pygame.error:
            tile_data["@image"] = None

        tile_data["@item_count_range"] = int_tuple_str_to_int_tuple(tile_data["@item_count_range"])

        if TileTag.MULTITILE in tile_data["@tags"]:
            tile_data["@multitile_dimensions"] = int_tuple_str_to_int_tuple(tile_data["@multitile_dimensions"])
            tile_data["@multitile_required_solids"] = int_tuple_list_str_to_int_tuple_list(tile_data["@multitile_required_solids"])
            try:
                tile_data["@multitile_image"] = pygame.transform.scale2x(pygame.image.load(tile_data["@multitile_image_path"]).convert_alpha())  # , (commons.BLOCKSIZE * tile_data["@multitile_dimensions"][0], commons.BLOCKSIZE * tile_data["@multitile_dimensions"][1])
                if override_average_colour:
                    tile_data["@average_colour"] = pygame.transform.average_color(tile_data["@multitile_image"])
            except FileNotFoundError:
                tile_data["@multitile_image"] = None
            except pygame.error:
                tile_data["@multitile_image"] = None

        if TileTag.CYCLABLE in tile_data["@tags"]:
            tile_data["@cycle_facing_left_tile_offset"] = int_tuple_str_to_int_tuple(tile_data["@cycle_facing_left_tile_offset"])
            tile_data["@cycle_facing_right_tile_offset"] = int_tuple_str_to_int_tuple(tile_data["@cycle_facing_right_tile_offset"])

        if TileTag.DAMAGING in tile_data["@tags"]:
            tile_data["@tile_damage"] = int(tile_data["@tile_damage"])


def create_tile_id_str_hash_table():
    global tile_id_str_hash_table
    for tile_index in range(len(xml_tile_data)):
        tile_id_str_hash_table[xml_tile_data[tile_index]["@id_str"]] = tile_index


def create_tile_light_reduction_lookup():
    global tile_id_light_reduction_lookup
    tile_id_light_reduction_lookup.clear()
    for tile_index in range(len(xml_tile_data)):
        tile_id_light_reduction_lookup.append(xml_tile_data[tile_index]["@light_reduction"])


def create_tile_light_emission_lookup():
    global tile_id_light_emission_lookup
    tile_id_light_emission_lookup.clear()
    for tile_index in range(len(xml_tile_data)):
        tile_id_light_emission_lookup.append(xml_tile_data[tile_index]["@light_emission"])


def get_tile_by_id(tile_id):
    if tile_id < len(xml_tile_data):
        return xml_tile_data[tile_id]


def get_tile_id_by_id_str(tile_id_str):
    return tile_id_str_hash_table[tile_id_str]


def get_tile_by_id_str(tile_id_str):
    return get_tile_by_id(get_tile_id_by_id_str(tile_id_str))


def get_current_tile_id_str_lookup():
    tile_id_str_lookup = []
    for tile in xml_tile_data:
        tile_id_str_lookup.append(tile["@id_str"])
    return tile_id_str_lookup


def parse_wall_data():
    global xml_wall_data
    xml_read_file = open("res/game_data/wall_data.xml", "r")
    xml_wall_data = xmltodict.parse(xml_read_file.read())["walls"]["wall"]
    xml_read_file.close()

    xml_wall_data = sorted(xml_wall_data, key=lambda x: int(x["@id"]))

    for wall_data in xml_wall_data:
        wall_data["@id"] = int(wall_data["@id"])
        wall_data["@mask_type"] = get_tile_mask_type_from_str(wall_data["@mask_type"])
        wall_data["@mask_merge_id_strs"] = wall_data["@mask_merge_id_strs"].split(",")

        if wall_data["@average_colour"] == "auto":
            wall_data["@average_colour"] = (255, 0, 255)
            override_average_colour = True
        else:
            val_array = wall_data["@average_colour"].split(",")
            wall_data["@average_colour"] = (int(val_array[0]), int(val_array[1]), int(val_array[2]))
            override_average_colour = False

        try:
            wall_data["@image"] = pygame.transform.scale(pygame.image.load(wall_data["@image_path"]).convert_alpha(), (commons.BLOCKSIZE, commons.BLOCKSIZE))
            wall_data["@image"].set_colorkey((255, 0, 255))
            if override_average_colour:
                wall_data["@average_colour"] = pygame.transform.average_color(wall_data["@image"])

        except FileNotFoundError:
            wall_data["@image"] = None
        except pygame.error:
            wall_data["@image"] = None


def create_wall_id_str_hash_table():
    global wall_id_str_hash_table
    for wall_index in range(len(xml_wall_data)):
        wall_id_str_hash_table[xml_wall_data[wall_index]["@id_str"]] = wall_index


def get_wall_by_id(wall_id):
    if wall_id < len(xml_wall_data):
        return xml_wall_data[wall_id]


def get_wall_id_by_id_str(wall_id_str):
    return wall_id_str_hash_table[wall_id_str]


def get_wall_by_id_str(wall_id_str):
    return get_wall_by_id(get_wall_id_by_id_str(wall_id_str))


def get_current_wall_id_str_lookup():
    wall_id_str_lookup = []
    for wall in xml_wall_data:
        wall_id_str_lookup.append(wall["@id_str"])
    return wall_id_str_lookup


def parse_sound_data():
    global xml_sound_data
    xml_read_file = open("res/game_data/sound_data.xml", "r")
    xml_sound_data = xmltodict.parse(xml_read_file.read())["sounds"]["sound"]
    xml_read_file.close()

    xml_sound_data = sorted(xml_sound_data, key=lambda x: int(x["@id"]))

    for sound_data in xml_sound_data:
        sound_data["@id"] = int(sound_data["@id"])
        sound_data["@volume"] = float(sound_data["@volume"])
        sound_data["@variation_paths"] = sound_data["@variation_paths"].split(",")
        sound_data["@variations"] = []
        for sound_variation in sound_data["@variation_paths"]:
            try:
                sound = pygame.mixer.Sound(sound_variation)
                sound.set_volume(sound_data["@volume"])
                sound_data["@variations"].append(sound)
            except FileNotFoundError:
                pass
            except pygame.error:
                pass


def create_sound_id_str_hash_table():
    global sound_id_str_hash_table
    for sound_index in range(len(xml_sound_data)):
        sound_id_str_hash_table[xml_sound_data[sound_index]["@id_str"]] = sound_index


def get_sound_by_id(sound_id):
    if sound_id < len(xml_sound_data):
        return xml_sound_data[sound_id]


def get_sound_id_by_id_str(sound_id_str):
    return sound_id_str_hash_table[sound_id_str]


def get_sound_by_id_str(sound_id_str):
    return get_sound_by_id(get_sound_id_by_id_str(sound_id_str))


def change_music_volume(amount):
    global music_volume_multiplier
    volume_before = music_volume_multiplier
    music_volume_multiplier += amount
    music_volume_multiplier = max(min(music_volume_multiplier, 1), 0)
    if music_volume_multiplier != volume_before:
        pygame.mixer.music.set_volume(music_volume_multiplier)
        entity_manager.add_message("Music volume set to " + str(round(music_volume_multiplier, 2)),  (255, 223, 10), life=2, outline_colour=(80, 70, 3))


def change_sound_volume(amount):
    global sound_volume_multiplier
    volume_before = sound_volume_multiplier
    sound_volume_multiplier += amount
    sound_volume_multiplier = max(min(sound_volume_multiplier, 1), 0)
    if sound_volume_multiplier != volume_before:
        for sound in xml_sound_data:
            sound["@sound"].set_volume(sound["@volume"] * sound_volume_multiplier)
        entity_manager.add_message("Sound volume set to " + str(round(sound_volume_multiplier, 2)), (255, 223, 10), life=2, outline_colour=(80, 70, 3))


def play_sound(sound_id_str):
    if commons.SOUND:
        sound_data = get_sound_by_id_str(sound_id_str)
        sound_index = random.randint(0, len(sound_data["@variations"]) - 1)
        sound_data["@variations"][sound_index].play()


def play_tile_hit_sfx(tile_id):
    if commons.SOUND:
        tile_data = get_tile_by_id(tile_id)
        play_sound(tile_data["@hit_sound"])


def play_tile_place_sfx(tile_id):
    if commons.SOUND:
        tile_data = get_tile_by_id(tile_id)
        play_sound(tile_data["@place_sound"])


def play_wall_hit_sfx(wall_id):
    if commons.SOUND:
        wall_data = get_wall_by_id(wall_id)
        play_sound(wall_data["@hit_sound"])


def play_wall_place_sfx(wall_id):
    if commons.SOUND:
        wall_data = get_wall_by_id(wall_id)
        play_sound(wall_data["@place_sound"])


class StructureConnectionOrientation(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


def parse_structure_data():
    global xml_structure_data
    xml_read_file = open("res/game_data/structure_data.xml", "r")
    xml_structure_data = xmltodict.parse(xml_read_file.read())["structures"]["structure"]
    xml_read_file.close()

    xml_structure_data = sorted(xml_structure_data, key=lambda x: int(x["@id"]))

    for structure_data in xml_structure_data:
        structure_data["@id"] = int(structure_data["@id"])
        structure_data["@spawn_weight"] = int(structure_data["@spawn_weight"])
        structure_data["@width"] = int(structure_data["@width"])
        structure_data["@height"] = int(structure_data["@height"])

        structure_data["@connections"] = []
        structure_data["@chest_loot"] = []

        tile_data = []
        columns = structure_data["@tile_data"].split("|")
        for column in columns:
            tile_data.append([])
            char_index = 0
            x_pos = len(tile_data) - 1
            while char_index < len(column):
                tile_data[-1].append([None, None, None])
                if column[char_index] != "-":
                    y_pos = len(tile_data[-1]) - 1
                    end_index = find_next_char_in_string(column, "]", char_index)
                    if end_index != -1:
                        tile_data_string = column[char_index + 1:end_index]
                        char_index = end_index
                        data_strs = tile_data_string.split(";")
                        for data_str in data_strs:
                            data_str_split = data_str.split(":")
                            data_str_id = int(data_str_split[0])
                            if data_str_id == 0:
                                tile_data[-1][-1][0] = data_str_split[1]
                            elif data_str_id == 2:
                                structure_data["@chest_loot"].append([(x_pos, y_pos), data_str_split[1]])
                            elif data_str_id == 3:
                                tile_data[-1][-1][1] = data_str_split[1]
                            elif data_str_id == 1:
                                split_str = data_str_split[1].split(",")
                                tile_data[-1][-1][2] = int(split_str[0]), int(split_str[1])
                            elif data_str_id == 4:
                                connection_data = data_str_split[1].split(",")
                                structure_data["@connections"].append([(x_pos, y_pos), connection_data[0],  get_structure_connection_orientation_from_str(connection_data[1])])
                char_index += 1

        structure_data["@tile_data"] = tile_data


def create_structure_id_str_hash_table():
    global structure_id_str_hash_table
    for structure_index in range(len(xml_structure_data)):
        structure_id_str_hash_table[xml_structure_data[structure_index]["@id_str"]] = structure_index


def get_structure_by_id(structure_id):
    if structure_id < len(xml_structure_data):
        return xml_structure_data[structure_id]


def get_structure_id_by_id_str(structure_id_str):
    return structure_id_str_hash_table[structure_id_str]


def get_structure_by_id_str(structure_id_str):
    return get_structure_by_id(get_structure_id_by_id_str(structure_id_str))


def find_structures_for_connection(connection_type, connection_orientation):
    out_connections = []
    opposite_connection_orientation = get_opposite_structure_connection_orientation(connection_orientation)
    for structure in xml_structure_data:
        for connection in structure["@connections"]:
            if connection[1] == connection_type and connection[2] == opposite_connection_orientation:
                out_connections.append([structure["@id_str"], connection[0]])

    return out_connections


def get_opposite_structure_connection_orientation(structure_connection_orientation):
    if structure_connection_orientation == StructureConnectionOrientation.DOWN:
        return StructureConnectionOrientation.UP
    elif structure_connection_orientation == StructureConnectionOrientation.LEFT:
        return StructureConnectionOrientation.RIGHT
    elif structure_connection_orientation == StructureConnectionOrientation.UP:
        return StructureConnectionOrientation.DOWN
    elif structure_connection_orientation == StructureConnectionOrientation.RIGHT:
        return StructureConnectionOrientation.LEFT


def get_structure_connection_orientation_from_str(structure_connection_orientation_str):
    if structure_connection_orientation_str == "Up":
        return StructureConnectionOrientation.UP
    elif structure_connection_orientation_str == "Right":
        return StructureConnectionOrientation.RIGHT
    elif structure_connection_orientation_str == "Down":
        return StructureConnectionOrientation.DOWN
    elif structure_connection_orientation_str == "Left":
        return StructureConnectionOrientation.LEFT


def parse_loot_data():
    global xml_loot_data
    xml_read_file = open("res/game_data/loot_data.xml", "r")
    xml_loot_data = xmltodict.parse(xml_read_file.read())["lootgroups"]["loot"]
    xml_read_file.close()

    xml_loot_data = sorted(xml_loot_data, key=lambda x: int(x["@id"]))

    for loot_data in xml_loot_data:
        loot_data["@id"] = int(loot_data["@id"])
        loot_data["@item_spawn_count_range"] = int_tuple_str_to_int_tuple(loot_data["@item_spawn_count_range"])
        possible_item_strs = loot_data["@item_list_data"].split("|")
        item_list_data = []
        for possible_item_properties_str in possible_item_strs:
            possible_item_properties = possible_item_properties_str.split(";")

            possible_item_id_str = possible_item_properties[0]
            possible_item_spawn_weight = int(possible_item_properties[1])
            possible_item_spawn_depth_range = int_tuple_str_to_int_tuple(possible_item_properties[2])
            possible_item_stack_count_range = int_tuple_str_to_int_tuple(possible_item_properties[3])
            possible_item_slot_priority = int(possible_item_properties[4])
            once_per_instance = bool(int(possible_item_properties[5]))

            item_list_data.append([possible_item_id_str, possible_item_spawn_weight, possible_item_spawn_depth_range, possible_item_stack_count_range, possible_item_slot_priority, once_per_instance])

        loot_data["@item_list_data"] = item_list_data

        loot_data["@coin_spawn_range"] = int_tuple_str_to_int_tuple(loot_data["@coin_spawn_range"])


def create_loot_id_str_hash_table():
    global loot_id_str_hash_table
    for loot_index in range(len(xml_loot_data)):
        loot_id_str_hash_table[xml_loot_data[loot_index]["@id_str"]] = loot_index


def get_loot_by_id(loot_id):
    if loot_id < len(xml_loot_data):
        return xml_loot_data[loot_id]


def get_loot_id_by_id_str(loot_id_str):
    return loot_id_str_hash_table[loot_id_str]


def get_loot_by_id_str(loot_id_str):
    return get_loot_by_id(get_loot_id_by_id_str(loot_id_str))


parse_item_data()
create_item_id_str_hash_table()

parse_tile_data()
create_tile_id_str_hash_table()
create_tile_light_reduction_lookup()
create_tile_light_emission_lookup()

parse_wall_data()
create_wall_id_str_hash_table()

parse_sound_data()
create_sound_id_str_hash_table()

parse_structure_data()
create_structure_id_str_hash_table()

parse_loot_data()
create_loot_id_str_hash_table()

air_tile_id = get_tile_id_by_id_str("fg.tile.air")
grass_tile_id = get_tile_id_by_id_str("fg.tile.grass")

air_wall_id = get_wall_id_by_id_str("fg.wall.air")
