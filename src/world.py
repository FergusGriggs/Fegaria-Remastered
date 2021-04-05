# world.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame, random, pickle, datetime, perlin, math
from pygame.locals import *

import commons
import game_data
import surface_manager
import entity_manager
import shared_methods
import item

from item import Item
from enum import Enum

from game_data import *


WORLD_SIZE_X = 0
WORLD_SIZE_Y = 0

world = None

terrain_surface = pygame.Surface((0, 0))

border_down = 0
border_up = 0
border_left = 0
border_right = 0

biome_border_x_1 = 0
biome_border_x_2 = 0

WORLD_NAME = ""

grass_grow_delay = 2.5
grass_grow_tick = grass_grow_delay

structure_rects = []


class WorldSize(Enum):
    TINY = 0
    SMALL = 1
    MEDIUM = 2
    LARGE = 3


class WorldType(Enum):
    PASSIVE = 0
    NORMAL = 1
    EXPERT = 2


class WorldGenType(Enum):
    DEFAULT = 0
    SUPERFLAT = 1
    ICE_CAVES = 2


class MaskType(Enum):
    TOP_MID = 0
    LEFT_MID = 1
    BOT_MID = 2
    RIGHT_MID = 3
    SINGLE_VERTICAL_MID = 4
    SINGLE_HORIZONTAL_MID = 5
    SINGLE_VERTICAL_TOP = 6
    SINGLE_VERTICAL_BOT = 7
    SINGLE_HORIZONTAL_LEFT = 8
    SINGLE_HORIZONTAL_RIGHT = 9
    SINGLE = 10
    CORNER_TOP_LEFT = 11
    CORNER_TOP_RIGHT = 12
    CORNER_BOT_LEFT = 13
    CORNER_BOT_RIGHT = 14
    MIDDLE = 15


"""================================================================================================================= 
    world.World

    Stores data about a world
-----------------------------------------------------------------------------------------------------------------"""
class World:
    def __init__(self):
        self.name = ""
        self.creation_date = None
        self.last_played_date = None
        self.size = WorldSize.TINY
        self.type = WorldType.NORMAL
        self.gen_type = WorldGenType.DEFAULT
        self.state_flags = {}
        self.play_time = 0
        self.spawn_position = (0, 0)
        self.chest_data = []
        self.tile_data = []
        self.tile_mask_data = []

    def get_creation_date_string(self):
        return str(str(self.creation_date)[:19])

    def get_last_played_date_string(self):
        return str(str(self.last_played_date)[:19])

    def save(self):
        # Save chest data using a better format
        formatted_chest_data = [[] for _ in range(len(self.chest_data))]
        for chest_data_index in range(len(self.chest_data)):
            chest_data_at_index = self.chest_data[chest_data_index]
            formatted_chest_data[chest_data_index] = [chest_data_at_index[0], []]
            for chest_item_index in range(len(chest_data_at_index[1])):
                item = chest_data_at_index[1][chest_item_index]
                if item is not None:
                    if item.prefix_data is None:
                        formatted_chest_data[chest_data_index][1].append([chest_item_index, item.get_id_str(), item.amnt, None])
                    else:
                        formatted_chest_data[chest_data_index][1].append([chest_item_index, item.get_id_str(), item.amnt, item.get_prefix_name()])

        save_map = {
            "name": self.name,
            "creation_date": self.creation_date,
            "last_played_date": self.last_played_date,
            "size": self.size,
            "type": self.type,
            "gen_type": self.gen_type,
            "state_flags": self.state_flags,
            "play_time": self.play_time,
            "spawn_position": self.spawn_position,
            "chest_data": formatted_chest_data,
            "tile_id_str_lookup": game_data.get_current_tile_id_str_lookup(),
            "wall_id_str_lookup": game_data.get_current_wall_id_str_lookup(),
        }

        pickle.dump(save_map, open("res/worlds/" + str(self.name) + ".dat", "wb"))  # save dat
        pickle.dump(self.tile_data, open("res/worlds/" + str(self.name) + ".wrld", "wb"))  # save wrld

    def load(self, world_name, load_all=True):
        save_map = pickle.load(open("res/worlds/" + world_name + ".dat", "rb"))  # open selected save dat file

        self.name = save_map["name"]
        self.creation_date = save_map["creation_date"]
        self.size = save_map["size"]
        self.gen_type = save_map["gen_type"]
        self.play_time = save_map["play_time"]
        self.spawn_position = save_map["spawn_position"]
        formatted_chest_data = save_map["chest_data"]

        if load_all:
            self.chest_data = [[(0, 0), [None for _ in range(20)]] for _ in range(len(formatted_chest_data))]

            for chest_data_index in range(len(formatted_chest_data)):
                formatted_chest_data_at_index = formatted_chest_data[chest_data_index]
                self.chest_data[chest_data_index][0] = formatted_chest_data_at_index[0]
                for item_data_index in range(len(formatted_chest_data_at_index[1])):
                    loaded_item_data = formatted_chest_data_at_index[1][item_data_index]
                    item = Item(game_data.get_item_id_by_id_str(loaded_item_data[1]), loaded_item_data[2])
                    item.assign_prefix(loaded_item_data[3])
                    self.chest_data[chest_data_index][1][loaded_item_data[0]] = item

            # Open selected save wrld file
            self.tile_data = pickle.load(open("res/worlds/" + world_name + ".wrld", "rb"))

            # And replace the tile and wall values with updated ones
            tile_id_str_lookup = save_map["tile_id_str_lookup"]
            wall_id_str_lookup = save_map["wall_id_str_lookup"]

            for tile_column_index in range(len(self.tile_data)):
                for tile_row_index in range(len(self.tile_data[tile_column_index])):
                    existing_tile_id_str = tile_id_str_lookup[self.tile_data[tile_column_index][tile_row_index][0]]
                    self.tile_data[tile_column_index][tile_row_index][0] = game_data.get_tile_id_by_id_str(existing_tile_id_str)

                    existing_wall_id_str = wall_id_str_lookup[self.tile_data[tile_column_index][tile_row_index][1]]
                    self.tile_data[tile_column_index][tile_row_index][1] = game_data.get_wall_id_by_id_str(existing_wall_id_str)


"""================================================================================================================= 
    World save and load functions

    Using pickle serialisation, they save/load all necessary info
-----------------------------------------------------------------------------------------------------------------"""
def save():
    world.save()
    entity_manager.add_message("Saved World: " + world.name + "!", (255, 255, 255))


def load(world_name, load_all=True):
    global world
    world = World()
    world.load(world_name, load_all)


"""================================================================================================================= 
    world.create_world_super_image -> void

    Saves the current level to a huge image on disk
-----------------------------------------------------------------------------------------------------------------"""
def create_world_super_image(include_shadows=True, include_player=True):
    if terrain_surface is not None:
        pygame.image.save(terrain_surface, "res/images/screenshots/" + world.name + " - " + world.get_creation_date_string())


"""================================================================================================================= 
    world.tile_in_map -> bool

    Checks if the given position falls within the map
-----------------------------------------------------------------------------------------------------------------"""
def tile_in_map(i, j, width=1):
    if i < -1 + width:
        return False
    if j < -1 + width:
        return False
    if i > WORLD_SIZE_X - width:
        return False
    if j > WORLD_SIZE_Y - width:
        return False
    return True


"""================================================================================================================= 
    world.get_neighbor_count -> int

    Used to work out if a block can be placed at a position based on neighbors
-----------------------------------------------------------------------------------------------------------------"""
def get_neighbor_count(i, j, tile=0, check_adjacent=True, check_centre_tile=True, check_centre_wall=True):
    if commons.CREATIVE:
        return 1
    neighbor_count = 0

    if tile == 0:
        air_value = game_data.air_tile_id
    else:
        air_value = game_data.air_wall_id

    if check_adjacent:
        # Left block
        if tile_in_map(i - 1, j):
            if world.tile_data[i - 1][j][tile] != air_value:
                neighbor_count += 1
        # Right block
        if tile_in_map(i + 1, j):
            if world.tile_data[i + 1][j][tile] != air_value:
                neighbor_count += 1
        # Top block
        if tile_in_map(i, j - 1):
            if world.tile_data[i][j - 1][tile] != air_value:
                neighbor_count += 1
        # Bottom block
        if tile_in_map(i, j + 1):
            if world.tile_data[i][j + 1][tile] != air_value:
                neighbor_count += 1
    if check_centre_tile:
        # Block at pos
        if tile_in_map(i, j):
            if world.tile_data[i][j][0] != air_value:
                neighbor_count += 1
    if check_centre_wall:
        # Wall behind block
        if tile_in_map(i, j):
            if world.tile_data[i][j][1] != air_value:
                neighbor_count += 1

    return neighbor_count


"""================================================================================================================= 
    world.check_tile_merge -> bool

    Checks if the two tile ids should merge with each other
-----------------------------------------------------------------------------------------------------------------"""
def check_tile_merge(tile_id_1, tile_id_2):
    tile_1 = game_data.get_tile_by_id(tile_id_1)
    tile_2 = game_data.get_tile_by_id(tile_id_2)

    if tile_1["@id_str"] in tile_2["@mask_merge_id_strs"] or tile_1["@id_str"] == tile_2["@id_str"]:
        return True
    return False


"""================================================================================================================= 
    world.check_wall_merge -> bool

    Checks if the two wall ids should merge with each other
-----------------------------------------------------------------------------------------------------------------"""
def check_wall_merge(wall_id_1, wall_id_2):
    wall_1 = game_data.get_wall_by_id(wall_id_1)
    wall_2 = game_data.get_wall_by_id(wall_id_2)

    if wall_1["@id_str"] in wall_2["@mask_merge_id_strs"] or wall_1["@id_str"] == wall_2["@id_str"]:
        return True
    return False


"""================================================================================================================= 
    world.get_mask_name_from_adjacent_blocks -> string

    Returns the mask type given an array of the surrounding blocks
-----------------------------------------------------------------------------------------------------------------"""
def get_mask_type_from_adjacent_blocks(adjacent_blocks):
    if adjacent_blocks == [0, 0, 0, 0]: return MaskType.SINGLE
    elif adjacent_blocks == [0, 0, 0, 1]: return MaskType.SINGLE_VERTICAL_BOT
    elif adjacent_blocks == [0, 0, 1, 0]: return MaskType.SINGLE_HORIZONTAL_RIGHT
    elif adjacent_blocks == [0, 0, 1, 1]: return MaskType.CORNER_BOT_RIGHT
    elif adjacent_blocks == [0, 1, 0, 0]: return MaskType.SINGLE_VERTICAL_TOP
    elif adjacent_blocks == [0, 1, 0, 1]: return MaskType.SINGLE_VERTICAL_MID
    elif adjacent_blocks == [0, 1, 1, 0]: return MaskType.CORNER_TOP_RIGHT
    elif adjacent_blocks == [0, 1, 1, 1]: return MaskType.RIGHT_MID
    elif adjacent_blocks == [1, 0, 0, 0]: return MaskType.SINGLE_HORIZONTAL_LEFT
    elif adjacent_blocks == [1, 0, 0, 1]: return MaskType.CORNER_BOT_LEFT
    elif adjacent_blocks == [1, 0, 1, 0]: return MaskType.SINGLE_HORIZONTAL_MID
    elif adjacent_blocks == [1, 0, 1, 1]: return MaskType.BOT_MID
    elif adjacent_blocks == [1, 1, 0, 0]: return MaskType.CORNER_TOP_LEFT
    elif adjacent_blocks == [1, 1, 0, 1]: return MaskType.LEFT_MID
    elif adjacent_blocks == [1, 0, 1, 0]: return MaskType.SINGLE_HORIZONTAL_MID
    elif adjacent_blocks == [0, 1, 1, 1]: return MaskType.LEFT_MID
    elif adjacent_blocks == [1, 1, 1, 1]: return MaskType.MIDDLE
    elif adjacent_blocks == [1, 1, 1, 0]: return MaskType.TOP_MID


"""================================================================================================================= 
    world.get_mask_index_from_name -> int

    Returns a random mask index for the given type
-----------------------------------------------------------------------------------------------------------------"""
def get_mask_index_from_type(mask_type):
    if mask_type == MaskType.TOP_MID: return random.randint(1, 3)
    elif mask_type == MaskType.LEFT_MID: return int(random.randint(0, 2) * 13)
    elif mask_type == MaskType.BOT_MID: return random.randint(27, 29)
    elif mask_type == MaskType.RIGHT_MID: return int(random.randint(0, 2) * 13) + 4
    elif mask_type == MaskType.SINGLE_VERTICAL_MID: return int(random.randint(0, 2) * 13) + 5
    elif mask_type == MaskType.SINGLE_HORIZONTAL_MID: return random.randint(58, 60)
    elif mask_type == MaskType.SINGLE_VERTICAL_TOP: return random.randint(6, 8)
    elif mask_type == MaskType.SINGLE_VERTICAL_BOT: return random.randint(45, 47)
    elif mask_type == MaskType.SINGLE_HORIZONTAL_LEFT: return int(random.randint(0, 2) * 13) + 9
    elif mask_type == MaskType.SINGLE_HORIZONTAL_RIGHT: return int(random.randint(0, 2) * 13) + 12
    elif mask_type == MaskType.SINGLE: return random.randint(48, 50)
    elif mask_type == MaskType.CORNER_TOP_LEFT: return 39 + int(random.randint(0, 2) * 2)
    elif mask_type == MaskType.CORNER_TOP_RIGHT: return 40 + int(random.randint(0, 2) * 2)
    elif mask_type == MaskType.CORNER_BOT_LEFT: return 52 + int(random.randint(0, 2) * 2)
    elif mask_type == MaskType.CORNER_BOT_RIGHT: return 53 + int(random.randint(0, 2) * 2)
    elif mask_type == MaskType.MIDDLE: return 14


"""================================================================================================================= 
    world.get_mask_name_from_index -> string

    Returns the type of a given mask index
-----------------------------------------------------------------------------------------------------------------"""
def get_mask_type_from_index(index):
    if index == 1 or index == 2 or index == 3: return MaskType.TOP_MID
    elif index == 0 or index == 13 or index == 26: return MaskType.LEFT_MID
    elif index == 27 or index == 28 or index == 29: return MaskType.BOT_MID
    elif index == 4 or index == 17 or index == 30: return MaskType.RIGHT_MID
    elif index == 5 or index == 18 or index == 31: return MaskType.SINGLE_VERTICAL_MID
    elif index == 58 or index == 59 or index == 60: return MaskType.SINGLE_HORIZONTAL_MID
    elif index == 6 or index == 7 or index == 8: return MaskType.SINGLE_VERTICAL_TOP
    elif index == 45 or index == 46 or index == 47: return MaskType.SINGLE_VERTICAL_TOP
    elif index == 9 or index == 22 or index == 35: return MaskType.SINGLE_HORIZONTAL_LEFT
    elif index == 12 or index == 25 or index == 38: return MaskType.SINGLE_HORIZONTAL_RIGHT
    elif index == 48 or index == 49 or index == 50: return MaskType.SINGLE
    elif index == 39 or index == 41 or index == 43: return MaskType.CORNER_TOP_LEFT
    elif index == 40 or index == 42 or index == 44: return MaskType.CORNER_TOP_RIGHT
    elif index == 52 or index == 54 or index == 56: return MaskType.CORNER_BOT_LEFT
    elif index == 53 or index == 55 or index == 57: return MaskType.CORNER_BOT_RIGHT


"""================================================================================================================= 
    world.get_wall_mask_index_from_pos -> int

    Returns the index of the mask for the wall at a given position
-----------------------------------------------------------------------------------------------------------------"""
def get_wall_mask_index_from_pos(i, j, wall_id):
    merge_blocks = [1, 1, 1, 1]
    if i > 0:
        if not check_wall_merge(world.tile_data[i - 1][j][1], wall_id):
            merge_blocks[2] = 0
    if i < WORLD_SIZE_X - 1:
        if not check_wall_merge(world.tile_data[i + 1][j][1], wall_id):
            merge_blocks[0] = 0
    if j > 0:
        if not check_wall_merge(world.tile_data[i][j - 1][1], wall_id):
            merge_blocks[3] = 0
    if j < WORLD_SIZE_Y - 1:
        if not check_wall_merge(world.tile_data[i][j + 1][1], wall_id):
            merge_blocks[1] = 0
    return get_mask_index_from_type(get_mask_type_from_adjacent_blocks(merge_blocks))


"""================================================================================================================= 
    world.get_mask_index_from_pos -> int

    Returns the index of the mask for the block at a given position
-----------------------------------------------------------------------------------------------------------------"""
def get_mask_index_from_pos(i, j, tile_id):
    merge_blocks = [1, 1, 1, 1]
    if i > 0:
        if not check_tile_merge(world.tile_data[i - 1][j][0], tile_id):
            merge_blocks[2] = 0
    if i < WORLD_SIZE_X - 1:
        if not check_tile_merge(world.tile_data[i + 1][j][0], tile_id):
            merge_blocks[0] = 0
    if j > 0:
        if not check_tile_merge(world.tile_data[i][j - 1][0], tile_id):
            merge_blocks[3] = 0
    if j < WORLD_SIZE_Y - 1:
        if not check_tile_merge(world.tile_data[i][j + 1][0], tile_id):
            merge_blocks[1] = 0
    return get_mask_index_from_type(get_mask_type_from_adjacent_blocks(merge_blocks))


"""================================================================================================================= 
    world.blit_generation_stage -> void

    Draws the given text to the screen and then immediately flips the display
-----------------------------------------------------------------------------------------------------------------"""
def blit_generation_stage(string):
    commons.screen.blit(surface_manager.large_backgrounds[1], (0, 0))
    text1 = shared_methods.outline_text("Generating " + WORLD_NAME, (255, 255, 255), commons.XLARGEFONT)
    text2 = shared_methods.outline_text(string, (255, 255, 255), commons.LARGEFONT)
    commons.screen.blit(text1, (commons.WINDOW_WIDTH * 0.5 - text1.get_width() * 0.5, 120))
    commons.screen.blit(text2, (commons.WINDOW_WIDTH * 0.5 - text2.get_width() * 0.5, 300))
    pygame.display.flip()


"""================================================================================================================= 
    world.generate_terrain -> void

    Initializes all structures related to terrain and generates a map of the given size using the given generation type
-----------------------------------------------------------------------------------------------------------------"""
def generate_terrain(gen_type, blit_progress=False):
    global world, tile_mask_data, wall_tile_mask_data, world_data

    global biome_border_x_1, biome_border_x_2
    biome_border_x_1 = WORLD_SIZE_X * 0.333333
    biome_border_x_2 = WORLD_SIZE_X * 0.666666

    global border_left, border_right, border_up, border_down
    border_left = int(commons.BLOCKSIZE)
    border_right = int(WORLD_SIZE_X * commons.BLOCKSIZE - commons.BLOCKSIZE)
    border_up = int(commons.BLOCKSIZE * 1.5)
    border_down = int(WORLD_SIZE_Y * commons.BLOCKSIZE - commons.BLOCKSIZE * 1.5)

    world = World()

    world.tile_data = [[[game_data.air_tile_id, game_data.air_wall_id] for _ in range(WORLD_SIZE_Y)] for _ in range(WORLD_SIZE_X)]
    world.tile_mask_data = [[[-1, -1] for _ in range(WORLD_SIZE_Y)] for _ in range(WORLD_SIZE_X)]

    date = datetime.datetime.now()

    world.name = WORLD_NAME
    world.creation_date = date
    world.last_played_date = date
    world.gen_type = gen_type

    noise_gen = perlin.SimplexNoise()  # Create NOISE object
    noise_offsets = [random.random() * 1000, random.random() * 1000, random.random() * 1000]  # Randomly generate offsets

    if gen_type == "ice caves":
        world.tile_data = [[[-1, 0] for _ in range(WORLD_SIZE_X)] for _ in range(WORLD_SIZE_Y)]

        for map_index_x in range(WORLD_SIZE_X):
            for map_index_y in range(WORLD_SIZE_Y):

                val = noise_gen.noise2(map_index_x / 15 + noise_offsets[0], map_index_y / 15 + noise_offsets[0])
                if val > -0.2:
                    val2 = noise_gen.noise2(map_index_x / 15 + noise_offsets[1], map_index_y / 15 + noise_offsets[1])
                    if val2 > 0.4:
                        world.tile_data[map_index_x][map_index_y][0] = 2
                    else:
                        world.tile_data[map_index_x][map_index_y][0] = 3
                else:
                    world.tile_data[map_index_x][map_index_y][0] = -1

    elif gen_type == "DEFAULT":
        print("Gen type: " + gen_type)
        print("World size: " + str(WORLD_SIZE_X * WORLD_SIZE_Y) + " blocks. (" + str(WORLD_SIZE_X) + "x" + str(WORLD_SIZE_Y) + ")\n")

        for map_index_x in range(WORLD_SIZE_X):
            if blit_progress:
                blit_generation_stage("Generating Terrain: " + str(round((map_index_x / WORLD_SIZE_X) * 100, 1)) + "%")

            for map_index_y in range(WORLD_SIZE_Y):
                if map_index_x < biome_border_x_1 + random.randint(-5, 5):
                    biome = 1
                elif map_index_x < biome_border_x_2 + random.randint(-5, 5):
                    biome = 0
                else:
                    biome = 2

                tile_value = "fg.tile.air"
                wall_value = "fg.wall.air"

                if map_index_y > 350 + random.randint(-5, 5):  # Caverns layer 2
                    val = noise_gen.noise2(map_index_x / 30 + noise_offsets[2], map_index_y / 20 + noise_offsets[2])
                    if val > 0.55:
                        tile_value = "fg.tile.air"
                        wall_value = "fg.wall.air"
                    elif val > 0.1:
                        tile_value = "fg.tile.air"
                        wall_value = game_data.biome_tile_vals[biome][1][1]
                    else:
                        tile_value = game_data.biome_tile_vals[biome][0][2]
                        wall_value = game_data.biome_tile_vals[biome][1][1]

                elif map_index_y > 250 + random.randint(-3, 3):  # Caverns layer 1
                    val = noise_gen.noise2(map_index_x / 30 + noise_offsets[2], map_index_y / 20 + noise_offsets[2])
                    val2 = noise_gen.noise2(map_index_x / 30 + noise_offsets[0], map_index_y / 30 + noise_offsets[0])
                    if -0.2 < val < 0.2:
                        tile_value = "fg.tile.air"
                        wall_value = "fg.wall.air"
                    elif -0.4 < val < 0.4:
                        tile_value = "fg.tile.air"
                        wall_value = game_data.biome_tile_vals[biome][1][1]
                    elif val2 > 0.5:
                        tile_value = game_data.biome_tile_vals[biome][0][1]
                        wall_value = game_data.biome_tile_vals[biome][1][0]
                    else:
                        tile_value = game_data.biome_tile_vals[biome][0][2]
                        wall_value = game_data.biome_tile_vals[biome][1][1]

                elif map_index_y > 200 + random.randint(-2, 2):  # Tier 2 small caves
                    val = noise_gen.noise2(map_index_x / 30 + noise_offsets[2], map_index_y / 20 + noise_offsets[2])
                    val2 = noise_gen.noise2(map_index_x / 30 + noise_offsets[0], map_index_y / 30 + noise_offsets[0])
                    if val > 0.3:
                        tile_value = "fg.tile.air"
                        wall_value = game_data.biome_tile_vals[biome][1][1]
                    elif val2 > 0.3:
                        tile_value = game_data.biome_tile_vals[biome][0][1]
                        wall_value = game_data.biome_tile_vals[biome][1][0]
                    else:
                        tile_value = game_data.biome_tile_vals[biome][0][2]
                        wall_value = game_data.biome_tile_vals[biome][1][1]

                elif map_index_y > 95:  # Tier 1 small caves
                    val = noise_gen.noise2(map_index_x / 100 + noise_offsets[1], map_index_y / 75 + noise_offsets[1]) + noise_gen.noise2(map_index_x / 20 + noise_offsets[1], map_index_y / 8 + noise_offsets[1]) * 0.2
                    val2 = noise_gen.noise2(map_index_x / 15 + noise_offsets[0], map_index_y / 15 + noise_offsets[0])

                    if -0.2 < val < 0.2:
                        tile_value = "fg.tile.air"
                    elif val2 > -0.75:
                        tile_value = game_data.biome_tile_vals[biome][0][2]
                    else:
                        tile_value = game_data.biome_tile_vals[biome][0][1]
                    wall_value = game_data.biome_tile_vals[biome][1][0]
                else:  # Surface
                    val = noise_gen.noise2(map_index_x / 30 + noise_offsets[1], map_index_y / 20 + noise_offsets[1])
                    val2 = noise_gen.noise2(map_index_x / 100 + noise_offsets[2], 0.1)
                    val3 = noise_gen.noise2(map_index_x / 15 + noise_offsets[0], map_index_y / 15 + noise_offsets[0])
                    val4 = noise_gen.noise2(map_index_x / 100 + noise_offsets[1], map_index_y / 75 + noise_offsets[1]) + noise_gen.noise2(map_index_x / 20 + noise_offsets[1], map_index_y / 8 + noise_offsets[1]) * 0.2
                    if map_index_y >= val * 5 + 60 + val2 * 30:
                        if -0.15 < val4 < 0.15:
                            tile_value = "fg.tile.air"
                            wall_value = game_data.biome_tile_vals[biome][1][0]
                        elif val3 > -0.6:
                            tile_value = game_data.biome_tile_vals[biome][0][1]
                            wall_value = game_data.biome_tile_vals[biome][1][0]
                        else:
                            tile_value = game_data.biome_tile_vals[biome][0][2]
                            wall_value = game_data.biome_tile_vals[biome][1][1]
                        if world.tile_data[map_index_x][map_index_y - 1][0] == game_data.air_tile_id and tile_value == game_data.biome_tile_vals[biome][0][1]:
                            tile_value = game_data.biome_tile_vals[biome][0][0]
                            wall_value = game_data.biome_tile_vals[biome][1][0]
                    else:
                        tile_value = "fg.tile.air"
                world.tile_data[map_index_x][map_index_y] = [game_data.get_tile_id_by_id_str(tile_value), game_data.get_wall_id_by_id_str(wall_value)]

        if blit_progress:
            blit_generation_stage("Spawning ores")

        copper_tile_id = game_data.get_tile_id_by_id_str("fg.tile.copper")
        silver_tile_id = game_data.get_tile_id_by_id_str("fg.tile.silver")

        for i in range(int(WORLD_SIZE_X * WORLD_SIZE_Y / 1200)):
            create_vein(random.randint(0, WORLD_SIZE_X - 1), random.randint(70, 500), copper_tile_id, random.randint(2, 4))

        for i in range(int(WORLD_SIZE_X * WORLD_SIZE_Y / 1200)):
            create_vein(random.randint(0, WORLD_SIZE_X - 1), random.randint(70, 500), silver_tile_id, random.randint(2, 4))

        if blit_progress:
            blit_generation_stage("Placing Pots")

        for i in range(int((WORLD_SIZE_X * WORLD_SIZE_Y) / 300)):
            spawn_pot(random.randint(0, WORLD_SIZE_X - 1), random.randint(0, WORLD_SIZE_Y - 50))

        if blit_progress:
            blit_generation_stage("Generating Structures")

        mine_shaft_positions = []

        for i in range(math.ceil(WORLD_SIZE_X / 250)):
            while 1:
                x_pos = random.randint(20, WORLD_SIZE_X - 20)

                can_place = True

                for j in range(len(mine_shaft_positions)):
                    if abs(x_pos - mine_shaft_positions[j]) < 30:
                        can_place = False

                if can_place:
                    for y_pos in range(80):
                        if world.tile_data[x_pos][y_pos][0] != game_data.air_tile_id:
                            spawn_structure(x_pos, y_pos, "fg.structure.mineshaft_top", (3, 6), True)
                            break

                    mine_shaft_positions.append(x_pos)
                    break

        for i in range(math.ceil((WORLD_SIZE_X * WORLD_SIZE_Y) / 15000)):
            spawn_structure(random.randint(50, WORLD_SIZE_X - 50), random.randint(100, WORLD_SIZE_Y - 50), "fg.structure.undergound_cabin_a", (4, 0), True, check_placement_validity=True)

        if blit_progress:
            blit_generation_stage("Growing Trees")

        for i in range(1, int(WORLD_SIZE_X / 5)):
            if random.randint(1, 2) == 1:
                create_tree(i * 5, 0, random.randint(5, 15))

    elif gen_type == "superflat":
        world.tile_data = []
        for i in range(WORLD_SIZE_X):
            world.tile_data.append([])
            for j in range(WORLD_SIZE_Y):
                if j > 100:
                    tile_value = 1
                    wall_value = 1
                else:
                    tile_value = -1
                    wall_value = -1
                world.tile_data[i].append([tile_value, wall_value])

    create_grounded_spawn_position()

    print("Generation complete!")


"""================================================================================================================= 
    world.create_terrain_surface -> void

    Renders all tiles in the map to a huge surface
-----------------------------------------------------------------------------------------------------------------"""
def create_terrain_surface():
    global terrain_surface
    print("Creating Terrain Surface...")
    terrain_surface = pygame.Surface((WORLD_SIZE_X * commons.BLOCKSIZE, WORLD_SIZE_Y * commons.BLOCKSIZE))
    terrain_surface.fill((255, 0, 255))
    terrain_surface.set_colorkey((255, 0, 255))
    for i in range(WORLD_SIZE_X):
        for j in range(WORLD_SIZE_Y):
            update_terrain_surface(i, j, affect_others=False)


"""================================================================================================================= 
    world.place_multitile -> void

    Place a multitile of the given id and dimensions at the given pos
-----------------------------------------------------------------------------------------------------------------"""
def place_multitile(top_left_x, top_left_y, dimensions, tile_id, update_surface):
    for x in range(dimensions[0]):
        for y in range(dimensions[1]):
            world.tile_data[top_left_x + x][top_left_y + y][0] = tile_id
            world.tile_data[top_left_x + x][top_left_y + y].append((x, y))
            if update_surface:
                update_terrain_surface(top_left_x + x, top_left_y + y)


"""================================================================================================================= 
    world.get_multitile_origin -> int tuple

    Get the origin of a multitile
-----------------------------------------------------------------------------------------------------------------"""
def get_multitile_origin(x, y):
    tile_data = world.tile_data[x][y]
    return x - tile_data[2][0], y - tile_data[2][1]


"""================================================================================================================= 
    world.remove_multitile -> void

    Uses special tile relative data to remove all tiles associated with a special tile at a given position
-----------------------------------------------------------------------------------------------------------------"""
def remove_multitile(top_left_pos, drop_items=True, remove_chest_data=True, update_surface=True):
    tile_data = world.tile_data[top_left_pos[0]][top_left_pos[1]]
    xml_tile_data = game_data.get_tile_by_id(tile_data[0])
    destroy = True
    chest_data_to_remove = -1

    if TileTag.CHEST in xml_tile_data["@tags"]:
        for chest_data_index in range(len(world.chest_data)):
            if world.chest_data[chest_data_index][0] == top_left_pos:
                for chest_items_index in range(len(world.chest_data[chest_data_index][1])):
                    if world.chest_data[chest_data_index][1][chest_items_index] is not None:
                        destroy = False
                chest_data_to_remove = chest_data_index
                break
                #for f in range(5):
                #    for m in range(4):
                #        if clientWorld.chestData[k][1][f][m] != None:
                #        entity_manager.SpawnPhysicsItem((i * commons.BLOCKSIZE, j * commons.BLOCKSIZE), clientWorld.chestData[k][1][f][m])

    if destroy:
        dimensions = xml_tile_data["@multitile_dimensions"]

        for x in range(dimensions[0]):
            for y in range(dimensions[1]):
                remove_x = top_left_pos[0] + x
                remove_y = top_left_pos[1] + y
                world.tile_data[remove_x][remove_y][0] = game_data.air_tile_id
                world.tile_data[remove_x][remove_y].pop(2)
                if update_surface:
                    update_terrain_surface(remove_x, remove_y)

        if drop_items:
            entity_manager.spawn_physics_item(Item(get_item_id_by_id_str(xml_tile_data["@item_id_str"]), 1), (remove_x * commons.BLOCKSIZE, remove_y * commons.BLOCKSIZE), pickup_delay=10)

        if remove_chest_data and chest_data_to_remove != -1:
            del world.chest_data[chest_data_to_remove]


"""================================================================================================================= 
    world.use_special_tile -> void

    Performs the action that a special tile does
-----------------------------------------------------------------------------------------------------------------"""
def use_special_tile(i, j):
    global world
    tile_id = world.tile_data[i][j][0]
    tile_data = game_data.get_tile_by_id(tile_id)

    if TileTag.CHEST in tile_data["@tags"]:
        for chest_data_index in range(len(world.chest_data)):
            if world.chest_data[chest_data_index][0] == (i, j):
                entity_manager.client_player.open_chest(world.chest_data[chest_data_index][1])

    if TileTag.CRAFTINGTABLE in tile_data["@tags"]:
        entity_manager.client_player.crafting_menu_offset_y = 120
        entity_manager.client_player.update_craftable_items()
        entity_manager.client_player.render_craftable_items_surf()
        entity_manager.client_player.inventory_open = True
        entity_manager.client_prompt = None

    if TileTag.CYCLABLE in tile_data["@tags"]:
        player_direction = entity_manager.client_player.direction
        if player_direction == 0:
            tile_cycle_id_str = tile_data["@cycle_facing_left_tile_id_str"]
            tile_cycle_data = game_data.get_tile_by_id_str(tile_cycle_id_str)
            tile_cycle_offset = tile_data["@cycle_facing_left_tile_offset"]
            tile_cycle_sound = tile_data["@cycle_facing_left_sound"]
        else:
            tile_cycle_id_str = tile_data["@cycle_facing_right_tile_id_str"]
            tile_cycle_data = game_data.get_tile_by_id_str(tile_cycle_id_str)
            tile_cycle_offset = tile_data["@cycle_facing_right_tile_offset"]
            tile_cycle_sound = tile_data["@cycle_facing_right_sound"]

        if TileTag.MULTITILE in tile_cycle_data["@tags"]:
            tile_cycle_dimensions = tile_cycle_data["@multitile_dimensions"]
        else:
            tile_cycle_dimensions = 1, 1

        tile_cycle_origin = i + tile_cycle_offset[0], j + tile_cycle_offset[1]

        can_cycle = True

        if TileTag.MULTITILE in tile_data["@tags"]:
            current_tile_dimensions = tile_data["@multitile_dimensions"]
        else:
            current_tile_dimensions = 1, 1

        # Check there is space to cycle
        for x in range(tile_cycle_dimensions[0]):
            for y in range(tile_cycle_dimensions[1]):
                check_x = tile_cycle_origin[0] + x
                check_y = tile_cycle_origin[1] + y
                testing_current_tile = False
                if i <= check_x < i + current_tile_dimensions[0]:
                    if j <= check_y < j + current_tile_dimensions[1]:
                        testing_current_tile = True

                if not testing_current_tile and world.tile_data[tile_cycle_origin[0] + x][tile_cycle_origin[1] + y][0] != game_data.air_tile_id:
                    can_cycle = False
                    break

            if not can_cycle:
                break

        if can_cycle:
            game_data.play_sound(tile_cycle_sound)

            # Remove existing cyclable
            if TileTag.MULTITILE in tile_data["@tags"]:
                for x in range(current_tile_dimensions[0]):
                    for y in range(current_tile_dimensions[1]):
                        world.tile_data[i + x][j + y][0] = game_data.air_tile_id
                        world.tile_data[i + x][j + y].pop(2)
                        update_terrain_surface(i + x, j + y)
            else:
                world.world.tile_data[i][j][0] = game_data.air_tile_id

            # Place the new one
            for x in range(tile_cycle_dimensions[0]):
                for y in range(tile_cycle_dimensions[1]):
                    world.tile_data[tile_cycle_origin[0] + x][tile_cycle_origin[1]+ y][0] = tile_cycle_data["@id"]
                    world.tile_data[tile_cycle_origin[0] + x][tile_cycle_origin[1] + y].append((x, y))
                    update_terrain_surface(tile_cycle_origin[0] + x, tile_cycle_origin[1] + y)

    commons.WAIT_TO_USE = True


"""================================================================================================================= 
    world.update_terrain_surface -> void

    Updates a tile in the terrain surface and optionally, the blocks around it.
-----------------------------------------------------------------------------------------------------------------"""
def update_terrain_surface(i, j, affect_others=True):
    global terrain_surface
    tiles_to_update = []
    if affect_others:
        if i > 0:
            tiles_to_update.append((i - 1, j))
        if i < WORLD_SIZE_X - 1:
            tiles_to_update.append((i + 1, j))
        if j > 0:
            tiles_to_update.append((i, j - 1))
        if j < WORLD_SIZE_Y - 1:
            tiles_to_update.append((i, j + 1))
    tiles_to_update.append((i, j))

    for tile in tiles_to_update:
        pygame.draw.rect(terrain_surface, (255, 0, 255), Rect(tile[0] * commons.BLOCKSIZE, tile[1] * commons.BLOCKSIZE, commons.BLOCKSIZE, commons.BLOCKSIZE), 0)
        tile_dat = world.tile_data[tile[0]][tile[1]]
        xml_tile_dat = game_data.get_tile_by_id(tile_dat[0])
        xml_wall_dat = game_data.get_wall_by_id(tile_dat[1])

        if TileTag.NODRAW not in xml_tile_dat["@tags"]:
            tile_mask_data[tile[0]][tile[1]] = get_mask_index_from_pos(tile[0], tile[1], tile_dat[0])  # Get the mask at i, j and store it in the tile_mask_data array

            if TileTag.MULTITILE in xml_tile_dat["@tags"]:
                tile_img = pygame.Surface((commons.BLOCKSIZE, commons.BLOCKSIZE)).convert()
                tile_img.blit(xml_tile_dat["@multitile_image"], (-tile_dat[2][0] * commons.BLOCKSIZE, -tile_dat[2][1] * commons.BLOCKSIZE))
            else:
                tile_img = xml_tile_dat["@image"].copy()

            tile_img.set_colorkey((255, 0, 255))

            if xml_tile_dat["@mask_type"] != TileMaskType.NONE:
                tile_img.blit(surface_manager.tile_masks[tile_mask_data[tile[0]][tile[1]]],  (0,  0),  None,  pygame.BLEND_RGBA_MULT)  # Blit the block mask to the block texture using a multiply blend flag

            if (tile_mask_data[tile[0]][tile[1]] != 14 or TileTag.TRANSPARENT not in xml_tile_dat["@tags"]) and tile_dat[1] != game_data.air_wall_id:  # If the block is not a centre block (and so there is some transparency in it) and there is a wall tile behind it,  blit the wall tile
                back_img = xml_wall_dat["@image"].copy()  # Get the wall texture
                wall_tile_mask_data[tile[0]][tile[1]] = get_wall_mask_index_from_pos(tile[0], tile[1], tile_dat[1])  # Get the wall mask
                if get_mask_type_from_index(wall_tile_mask_data[tile[0]][tile[1]]) == get_mask_type_from_index(tile_mask_data[tile[0]][tile[1]]):  # If the mask of the wall and the mask of the tile are from the same type
                    wall_tile_mask_data[tile[0]][tile[1]] = tile_mask_data[tile[0]][tile[1]]  # Set the wall mask to the tile mask
                back_img.blit(surface_manager.tile_masks[wall_tile_mask_data[tile[0]][tile[1]]],  (0,  0),  None,  pygame.BLEND_RGBA_MULT)  # Blit the mask onto the wall texture using a multiply blend flag
                back_img.blit(tile_img, (0, 0))  # Blit the masked block texture to the main surface
                terrain_surface.blit(back_img, (tile[0] * commons.BLOCKSIZE,  tile[1] * commons.BLOCKSIZE))  # Blit the masked wall surf to the main surf
            else:
                terrain_surface.blit(tile_img, (tile[0] * commons.BLOCKSIZE,  tile[1] * commons.BLOCKSIZE))  # Blit the masked wall surf to the main surf

        elif tile_dat[1] != game_data.air_wall_id:  # If there is no block but there is a wall
            back_img = xml_wall_dat["@image"].copy()  # Get the wall texture
            wall_tile_mask_data[tile[0]][tile[1]] = get_wall_mask_index_from_pos(tile[0], tile[1], tile_dat[1])  # Get the wall mask
            back_img.blit(surface_manager.tile_masks[wall_tile_mask_data[tile[0]][tile[1]]], (0, 0), None, pygame.BLEND_RGBA_MULT)  # Blit the mask onto the wall texture using a multiply blend flag
            terrain_surface.blit(back_img, (tile[0] * commons.BLOCKSIZE, tile[1] * commons.BLOCKSIZE))  # Blit the masked wall surf to the main surf


"""================================================================================================================= 
    world.create_vein -> void

    Recursively creates ore at a location
-----------------------------------------------------------------------------------------------------------------"""
def create_vein(i, j, tile_id, size):
    global world
    if tile_in_map(i, j):
        if world.tile_data[i][j][0] != game_data.air_tile_id and world.tile_data[i][j][0] != tile_id and size > 0:
            if random.randint(1, 10) == 1:
                size += 1
            world.tile_data[i][j][0] = tile_id
            create_vein(i - 1, j, tile_id, size - 1)
            create_vein(i + 1, j, tile_id, size - 1)
            create_vein(i, j - 1, tile_id, size - 1)
            create_vein(i, j + 1, tile_id, size - 1)


"""================================================================================================================= 
    world.create_tree -> void

    Spawns a tree at the given location and with the given height
-----------------------------------------------------------------------------------------------------------------"""
def create_tree(i, j, height):
    global world

    trunk_tile_id = game_data.get_tile_id_by_id_str("fg.tile.trunk")
    snow_leaves_tile_id = game_data.get_tile_id_by_id_str("fg.tile.leaves_snow")
    leaves_tile_id = game_data.get_tile_id_by_id_str("fg.tile.leaves")
    grass_tile_id = game_data.get_tile_id_by_id_str("fg.tile.grass")
    snow_tile_id = game_data.get_tile_id_by_id_str("fg.tile.snow")

    grounded = False

    for k in range(WORLD_SIZE_Y - j - 1):
        tile_id = world.tile_data[i][j + 1][0]
        leaf_tile = leaves_tile_id

        if tile_id == grass_tile_id:
            grounded = True
            break

        elif tile_id == snow_tile_id:
            leaf_tile = snow_leaves_tile_id
            grounded = True
            break

        elif tile_id != game_data.air_tile_id:
            break

        j += 1

    if not grounded:
        return

    if world.tile_data[i - 1][j + 1][0] == grass_tile_id or world.tile_data[i - 1][j + 1][0] == snow_tile_id:
        world.tile_data[i - 1][j][0] = trunk_tile_id
    if world.tile_data[i + 1][j + 1][0] == grass_tile_id or world.tile_data[i + 1][j + 1][0] == snow_tile_id:
        world.tile_data[i + 1][j][0] = trunk_tile_id

    h = height
    for k in range(height):
        world.tile_data[i][j][0] = trunk_tile_id
        if 2 < h < height - 1:
            if random.randint(1, 5) == 1:
                if random.randint(0, 1) == 0:
                    world.tile_data[i - 1][j][0] = leaf_tile
                else:
                    world.tile_data[i + 1][j][0] = leaf_tile
        h -= 1
        j -= 1
    # Create canopy
    for k in range(-1, 2):
        world.tile_data[i + k][j - 2][0] = leaf_tile
    for k in range(-2, 3):
        world.tile_data[i + k][j - 1][0] = leaf_tile
    for k in range(-2, 3):
        world.tile_data[i + k][j][0] = leaf_tile
    world.tile_data[i - 1][j + 1][0] = leaf_tile
    world.tile_data[i + 1][j + 1][0] = leaf_tile


"""================================================================================================================= 
    world.spawn_structure -> void

    Creates a structure at the given position using the data stored in the structure_tiles table and
    the given structure id
-----------------------------------------------------------------------------------------------------------------"""
def spawn_structure(pos_x, pos_y, structure_id_str, structure_connection_position=None, allow_connection_connecting_from=False, remaining_parts=20, check_placement_validity=False):
    global world

    structure_data = game_data.get_structure_by_id_str(structure_id_str)
    structure_world_top_left = (pos_x, pos_y)

    # Connection being spawned at
    if structure_connection_position is not None:
        for connection in structure_data["@connections"]:
            if connection[0] == structure_connection_position:
                structure_world_top_left = (pos_x - structure_connection_position[0], pos_y - structure_connection_position[1])

    structure_rect = Rect(structure_world_top_left[0], structure_world_top_left[1], structure_data["@width"], structure_data["@height"])

    if check_placement_validity:
        if not is_structure_rect_valid(structure_rect):
            return

    global structure_rects
    structure_rects.append(structure_rect)
    current_structure_index = len(structure_rects) - 1

    # Remove multitile and chest data
    for x in range(structure_data["@width"]):
        world_x = structure_world_top_left[0] + x
        for y in range(structure_data["@height"]):
            world_y = structure_world_top_left[1] + y
            tile_data = structure_data["@tile_data"][x][y]
            if tile_data[0] is not None:
                existing_tile_data = game_data.get_tile_by_id(world.tile_data[world_x][world_y][0])

                if TileTag.MULTITILE in existing_tile_data["@tags"]:
                    tile_origin = get_multitile_origin(world_x, world_y)
                    remove_multitile(tile_origin, False, False, False)
                else:
                    tile_origin = (world_x, world_y)

                if TileTag.CHEST in existing_tile_data["@tags"]:
                    for chest_data_index in range(len(world.chest_data) - 1, -1, -1):
                        if world.chest_data[chest_data_index][0] == tile_origin:
                            del world.chest_data[chest_data_index]

    # Add new multitile data
    for x in range(structure_data["@width"]):
        world_x = structure_world_top_left[0] + x
        for y in range(structure_data["@height"]):
            world_y = structure_world_top_left[1] + y
            tile_data = structure_data["@tile_data"][x][y]
            if tile_data[0] is not None:
                new_tile = game_data.get_tile_by_id_str(tile_data[0])
                if TileTag.MULTITILE in new_tile["@tags"]:
                    place_multitile(world_x, world_y, new_tile["@multitile_dimensions"], new_tile["@id"], False)
                else:
                    world.tile_data[world_x][world_y][0] = new_tile["@id"]

            if tile_data[1] is not None:
                world.tile_data[world_x][world_y][1] = game_data.get_wall_id_by_id_str(tile_data[1])

    # Create chest loot
    for chest in structure_data["@chest_loot"]:
        tile_origin = (structure_world_top_left[0] + chest[0][0], structure_world_top_left[1] + chest[0][1])
        item_list = item.generate_loot_items(chest[1], tile_origin, True)
        world.chest_data.append([tile_origin, item_list])

    if remaining_parts == 0:
        return

    # Fill out other connections
    for connection in structure_data["@connections"]:
        if connection[0] != structure_connection_position or allow_connection_connecting_from:
            possible_connections = find_structures_for_connection(connection[1], connection[2])
            if len(possible_connections) > 0:
                # Remove colliding connections and make a total weight
                total_weight = 0
                for possible_connection_index in range(len(possible_connections) - 1, -1, -1):
                    possible_connection = possible_connections[possible_connection_index]
                    possible_structure_data = game_data.get_structure_by_id_str(possible_connection[0])
                    possible_top_left = structure_world_top_left[0] + connection[0][0] - possible_connection[1][0], structure_world_top_left[1] + connection[0][1] - possible_connection[1][1]
                    possible_structure_rect = Rect(possible_top_left[0], possible_top_left[1], possible_structure_data["@width"], possible_structure_data["@height"])
                    if is_structure_rect_valid(possible_structure_rect, current_structure_index):
                        total_weight += possible_structure_data["@spawn_weight"]
                    else:
                        possible_connections.pop(possible_connection_index)

                if len(possible_connections) > 0:
                    random_pick = random.randint(0, total_weight)

                    for possible_connection in possible_connections:
                        possible_structure_data = game_data.get_structure_by_id_str(possible_connection[0])
                        if random_pick < possible_structure_data["@spawn_weight"]:
                            spawn_structure(structure_world_top_left[0] + connection[0][0], structure_world_top_left[1] + connection[0][1], possible_connection[0], possible_connection[1], False, remaining_parts - 1)
                            break
                        else:
                            random_pick -= possible_structure_data["@spawn_weight"]


"""================================================================================================================= 
    world.is_structure_rect_valid -> bool

    Checks if a given rect is within the map rect and does not overlap with any other structure rects
-----------------------------------------------------------------------------------------------------------------"""
def is_structure_rect_valid(structure_rect, rect_index_to_ignore=-1):
    if structure_rect.x >= 0 and structure_rect.x + structure_rect.w < WORLD_SIZE_X and structure_rect.y >= 0 and structure_rect.y + structure_rect.h < WORLD_SIZE_Y:
        is_valid = True

        for rect_index in range(len(structure_rects)):
            if rect_index != rect_index_to_ignore:
                union_rect = structure_rect.clip(structure_rects[rect_index])
                if union_rect.w > 1 and union_rect.h > 1:
                    is_valid = False

        return is_valid
    return False


"""================================================================================================================= 
    world.create_grounded_spawn_position -> void

    Creates a random spawn point on the x axis, then places it on the ground
-----------------------------------------------------------------------------------------------------------------"""
def create_grounded_spawn_position():
    global world
    block_pos_x = random.randint(20, max(20, WORLD_SIZE_X - 20))
    world.spawn_position = (commons.BLOCKSIZE * block_pos_x, commons.BLOCKSIZE * 1.5)
    for i in range(300):
        world.spawn_position = (world.spawn_position[0], world.spawn_position[1] + commons.BLOCKSIZE)
        x1 = int(world.spawn_position[0] - commons.BLOCKSIZE * 0.5) // commons.BLOCKSIZE
        y = int(world.spawn_position[1] + commons.BLOCKSIZE) // commons.BLOCKSIZE
        x2 = int(world.spawn_position[0] + commons.BLOCKSIZE * 0.5) // commons.BLOCKSIZE

        left_tile_dat = game_data.get_tile_by_id(world.tile_data[x1][y][0])
        right_tile_dat = game_data.get_tile_by_id(world.tile_data[x2][y][0])

        if TileTag.NOCOLLIDE not in left_tile_dat["@tags"] and TileTag.NOCOLLIDE not in right_tile_dat["@tags"]:
            world.spawnPosition = (world.spawn_position[0], world.spawn_position[1] - commons.BLOCKSIZE * 1.5)
            break


"""================================================================================================================= 
    world.check_grow_grass -> void

    Waits 'grass_grow_delay' seconds to grow grass
-----------------------------------------------------------------------------------------------------------------"""
def check_grow_grass():
    global grass_grow_tick
    if grass_grow_tick <= 0:
        grass_grow_tick += grass_grow_delay
        grow_grass()

    else:
        grass_grow_tick -= commons.DELTA_TIME


"""================================================================================================================= 
    world.grow_grass -> void

    Checks 1/20 highest tiles randomly to see if they are dirt, if they are, it will change them to grass
-----------------------------------------------------------------------------------------------------------------"""
def grow_grass():
    global world
    for i in range(int(WORLD_SIZE_X * 0.05)):
        random_x = random.randint(0, WORLD_SIZE_X - 1)
        for j in range(110):
            if world.tile_data[random_x][j][0] != -1:
                if world.tile_data[random_x][j][0] == 0:
                    world.tile_data[random_x][j][0] = 5
                    update_terrain_surface(random_x, j)
                break


"""================================================================================================================= 
    world.spawn_pot -> void

    Checks 50 tiles below the target location for two tiles with a backwall and no block
-----------------------------------------------------------------------------------------------------------------"""
def spawn_pot(pos_x, pos_y):
    global world
    viable_blocks = 0
    for i in range(50):
        if tile_in_map(pos_x, pos_y):
            if viable_blocks >= 1 and world.tile_data[pos_x][pos_y][0] != game_data.air_tile_id:
                pot_options = ["fg.tile.pot_short_gray", "fg.tile.pot_short_brown"]
                if viable_blocks >= 2:
                    pot_options += ["fg.tile.pot_tall_gray", "fg.tile.pot_tall_brown"]

                random_choice = pot_options[random.randint(0, len(pot_options) - 1)]
                random_choice_tile_data = game_data.get_tile_by_id_str(random_choice)

                if TileTag.MULTITILE in random_choice_tile_data["@tags"]:
                    tile_dimensions = random_choice_tile_data["@multitile_dimensions"]
                    place_multitile(pos_x, pos_y - tile_dimensions[1], tile_dimensions, random_choice_tile_data["@id"], False)
                else:
                    world.tile_data[pos_x][pos_y - 1][0] = random_choice_tile_data["@id"]
                return

            if world.tile_data[pos_x][pos_y][0] == game_data.air_tile_id and world.tile_data[pos_x][pos_y][1] != game_data.air_wall_id:
                viable_blocks += 1

            pos_y += 1
        else:
            return
