# entity_manager.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame
import math
import random
from pygame.locals import *

import commons
import game_data
import world

import shared_methods

from player import Player
from enemy import Enemy
from particle import Particle
from projectile import Projectile
from physics_item import PhysicsItem
from colour_picker import ColourPicker
from item import Item


enemies = []
particles = []
projectiles = []
physics_items = []
messages = []
damage_numbers = []
recent_pickups = []

client_player = None
client_prompt = None
client_colour_picker = ColourPicker((int(commons.WINDOW_WIDTH * 0.5 - 155),  190),  300,  300)

camera_position = (0, 0)
old_camera_position = (0, 0)
camera_position_difference = (0, 0)


"""================================================================================================================= 
    entity_manager.create_player -> void

    Sets the client player to a new player instance created with the data in PLAYER_DATA
-----------------------------------------------------------------------------------------------------------------"""


def create_player():
    global client_player
    name = commons.PLAYER_DATA[0]
    model = commons.PLAYER_DATA[1]

    # Load hotbar
    hotbar = [None for _ in range(10)]
    if commons.PLAYER_DATA[2] is not None:
        for loaded_hotbar_index in range(len(commons.PLAYER_DATA[2])):
            loaded_item_data = commons.PLAYER_DATA[2][loaded_hotbar_index]
            item = Item(game_data.get_item_id_by_id_str(loaded_item_data[1]), loaded_item_data[2])
            item.assign_prefix(loaded_item_data[3])
            hotbar[loaded_item_data[0]] = item

    # Load inventory
    inventory = [None for _ in range(40)]
    if commons.PLAYER_DATA[3] is not None:
        for loaded_inventory_index in range(len(commons.PLAYER_DATA[3])):
            loaded_item_data = commons.PLAYER_DATA[3][loaded_inventory_index]
            item = Item(game_data.get_item_id_by_id_str(loaded_item_data[1]), loaded_item_data[2])
            item.assign_prefix(loaded_item_data[3])
            inventory[loaded_item_data[0]] = item

    hp = commons.PLAYER_DATA[4]
    max_hp = commons.PLAYER_DATA[5]
    play_time = commons.PLAYER_DATA[6]
    creation_date = commons.PLAYER_DATA[7]
    last_played_date = commons.PLAYER_DATA[8]
    client_player = Player((0, 0), model, name=name, hotbar=hotbar, inventory=inventory, hp=hp, max_hp=max_hp, play_time=play_time, creation_date=creation_date, last_played_date=last_played_date)


"""================================================================================================================= 
    entity_manager.check_enemy_spawn -> void

    Checks if an enemy needs to spawn around the player
-----------------------------------------------------------------------------------------------------------------"""


def check_enemy_spawn():
    if not commons.PASSIVE:
        if commons.ENEMY_SPAWN_TICK <= 0:
            commons.ENEMY_SPAWN_TICK += 1.0
            val = int(14 - ((client_player.position[1] // commons.BLOCKSIZE) // 30))
            if val < 1:
                val = 1
            if len(enemies) < commons.MAXENEMYSPAWNS + (7 - val * 0.5) and random.randint(1,
                                                                                          val) == 1:  # Reduce enemy spawns
                spawn_enemy()
        else:
            commons.ENEMY_SPAWN_TICK -= commons.DELTA_TIME


"""================================================================================================================= 
    entity_manager.draw_enemy_hover_text -> void

    Checks if an enemy is being hovered over by the mouse, if it is, draw it's name and it's health
-----------------------------------------------------------------------------------------------------------------"""


def draw_enemy_hover_text():
    transformed_mouse_pos = (commons.MOUSE_POS[0] + camera_position[0] - commons.WINDOW_WIDTH * 0.5,
                             commons.MOUSE_POS[1] + camera_position[1] - commons.WINDOW_HEIGHT * 0.5)
    for enemy in enemies:
        if enemy.rect.collidepoint(transformed_mouse_pos):
            text1 = commons.DEFAULTFONT.render(enemy.name + " " + str(math.ceil(enemy.hp)) + "/" + str(enemy.max_hp),
                                               True, (255, 255, 255))
            text2 = commons.DEFAULTFONT.render(enemy.name + " " + str(math.ceil(enemy.hp)) + "/" + str(enemy.max_hp),
                                               True, (0, 0, 0))

            commons.screen.blit(text2, (commons.MOUSE_POS[0] - text2.get_width() * 0.5, commons.MOUSE_POS[1] - 39))
            commons.screen.blit(text2, (commons.MOUSE_POS[0] - text2.get_width() * 0.5, commons.MOUSE_POS[1] - 41))
            commons.screen.blit(text2, (commons.MOUSE_POS[0] - text2.get_width() * 0.5 - 1, commons.MOUSE_POS[1] - 40))
            commons.screen.blit(text2, (commons.MOUSE_POS[0] - text2.get_width() * 0.5 + 1, commons.MOUSE_POS[1] - 40))

            commons.screen.blit(text1, (commons.MOUSE_POS[0] - text1.get_width() * 0.5, commons.MOUSE_POS[1] - 40))
            break


"""================================================================================================================= 
    entity_manager.kill_all_entities -> void

    Kills all entities, used before quitting a world
-----------------------------------------------------------------------------------------------------------------"""


def kill_all_entities():
    enemies.clear()
    particles.clear()
    projectiles.clear()
    physics_items.clear()
    messages.clear()
    damage_numbers.clear()
    recent_pickups.clear()


"""================================================================================================================= 
    Entity Update Functions

    Calls update on every entity in their respective list
-----------------------------------------------------------------------------------------------------------------"""


def update_enemies():
    for enemy in enemies:
        enemy.update()


def update_particles():
    for particle in particles:
        particle.update()


def update_physics_items():
    for physicsItem in physics_items:
        physicsItem.update()


def update_projectiles():
    for projectile in projectiles:
        projectile.update()


def update_messages():
    global messages
    for message in messages:
        message[1] -= commons.DELTA_TIME
        if message[1] <= 0:
            messages.remove(message)


def update_damage_numbers():
    for damageNumber in damage_numbers:
        damageNumber[1] = (damageNumber[1][0] * 0.95, damageNumber[1][1] * 0.95)
        damageNumber[0] = (damageNumber[0][0] + damageNumber[1][0] - camera_position_difference[0], damageNumber[0][1] + damageNumber[1][1] - camera_position_difference[1])
        damageNumber[3] -= commons.DELTA_TIME
        if damageNumber[3] <= 0:
            damage_numbers.remove(damageNumber)


def update_recent_pickups():
    global recent_pickups
    to_remove = []
    for i in range(len(recent_pickups)):
        recent_pickups[i][5] -= commons.DELTA_TIME
        if recent_pickups[i][5] < 0.5:
            recent_pickups[i][2].set_alpha(recent_pickups[i][5] * 510)
            if recent_pickups[i][5] <= 0:
                to_remove.append(recent_pickups[i])
        for j in range(0, i):
            if i != j:
                # Check if it is colliding with previous messages, if so, move up
                if Rect(recent_pickups[i][3][0], recent_pickups[i][3][1], recent_pickups[i][2].get_width(), recent_pickups[i][2].get_height()).colliderect(Rect(recent_pickups[j][3][0], recent_pickups[j][3][1], recent_pickups[j][2].get_width(), recent_pickups[j][2].get_height())):
                    recent_pickups[i][4] = (recent_pickups[i][4][0], recent_pickups[i][4][1] - 1 * commons.DELTA_TIME)
                    recent_pickups[i][3] = (recent_pickups[i][3][0], recent_pickups[i][3][1] - 50 * commons.DELTA_TIME)
        drag_factor = 1.0 - commons.DELTA_TIME * 10
        recent_pickups[i][4] = (recent_pickups[i][4][0] * drag_factor, recent_pickups[i][4][1] * drag_factor)
        recent_pickups[i][3] = (recent_pickups[i][3][0] + recent_pickups[i][4][0] * commons.DELTA_TIME * commons.BLOCKSIZE, recent_pickups[i][3][1] + recent_pickups[i][4][1] * commons.DELTA_TIME * commons.BLOCKSIZE)
    for item in to_remove:
        recent_pickups.remove(item)


"""================================================================================================================= 
    Entity Draw Functions

    Calls draw on every entity in their respective list
-----------------------------------------------------------------------------------------------------------------"""


def draw_enemies():
    for enemy in enemies:
        enemy.draw()


def draw_particles():
    for particle in particles:
        particle.draw()


def draw_physics_items():
    for physicsItem in physics_items:
        physicsItem.draw()


def draw_projectiles():
    for projectile in projectiles:
        projectile.draw()


def draw_messages():
    for i in range(len(messages)):
        if messages[i][1] < 1.0:
            messages[i][0].set_alpha((messages[i][1] / 1.0) * 255)
        commons.screen.blit(messages[i][0], (10, commons.WINDOW_HEIGHT - 25 - i * 20))


def draw_damage_numbers():
    for damage_number in damage_numbers:
        if damage_number[3] < 0.5:
            damage_number[2].set_alpha(damage_number[3] * 510)
        surf = damage_number[2].copy()
        surf = shared_methods.rotate_surface(surf, -damage_number[1][0] * 35)
        commons.screen.blit(surf, (damage_number[0][0] - surf.get_width() * 0.5, damage_number[0][1] - surf.get_height() * 0.5))


def draw_recent_pickups():
    for recent_pickup in recent_pickups:
        commons.screen.blit(recent_pickup[2], (recent_pickup[3][0] - recent_pickup[2].get_width() * 0.5 - camera_position[0] + commons.WINDOW_WIDTH * 0.5, recent_pickup[3][1] - camera_position[1] + commons.WINDOW_HEIGHT * 0.5))


"""================================================================================================================= 
    Entity Spawn Functions

    Construct an instance of an entity and append it to their respective list
-----------------------------------------------------------------------------------------------------------------"""


def spawn_enemy(position=None, enemy_id=None):
    if client_player is None:
        return
    if enemy_id is None:
        if client_player.position[1] < 200 * commons.BLOCKSIZE:
            enemy_id = random.randint(0, 1)
        elif client_player.position[1] < 300 * commons.BLOCKSIZE:
            enemy_id = random.randint(1, 2)
        elif client_player.position[1] >= 300 * commons.BLOCKSIZE:
            enemy_id = random.randint(3, 4)
    if position is None:
        player_block_pos = (int(camera_position[0]) // commons.BLOCKSIZE, int(camera_position[1]) // commons.BLOCKSIZE)
        for i in range(500):
            if random.random() < 0.5:
                x = random.randint(player_block_pos[0] - commons.MAX_ENEMY_SPAWN_TILES_X, player_block_pos[0] - commons.MIN_ENEMY_SPAWN_TILES_X)
                if random.random() < 0.5:
                    y = random.randint(player_block_pos[1] - commons.MAX_ENEMY_SPAWN_TILES_Y, player_block_pos[1] - commons.MIN_ENEMY_SPAWN_TILES_Y)
                else:
                    y = random.randint(player_block_pos[1] + commons.MIN_ENEMY_SPAWN_TILES_Y, player_block_pos[1] + commons.MAX_ENEMY_SPAWN_TILES_Y)
            else:
                x = random.randint(player_block_pos[0] + commons.MIN_ENEMY_SPAWN_TILES_X, player_block_pos[0] + commons.MAX_ENEMY_SPAWN_TILES_X)
                if random.random() < 0.5:
                    y = random.randint(player_block_pos[1] - commons.MAX_ENEMY_SPAWN_TILES_Y, player_block_pos[1] - commons.MIN_ENEMY_SPAWN_TILES_Y)
                else:
                    y = random.randint(player_block_pos[1] + commons.MIN_ENEMY_SPAWN_TILES_Y, player_block_pos[1] + commons.MAX_ENEMY_SPAWN_TILES_Y)
            if world.tile_in_map(x, y, width=2):
                if world.world.tile_data[x][y][0] == game_data.air_tile_id:
                    if world.world.tile_data[x - 1][y][0] == game_data.air_tile_id:
                        if world.world.tile_data[x][y - 1][0] == game_data.air_tile_id:
                            if world.world.tile_data[x + 1][y][0] == game_data.air_tile_id:
                                if world.world.tile_data[x][y + 1][0] == game_data.air_tile_id:
                                    enemies.append(Enemy((x * commons.BLOCKSIZE, y * commons.BLOCKSIZE), enemy_id))
                                    return
    else:
        enemies.append(Enemy(position, enemy_id))


def spawn_particle(position, colour, life=2, magnitude=1, size=5, angle=None, spread=math.pi / 4, gravity=0.25, velocity=None, outline=True):
    particles.append(Particle(position, colour, life, magnitude, size, angle, spread, gravity, velocity, outline))


def spawn_physics_item(item, position, velocity=None, pickup_delay=100):
    physics_items.append(PhysicsItem(item, position, velocity, pickup_delay))


def spawn_projectile(position, angle, weapon_item, ammo_item_id, source):
    ammo_item_data = game_data.get_item_by_id(ammo_item_id)

    total_damage = weapon_item.get_attack_damage() + ammo_item_data["@ammo_damage"]
    
    speed = weapon_item.get_ranged_projectile_speed()
    
    knockback = weapon_item.get_knockback() * ammo_item_data["@ammo_knockback_mod"]

    ammo_gravity_mod = ammo_item_data["@ammo_gravity_mod"]
    ammo_drag = ammo_item_data["@ammo_drag"]

    for _ in range(weapon_item.get_ranged_num_projectiles()):
        inaccuracy = 1.0 - weapon_item.get_ranged_accuracy()
        angle += random.random() * inaccuracy - inaccuracy * 0.5
        velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

        is_crit = False
        if random.random() <= weapon_item.get_crit_chance():
            is_crit = True

        # Hack until we have projectile data loaded from the tool
        projectiles.append(Projectile(position, velocity, "Arrow", 0, source, total_damage, knockback,
                                      is_crit, 1, "arrow", gravity=ammo_gravity_mod, drag=ammo_drag))


def add_message(text, colour, life=5, outline_colour=(0, 0, 0)):
    global messages
    text1 = commons.DEFAULTFONT.render(text, False, colour)
    text2 = commons.DEFAULTFONT.render(text, False, outline_colour)
    surf = pygame.Surface((text1.get_width() + 2, text1.get_height() + 2))
    surf.fill((255, 0, 255))
    surf.set_colorkey((255, 0, 255))
    if commons.FANCYTEXT:
        surf.blit(text2, (0, 1))
        surf.blit(text2, (2, 1))
        surf.blit(text2, (1, 0))
        surf.blit(text2, (1, 2))

    surf.blit(text1, (1, 1))
    messages.insert(0, [surf, life])


def add_damage_number(pos, val, crit=False, colour=None):
    global damage_numbers

    if colour is None:
        if crit:
            colour = (246, 97, 28)
        else:
            colour = (207, 127, 63)

    t1 = commons.DEFAULTFONT.render(str(int(val)), False, colour)
    t2 = commons.DEFAULTFONT.render(str(int(val)), False, (colour[0] * 0.8, colour[1] * 0.8, colour[2] * 0.8))

    width = t1.get_width() + 2
    height = t1.get_height() + 2

    if width > height:
        size = width
    else:
        size = height

    surf = pygame.Surface((size, size))
    surf.fill((255, 0, 255))
    surf.set_colorkey((255, 0, 255))

    midx = size * 0.5 - width * 0.5
    midy = size * 0.5 - height * 0.5

    if commons.FANCYTEXT:
        surf.blit(t2, (midx, midy))
        surf.blit(t2, (midx + 2, midy))
        surf.blit(t2, (midx + 1, midy - 1))
        surf.blit(t2, (midx + 1, midy + 1))

    surf.blit(t1, (midx, midy))

    damage_numbers.append([(pos[0] - camera_position[0] + commons.WINDOW_WIDTH * 0.5,
                            pos[1] - camera_position[1] + commons.WINDOW_HEIGHT * 0.5),
                           (random.random() * 4 - 2, -1 - random.random() * 4), surf, 1.5])


def add_recent_pickup(item_id, amnt, tier, pos, unique=False, item=None):
    global recent_pickups
    if not unique:
        for recent_pickup in recent_pickups:
            if recent_pickup[0] == item_id:
                amnt += recent_pickup[1]
                recent_pickups.remove(recent_pickup)
    if amnt > 1:
        string = game_data.xml_item_data[item_id]["@name"] + "(" + str(amnt) + ")"
    else:
        if item is not None:
            string = item.get_name()
        else:
            string = game_data.xml_item_data[item_id]["@name"]
    size = commons.DEFAULTFONT.size(string)
    size = (size[0] + 2, size[1] + 2)
    surf = pygame.Surface(size)
    surf.set_colorkey((255, 0, 255))
    surf.fill((255, 0, 255))
    surf.blit(shared_methods.outline_text(string, shared_methods.get_tier_colour(tier), commons.DEFAULTFONT), (1, 1))
    vel = (random.random() * 2 - 1, -50.0)
    recent_pickups.append([item_id, amnt, surf, pos, vel, 3.0])
