# item.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import random
import pygame

import game_data
from game_data import ItemPrefixGroup, ItemTag

from enum import Enum


class ItemLocation(Enum):
    HOTBAR = 0
    INVENTORY = 1
    CHEST = 2
    CRAFTING_MENU = 3


class ItemSlotClickResult(Enum):
    GAVE_ALL = 0
    GAVE_SOME = 1
    SWAPPED = 2


"""================================================================================================================= 
    item.get_random_item_prefix -> [prefix category, prefix]

    Gets a random prefix from the prefix category
-----------------------------------------------------------------------------------------------------------------"""
def get_random_item_prefix(prefix_category):
    return [prefix_category, game_data.prefix_data[prefix_category][random.randint(0, len(game_data.prefix_data[prefix_category]) - 1)]]


"""================================================================================================================= 
    item.Item

    Stores information about an item
    
    Weapons, pickaxes etc will be automatically given a random prefix from the appropriate category when
    constructed
-----------------------------------------------------------------------------------------------------------------"""
class Item:
    def __init__(self, item_id, amnt=1, auto_assign_prefix=False, prefix_name=None):
        self.xml_item = game_data.get_item_by_id(item_id)

        self.item_id = item_id
        self.amnt = amnt
        self.has_prefix = False
        self.prefix_data = None

        # Auto assign prefix
        if prefix_name is None or prefix_name == "":
            if auto_assign_prefix and ItemTag.WEAPON in self.xml_item["@tags"]:
                # 15% chance to be given a prefix if it has a prefix category
                if len(self.xml_item["@prefixes"]) > 0 and random.random() < 0.85:
                    self.prefix_data = get_random_item_prefix(self.xml_item["@prefixes"][random.randint(0, len(self.xml_item["@prefixes"]) - 1)])
                    self.has_prefix = True

        else:
            self.assign_prefix(prefix_name)

    def copy(self, new_amnt=None):
        if new_amnt is None:
            new_amnt = self.amnt
        return Item(self.item_id, new_amnt, False, self.get_prefix_name())

    def has_tag(self, tag):
        if tag in self.xml_item["@tags"]:
            return True
        return False

    def get_prefix_name(self):
        if self.has_prefix:
            return self.prefix_data[1][0]
        return ""

    def get_attack_damage(self):
        if self.prefix_data is not None:
            return self.xml_item["@attack_damage"] * (1 + self.prefix_data[1][1])
        else:
            return self.xml_item["@attack_damage"]

    def get_crit_chance(self):
        if self.prefix_data is not None:
            if self.prefix_data[0] == ItemPrefixGroup.UNIVERSAL:
                return max(min(1.0, self.xml_item["@crit_chance"] + self.prefix_data[1][2]), 0.0)
            else:
                return max(min(1.0, self.xml_item["@crit_chance"] + self.prefix_data[1][3]), 0.0)
        else:
            return self.xml_item["@crit_chance"]

    def get_knockback(self):
        if self.prefix_data is not None:
            if self.prefix_data[0] == ItemPrefixGroup.UNIVERSAL:
                return self.xml_item["@knockback"] * (1 + self.prefix_data[1][3])
            elif self.prefix_data[0] == ItemPrefixGroup.COMMON:
                return self.xml_item["@knockback"] * (1 + self.prefix_data[1][4])
            else:
                return self.xml_item["@knockback"] * (1 + self.prefix_data[1][5])
        else:
            return self.xml_item["@knockback"]

    def get_tier(self):
        if self.prefix_data is not None:
            if self.prefix_data[0] == ItemPrefixGroup.UNIVERSAL:
                return min(max(self.xml_item["@tier"] + self.prefix_data[1][4], 0), 10)
            elif self.prefix_data[0] == ItemPrefixGroup.COMMON:
                return min(max(self.xml_item["@tier"] + self.prefix_data[1][5], 0), 10)
            else:
                return min(max(self.xml_item["@tier"] + self.prefix_data[1][6], 0), 10)
        else:
            return self.xml_item["@tier"]

    def get_attack_speed(self):
        if self.prefix_data is not None:
            if self.prefix_data[0] != ItemPrefixGroup.UNIVERSAL:
                return self.xml_item["@attack_speed"] * (1 - self.prefix_data[1][2])
        return self.xml_item["@attack_speed"]

    def get_scale(self):
        if self.prefix_data is not None:
            if self.prefix_data[0] == ItemPrefixGroup.MELEE:
                return 1.0 + self.prefix_data[1][4]
        return 1.0

    def get_ranged_projectile_speed(self):
        if self.prefix_data is not None:
            if self.prefix_data[0] == ItemPrefixGroup.RANGED:
                return self.xml_item["@ranged_projectile_speed"] * (1 + self.prefix_data[1][4])
        return self.xml_item["@ranged_projectile_speed"]

    def get_mana_cost(self):
        if self.prefix_data is not None:
            if self.prefix_data[0] == ItemPrefixGroup.MAGICAL:
                return self.xml_item["@mana_cost"] * (1 + self.prefix_data[1][4])
        return self.xml_item["@mana_cost"]

    def get_name(self):
        if self.has_prefix:
            return self.get_prefix_name() + " " + self.xml_item["@name"]
        else:
            return self.xml_item["@name"]

    def get_id_str(self):
        return self.xml_item["@id_str"]

    def get_description(self):
        return self.xml_item["@desc"]

    def get_ammo_type(self):
        return self.xml_item["@ammo_type"]

    def get_ammo_damage(self):
        return self.xml_item["@ammo_damage"]

    def get_ammo_drag(self):
        return self.xml_item["@ammo_drag"]

    def get_ammo_gravity_mod(self):
        return self.xml_item["@ammo_gravity_mod"]

    def get_ammo_knockback_mod(self):
        return self.xml_item["@ammo_knockback_mod"]

    def assign_prefix(self, prefix_name):
        self.prefix_data = game_data.find_prefix_data_by_name(prefix_name)
        if self.prefix_data is not None:
            self.has_prefix = True
        else:
            self.has_prefix = False

    def get_image(self):
        image = self.xml_item["@image"]
        if image is None:
            return pygame.Surface((32, 32))
        else:
            return image

    def get_item_slot_offset_x(self):
        try:
            return self.xml_item["@item_slot_offset_x"]
        except KeyError:
            return 8

    def get_item_slot_offset_y(self):
        try:
            return self.xml_item["@item_slot_offset_y"]
        except KeyError:
            return 8

    def get_world_override_image(self):
        return self.xml_item["@world_override_image"]

    def get_tile_id_str(self):
        return self.xml_item["@tile_id_str"]

    def get_wall_id_str(self):
        return self.xml_item["@wall_id_str"]

    def get_hold_offset(self):
        return self.xml_item["@hold_offset"]

    def get_ranged_projectile_id_str(self):
        return self.xml_item["@ranged_projectile_id_str"]

    def get_ranged_ammo_type(self):
        return self.xml_item["@ranged_ammo_type"]

    def get_ranged_accuracy(self):
        return self.xml_item["@ranged_accuracy"]

    def get_ranged_num_projectiles(self):
        return self.xml_item["@ranged_num_projectiles"]

    def get_pickaxe_power(self):
        return self.xml_item["@pickaxe_power"]

    def get_axe_power(self):
        return self.xml_item["@axe_power"]

    def get_hammer_power(self):
        return self.xml_item["@hammer_power"]

    def get_grapple_speed(self):
        return self.xml_item["@grapple_speed"]

    def get_grapple_chain_length(self):
        return self.xml_item["@grapple_chain_length"]

    def get_grapple_max_chains(self):
        return self.xml_item["@grapple_max_chains"]

    def get_grapple_chain_image(self):
        return self.xml_item["@grapple_chain_image"]

    def get_grapple_claw_image(self):
        return self.xml_item["@grapple_claw_image"]

    def get_max_stack(self):
        return self.xml_item["@max_stack"]

    def get_buy_price(self):
        return self.xml_item["@buy_price"]

    def get_sell_price(self):
        return self.xml_item["@sell_price"]

    def get_pickup_sound_id_str(self):
        return self.xml_item["@pickup_sound"]

    def get_drop_sound_id_str(self):
        return self.xml_item["@drop_sound"]


def get_coins_from_int(coin_int):
    plat_coins = coin_int // 1000000
    gold_coins = (coin_int // 10000) % 100
    silver_coins = (coin_int // 100) % 100
    copper_coins = coin_int % 100

    item_list = []
    if plat_coins != 0:
        item_list.append(Item(game_data.get_item_id_by_id_str("fg.item.coin_platinum"), plat_coins))
    if gold_coins != 0:
        item_list.append(Item(game_data.get_item_id_by_id_str("fg.item.coin_gold"), gold_coins))
    if silver_coins != 0:
        item_list.append(Item(game_data.get_item_id_by_id_str("fg.item.coin_silver"), silver_coins))
    if copper_coins != 0:
        item_list.append(Item(game_data.get_item_id_by_id_str("fg.item.coin_copper"), copper_coins))

    return item_list


def generate_loot_items(loot_id_str, tile_pos, fill_with_none):
    loot_data = game_data.get_loot_by_id_str(loot_id_str)
    item_count_range = loot_data["@item_spawn_count_range"]
    item_count = random.randint(item_count_range[0], item_count_range[1])
    possible_items = loot_data["@item_list_data"]

    spawn_list = []
    void_indicies = []

    for _ in range(item_count):
        total_weight = 0
        possible_item_indices = []

        for possible_item_index in range(len(possible_items)):
            if possible_item_index not in void_indicies:
                possible_item = possible_items[possible_item_index]
                if possible_item[2][0] == possible_item[2][1] or possible_item[2][0] < tile_pos[1] < possible_item[2][1]:
                    total_weight += possible_item[1]
                    possible_item_indices.append(possible_item_index)

        random_num = random.randint(0, total_weight)

        for possible_item_index in possible_item_indices:
            if possible_item_index not in void_indicies:
                possible_item = possible_items[possible_item_index]
                if random_num <= possible_item[1]:
                    random_count = random.randint(possible_item[3][0], possible_item[3][1])
                    new_item_id = game_data.get_item_id_by_id_str(possible_item[0])

                    should_add_instance = True
                    for item_index in range(len(spawn_list)):
                        if spawn_list[item_index][0] == new_item_id:
                            spawn_list[item_index][1] += random_count
                            max_stack = game_data.get_item_by_id(spawn_list[item_index][0])["@max_stack"]
                            if spawn_list[item_index][1] > max_stack:
                                random_count = spawn_list[item_index][1] - max_stack
                                spawn_list[item_index][1] = max_stack
                            else:
                                should_add_instance = False

                    if should_add_instance:
                        spawn_list.append([new_item_id, random_count, possible_item[4]])

                        if possible_item[5]:  # Only once
                            void_indicies.append(possible_item_index)
                        break
                else:
                    random_num -= possible_item[1]

    # Sort the spawn list and insert actual items
    spawn_list = sorted(spawn_list, key=lambda x: int(x[2]))
    for item_index in range(len(spawn_list)):
        spawn_item_data = spawn_list[item_index]
        spawn_list[item_index] = Item(spawn_item_data[0], spawn_item_data[1], auto_assign_prefix=True)

    # Coins
    random_coin_range = loot_data["@coin_spawn_range"]
    random_coin_count = random.randint(random_coin_range[0], random_coin_range[1])
    coin_items = get_coins_from_int(random_coin_count)
    for coin_item in coin_items:
        spawn_list.append(coin_item)

    if fill_with_none:
        for _ in range(20 - len(spawn_list)):
            spawn_list.append(None)

    return spawn_list
