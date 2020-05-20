#tables.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

# Biome Tile Information
# [[surface tile,base tile, alt tile],[wall tile, alt wall tile]]
biomeTileVals = [[[5, 0, 1], [0, 1]],
                 [[2, 2, 3], [2, 2]],
                 [[8, 8, 9], [8, 9]]
                ];

# Voided Collision Blocks
uncollidableBlocks = [-1, 10, 11, 12, 255, 256, 265, 266, 267, 268, 259, 260, 269, 270, 279, 280, 262, 263, 272, 273, 274, 282, 283, 284];

# Blocks that always have their wall drawn behind them
transparentBlocks = [257, 255, 256, 269, 270, 271, 272, 273];

platformBlocks = [257];


#         Item information
#                  0                                    1                                               2                                                             3                                                       4                       5                 6
#         ||     Name     ||                          Tags                             ||      Possible Prefix Types      ||attdamage|attspeed|critchance|size|vel|manaCost|knockback|tier|buyCost|sellPrice|stackCount||      Description      || tileVal||  Extra Item Information ||
itemData = [[          "Dirt",                                                 ["block"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                       "Looks dirty",    0], #01
            [         "Stone",                                     ["block", "material"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                                None,    1], #02
            [          "Snow",                                                 ["block"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],          "It's starting to melt...",    2], #02
            [           "Ice",                                                 ["block"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                     "It's icy cold",    3], #03
            [          "Wood",                                     ["block", "material"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                   "Looks craftable",    4], #04
            [         "Grass",                                                 ["block"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                                None,    5], #05
            [        "Copper",                                     ["block", "material"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                    "Looks maleable",    6], #06
            [        "Silver",                                     ["block", "material"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                    "Looks maleable",    7], #07
            [          "Sand",                                     ["block", "material"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999], "It's falling through your fingers",    8], #08
            [     "Sandstone",                                                 ["block"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                  "It looks ancient",    9], #09
            [         "Trunk",                                                 ["block"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                                None,   10], #10
            [        "Leaves",                                                 ["block"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                                None,   11], #11
            [   "Snow Leaves",                                                 ["block"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                                None,   12], #12
            [      "Platform",                                      ["block", "nowall"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],      "A good alternative to stairs",  257], #13
            [  "Wooden Sword",                                       ["melee", "weapon"],  ["melee", "common", "universal"], [   7,   30, 0.04,  40, None, None,    4,  0, [0, 0, 0, 0], [0, 0, 0, 0],   1],                       "Go get 'em!", None], #14
            [  "Copper Sword",                                       ["melee", "weapon"],  ["melee", "common", "universal"], [   8,   26, 0.04,  45, None, None,    5,  0, [0, 0, 0, 0], [0, 0, 0, 0],   1],                       "Go get 'em!", None], #15
            [    "GOD SLAYER",                                       ["melee", "weapon"],  ["melee", "common", "universal"], [  10,    1,  0.1, 100, None, None,   12, 10, [0, 0, 0, 0], [0, 0, 0, 0],   1],                            "Divine", None], #16
            [    "Wooden Bow",                               ["ranged", "weapon", "bow"], ["ranged", "common", "universal"], [   4,   29, 0.04,  50,   50, None,    1,  0, [0, 0, 0, 0], [0, 0, 0, 0],   1],              "Shoots pointy things", None], #17
            [  "Wooden Arrow",                                      ["material", "ammo"],                                [], [None, None, None,  50, None, None, None,  0, [0, 0, 0, 0], [0, 0, 0, 0], 999],                            "Pointy", None, 0], #18
            [        "Musket",                               ["ranged", "weapon", "gun"], ["ranged", "common", "universal"], [  31,   65, 0.04,  50,   60, None, 3.25,  0, [0, 0, 0, 0], [0, 0, 0, 0],   1],        "You know how to fire that?", None], #19
            [   "Musket Ball",                                      ["material", "ammo"],                                [], [None, None, None,  50, None, None, None,  0, [0, 0, 0, 0], [0, 0, 0, 0], 999],                             "Blunt", None, 1], #20
            [   "Copper Coin",                                          ["ammo", "coin"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 100],  "Keep the change ya filthy animal", None, 2], #21
            [   "Silver Coin",                                          ["ammo", "coin"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 100],           "It is cold to the touch", None, 3], #22
            [     "Gold Coin",                                          ["ammo", "coin"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 100],                    "Oooh, shiny...", None, 4], #23
            [ "Platinum Coin",                                          ["ammo", "coin"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                      "You're rich!", None, 5], #24
            ["Copper Pickaxe",                                       ["pickaxe", "tool"],           ["universal", "common"], [   4,   25, 0.04,  40, None, None,    2,  0,         None,         None,   1], "The power of destruction is yours", None], #25
            [           "Gel",                                              ["material"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                            "Sticky", None], #26
            [  "Wooden Chest", ["nowall", "chest", "block", "multitile", "interactable"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                "Fill it with loot!", [(255, 0, 0), (256, 1, 0), (265, 0, 1), (266, 1, 1)], [(0, 2), (1, 2)]], #27
            ["Crafting Table",        ["nowall", "crafting table", "block", "multitile"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999], "In a time of destruction,  create", [(267, 0, 0), (268, 1, 0)], [(0, 1), (1, 1)]], #28
            [   "Wooden Door",  ["nowall", "door", "block", "multitile", "interactable"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                "Amazing technology", [(261, 0, 0), (271, 0, 1), (281, 0, 2)], [(0, -1), (0, 3)]], #29
            [          "Lamp",                                       ["block", "nowall"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                      "Light it up!",  264], #30
            [         "Spike",                                       ["block", "nowall"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],                "It's spikey, ouch!",  258], #31
            [           "Pot",                          ["block", "nowall", "multitile"],                                [], [None, None, None,   1, None, None, None,  0,         None,         None, 999],           "How did this not break?", [(284, 0, 0), (274, 0, -1)], [(0, 1)]], #32
           ];


#           Tile information
#
#           [item ID, light reduction]
tileData = [[0, 2],  [1, 2],  [2, 2],  [3, 2],  [4, 2],  [5, 2],  [6, 2],  [7, 2], # 0 -> 7
            [8, 2],  [9, 2], [10, 1], [11, 1], [12, 1], [30, 1],      [],      [], # 8 -> 15
                [],      [],      [],      [],      [],      [],      [],      [], # 16 -> 23
                [],      [],      [],      [],      [],      [],      [],      [], # 24 -> 31
                [],      [],      [],      [],      [],      [],      [],      [], # 32 -> 39
                [],      [],      [],      [],      [],      [],      [],      [], # 40 -> 47
                [],      [],      [],      [],      [],      [],      [],      [], # 48 -> 55
                [],      [],      [],      [],      [],      [],      [],      [], # 56 -> 63
                [],      [],      [],      [],      [],      [],      [],      [], # 64 -> 71
                [],      [],      [],      [],      [],      [],      [],      [], # 72 -> 79
                [],      [],      [],      [],      [],      [],      [],      [], # 80 -> 87
                [],      [],      [],      [],      [],      [],      [],      [], # 88 -> 95
                [],      [],      [],      [],      [],      [],      [],      [], # 96 -> 103
                [],      [],      [],      [],      [],      [],      [],      [], # 104 -> 111
                [],      [],      [],      [],      [],      [],      [],      [], # 112 -> 119
                [],      [],      [],      [],      [],      [],      [],      [], # 120 -> 127
                [],      [],      [],      [],      [],      [],      [],      [], # 128 -> 135
                [],      [],      [],      [],      [],      [],      [],      [], # 136 -> 143
                [],      [],      [],      [],      [],      [],      [],      [], # 144 -> 151
                [],      [],      [],      [],      [],      [],      [],      [], # 152 -> 159
                [],      [],      [],      [],      [],      [],      [],      [], # 160 -> 167
                [],      [],      [],      [],      [],      [],      [],      [], # 168 -> 175
                [],      [],      [],      [],      [],      [],      [],      [], # 176 -> 183
                [],      [],      [],      [],      [],      [],      [],      [], # 184 -> 191
                [],      [],      [],      [],      [],      [],      [],      [], # 192 -> 199
                [],      [],      [],      [],      [],      [],      [],      [], # 200 -> 207
                [],      [],      [],      [],      [],      [],      [],      [], # 208 -> 215
                [],      [],      [],      [],      [],      [],      [],      [], # 216 -> 223
                [],      [],      [],      [],      [],      [],      [],      [], # 224 -> 231
                [],      [],      [],      [],      [],      [],      [],      [], # 232 -> 239
                [],      [],      [],      [],      [],      [],      [],      [], # 240 -> 247
                [],      [],      [],      [],      [],      [],      [], [27, 1], # 248 -> 255
           [27, 1], [13, 1], [31, 1], [29, 1], [29, 1], [29, 3], [29, 1], [29, 1], # 256 -> 263
           [30, 0], [27, 1], [27, 1], [28, 1], [28, 1], [29, 1], [29, 1], [29, 3], # 264 -> 271
           [29, 1], [29, 1], [32, 1],      [],      [],      [],      [], [29, 1], # 272 -> 279
           [29, 1], [29, 3], [29, 1], [29, 1], [32, 1],      [],      [],      [], # 280 -> 287
           [0, 1]# air
          ];


#           Enemy Information
#
#           ||     Name     |  Type  |HP |Defense|KB Resist|Damage|    Blood Col   |   Item Drops   | Coin Drops ||
enemyData = [[ "Green Slime", "Slime", 14,      0,     -0.2,     6, (10,  200,  10), [(26, 1, 3, 1)], ( 5,  30)],
             [  "Blue Slime", "Slime", 25,      2,        0,     7, (10,   10, 200), [(26, 1, 3, 1)], (15,  50)],
             [   "Red Slime", "Slime", 35,      4,        0,    12, (200,  10,  10), [(26, 1, 3, 1)], (25,  75)],
             ["Purple Slime", "Slime", 40,      6,      0.1,    12, (200,  10, 200), [(26, 1, 3, 1)], (35, 110)],
             ["Yellow Slime", "Slime", 45,      7,        0,    15, (200, 150,  10), [(26, 1, 3, 1)], (45, 130)],
            ];


#                Projectile Information
#
#                ||     Name     |   Type  | Damage |Knockback|Bounces|Hitbox Size|  Trail  |  Gravity |Drag Mod|Sound ID |
projectileData = [  ["Wooden Arrow",  "Arrow",     5,        0,      0,         13,  "arrow",       0.5,       1,       16],
                  [   "Musket Ball", "Bullet",     7,        2,      0,         10, "bullet",      0.05,     0.1,       17],
                  [   "Copper Coin", "Bullet",     1,        2,      0,         10, "bullet",      0.40,       3,       17],
                  [   "Silver Coin", "Bullet",     3,        2,      0,         10, "bullet",      0.20,       2,       17],
                  [     "Gold Coin", "Bullet",    15,        2,      0,         10, "bullet",      0.10,       1,       17],
                  [ "Platinum Coin", "Bullet",    50,        2,      0,         10, "bullet",      0.05,     0.1,       17],
                 ];


#                Special Tile Information
#
#                 ||Relative Origin|            Linked Tiles Relative Positions             |String Tile ID|     Name    |Item ID|  Misc Data  ||
specialTileData = [(         (0, 0),                        ((0, 0), (1, 0), (1, 1), (0, 1)),         "CTL",      "CHEST",     27), #255
                   (        (-1, 0),                      ((0, 0), (-1, 0), (-1, 1), (0, 1)),         "CTR",      "CHEST",     27), #256
                   (         (0, 0),                                               ((0, 0),),           "C",   "PLATFORM",     13), #257
                   (         (0, 0),                                               ((0, 0),),           "C",      "SPIKE",     31), #258       
                   (         (0, 0),        ((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)),        "OLTL",       "DOOR",     29, ((261, 1, 0), (271, 1, 1), (281, 1, 2), (-1, 0, 0), (-1, 0, 1), (-1, 0, 2))), #259
                   (        (-1, 0),     ((0, 0), (-1, 0), (0, 1), (-1, 1), (0, 2), (-1, 2)),        "OLTR",       "DOOR",     29), #260
                   (         (0, 0),                                ((0, 0), (0, 1), (0, 2)),          "CT",       "DOOR",     29, (((259, -1, 0), (260, 0, 0), (269, -1, 1), (270, 0, 1), (279, -1, 2), (280, 0, 2)), ((262, 0, 0), (263, 1, 0), (272, 0, 1), (273, 1, 1), (282, 0, 2), (283, 1, 2)))), #261
                   (         (0, 0),        ((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)),        "ORTL",       "DOOR",     29, ((261, 0, 0), (271, 0, 1), (281, 0, 2), (-1, 1, 0), (-1, 1, 1), (-1, 1, 2))), #262
                   (        (-1, 0),     ((0, 0), (-1, 0), (0, 1), (-1, 1), (0, 2), (-1, 2)),        "ORTR",       "DOOR",     29), #263
                   (         (0, 0),                                               ((0, 0),),           "C",       "LAMP",     30), #264   
                   (        (0, -1),                      ((0, 0), (1, 0), (0, -1), (1, -1)),         "CBL",      "CHEST",     27), #265
                   (       (-1, -1),                    ((0, 0), (-1, 0), (-1, -1), (0, -1)),         "CBR",      "CHEST",     27), #266
                   (         (0, 0),                                        ((0, 0), (1, 0)),           "L", "CRAFTTABLE",     28), #267
                   (        (-1, 0),                                       ((0, 0), (-1, 0)),           "R", "CRAFTTABLE",     28), #268
                   (        (0, -1),      ((0, -1), (1, -1), (0, 0), (1, 0), (0, 1), (1, 1)),        "OLML",       "DOOR",     29), #269
                   (       (-1, -1),   ((-1, -1), (0, -1), (-1, 0), (0, 0), (-1, 1), (0, 1)),        "OLMR",       "DOOR",     29), #270
                   (        (0, -1),                               ((0, 0), (0, -1), (0, 1)),          "CM",       "DOOR",     29), #271
                   (        (0, -1),      ((0, -1), (1, -1), (0, 0), (1, 0), (0, 1), (1, 1)),        "ORML",       "DOOR",     29), #272
                   (       (-1, -1),   ((-1, -1), (0, -1), (-1, 0), (0, 0), (-1, 1), (0, 1)),        "ORMR",       "DOOR",     29), #273
                   (        (0,  0),                                       ((0,  0), (0, 1)),          "PT",        "POT",     32), #274
                   None, #275
                   None, #276
                   None, #277
                   None, #278
                   (        (0, -2),    ((0, -2), (1, -2), (0, -1), (1, -1), (0, 0), (1, 0)),        "OLBL",       "DOOR",     29), #279
                   (       (-1, -2), ((-1, -2), (0, -2), (-1, -1), (0, -1), (-1, 0), (0, 0)),        "OLBR",       "DOOR",     29), #280
                   (        (0, -2),                              ((0, 0), (0, -1), (0, -2)),          "CB",       "DOOR",     29), #281
                   (        (0, -2),    ((0, -2), (1, -2), (0, -1), (1, -1), (0, 0), (1, 0)),        "ORBL",       "DOOR",     29), #282
                   (       (-1, -2), ((-1, -2), (0, -2), (-1, -1), (0, -1), (-1, 0), (0, 0)),        "ORBR",       "DOOR",     29), #283
                   (        (0, -1),                                       ((0, -1), (0, 0)),          "PB",        "POT",     32), #284
                  ];

# Item Prefix Information
prefixData = {
"universal":
    [# ||    Name    |Damage|Crit Chance|Knockback|Tier||
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

"common":
    [# ||   Name    |Damage|Speed|Crit Chance|Knockback|Tier||
        [    "Quick",     0,  0.1,          0,        0,   1],
        [   "Deadly",   0.1,  0.1,          0,        0,   2],
        [    "Agile",     0,  0.1,       0.03,        0,   1],
        [   "Nimble",     0, 0.05,          0,        0,   1],
        ["Murderous", -0.07, 0.06,       0.03,        0,   2],
        [     "Slow",     0,-0.15,          0,        0,  -1],
        [ "Sluggish",     0, -0.2,          0,        0,  -2],
        [     "Lazy",     0,-0.08,          0,        0,  -1],
        [ "Annoying",  -0.2,-0.15,          0,        0,  -2],
        [    "Nasty",  0.05,  0.1,       0.02,     -0.1,   1],
        [ "Quick AF",     0,    1,          0,        0,   10],
    ],

"melee":
    [# ||   Name    |Damage|Speed|Crit Chance|Size |Knockback|Tier||
        [    "Large",     0,    0,          0, 0.12,        0,   1],
          ["Massive",     0,    0,          0, 0.18,        0,   1],
        ["Dangerous",  0.05,    0,       0.02, 0.05,        0,   1],
        [   "Savage",   0.1,    0,          0,  0.1,      0.1,   2],
        [    "Sharp",  0.15,    0,          0,    0,        0,   1],
        [   "Pointy",   0.1,    0,          0,    0,        0,   1],
        [     "Tiny",     0,    0,          0,-0.18,        0,  -1],
        [ "Terrible", -0.15,    0,          0,-0.13,    -0.15,  -2],
        [    "Small",     0,    0,          0, -0.1,        0,  -1],
        [     "Dull", -0.15,    0,          0,    0,        0,  -1],
        [  "Unhappy",     0, -0.1,          0, -0.1,     -0.1,  -2],
        [    "Bulky",  0.05,-0.15,          0,  0.1,      0.1,   1],
        [ "Shameful",  -0.1,    0,          0,  0.1,     -0.2,  -2],
        [    "Heavy",     0, -0.1,          0,    0,     0.15,   0],
        [    "Light",     0, 0.15,          0,    0,     -0.1,   0],
        ["Legendary",  0.15,  0.1,       0.05,  0.1,     0.15,   2]
    ],

"ranged":
    [# ||     Name     | Damage  |Speed|Crit Chance|Velocity|Knockback|Tier||
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

"magic":
    [# ||   Name    |Damage|Speed|Crit Chance|Mana Cost|Knockback|Tier||
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

#(((result,((component1,amnt),(component2,amnt),etc..))#recipe)#bench type)
craftingData = [((4, ((10, 1))), 
                (17, ((4, 10), (2, 10)))), #inventory/no bench
                (), 
                (), 
                (), 
               ]


# Randomly chosen when the player dies

# <p> inserts the players name 
# <e> inserts the name of the enemy that killed the player
# <w> inserts the world name

deathLines = {
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
    "<p> faceplanted the ground.",
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

helpfulTips = ["Too dark? Light things up with a lamp block",
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

titleMessages = [
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

exitMessages = ["Are you sure you want to exit?",
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

activeMenuButtons = [["MAIN", 0, 2, 3, 4, 5, 6],
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
                     ["CHANGES", 0, 1, 36, 37, 38, 39],
                    ]

structureTiles = [
    [# Mine shaft hut
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
    [# Mine shaft vertical
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
    [# Mine shaft vertical door left
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
    [# Mine shaft vertical door right
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
    [# Mine shaft vertical bottom
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
    [# Mine shaft chest room left
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
    [# Mine shaft chest room right
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
#               | Item ID | Chance | Block Depth | Random Count Range |
specialLoot = [
                [       19,     0.5,            0,           [1, 1]],
                [       17,     0.5,            0,           [1, 1]],
              ];

# Misc items for loot chests
#           | Item ID | Chance | Block Depth | Random Count Range |
miscLoot = [
            [       18,   0.333,            0,            [10, 100]],
            [       20,   0.333,            0,            [10, 100]],
            [       30,   0.333,            0,              [5, 30]],
           ];