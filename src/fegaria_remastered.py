# fegaria_remastered.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"
__version__ = "0.1.1"

# External module importing
import pygame
import sys
import math
import random
import pickle
import _thread
import datetime

from pygame.locals import *

# Set to 8000 for creepy mode (48000 norm)
pygame.mixer.pre_init(48000, -16, 2, 1024)
pygame.init()

# Loads config file and common variables
import commons
import shared_methods
import surface_manager
import entity_manager
import world
import menu_manager
import player
import game_data
from game_data import TileTag
import prompt

from item import *


class TimeState(Enum):
    DAWN = 0
    DAY = 1
    DUSK = 2
    NIGHT = 3


"""================================================================================================================= 
    move_parallax -> void

    Moves the background by a set amount, looping back when necessary
-----------------------------------------------------------------------------------------------------------------"""
def move_parallax(val):
    global parallax_pos
    parallax_pos = (parallax_pos[0] + val[0], parallax_pos[1] + val[1])
    if parallax_pos[0] > 0:
        parallax_pos = (-40 + parallax_pos[0], parallax_pos[1])
    elif parallax_pos[0] < -39: parallax_pos = (parallax_pos[0] + 40, parallax_pos[1])
    if parallax_pos[1] > 0:
        parallax_pos = (parallax_pos[0], -40 + parallax_pos[1])
    elif parallax_pos[1] < -39:
        parallax_pos = (parallax_pos[0], parallax_pos[1] + 40)


"""================================================================================================================= 
    fade_background -> void

    Fade the background to a different background type
-----------------------------------------------------------------------------------------------------------------"""
def fade_background(new_background_id):
    global fade_background_id, fade_back, fade_float
    fade_background_id = new_background_id
    fade_back = True
    fade_float = 0.0


"""================================================================================================================= 
    check_change_background -> void

    Check if player has moved biome and change the background if necessary
-----------------------------------------------------------------------------------------------------------------"""
def check_change_background():
    global background_tick, background_scroll_vel
    if background_tick <= 0:
        background_tick += 0.25
        if entity_manager.camera_position[1] > 200 * commons.BLOCKSIZE:
            if entity_manager.camera_position[0] < world.biome_border_x_1 * commons.BLOCKSIZE:
                if fade_background_id != 0:
                    fade_background(0)
            elif entity_manager.camera_position[0] < world.biome_border_x_2 * commons.BLOCKSIZE:
                if fade_background_id != 2:
                    fade_background(2)
            else:
                if fade_background_id != 2:
                    fade_background(2)
            background_scroll_vel = 0
        if entity_manager.camera_position[1] > 110 * commons.BLOCKSIZE:
            if entity_manager.camera_position[0] < world.biome_border_x_1 * commons.BLOCKSIZE:
                if fade_background_id != 0:
                    fade_background(0)
            elif entity_manager.camera_position[0] < world.biome_border_x_2 * commons.BLOCKSIZE:
                if fade_background_id != 1:
                    fade_background(1)
            else:
                if fade_background_id != 4:
                    fade_background(4)
            background_scroll_vel = 0

        elif entity_manager.camera_position[1] > 15 * commons.BLOCKSIZE:
            if commons.CURRENT_TIME_STATE == TimeState.NIGHT:
                if fade_background_id != 7:
                    fade_background(7)
            elif commons.CURRENT_TIME_STATE == TimeState.DAWN or commons.CURRENT_TIME_STATE == TimeState.DUSK:
                if fade_background_id != 8:
                    fade_background(8)
            else:
                if fade_background_id != 3:
                    fade_background(3)

        else:
            if commons.CURRENT_TIME_STATE == TimeState.NIGHT:
                if fade_background_id != 7:
                    fade_background(7)
            elif commons.CURRENT_TIME_STATE == TimeState.DAWN or commons.CURRENT_TIME_STATE == TimeState.DUSK:
                if fade_background_id != 8:
                    fade_background(8)
            else:
                if fade_background_id != 5:
                    fade_background(5)
            background_scroll_vel = 0.1
    else:
        background_tick -= commons.DELTA_TIME


"""================================================================================================================= 
    draw_death_message -> void

    Renders and draws a large death message to the screen
-----------------------------------------------------------------------------------------------------------------"""
def draw_death_message():
    death_text = shared_methods.outline_text("You Were Slain", (255, 255, 255), commons.LARGEFONT)
    alpha = (1 - (entity_manager.client_player.respawn_tick / 5.0)) * 255
    if alpha > 255:
        alpha = 255
    death_text.set_alpha(alpha)
    commons.screen.blit(death_text, (commons.WINDOW_WIDTH * 0.5 - death_text.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.5))


"""================================================================================================================= 
    render_hand_text -> void

    Renders the full name of the item that the player has equipped in their hotbar to a surface
-----------------------------------------------------------------------------------------------------------------"""
def render_hand_text():
    global hand_text
    item = entity_manager.client_player.items[ItemLocation.HOTBAR][entity_manager.client_player.hotbar_index]
    if item is not None:
        colour = shared_methods.get_tier_colour(item.get_tier())
        hand_text = shared_methods.outline_text(item.get_name(), colour, commons.DEFAULTFONT)
    else:
        hand_text = shared_methods.outline_text("", (255, 255, 255), commons.DEFAULTFONT)
        

"""================================================================================================================= 
    run_splash_screen -> void

    Run when booting the game to display some text and the default character running across the screen
-----------------------------------------------------------------------------------------------------------------"""
def run_splash_screen():
    age = 0
    splash_text = shared_methods.outline_text("A Fergus Griggs game...", (255, 255, 255), commons.LARGEFONT)
    black_surf = pygame.Surface((commons.WINDOW_WIDTH, commons.WINDOW_HEIGHT))
    sprites = player.render_sprites(commons.DEFAULT_PLAYER_MODEL, directions=1)

    torso_frame = 2
    arm_frame = 6

    x_pos = -30

    slow_tick = 0
    fast_tick = 0

    commons.OLD_TIME_MILLISECONDS = pygame.time.get_ticks()
    
    splash_screen_running = True

    while splash_screen_running:
        commons.DELTA_TIME = (pygame.time.get_ticks() - commons.OLD_TIME_MILLISECONDS) * 0.001
        commons.OLD_TIME_MILLISECONDS = pygame.time.get_ticks()

        commons.screen.blit(surface_manager.large_backgrounds[1], (0, 0))
        entity_manager.draw_particles()

        if age < 0.5:
            black_surf.set_alpha(255)

        elif 0.5 < age < 1.5:
            alpha = (1.5 - age) * 255
            black_surf.set_alpha(alpha)

        elif 1.5 < age < 4.5:
            entity_manager.update_particles()
            if slow_tick <= 0:
                slow_tick += 0.2
                game_data.play_sound("fg.sound.run")
            else:
                slow_tick -= commons.DELTA_TIME

            if fast_tick <= 0:
                fast_tick += 0.025
                if torso_frame < 14:
                    torso_frame += 1
                else:
                    torso_frame = 2

                if arm_frame < 18:
                    arm_frame += 1
                else:
                    arm_frame = 6

                if commons.PARTICLES:
                    for _ in range(int(4 * commons.PARTICLEDENSITY)):
                        entity_manager.spawn_particle((x_pos + commons.PLAYER_WIDTH - commons.WINDOW_WIDTH * 0.5, commons.WINDOW_HEIGHT * 0.25 + commons.PLAYER_HEIGHT * 1.15), (255, 255, 255), life=0.5, gravity=-0.4, size=10, angle=math.pi, spread=math.pi, magnitude=random.random() * 8)

            else:
                fast_tick -= commons.DELTA_TIME

            x_pos += commons.WINDOW_WIDTH * commons.DELTA_TIME * 0.35

            commons.screen.blit(sprites[0][torso_frame], (x_pos, commons.WINDOW_HEIGHT * 0.75))
            commons.screen.blit(sprites[1][arm_frame], (x_pos, commons.WINDOW_HEIGHT * 0.75))

        elif 4.5 < age < 5.5:
            entity_manager.update_particles()
            alpha = (age - 4.5) * 255
            black_surf.set_alpha(alpha)

        elif age > 6.0:
            splash_screen_running = False
        commons.screen.blit(splash_text, (commons.WINDOW_WIDTH * 0.5 - splash_text.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.5))
        commons.screen.blit(black_surf, (0, 0))

        age += commons.DELTA_TIME

        for splash_screen_event in pygame.event.get():
            if splash_screen_event.type == QUIT:
                pygame.quit()
                sys.exit()
            if splash_screen_event.type == KEYDOWN:
                splash_screen_running = False
        pygame.display.flip()

        clock.tick(commons.TARGETFPS)


"""================================================================================================================= 
    render_stats_text -> bool

    Gets an item using the parsed position and renders it's information to a surface
-----------------------------------------------------------------------------------------------------------------"""
def render_stats_text(pos):
    global stats_text, last_hovered_item

    if pos[0] == ItemLocation.CRAFTING_MENU:
        item = Item(entity_manager.client_player.items[pos[0]][pos[1]][0], entity_manager.client_player.items[pos[0]][pos[1]][1])
    else:
        item = entity_manager.client_player.items[pos[0]][pos[1]]

    if item is not None:
        if item != last_hovered_item:
            last_hovered_item = item
            stats_text = pygame.Surface((340, 200))
            stats_text.fill((255, 0, 255))
            stats_text.set_colorkey((255, 0, 255))
            
            stats = [shared_methods.outline_text(item.get_name(), shared_methods.get_tier_colour(item.get_tier()), commons.DEFAULTFONT)]

            if item.has_tag(ItemTag.WEAPON):
                stats.append(shared_methods.outline_text(str(round(item.get_attack_damage(), 1)).rstrip('0').rstrip('.') + " damage", (255, 255, 255), commons.DEFAULTFONT))
                stats.append(shared_methods.outline_text(str(round(item.get_crit_chance() * 100, 1)).rstrip('0').rstrip('.') + "% critical strike chance", (255, 255, 255), commons.DEFAULTFONT))
                stats.append(shared_methods.outline_text(get_speed_text(item.get_attack_speed()), (255, 255, 255), commons.DEFAULTFONT))
                stats.append(shared_methods.outline_text(get_knockback_text(item.get_knockback()), (255, 255, 255), commons.DEFAULTFONT))
            
            if item.has_tag(ItemTag.AMMO):
                stats.append(shared_methods.outline_text("Ammunition", (255, 255, 255), commons.DEFAULTFONT))
                stats.append(shared_methods.outline_text(str(item.get_ammo_damage()) + " damage", (255, 255, 255), commons.DEFAULTFONT))
                stats.append(shared_methods.outline_text(str(round(item.get_ammo_knockback_mod() * 100, 1)) + "% knockback", (255, 255, 255), commons.DEFAULTFONT))
                stats.append(shared_methods.outline_text(str(round(item.get_ammo_gravity_mod() * 100, 1)) + "% gravity", (255, 255, 255), commons.DEFAULTFONT))
                stats.append(shared_methods.outline_text(str(round(item.get_ammo_drag() * 100, 1)) + "% drag", (255, 255, 255), commons.DEFAULTFONT))

            if item.has_tag(ItemTag.MATERIAL):
                stats.append(shared_methods.outline_text("Material", (255, 255, 255), commons.DEFAULTFONT))
            
            if item.has_tag(ItemTag.TILE):
                stats.append(shared_methods.outline_text("Can be placed", (255, 255, 255), commons.DEFAULTFONT))

            stats.append(shared_methods.outline_text(item.get_description(), (255, 255, 255), commons.DEFAULTFONT))

            if item.has_prefix:
                if item.prefix_data[1][1] != 0:
                    if item.prefix_data[1][1] > 0:
                        colour = tuple(good_colour)
                    else:
                        colour = tuple(bad_colour)
                    stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][1] * 100))) + "% damage", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
                if item.prefix_data[0] != ItemPrefixGroup.UNIVERSAL:
                    if item.prefix_data[1][2] != 0:
                        if item.prefix_data[1][2] > 0:
                            colour = tuple(good_colour)
                        else:
                            colour = tuple(bad_colour)
                        stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][2] * 100))) + "% speed", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
                else:
                    if item.prefix_data[1][2] != 0:
                        if item.prefix_data[1][2] > 0:
                            colour = tuple(good_colour)
                        else:
                            colour = tuple(bad_colour)
                        stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][2] * 100))) + "% critical strike chance", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
                    if item.prefix_data[1][3] != 0:
                        if item.prefix_data[1][3] > 0:
                            colour = tuple(good_colour)
                        else:
                            colour = tuple(bad_colour)
                        stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][3] * 100))) + "% knockback", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
                if item.prefix_data[0] != ItemPrefixGroup.UNIVERSAL:
                    if item.prefix_data[1][3] != 0:
                        if item.prefix_data[1][3] > 0:
                            colour = tuple(good_colour)
                        else:
                            colour = tuple(bad_colour)
                        stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][3] * 100))) + "% critical strike chance", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
                if item.prefix_data[0] == ItemPrefixGroup.COMMON:
                    if item.prefix_data[1][4] != 0:
                        if item.prefix_data[1][4] > 0:
                            colour = tuple(good_colour)
                        else:
                            colour = tuple(bad_colour)
                        stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][4] * 100))) + "% knockback", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
                if item.prefix_data[0] == ItemPrefixGroup.MELEE:
                    if item.prefix_data[1][4] != 0:
                        if item.prefix_data[1][4] > 0:
                            colour = tuple(good_colour)
                        else:
                            colour = tuple(bad_colour)
                        stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][4] * 100))) + "% size", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
                elif item.prefix_data[0] == ItemPrefixGroup.RANGED:
                    if item.prefix_data[1][4] != 0:
                        if item.prefix_data[1][4] > 0:
                            colour = tuple(good_colour)
                        else:
                            colour = tuple(bad_colour)
                        stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][4] * 100))) + "% projectile velocity", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
                elif item.prefix_data[0] == ItemPrefixGroup.MAGICAL:
                    if item.prefix_data[1][4] != 0:
                        if item.prefix_data[1][4] < 0:
                            colour = tuple(good_colour)
                        else:
                            colour = tuple(bad_colour)
                        stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][4] * 100))) + "% size", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
                if item.prefix_data[0] == ItemPrefixGroup.MELEE or item.prefix_data[0] == ItemPrefixGroup.RANGED or item.prefix_data[0] == ItemPrefixGroup.MAGICAL:
                    if item.prefix_data[1][5] != 0:
                        if item.prefix_data[1][5] > 0:
                            colour = tuple(good_colour)
                        else:
                            colour = tuple(bad_colour)
                        stats.append(shared_methods.outline_text(add_plus(str(int(item.prefix_data[1][5] * 100))) + "% knockback", colour, commons.DEFAULTFONT, outline_colour=shared_methods.darken_colour(colour)))
            for stat_index in range(len(stats)):
                stats_text.blit(stats[stat_index], (0, stat_index * 15))
        return True
    return False


"""================================================================================================================= 
    update_light -> void

    Run by the lighting thread to update the light surface and it's position in the world
-----------------------------------------------------------------------------------------------------------------"""
def update_light(thread_name, thread_id):
    global light_surf, map_light, light_min_x, light_max_x, light_min_y, light_max_y, thread_active, newest_light_surf, newest_light_surf_pos, last_thread_time
    thread_active = True

    target_position = (entity_manager.camera_position[0] + (entity_manager.camera_position_difference[0] / commons.DELTA_TIME) * last_thread_time, entity_manager.camera_position[1] + (entity_manager.camera_position_difference[1] / commons.DELTA_TIME) * last_thread_time)

    light_min_x = int(target_position[0] // commons.BLOCKSIZE - LIGHTRENDERDISTANCEX)
    light_max_x = int(target_position[0] // commons.BLOCKSIZE + LIGHTRENDERDISTANCEX)
    light_min_y = int(target_position[1] // commons.BLOCKSIZE - LIGHTRENDERDISTANCEY)
    light_max_y = int(target_position[1] // commons.BLOCKSIZE + LIGHTRENDERDISTANCEY)

    min_change_x = 0
    min_change_y = 0

    if light_min_x < 0:
        min_change_x = -light_min_x
        light_min_x = 0
    if light_min_y < 0:
        min_change_y = -light_min_y
        light_min_y = 0

    if light_min_x >= world.WORLD_SIZE_X or light_min_y >= world.WORLD_SIZE_Y or light_max_x < 0 or light_max_y < 0:
        thread_active = False
        return

    temp_pos = ((target_position[0] // commons.BLOCKSIZE - LIGHTRENDERDISTANCEX + min_change_x) * commons.BLOCKSIZE, (target_position[1] // commons.BLOCKSIZE - LIGHTRENDERDISTANCEY + min_change_y) * commons.BLOCKSIZE)
    
    if light_max_x > world.WORLD_SIZE_X:
        light_max_x = world.WORLD_SIZE_X
    if light_max_y > world.WORLD_SIZE_Y:
        light_max_y = world.WORLD_SIZE_Y

    # timeBefore = pygame.time.get_ticks()

    for x_index in range(light_min_x, light_max_x):
        for y_index in range(light_min_y, light_max_y):
            map_light[x_index][y_index] = max(0, map_light[x_index][y_index] - 16)

    # mapLight = [[0 for i in range(world.WORLD_SIZE_Y)] for j in range(world.WORLD_SIZE_X)]

    for x_index in range(light_min_x, light_max_x):
        for y_index in range(light_min_y, light_max_y):
            if y_index < 110:
                if world.world.tile_data[x_index][y_index][1] == game_data.air_wall_id and world.world.tile_data[x_index][y_index][0] == game_data.air_tile_id:
                    fill_light(x_index, y_index, commons.CURRENT_SKY_LIGHTING)
            tile_emission = game_data.tile_id_light_emission_lookup[world.world.tile_data[x_index][y_index][0]]
            if tile_emission > 0:
                fill_light(x_index, y_index, tile_emission)

    # print("Fill Light MS: ", pygame.time.get_ticks() - timeBefore)

    range_x = light_max_x - light_min_x
    range_y = light_max_y - light_min_y

    # timeBefore = pygame.time.get_ticks()

    light_surf = pygame.Surface((range_x, range_y), pygame.SRCALPHA)

    for x_index in range(range_x):
        for y_index in range(range_y):
            tile_dat = world.world.tile_data[light_min_x + x_index][light_min_y + y_index]
            if tile_dat[0] == game_data.air_tile_id and tile_dat[1] == game_data.air_wall_id:
                light_surf.set_at((x_index, y_index), (0, 0, 0, 255 - commons.CURRENT_SKY_LIGHTING))
            else:
                light_surf.set_at((x_index, y_index), (0, 0, 0, 255 - map_light[x_index + light_min_x][y_index + light_min_y]))

    light_surf = pygame.transform.scale(light_surf, (range_x * commons.BLOCKSIZE, range_y * commons.BLOCKSIZE))

    newest_light_surf_pos = temp_pos
    newest_light_surf = light_surf
    thread_active = False

    # print("Scale Copy MS: ", pygame.time.get_ticks() - timeBefore)


"""================================================================================================================= 
    fill_light -> void

    Recursively calls itself to populate data in the map_light array
-----------------------------------------------------------------------------------------------------------------"""
def fill_light(x_pos, y_pos, light_value):
    global map_light
    if light_min_x <= x_pos < light_max_x and light_min_y <= y_pos < light_max_y:
        light_reduction = game_data.tile_id_light_reduction_lookup[world.world.tile_data[x_pos][y_pos][0]]
        new_light_value = max(0, light_value - light_reduction)
        if new_light_value > map_light[x_pos][y_pos]:
            map_light[x_pos][y_pos] = int(new_light_value)
            fill_light(x_pos - 1, y_pos, new_light_value)
            fill_light(x_pos + 1, y_pos, new_light_value)
            fill_light(x_pos, y_pos - 1, new_light_value)
            fill_light(x_pos, y_pos + 1, new_light_value)
        else:
            return
    else:
        return


"""================================================================================================================= 
    get_speed_text -> string

    Gets a string relating to the speed value given
-----------------------------------------------------------------------------------------------------------------"""
def get_speed_text(speed):
    if speed < 2:
        return "Insanely fast speed"
    elif speed < 10:
        return "Extremely fast speed"
    elif speed < 25:
        return "Very fast speed"
    elif speed < 40:
        return "Fast speed"
    elif speed < 60:
        return "Normal speed"
    elif speed < 80:
        return "Slow speed"
    else:
        return "Very Slow Speed"


"""================================================================================================================= 
    get_knockback_text -> string

    Gets a string relating to the knockback value given
-----------------------------------------------------------------------------------------------------------------"""
def get_knockback_text(knockback):
    if knockback == 0:
        return "No knockback"
    elif knockback < 2:
        return "Very weak knockback"
    elif knockback < 5:
        return "Weak knockback"
    elif knockback < 7:
        return "Average knockback"
    elif knockback < 9:
        return "Strong knockback"
    else:
        return "Very strong knockback"


"""================================================================================================================= 
    get_bounces_text -> string

    Cleans up ammunition's bounce text
-----------------------------------------------------------------------------------------------------------------"""
def get_bounces_text(bounces):
    if bounces == 0:
        return "No bounces"
    elif bounces == 1:
        return "1 bounce"
    else:
        return str(bounces) + " bounces"


"""================================================================================================================= 
    add_plus -> string

    Adds a plus to a string if it doesn't start with a minus
-----------------------------------------------------------------------------------------------------------------"""
def add_plus(string):
    if string[0] != "-":
        string = "+" + string
    return string


"""================================================================================================================= 
    draw_inventory_hover_text -> void

    Checks if the player is hovering over an item in the UI and displays the item's info if they are
-----------------------------------------------------------------------------------------------------------------"""
def draw_inventory_hover_text():
    global can_drop_holding, can_pickup_item, item_drop_tick, item_drop_rate
    pos = None

    # Inventory
    if Rect(5, 20, 480, 244).collidepoint(commons.MOUSE_POS):
        for hotbar_index in range(10):
            if Rect(5 + 48 * hotbar_index, 20, 48, 48).collidepoint(commons.MOUSE_POS):
                pos = [ItemLocation.HOTBAR, hotbar_index]
                break

        for inventory_index in range(40):
            slot_x = inventory_index % 10
            slot_y = inventory_index // 10
            if Rect(5 + 48 * slot_x, 67 + 48 * slot_y, 48, 48).collidepoint(commons.MOUSE_POS):
                pos = [ItemLocation.INVENTORY, inventory_index]
                break

    # Chest
    elif entity_manager.client_player.chest_open and Rect(245, 265, 384, 192).collidepoint(commons.MOUSE_POS):
        for chest_index in range(20):
            slot_x = chest_index % 10
            slot_y = chest_index // 10
            if Rect(245 + 48 * slot_x, 265 + slot_y * 48, 48, 48).collidepoint(commons.MOUSE_POS):
                pos = [ItemLocation.CHEST, chest_index]
                break

    # Crafting menu
    elif Rect(5, 270, 48, 288).collidepoint(commons.MOUSE_POS):
        array_index = (commons.MOUSE_POS[1] - 270 - int(entity_manager.client_player.crafting_menu_offset_y)) // 48
        if 0 <= array_index < len(entity_manager.client_player.items[ItemLocation.CRAFTING_MENU]):
            if pygame.mouse.get_pressed()[0]:  
                if not commons.IS_HOLDING_ITEM:
                    commons.ITEM_HOLDING = Item(entity_manager.client_player.items[ItemLocation.CRAFTING_MENU][array_index][0],
                                                amnt=entity_manager.client_player.items[ItemLocation.CRAFTING_MENU][array_index][1],
                                                auto_assign_prefix=True)
                    commons.IS_HOLDING_ITEM = True
                    can_pickup_item = False
                    can_drop_holding = False
                    game_data.play_sound(commons.ITEM_HOLDING.get_pickup_sound_id_str())
                elif can_drop_holding:
                    if commons.ITEM_HOLDING.item_id == entity_manager.client_player.items[ItemLocation.CRAFTING_MENU][array_index][0]:
                        if commons.ITEM_HOLDING.amnt < commons.ITEM_HOLDING.get_max_stack():
                            commons.ITEM_HOLDING.amnt += entity_manager.client_player.items[ItemLocation.CRAFTING_MENU][array_index][1]
                            game_data.play_sound("fg.sound.grab")
            
            if render_stats_text([ItemLocation.CRAFTING_MENU, array_index]) and not commons.IS_HOLDING_ITEM:
                commons.screen.blit(stats_text, (commons.MOUSE_POS[0] + 10, commons.MOUSE_POS[1] + 10))

    if pos is not None:
        mouse_buttons = pygame.mouse.get_pressed()

        if mouse_buttons[0] or mouse_buttons[2]:
            # Dropping holding item
            if can_drop_holding and commons.ITEM_HOLDING is not None:
                if mouse_buttons[0]:
                    amnt = commons.ITEM_HOLDING.amnt
                else:
                    amnt = 1

                item_add_data = None

                if mouse_buttons[0] or item_drop_tick <= 0:
                    item_add_data = entity_manager.client_player.give_item(commons.ITEM_HOLDING, amnt, position=pos)

                if item_add_data is not None:
                    can_drop_holding = False

                    # Items are being dropped
                    if item_add_data[0] == ItemSlotClickResult.GAVE_ALL:
                        game_data.play_sound(commons.ITEM_HOLDING.get_drop_sound_id_str())
                        if mouse_buttons[0]:
                            commons.ITEM_HOLDING = None
                            commons.IS_HOLDING_ITEM = False
                        else:
                            commons.ITEM_HOLDING.amnt -= 1

                    # Dropping some of the items in hand
                    elif item_add_data[0] == ItemSlotClickResult.GAVE_SOME:
                        game_data.play_sound(commons.ITEM_HOLDING.get_drop_sound_id_str())
                        commons.ITEM_HOLDING.amnt = item_add_data[1]

                    # Items are being swapped
                    elif item_add_data[0] == ItemSlotClickResult.SWAPPED:
                        game_data.play_sound(commons.ITEM_HOLDING.get_drop_sound_id_str())
                        entity_manager.client_player.items[item_add_data[2]][pos[1]] = commons.ITEM_HOLDING
                        commons.ITEM_HOLDING = item_add_data[1]

                    if pos not in entity_manager.client_player.old_inventory_positions:
                        entity_manager.client_player.old_inventory_positions.append(pos)

                if item_drop_tick <= 0:
                    item_drop_rate -= 1
                    if item_drop_rate <= 0:
                        item_drop_rate = 0
                    item_drop_tick = int(item_drop_rate)
                    if commons.ITEM_HOLDING is not None and commons.ITEM_HOLDING.amnt <= 0:
                        commons.ITEM_HOLDING = None
                        commons.IS_HOLDING_ITEM = False
                else:
                    item_drop_tick -= commons.DELTA_TIME

            # Picking up item
            elif can_pickup_item and not mouse_buttons[2]:
                can_pickup_item = False
                commons.ITEM_HOLDING = entity_manager.client_player.remove_item(pos)
                if commons.ITEM_HOLDING is not None:
                    game_data.play_sound(commons.ITEM_HOLDING.get_pickup_sound_id_str())
                    commons.IS_HOLDING_ITEM = True
                entity_manager.client_player.render_current_item_image()

        if render_stats_text(pos) and not commons.IS_HOLDING_ITEM:
            commons.screen.blit(stats_text, (commons.MOUSE_POS[0] + 10, commons.MOUSE_POS[1] + 10))

    elif pygame.mouse.get_pressed()[2] and commons.IS_HOLDING_ITEM:
        if entity_manager.client_player.direction == 1:
            velocity = (16, -random.random())
        else:
            velocity = (-16, -random.random())

        entity_manager.spawn_physics_item(commons.ITEM_HOLDING, entity_manager.client_player.position, pickup_delay=250, velocity=velocity)
        
        commons.IS_HOLDING_ITEM = False
        can_drop_holding = False
        commons.ITEM_HOLDING = None


"""================================================================================================================= 
    draw_item_holding -> void

    Draws the exit button in the bottom left, also spawns the exit confirmation prompt
-----------------------------------------------------------------------------------------------------------------"""


def draw_item_holding():
    if commons.IS_HOLDING_ITEM:
        commons.screen.blit(commons.ITEM_HOLDING.get_image(), (commons.MOUSE_POS[0] + 10, commons.MOUSE_POS[1] + 10))
        if commons.ITEM_HOLDING.amnt > 1:
            commons.screen.blit(shared_methods.outline_text(str(commons.ITEM_HOLDING.amnt), (255, 255, 255), commons.SMALLFONT), (commons.MOUSE_POS[0] + 34, commons.MOUSE_POS[1] + 40))


"""================================================================================================================= 
    draw_exit_button -> void

    Draws the exit button in the bottom left, also spawns the exit confirmation prompt
-----------------------------------------------------------------------------------------------------------------"""


def draw_exit_button():
    global quit_button_hover
    top = commons.WINDOW_HEIGHT - 20
    left = commons.WINDOW_WIDTH - 50
    if Rect(left, top, 50, 20).collidepoint(commons.MOUSE_POS):
        if not quit_button_hover:
            quit_button_hover = True
            game_data.play_sound("fg.sound.menu_select")
        colour = (230, 230, 0)
        if pygame.mouse.get_pressed()[0]:
            entity_manager.client_player.inventory_open = False
            entity_manager.client_player.chest_open = False
            entity_manager.client_prompt = prompt.Prompt("Exit", game_data.exit_messages[random.randint(0, len(game_data.exit_messages) - 1)], button_1_name="Yep", size=(6, 2))
            commons.WAIT_TO_USE = True
    else:
        colour = (255, 255, 255)
        quit_button_hover = False
    exit_text = shared_methods.outline_text("Quit", colour, commons.DEFAULTFONT)
    commons.screen.blit(exit_text, (left, top))


"""================================================================================================================= 
    draw_interactable_block_hover -> void

    Draws the item image of an interactable block being hovered by the mouse
-----------------------------------------------------------------------------------------------------------------"""


def draw_interactable_block_hover():
    if world.tile_in_map(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1]):
        tile_id = world.world.tile_data[commons.TILE_POSITION_MOUSE_HOVERING[0]][commons.TILE_POSITION_MOUSE_HOVERING[1]][0]
        tile_data = game_data.get_tile_by_id(tile_id)
        if TileTag.CHEST in tile_data["@tags"] or TileTag.CYCLABLE in tile_data["@tags"]:
            item_data = game_data.get_item_by_id_str(tile_data["@item_id_str"])
            commons.screen.blit(item_data["@image"], commons.MOUSE_POS)


good_colour = (10, 230, 10)
bad_colour = (230, 10, 10)

# MAX SURF WIDTH IS 16383

pygame.display.set_caption("Fegaria Remastered " + __version__)

song_end_event = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(song_end_event)

ICON = pygame.image.load("res/images/icon.png")
pygame.display.set_icon(ICON)

clock = pygame.time.Clock()

commons.DEFAULT_PLAYER_MODEL = player.Model(0, 0, (127, 72, 36),
                                            (62, 22, 0),
                                            (0, 0, 0),
                                            (95, 125, 127),
                                            (48, 76, 127),
                                            (129, 113, 45),
                                            (80,  100,  45)
                                            )

if commons.SPLASHSCREEN:
    run_splash_screen()
    
fps_text = shared_methods.outline_text(str(0), (255, 255, 255), commons.DEFAULTFONT)
hand_text = pygame.Surface((0, 0))
stats_text = pygame.Surface((0, 0))

fade_back = False
fade_float = 0.0
fade_background_id = -1
fade_surf = pygame.Surface((0, 0))
background_id = 5

background_tick = 0
background_scroll_vel = 0
auto_save_tick = 0
fps_tick = 0
last_hovered_item = None
parallax_pos = (0, 0)
can_drop_holding = False
can_pickup_item = False
quit_button_hover = False
thread_active = False
item_drop_tick = 0
item_drop_rate = 0

light_surf = pygame.Surface((0, 0))
newest_light_surf = pygame.Surface((0, 0))
newest_light_surf_pos = (0, 0)
light_min_x = 0
light_max_x = 0
light_min_y = 0
light_max_y = 0

global_lighting = 255

LIGHTRENDERDISTANCEX = int((commons.WINDOW_WIDTH * 0.5) / commons.BLOCKSIZE) + 9
LIGHTRENDERDISTANCEY = int((commons.WINDOW_HEIGHT * 0.5) / commons.BLOCKSIZE) + 9

last_thread_time = 0.2
last_thread_start = pygame.time.get_ticks()

save_select_surf = pygame.Surface((315, 360))
save_select_surf.set_colorkey((255, 0, 255))
save_select_y_offset = 0
save_select_y_velocity = 0

load_menu_surf = shared_methods.create_menu_surface(7, 8, "")
load_menu_box_left1 = commons.WINDOW_WIDTH * 0.5 - 336 * 0.5
load_menu_box_left2 = commons.WINDOW_WIDTH * 0.5 - 315 * 0.5

screenshot_img = pygame.image.load("res/images/screenshots/" + str(random.randint(1, 16)) + ".png")
scale = 280 / screenshot_img.get_height()
screenshot_img = pygame.transform.scale(screenshot_img, (int(scale * screenshot_img.get_width()), 280))
border_img = shared_methods.create_menu_surface(screenshot_img.get_width() // 48 + 2, 7, "")
        
old_time_milliseconds = pygame.time.get_ticks()

game_running = True

while game_running:
    commons.MOUSE_POS = pygame.mouse.get_pos()
    commons.TILE_POSITION_MOUSE_HOVERING = (int((entity_manager.camera_position[0] + commons.MOUSE_POS[0] - commons.WINDOW_WIDTH * 0.5) // commons.BLOCKSIZE), int((entity_manager.camera_position[1] + commons.MOUSE_POS[1] - commons.WINDOW_HEIGHT * 0.5) // commons.BLOCKSIZE))
    
    commons.DELTA_TIME = (pygame.time.get_ticks() - old_time_milliseconds) * 0.001
    old_time_milliseconds = pygame.time.get_ticks()

    # If framerate is less than 30, simulate at a slower speed
    if commons.DELTA_TIME > 0.033333:
        commons.DELTA_TIME = 0.033333

    # Update the sky light value
    base_zero_to_one_float = math.sin(pygame.time.get_ticks() * 0.00005) * 0.5 + 0.5
    smoothed_zero_to_one_float = shared_methods.smooth_zero_to_one(base_zero_to_one_float, 2)
    smoothed_zero_to_one_float = smoothed_zero_to_one_float * 0.75 + 0.25

    commons.CURRENT_SKY_LIGHTING = int(smoothed_zero_to_one_float * global_lighting)
    # Update the time states using the sky light value
    if commons.CURRENT_SKY_LIGHTING < 100:
        commons.CURRENT_TIME_STATE = TimeState.NIGHT
    elif commons.CURRENT_SKY_LIGHTING < 150:
        commons.CURRENT_TIME_STATE = TimeState.DAWN
    else:
        commons.CURRENT_TIME_STATE = TimeState.DAY

    if pygame.key.get_mods() & (KMOD_LSHIFT | KMOD_RSHIFT):
        commons.SHIFT_ACTIVE = True
    else:
        commons.SHIFT_ACTIVE = False

    if commons.GAME_STATE == "PLAYING":
        world.world.play_time += commons.DELTA_TIME
        entity_manager.client_player.play_time += commons.DELTA_TIME

        evenOlderCamPos = entity_manager.old_camera_position

        entity_manager.old_camera_position = (entity_manager.camera_position[0], entity_manager.camera_position[1])
        
        entity_manager.update_enemies()
        entity_manager.update_projectiles()
        entity_manager.update_particles()
        entity_manager.update_messages()
        entity_manager.update_physics_items()
        entity_manager.check_enemy_spawn()

        entity_manager.client_player.update()
        entity_manager.client_player.animate()

        entity_manager.update_damage_numbers()
        entity_manager.update_recent_pickups()
        
        world.check_grow_grass()

        temp_cam_pos_x = entity_manager.camera_position[0]
        temp_cam_pos_y = entity_manager.camera_position[1]

        if commons.SMOOTHCAM:
            need_to_move_x = (entity_manager.client_player.position[0] - temp_cam_pos_x) * commons.DELTA_TIME * 4
            need_to_move_y = (entity_manager.client_player.position[1] - temp_cam_pos_y) * commons.DELTA_TIME * 4

            need_to_move_magnitude = math.sqrt(need_to_move_x ** 2 + need_to_move_y ** 2)
            need_to_move_angle = math.atan2(need_to_move_y, need_to_move_x)

            cam_diff_magnitude = math.sqrt(entity_manager.camera_position_difference[0] ** 2 + entity_manager.camera_position_difference[1] ** 2)

            if cam_diff_magnitude < 1:
                cam_diff_magnitude = 1

            can_move_magnitude = cam_diff_magnitude * (1 + commons.DELTA_TIME * 8)

            # Make sure it does not exceed a max camera speed
            can_move_magnitude = min(can_move_magnitude, 200 * commons.BLOCKSIZE * commons.DELTA_TIME)

            if need_to_move_magnitude > can_move_magnitude:
                temp_cam_pos_x = temp_cam_pos_x + math.cos(need_to_move_angle) * can_move_magnitude
                temp_cam_pos_y = temp_cam_pos_y + math.sin(need_to_move_angle) * can_move_magnitude
            else:
                temp_cam_pos_x = temp_cam_pos_x + math.cos(need_to_move_angle) * need_to_move_magnitude
                temp_cam_pos_y = temp_cam_pos_y + math.sin(need_to_move_angle) * need_to_move_magnitude

        else:
            temp_cam_pos_x = entity_manager.client_player.position[0]
            temp_cam_pos_y = entity_manager.client_player.position[1]

        if temp_cam_pos_x > world.border_right + commons.BLOCKSIZE - commons.WINDOW_WIDTH * 0.5:
            temp_cam_pos_x = world.border_right + commons.BLOCKSIZE - commons.WINDOW_WIDTH * 0.5
        elif temp_cam_pos_x < commons.WINDOW_WIDTH * 0.5:
            temp_cam_pos_x = commons.WINDOW_WIDTH * 0.5
        if temp_cam_pos_y > world.border_down + commons.BLOCKSIZE * 1.5 - commons.WINDOW_HEIGHT * 0.5:
            temp_cam_pos_y = world.border_down + commons.BLOCKSIZE * 1.5 - commons.WINDOW_HEIGHT * 0.5
        elif temp_cam_pos_y < commons.WINDOW_HEIGHT * 0.5:
            temp_cam_pos_y = commons.WINDOW_HEIGHT * 0.5
        
        entity_manager.camera_position = (temp_cam_pos_x, temp_cam_pos_y)

        entity_manager.camera_position_difference = (entity_manager.camera_position[0] - entity_manager.old_camera_position[0], entity_manager.camera_position[1] - entity_manager.old_camera_position[1])

        move_parallax((-entity_manager.camera_position_difference[0] * commons.PARALLAXAMNT, -entity_manager.camera_position_difference[1] * commons.PARALLAXAMNT))  # move parallax based on vel
        
        if entity_manager.client_prompt is not None:
            entity_manager.client_prompt.update()
            if entity_manager.client_prompt.close:
                entity_manager.client_prompt = None
                commons.WAIT_TO_USE = True
        
        if commons.BACKGROUND:
            if fade_back:
                if fade_float < 1.0:
                    fade_surf = surface_manager.large_backgrounds[fade_background_id].copy()
                    fade_surf.set_alpha(fade_float * 255)
                    fade_float += commons.DELTA_TIME
                else:
                    fade_back = False
                    background_id = int(fade_background_id)
            commons.screen.blit(surface_manager.large_backgrounds[background_id], parallax_pos)
            if fade_back:
                commons.screen.blit(fade_surf, parallax_pos)
        else:
            commons.screen.fill((153, 217, 234))
        
        terrain_position = (commons.WINDOW_WIDTH * 0.5 - entity_manager.camera_position[0], commons.WINDOW_HEIGHT * 0.5 - entity_manager.camera_position[1])
        commons.screen.blit(world.terrain_surface, terrain_position)
        entity_manager.draw_projectiles()
        entity_manager.client_player.draw()
        entity_manager.draw_particles()
        entity_manager.draw_enemies()
        entity_manager.draw_physics_items()
                
        if commons.EXPERIMENTALLIGHTING:
            if not thread_active:
                last_thread_time = (pygame.time.get_ticks() - last_thread_start) * 0.001
                _thread.start_new_thread(update_light, ("LT", 1))
                last_thread_start = pygame.time.get_ticks()

            newest_light_surf.unlock()
            commons.screen.blit(newest_light_surf, (newest_light_surf_pos[0] - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5, newest_light_surf_pos[1] - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5))

        if commons.DRAWUI:
            entity_manager.client_player.draw_hp()
            commons.screen.blit(entity_manager.client_player.hotbar_image, (5, 20))
            entity_manager.draw_messages()
            
        entity_manager.draw_damage_numbers()
        entity_manager.draw_enemy_hover_text()
        entity_manager.draw_recent_pickups()
        draw_interactable_block_hover()

        if entity_manager.client_prompt is not None:
            entity_manager.client_prompt.draw()

        if not entity_manager.client_player.alive:
            draw_death_message()

        if commons.DRAWUI:
            if entity_manager.client_player.inventory_open:
                commons.screen.blit(entity_manager.client_player.inventory_image, (5, 70))
                entity_manager.client_player.blit_craft_surf.fill((255, 0, 255))
                entity_manager.client_player.blit_craft_surf.blit(entity_manager.client_player.craftable_items_surf, (0, entity_manager.client_player.crafting_menu_offset_y))
                commons.screen.blit(entity_manager.client_player.blit_craft_surf, (5, 270))
            
            if entity_manager.client_player.chest_open:
                commons.screen.blit(entity_manager.client_player.chest_image, (245, 265))

            pygame.draw.rect(commons.screen, (230, 230, 10), Rect(5 + entity_manager.client_player.hotbar_index * 48, 20, 48, 48), 3)

            if entity_manager.client_player.inventory_open:
                draw_inventory_hover_text()
                draw_exit_button()

            if hand_text is not None:
                commons.screen.blit(hand_text, (242 - hand_text.get_width() * 0.5, 0))
            draw_item_holding()
        
        if commons.BACKGROUND:
            check_change_background()
            move_parallax((background_scroll_vel, 0))
            
        if auto_save_tick <= 0:
            auto_save_tick += commons.AUTOSAVEFREQUENCY
            entity_manager.client_player.save()
            world.save()
        else:
            auto_save_tick -= commons.DELTA_TIME
                
    elif commons.GAME_STATE == "MAINMENU":
        parallax_pos = (parallax_pos[0] - commons.DELTA_TIME * 20, 0)
        if parallax_pos[0] < -40:
            parallax_pos = (0, 0)
        commons.screen.blit(surface_manager.large_backgrounds[1], parallax_pos)

        menu_manager.update_menu_buttons()
        menu_manager.draw_menu_buttons()

        if commons.GAME_SUB_STATE == "MAIN":
            commons.screen.blit(border_img, (commons.WINDOW_WIDTH * 0.5 - border_img.get_width() * 0.5, 95))
            commons.screen.blit(screenshot_img, (commons.WINDOW_WIDTH * 0.5 - screenshot_img.get_width() * 0.5, 120))
            commons.screen.blit(menu_manager.title_message_text, (menu_manager.title_message_text_left, 65))

        elif commons.GAME_SUB_STATE == "PLAYERSELECTION":
            if pygame.mouse.get_pressed()[0] and not commons.WAIT_TO_USE:
                if Rect(load_menu_box_left1, 120, 336, 384).collidepoint(commons.MOUSE_POS):
                    for i in range(len(commons.PLAYER_SAVE_OPTIONS)):
                        if Rect(load_menu_box_left2, 132 + i * 62 + save_select_y_offset, 315, 60).collidepoint(commons.MOUSE_POS):
                            commons.WAIT_TO_USE = True
                            commons.PLAYER_DATA = commons.PLAYER_SAVE_OPTIONS[i][0]
                            menu_manager.load_menu_world_data()
                            game_data.play_sound("fg.sound.menu_open")
                            commons.GAME_SUB_STATE = "WORLDSELECTION"
                            commons.GAME_SUB_STATE_STACK.append("PLAYERSELECTION")
                            menu_manager.update_active_menu_buttons()
                            save_select_y_offset = 0
                            
            save_select_y_velocity *= 0.9
            if len(commons.PLAYER_SAVE_OPTIONS) > 5:
                save_select_y_offset += save_select_y_velocity
                if save_select_y_offset < -61 * len(commons.PLAYER_SAVE_OPTIONS) + 350:
                    save_select_y_offset = -61 * len(commons.PLAYER_SAVE_OPTIONS) + 350
                if save_select_y_offset > 0:
                    save_select_y_offset = 0

            commons.screen.blit(load_menu_surf, (load_menu_box_left1, 120))
            save_select_surf.fill((255, 0, 255))
            for i in range(len(commons.PLAYER_SAVE_OPTIONS)): 
                save_select_surf.blit(commons.PLAYER_SAVE_OPTIONS[i][1], (0, i * 62 + save_select_y_offset))
            commons.screen.blit(save_select_surf, (load_menu_box_left2,  132))

        elif commons.GAME_SUB_STATE == "PLAYERCREATION":
            commons.screen.blit(commons.PLAYER_FRAMES[0][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[0][0].get_width() * 0.5, 100))
            commons.screen.blit(commons.PLAYER_FRAMES[1][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[1][0].get_width() * 0.5, 100))

        elif commons.GAME_SUB_STATE == "WORLDSELECTION":
            should_break = False
            if pygame.mouse.get_pressed()[0] and not commons.WAIT_TO_USE:
                if Rect(load_menu_box_left1, 120, 336, 384).collidepoint(commons.MOUSE_POS):
                    for i in range(len(commons.WORLD_SAVE_OPTIONS)):
                        if Rect(load_menu_box_left2, 132 + i * 60 + save_select_y_offset, 315, 60).collidepoint(commons.MOUSE_POS):
                            game_data.play_sound("fg.sound.menu_open")

                            world.load(commons.WORLD_SAVE_OPTIONS[i][0])

                            world.WORLD_SIZE_X, world.WORLD_SIZE_Y = len(world.world.tile_data), len(world.world.tile_data[0])

                            world.biome_border_x_1 = world.WORLD_SIZE_X * 0.333333
                            world.biome_border_x_2 = world.WORLD_SIZE_X * 0.666666

                            world.border_left = int(commons.BLOCKSIZE)
                            world.border_right= int(world.WORLD_SIZE_X * commons.BLOCKSIZE - commons.BLOCKSIZE)
                            world.border_up = int(commons.BLOCKSIZE*1.5)
                            world.border_down = int(world.WORLD_SIZE_Y * commons.BLOCKSIZE - commons.BLOCKSIZE * 1.5)

                            world.tile_mask_data = [[-1 for _ in range(world.WORLD_SIZE_Y)] for _ in range(world.WORLD_SIZE_X)]
                            world.wall_tile_mask_data = [[-1 for _ in range(world.WORLD_SIZE_Y)] for _ in range(world.WORLD_SIZE_X)]
                            background_id = 5

                            entity_manager.create_player()

                            commons.screen.fill((0, 0, 0))

                            text0 = shared_methods.outline_text("Greetings " + entity_manager.client_player.name + ", bear with us while", (255, 255, 255), commons.LARGEFONT)
                            text1 = shared_methods.outline_text("we load up '" + world.world.name + "'", (255, 255, 255), commons.LARGEFONT)
                            text2 = shared_methods.outline_text(game_data.helpful_tips[random.randint(0, len(game_data.helpful_tips) - 1)], (255, 255, 255), commons.DEFAULTFONT)

                            commons.screen.blit(text0, (commons.WINDOW_WIDTH * 0.5 - text0.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.5 - 30))
                            commons.screen.blit(text1, (commons.WINDOW_WIDTH * 0.5 - text1.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.5))
                            commons.screen.blit(text2, (commons.WINDOW_WIDTH * 0.5 - text2.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.75))

                            pygame.display.flip()
                            world.create_terrain_surface()

                            entity_manager.camera_position = (world.world.spawn_position[0], 0)
                            entity_manager.client_player.position = tuple(world.world.spawn_position)
                            entity_manager.client_player.render_current_item_image()
                            entity_manager.client_player.render_hotbar()
                            entity_manager.client_player.render_inventory()

                            render_hand_text()
                            
                            map_light = [[0 for _ in range(world.WORLD_SIZE_Y)]for _ in range(world.WORLD_SIZE_X)]
                            for map_index_x in range(world.WORLD_SIZE_X - 1):
                                for map_index_y in range(world.WORLD_SIZE_Y - 1):
                                    if world.world.tile_data[map_index_x][map_index_y][0] == -1 and world.world.tile_data[map_index_x][map_index_y][1] == -1 and map_index_y < 110:
                                        map_light[map_index_x][map_index_y] = global_lighting
                                    else:
                                        map_light[map_index_x][map_index_y] = 0
                            
                            commons.GAME_STATE = "PLAYING"
                            should_break = True
                            break

            if not should_break:
                save_select_y_velocity *= 0.9
                if len(commons.WORLD_SAVE_OPTIONS) > 5:
                    save_select_y_offset += save_select_y_velocity
                    if save_select_y_offset < -61 * len(commons.WORLD_SAVE_OPTIONS) + 350:
                        save_select_y_offset = -61 * len(commons.WORLD_SAVE_OPTIONS) + 350
                    if save_select_y_offset > 0:
                        save_select_y_offset = 0
                        
                commons.screen.blit(load_menu_surf, (load_menu_box_left1, 120))
                save_select_surf.fill((255, 0, 255))
                for save_option_index in range(len(commons.WORLD_SAVE_OPTIONS)):
                    save_select_surf.blit(commons.WORLD_SAVE_OPTIONS[save_option_index][1], (0, save_option_index * 62 + save_select_y_offset))
                commons.screen.blit(save_select_surf, (load_menu_box_left2, 132))

        elif commons.GAME_SUB_STATE == "CLOTHES":
            commons.screen.blit(commons.PLAYER_FRAMES[0][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[0][0].get_width() * 0.5, 100))
            commons.screen.blit(commons.PLAYER_FRAMES[1][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[1][0].get_width() * 0.5, 100))

        elif commons.GAME_SUB_STATE == "WORLDNAMING":
            text = shared_methods.outline_text(commons.TEXT_INPUT + "|", (255, 255, 255), commons.LARGEFONT)
            commons.screen.blit(text, (commons.WINDOW_WIDTH * 0.5 - text.get_width() * 0.5, 175))

        elif commons.GAME_SUB_STATE == "PLAYERNAMING":
            text = shared_methods.outline_text(commons.TEXT_INPUT + "|", (255, 255, 255), commons.LARGEFONT)
            commons.screen.blit(text, (commons.WINDOW_WIDTH * 0.5 - text.get_width() * 0.5, 175))
            commons.screen.blit(commons.PLAYER_FRAMES[0][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[0][0].get_width() * 0.5, 100))
            commons.screen.blit(commons.PLAYER_FRAMES[1][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[1][0].get_width() * 0.5, 100))

        elif commons.GAME_SUB_STATE == "COLOURPICKER":

            entity_manager.client_colour_picker.update()

            if entity_manager.client_colour_picker.selected_x is not None and entity_manager.client_colour_picker.selected_y is not None:
                commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][1] = entity_manager.client_colour_picker.selected_x
                commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][2] = entity_manager.client_colour_picker.selected_y
                commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][0] = tuple(entity_manager.client_colour_picker.selected_colour)
                player.update_player_model_using_model_data()
                commons.PLAYER_FRAMES = player.render_sprites(commons.PLAYER_MODEL, directions=1, arm_frame_count=1, torso_frame_count=1)
            
            commons.screen.blit(commons.PLAYER_FRAMES[0][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[0][0].get_width() * 0.5, 100))
            commons.screen.blit(commons.PLAYER_FRAMES[1][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[1][0].get_width() * 0.5, 100))
            entity_manager.client_colour_picker.draw()
            
    # Draw a prompt if there is one
    if entity_manager.client_prompt is not None:
        entity_manager.client_prompt.update()
        entity_manager.client_prompt.draw()
        if entity_manager.client_prompt.close:
            entity_manager.client_prompt = None
            
    # Update fps text
    if commons.DRAWUI:
        if fps_tick <= 0:
            fps_tick += 0.5
            if commons.DELTA_TIME > 0:
                fps_text = shared_methods.outline_text(str(int(1.0 / commons.DELTA_TIME)), (255, 255, 255), commons.DEFAULTFONT)
        else:
            fps_tick -= commons.DELTA_TIME
        commons.screen.blit(fps_text, (commons.WINDOW_WIDTH - fps_text.get_width(), 0))

    # Reset some variables when the mousebutton is lifted
    if not pygame.mouse.get_pressed()[0]:
        if commons.WAIT_TO_USE and not pygame.mouse.get_pressed()[2]:
            commons.WAIT_TO_USE = False
        if commons.IS_HOLDING_ITEM:
            can_drop_holding = True
        elif not commons.IS_HOLDING_ITEM:
            can_pickup_item = True

    if not pygame.mouse.get_pressed()[2]:
        item_drop_rate = 25
        item_drop_tick = 0
            
    for event in pygame.event.get():
        if event.type == QUIT:
            if commons.GAME_STATE == "PLAYING":
                entity_manager.client_player.inventory_open = False
                entity_manager.client_player.chest_open = False
                entity_manager.client_prompt = prompt.Prompt("Exit", game_data.exit_messages[random.randint(0, len(game_data.exit_messages) - 1)], button_1_name="Yep", size=(6, 2))
            else:
                pygame.quit()
                sys.exit()
            commons.WAIT_TO_USE = True
        
        if event.type == song_end_event:
            pygame.mixer.music.load("res/sounds/day.mp3")
            pygame.mixer.music.set_volume(sound_manager.music_volume)
            pygame.mixer.music.play()

            # if event.key == K_CAPSLOCK:
            #    if commons.SHIFT_ACTIVE:
            #        commons.SHIFT_ACTIVE = False
            #    else:
            #        commons.SHIFT_ACTIVE = True

        if commons.GAME_STATE == "PLAYING":
            if event.type == KEYDOWN:
                # Toggle Inventory
                if event.key == K_ESCAPE:
                    if entity_manager.client_player.inventory_open:
                        game_data.play_sound("fg.sound.menu_close")
                        entity_manager.client_player.render_current_item_image()
                        entity_manager.client_player.inventory_open = False
                        entity_manager.client_player.chest_open = False
                    else:
                        game_data.play_sound("fg.sound.menu_open")
                        entity_manager.client_player.inventory_open = True
                        entity_manager.client_player.crafting_menu_offset_y = 120
                        entity_manager.client_player.update_craftable_items()
                        entity_manager.client_player.render_craftable_items_surf()
                        entity_manager.client_prompt = None
                
                # Player Move Left
                if event.key == K_a:
                    entity_manager.client_player.moving_left = True
                    entity_manager.client_player.animation_frame = random.randint(17, 29)
                    if not entity_manager.client_player.swinging_arm:
                        entity_manager.client_player.arm_animation_frame = random.randint(26, 39)
                    entity_manager.client_player.direction = 0
                
                # Player Move Right
                if event.key == K_d:
                    entity_manager.client_player.moving_right = True
                    entity_manager.client_player.animation_frame = random.randint(2, 15)
                    if not entity_manager.client_player.swinging_arm:
                        entity_manager.client_player.arm_animation_frame = random.randint(6, 19)
                    entity_manager.client_player.direction = 1

                # Player Walk
                if event.key == K_s:
                    entity_manager.client_player.moving_down = True
                    entity_manager.client_player.animation_speed = 0.05

                # Player Jump
                if event.key == K_SPACE:
                    entity_manager.client_player.jump()

                # Kill All Enemies Cheat
                if event.key == K_x:
                    if commons.SHIFT_ACTIVE:
                        while len(entity_manager.enemies) > 0:
                            entity_manager.enemies[0].kill((0, -50))
                        entity_manager.add_message("All enemies killed", (255, 223, 10), outline_colour=(80, 70, 3))
                
                # Spawn Enemy Cheat
                if event.key == K_f:
                    if commons.SHIFT_ACTIVE:
                        entity_manager.spawn_enemy((entity_manager.camera_position[0] - commons.WINDOW_WIDTH * 0.5 + commons.MOUSE_POS[0], entity_manager.camera_position[1] - commons.WINDOW_HEIGHT * 0.5 + commons.MOUSE_POS[1]))
                        entity_manager.add_message("Spawned enemy", (255, 223, 10), outline_colour=(80, 70, 3))

                # Respawn Cheats
                if event.key == K_r:
                    if commons.SHIFT_ACTIVE:
                        world.world.spawn_position = tuple(entity_manager.client_player.position)
                        entity_manager.add_message("Spawn point moved to " + str(world.world.spawn_position), (255, 223, 10), outline_colour=(80, 70, 3))
                    else:
                        if commons.PARTICLES:
                            for i in range(int(20 * commons.PARTICLEDENSITY)):
                                entity_manager.spawn_particle(entity_manager.client_player.position, (230, 230, 255), magnitude=1 + random.random() * 6, size=15, gravity=0)

                        game_data.play_sound("fg.sound.mirror")

                        entity_manager.client_player.respawn()
                        entity_manager.add_message("Player respawned", (255, 223, 10), outline_colour=(80, 70, 3))

                        if commons.PARTICLES:
                            for i in range(int(40 * commons.PARTICLEDENSITY)):
                                entity_manager.spawn_particle(entity_manager.client_player.position, (230, 230, 255), magnitude=1 + random.random() * 6, size=15, gravity=0)

                # World Snapshot
                if event.key == K_t:
                    if commons.SHIFT_ACTIVE:
                        tile_scale = 2
                        size_string = str(world.WORLD_SIZE_X * tile_scale) + "x" + str(world.WORLD_SIZE_Y * tile_scale)
                        date_string = str(datetime.datetime.now()).replace("-", ".").replace(" ", " - ").replace(":", ".")[:-7]
                        path = "res/images/world_snapshots/" + date_string + " - " + size_string + ".png"
                        world_surf = pygame.Surface((tile_scale * world.WORLD_SIZE_X, tile_scale * world.WORLD_SIZE_Y))
                        for tile_x in range(len(world.world.tile_data)):
                            for tile_y in range(len(world.world.tile_data[tile_x])):
                                tile_id = world.world.tile_data[tile_x][tile_y][0]
                                wall_id = world.world.tile_data[tile_x][tile_y][1]

                                if tile_id != game_data.air_tile_id:
                                    tile_data = game_data.get_tile_by_id(tile_id)
                                    if tile_data["@average_colour"] != (255, 0, 255):
                                        pygame.draw.rect(world_surf, tile_data["@average_colour"], Rect(tile_x * tile_scale, tile_y * tile_scale, tile_scale, tile_scale), 0)
                                        continue

                                if wall_id != game_data.air_wall_id:
                                    wall_data = game_data.get_wall_by_id(wall_id)
                                    if wall_data["@average_colour"] != (255, 0, 255):
                                        pygame.draw.rect(world_surf, wall_data["@average_colour"], Rect(tile_x * tile_scale, tile_y * tile_scale, tile_scale, tile_scale), 0)
                                        continue

                                sky_darken_factor = 1.0 - 0.7 * min(1.0, max(0.0, (tile_y - 55) / 110))
                                colour = shared_methods.darken_colour((135, 206, 234), sky_darken_factor)
                                pygame.draw.rect(world_surf, colour, Rect(tile_x * tile_scale, tile_y * tile_scale, tile_scale, tile_scale), 0)

                        pygame.image.save(world_surf, path)
                        entity_manager.add_message("World Snapshotshot Saved to: '" + path + "'", (255, 223, 10), outline_colour=(80, 70, 3))

                # Gravity Reverse Cheat
                if event.key == K_g:
                    if commons.SHIFT_ACTIVE:
                        commons.GRAVITY = -commons.GRAVITY
                        entity_manager.add_message("Gravity reversed", (255, 223, 10), outline_colour=(80, 70, 3))

                # Random Item Prefix Cheat
                if event.key == K_c:
                    if commons.SHIFT_ACTIVE:
                        if entity_manager.client_player.items[ItemLocation.HOTBAR][entity_manager.client_player.hotbar_index] is not None:
                            entity_manager.client_player.items[ItemLocation.HOTBAR][entity_manager.client_player.hotbar_index] = Item(entity_manager.client_player.items[ItemLocation.HOTBAR][entity_manager.client_player.hotbar_index].item_id, auto_assign_prefix=True)
                            entity_manager.add_message("Item prefix randomized", (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), life=2.5)
                            entity_manager.client_player.render_current_item_image()
                            render_hand_text()
                
                # Test Prompt Cheat
                if event.key == K_v:
                    if commons.SHIFT_ACTIVE:
                        entity_manager.client_prompt = prompt.Prompt("test", "My name's the guide, I can help you around this awfully crafted world. It's basically just a rip off of terraria so this should be child's play")
                        entity_manager.add_message("Random prompt deployed", (255, 223, 10), outline_colour=(80, 70, 3))

                # Get Tile and Wall IDS
                if event.key == K_p:
                    if commons.SHIFT_ACTIVE: 
                        if world.tile_in_map(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1]):
                            wallID = world.world.tile_data[commons.TILE_POSITION_MOUSE_HOVERING[0]][commons.TILE_POSITION_MOUSE_HOVERING[1]][1]
                            entity_manager.add_message("Wall at (" + str(commons.TILE_POSITION_MOUSE_HOVERING[0]) + ", " + str(commons.TILE_POSITION_MOUSE_HOVERING[1]) + ") has ID: " + str(wallID), (255, 223, 10), outline_colour=(80, 70, 3))
                    else:
                        if world.tile_in_map(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1]):
                            tileID = world.world.tile_data[commons.TILE_POSITION_MOUSE_HOVERING[0]][commons.TILE_POSITION_MOUSE_HOVERING[1]][0]
                            entity_manager.add_message("Tile at (" + str(commons.TILE_POSITION_MOUSE_HOVERING[0]) + ", " + str(commons.TILE_POSITION_MOUSE_HOVERING[1]) + ") has ID: " + str(tileID), (255, 223, 10), outline_colour=(80, 70, 3))

                # Toggle UI
                if event.key == K_u:
                    commons.DRAWUI = not commons.DRAWUI
                    entity_manager.add_message("UI " + shared_methods.get_on_off(commons.DRAWUI), (255, 223, 10), outline_colour=(80, 70, 3))

                # Toggle SMOOTHCAM
                if event.key == K_j:
                    commons.SMOOTHCAM = not commons.SMOOTHCAM
                    entity_manager.add_message("Smooth camera " + shared_methods.get_on_off(commons.SMOOTHCAM), (255, 223, 10), outline_colour=(80, 70, 3))

                # Toggle HITBOXES
                if event.key == K_h:
                    commons.HITBOXES = not commons.HITBOXES
                    entity_manager.add_message("Hitboxes " + shared_methods.get_on_off(commons.HITBOXES), (255, 223, 10), outline_colour=(80, 70, 3))

                # Hotbar Item Selection
                if event.key == K_1:
                    entity_manager.client_player.hotbar_index = 0
                if event.key == K_2:
                    entity_manager.client_player.hotbar_index = 1
                if event.key == K_3:
                    entity_manager.client_player.hotbar_index = 2
                if event.key == K_4:
                    entity_manager.client_player.hotbar_index = 3
                if event.key == K_5:
                    entity_manager.client_player.hotbar_index = 4
                if event.key == K_6:
                    entity_manager.client_player.hotbar_index = 5
                if event.key == K_7:
                    entity_manager.client_player.hotbar_index = 6
                if event.key == K_8:
                    entity_manager.client_player.hotbar_index = 7
                if event.key == K_9:
                    entity_manager.client_player.hotbar_index = 8
                if event.key == K_0:
                    entity_manager.client_player.hotbar_index = 9

                if event.key == K_1 or event.key == K_2 or event.key == K_3 or event.key == K_4 or event.key == K_5 or event.key == K_6 or event.key == K_7 or event.key == K_8 or event.key == K_9 or event.key == K_0:
                    entity_manager.client_player.render_current_item_image()
                    entity_manager.client_player.item_swing = False
                    render_hand_text()

                    game_data.play_sound("fg.sound.menu_select")
                
                # Toggle Lighting
                if event.key == K_l:
                    commons.EXPERIMENTALLIGHTING = not commons.EXPERIMENTALLIGHTING
                    entity_manager.add_message("Experimental lighting " + shared_methods.get_on_off(commons.EXPERIMENTALLIGHTING), (255, 223, 10), outline_colour=(80, 70, 3))

                # Toggle Background
                if event.key == K_b:
                    if commons.SHIFT_ACTIVE:
                        commons.BACKGROUND = not commons.BACKGROUND
                        entity_manager.add_message("Background " + shared_methods.get_on_off(commons.BACKGROUND), (255, 223, 10), outline_colour=(80, 70, 3))

                # Music Volume Up
                if event.key == K_UP and commons.SHIFT_ACTIVE:
                    sound_manager.change_music_volume(0.05)
                
                # Music Volume Down
                if event.key == K_DOWN and commons.SHIFT_ACTIVE:
                    sound_manager.change_music_volume(-0.05)
                
                # Sound Volume Up
                if event.key == K_RIGHT and commons.SHIFT_ACTIVE:
                    sound_manager.change_sound_volume(0.05)

                # Sound Volume Down
                if event.key == K_LEFT and commons.SHIFT_ACTIVE:
                    sound_manager.change_sound_volume(-0.05)
                
            # Key up Events
            if event.type == KEYUP:
                if event.key == K_a:
                    entity_manager.client_player.moving_left = False
                if event.key == K_d:
                    entity_manager.client_player.moving_right = False
                if event.key == K_s:
                    entity_manager.client_player.moving_down_tick = 5
                    entity_manager.client_player.stop_moving_down = True
                    entity_manager.client_player.animation_speed = 0.025
                    
            # Hotbar Item and Crafting Scrolling
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    if entity_manager.client_player.inventory_open:
                        entity_manager.client_player.crafting_menu_offset_velocity_y += 200
                    else:
                        if entity_manager.client_player.hotbar_index > 0:
                            entity_manager.client_player.hotbar_index -= 1
                            entity_manager.client_player.render_current_item_image()
                            entity_manager.client_player.item_swing = False
                            render_hand_text()
                            game_data.play_sound("fg.sound.menu_select")
                        else:
                            entity_manager.client_player.hotbar_index = 9

                if event.button == 5:
                    if entity_manager.client_player.inventory_open:
                        entity_manager.client_player.crafting_menu_offset_velocity_y -= 200
                    else:
                        if entity_manager.client_player.hotbar_index < 9:
                            entity_manager.client_player.hotbar_index += 1
                            entity_manager.client_player.render_current_item_image()
                            entity_manager.client_player.item_swing = False
                            render_hand_text()
                            game_data.play_sound("fg.sound.menu_select")
                        else:
                            entity_manager.client_player.hotbar_index = 0

        elif commons.GAME_STATE == "MAINMENU":

            if commons.GAME_SUB_STATE == "PLAYERSELECTION" or commons.GAME_SUB_STATE == "WORLDSELECTION":
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 4:
                        save_select_y_velocity += 3
                    if event.button == 5:
                        save_select_y_velocity -= 3

            elif commons.GAME_SUB_STATE == "PLAYERNAMING" or commons.GAME_SUB_STATE == "WORLDNAMING":
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        commons.TEXT_INPUT = commons.TEXT_INPUT[:-1]
                    elif (len(commons.TEXT_INPUT) <= 15 and commons.GAME_SUB_STATE == "PLAYERNAMING") or (len(commons.TEXT_INPUT) <= 27 and commons.GAME_SUB_STATE == "WORLDNAMING"):
                        commons.TEXT_INPUT += event.unicode
                    
    pygame.display.flip()
    clock.tick(commons.TARGETFPS)
