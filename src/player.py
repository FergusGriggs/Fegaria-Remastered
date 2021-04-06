# player.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame
import math
import random
import pickle
import datetime
from pygame.locals import *

import game_data
from game_data import *

import commons
import world

import shared_methods
import surface_manager
import entity_manager

from item import *


"""=================================================================================================================
    player.get_death_message -> string
    
    Uses the player's name, the thing that killed them, and the worlds name to generate a random death message
-----------------------------------------------------------------------------------------------------------------"""
def get_death_message(name, source):
    string = game_data.death_lines[source[0]][random.randint(0, len(game_data.death_lines[source[0]]) - 1)]
    string = string.replace("<p>", name)
    string = string.replace("<w>", world.world.name)
    string = string.replace("<e>", source[1])
    return string


"""================================================================================================================= 
    player.update_player_model_using_model_data -> void
    
    Transfers the data stored in PLAYER_MODEL_DATA to PLAYER_MODEL
-----------------------------------------------------------------------------------------------------------------"""
def update_player_model_using_model_data():
    commons.PLAYER_MODEL.sex = commons.PLAYER_MODEL_DATA[0]
    commons.PLAYER_MODEL.hair_id = commons.PLAYER_MODEL_DATA[1]
    commons.PLAYER_MODEL.skin_col = commons.PLAYER_MODEL_DATA[2][0]
    commons.PLAYER_MODEL.hair_col = commons.PLAYER_MODEL_DATA[3][0]
    commons.PLAYER_MODEL.eye_col = commons.PLAYER_MODEL_DATA[4][0]
    commons.PLAYER_MODEL.shirt_col = commons.PLAYER_MODEL_DATA[5][0]
    commons.PLAYER_MODEL.under_shirt_col = commons.PLAYER_MODEL_DATA[6][0]
    commons.PLAYER_MODEL.trouser_col = commons.PLAYER_MODEL_DATA[7][0]
    commons.PLAYER_MODEL.shoe_col = commons.PLAYER_MODEL_DATA[8][0]


"""================================================================================================================= 
    player.Model
    
    Stores information about the appearance of a player
-----------------------------------------------------------------------------------------------------------------"""
class Model:
    def __init__(self, sex, hair_id, skin_col, hair_col, eye_col, shirt_col, under_shirt_col, trouser_col, shoe_col):
        self.sex = sex
        self.hair_id = hair_id
        self.skin_col = skin_col
        self.hair_col = hair_col
        self.eye_col = eye_col
        self.shirt_col = shirt_col
        self.under_shirt_col = under_shirt_col
        self.trouser_col = trouser_col
        self.shoe_col = shoe_col


"""================================================================================================================= 
    player.Player
    
    Performs physics and renders a player within the current world
-----------------------------------------------------------------------------------------------------------------"""
class Player:
    def __init__(self, position, model, name="unassigned", hp=0, max_hp=100, hotbar=None, inventory=None, play_time=0, creation_date=None, last_played_date=None):
        self.position = position
        self.block_position = (0, 0)
        self.model = model
        self.name = name

        # Set hp bits
        if hp == 0:
            self.hp = max_hp
        else:
            self.hp = hp
        self.max_hp = max_hp

        self.items = {
            ItemLocation.HOTBAR: [None for _ in range(10)],
            ItemLocation.INVENTORY: [None for _ in range(40)],
            ItemLocation.CHEST: [None for _ in range(20)],
            ItemLocation.CRAFTING_MENU: [],
        }

        # Set hotbar info
        if hotbar is None:
            self.items[ItemLocation.HOTBAR] = [
                Item(game_data.get_item_id_by_id_str("fg.item.pickaxe_copper"), auto_assign_prefix=True),
                Item(game_data.get_item_id_by_id_str("fg.item.stone"), amnt=100),
                None, None, None, None, None, None, None, None
            ]
        else:
            self.items[ItemLocation.HOTBAR] = hotbar
        self.hotbar_index = 0

        # Inventory setup
        if inventory is None:
            self.items[ItemLocation.INVENTORY] = [None for _ in range(40)]
        else:
            self.items[ItemLocation.INVENTORY] = inventory

        # Save stats
        self.play_time = play_time

        date = datetime.datetime.now()

        if creation_date is None:
            self.creation_date = date
        else:
            self.creation_date = creation_date

        if last_played_date is None:
            self.last_played_date = date
        else:
            self.last_played_date = last_played_date

        self.rect = Rect(self.position[0] - commons.PLAYER_WIDTH * 0.5, self.position[1] - commons.PLAYER_HEIGHT * 0.5, commons.PLAYER_WIDTH, commons.PLAYER_HEIGHT)  # hitbox
        self.velocity = (0, 0)

        sprites = render_sprites(self.model)

        self.sprites = sprites[0]
        self.arm_sprites = sprites[1]

        self.animation_tick = 0
        self.animation_frame = 5
        self.animation_speed = 0.025

        self.arm_animation_frame = 0
        self.arm_animation_tick = 0
        self.arm_animation_speed = 0.015
        
        self.alive = True
        self.respawn_tick = 0

        self.invincible_timer = 2.0
        self.invincible = True

        hp_text_colour = (255 * (1 - self.hp / self.max_hp), 255 * (self.hp / self.max_hp), 0)
        self.hp_text = shared_methods.outline_text(str(self.hp), hp_text_colour, commons.DEFAULTFONT, outline_colour=(hp_text_colour[0] * 0.5, hp_text_colour[1] * 0.5, hp_text_colour[2] * 0.5))
        self.hp_x_position = commons.WINDOW_WIDTH - 10 - self.hp - self.hp_text.get_width() * 0.5

        self.grounded = True

        self.moving_left = False
        self.moving_right = False

        self.moving_down = False
        self.moving_down_tick = 0
        self.stop_moving_down = False

        self.stop_left = False
        self.stop_right = False

        self.direction = 1

        self.swinging_arm = False
        self.should_swing_arm = False
        
        self.last_block_on = 0

        self.knockback_resist = 0
        self.defense = 0

        self.use_tick = 0
        self.use_delay = 0
        self.use_delta = 0
        self.can_use = False
        self.arm_out = False
        self.arm_out_angle = 0
        self.swing_angle = 0
        self.item_swing = False
        self.current_item_image = None
        self.current_item_swing_image = None
        self.current_item_swing_offset = 0
        self.enemies_hit = []

        self.un_pickupable_items = []

        self.hotbar_image = pygame.Surface((480, 48))
        self.hotbar_image.set_colorkey((255, 0, 255))

        self.inventory_image = pygame.Surface((480, 192))
        self.inventory_image.set_colorkey((255, 0, 255))

        self.chest_image = pygame.Surface((240, 192))
        self.chest_image.set_colorkey((255, 0, 255))

        self.blit_craft_surf = pygame.Surface((48, 288))
        self.blit_craft_surf.set_colorkey((255, 0, 255))

        self.craftable_items_surf = pygame.Surface((48, 0))

        self.crafting_menu_offset_y = 120
        self.crafting_menu_offset_velocity_y = 0

        self.inventory_open = False
        self.chest_open = False

        self.old_inventory_positions = []

    """================================================================================================================= 
        player.Player.update -> void
        
        Updates many variables within the player object
    -----------------------------------------------------------------------------------------------------------------"""
    def update(self):
        if self.alive:
            if self.invincible:
                if self.invincible_timer <= 0.0:
                    self.invincible = False
                else:
                    self.invincible_timer -= commons.DELTA_TIME
        
            if self.moving_left:  # moves player left
                if not self.stop_left:
                    if self.moving_down:
                        self.velocity = (-5, self.velocity[1])
                    else:
                        self.velocity = (-12, self.velocity[1])
            if self.moving_right:  # moves player right
                if not self.stop_right:
                    if self.moving_down:
                        self.velocity = (5, self.velocity[1])
                    else:
                        self.velocity = (12, self.velocity[1])

            drag_factor = 1.0 - commons.DELTA_TIME

            self.velocity = (self.velocity[0] * drag_factor, self.velocity[1] * drag_factor + commons.GRAVITY * commons.DELTA_TIME)
            self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE)

            self.rect.left = self.position[0] - commons.PLAYER_WIDTH * 0.5  # updating rect
            self.rect.top = self.position[1] - commons.PLAYER_HEIGHT * 0.5

            self.block_position = (math.floor(self.position[1] // commons.BLOCKSIZE), math.floor(self.position[0] // commons.BLOCKSIZE))

            self.grounded = False

            self.stop_left = False
            self.stop_right = False

            fall_damaged = False  # so fall damage is only applied once
            
            if not self.can_use:
                if self.use_tick > self.use_delay:
                    self.arm_out = False
                    self.can_use = True
                    self.item_swing = False
                    self.swinging_arm = False
                else:
                    self.use_tick += commons.DELTA_TIME
                    if self.use_delay > 0.0001:
                        self.use_delta = self.use_tick / self.use_delay
            
            if self.velocity[0] < 0:
                if self.position[0] < world.border_left:
                    self.position = (int(world.border_left), self.position[1])
            elif self.velocity[0] > 0:
                if self.position[0] > world.border_right:
                    self.position = (int(world.border_right), self.position[1])
            if self.velocity[1] < 0:
                if self.position[1] < world.border_up:
                    self.position = (self.position[0], int(world.border_up))
                    self.velocity = (self.velocity[0], 0)
            elif self.velocity[1] > 0:
                if self.position[1] > world.border_down:
                    self.position = (self.position[0], int(world.border_down))
                    self.velocity = (self.velocity[0], 0)
                    self.grounded = True

            if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                use = False
                if self.inventory_open:
                    if not Rect(5, 5, 480, 244).collidepoint(commons.MOUSE_POS) and not Rect(commons.WINDOW_WIDTH - 50, commons.WINDOW_HEIGHT - 20, 50, 20).collidepoint(commons.MOUSE_POS) and not Rect(5, 270, 48, 288).collidepoint(commons.MOUSE_POS):
                        if self.chest_open:
                            if not Rect(245, 265, 240, 192).collidepoint(commons.MOUSE_POS):
                                use = True
                        else:
                            use = True
                else:
                    use = True
                if use and entity_manager.client_prompt is None and not commons.WAIT_TO_USE:
                    if pygame.mouse.get_pressed()[0]:
                        self.use_item()
                    elif pygame.mouse.get_pressed()[2]:
                        self.use_item(right_click=True)

            collide = False

            for j in range(-2, 3):
                for i in range(-2, 3):
                    if world.tile_in_map(self.block_position[1] + j, self.block_position[0] + i):
                        if self.block_position[1] + j >= 0:
                            tile_id = world.world.tile_data[self.block_position[1] + j][self.block_position[0] + i][0]
                            tile_data = game_data.get_tile_by_id(tile_id)
                            if TileTag.NOCOLLIDE not in tile_data["@tags"]:
                                block_rect = Rect(commons.BLOCKSIZE * (self.block_position[1] + j), commons.BLOCKSIZE * (self.block_position[0] + i), commons.BLOCKSIZE, commons.BLOCKSIZE)
                                is_platform = False
                                if TileTag.PLATFORM in tile_data["@tags"]:
                                    is_platform = True
                                    if block_rect.colliderect(int(self.rect.left - 1), int(self.rect.top + 2), 1, int(self.rect.height - 4)):
                                        self.stop_left = True  # is there a solid block left
                                    if block_rect.colliderect(int(self.rect.right + 1), int(self.rect.top + 2), 1, int(self.rect.height - 4)):
                                        self.stop_right = True  # is there a solid block right
                                if block_rect.colliderect(self.rect):
                                    if tile_id == 258:
                                        self.damage(5, ["spike", "World"])

                                    delta_x = self.position[0] - block_rect.centerx
                                    delta_y = self.position[1] - block_rect.centery
                                    if abs(delta_x) > abs(delta_y):
                                        if delta_x > 0:
                                            if not is_platform:
                                                self.position = (block_rect.right + commons.PLAYER_WIDTH * 0.5, self.position[1])  # Move player right
                                                self.velocity = (0, self.velocity[1])  # Stop player horizontally
                                        else:
                                            if not is_platform:
                                                self.position = (block_rect.left - commons.PLAYER_WIDTH * 0.5, self.position[1])  # Move player left
                                                self.velocity = (0, self.velocity[1])  # Stop player horizontally
                                    else:
                                        if delta_y > 0:
                                            if self.velocity[1] < 0:
                                                if not is_platform:
                                                    if Rect(self.rect.left + 3, self.rect.top, self.rect.width - 6, self.rect.height).colliderect(block_rect):
                                                        self.position = (self.position[0], block_rect.bottom + commons.PLAYER_HEIGHT * 0.5)  # Move player down
                                                        self.velocity = (self.velocity[0], 0)  # Stop player vertically
                                        else:
                                            if self.velocity[1] > 0:
                                                if Rect(self.rect.left + 3, self.rect.top, self.rect.width - 6, self.rect.height).colliderect(block_rect):
                                                    if is_platform:
                                                        if self.moving_down:
                                                            collide = False
                                                        else:
                                                            if self.velocity[1] < 5:
                                                                if self.position[1] + commons.BLOCKSIZE < block_rect.top:
                                                                    collide = True
                                                            else:
                                                                collide = True
                                                    else:
                                                        collide = True
                                                    if collide:
                                                        if not fall_damaged:
                                                            if self.velocity[1] > 58:
                                                                damage = int((self.velocity[1] - 57) ** 2)  # Work out fall damage
                                                                self.damage(damage, ["falling", "World"])  # Apply fall damage once
                                                                fall_damaged = True
                                                        self.last_block_on = int(tile_id)
                                                        self.moving_down_tick = -1
                                                        self.position = (self.position[0], block_rect.top - commons.PLAYER_HEIGHT * 0.5 + 1)  # Move player up
                                                        self.velocity = (self.velocity[0] * 0.5, 0)  # Slow down player horizontally and stop player vertically
                                                        self.grounded = True

            if self.stop_moving_down:  # Wait before setting moving_down to false based on player y velocity
                if self.moving_down_tick < 0:
                    self.moving_down = False
                    self.stop_moving_down = False
                else:
                    self.moving_down_tick -= self.velocity[1]

            if self.inventory_open:
                self.crafting_menu_offset_velocity_y *= 1.0 - commons.DELTA_TIME * 10
                self.crafting_menu_offset_y += self.crafting_menu_offset_velocity_y * commons.DELTA_TIME
                if self.crafting_menu_offset_y < -len(self.items[ItemLocation.CRAFTING_MENU]) * 48 + 168:
                    self.crafting_menu_offset_y = -len(self.items[ItemLocation.CRAFTING_MENU]) * 48 + 168
                elif self.crafting_menu_offset_y > 120:
                    self.crafting_menu_offset_y = 120

        else:  # if player is not alive, wait to respawn
            if self.respawn_tick > 0:
                self.respawn_tick -= commons.DELTA_TIME
            else:
                self.respawn()

        self.update_inventory_old_slots()

    """================================================================================================================= 
        player.Player.damage -> void
        
        Kills the player, adds a death message, spawns particles, plays a sound
    -----------------------------------------------------------------------------------------------------------------"""
    def damage(self, value, source_name, knockback=0, direction=None, source_velocity=None):
        if not commons.CREATIVE and self.alive and not self.invincible:
            self.invincible = True
            self.invincible_timer = 0.35

            value -= self.defense
            value += random.randint(-1, 1)
            if value < 1:
                value = 1
            self.hp -= value

            entity_manager.add_damage_number(self.position, value, colour=(240, 20, 20))

            if self.hp < 0:
                self.hp = 0

            if self.hp > 0:  # check if the player has died from damage
                game_data.play_sound("fg.sound.player_hurt")  # random hurt sound

                if commons.PARTICLES:
                    if source_velocity is not None:
                        velocity_angle = math.atan2(self.velocity[1] + source_velocity[0], self.velocity[0] + source_velocity[1])
                        velocity_magnitude = math.sqrt((self.velocity[0] + source_velocity[0]) ** 2 + (self.velocity[1] + source_velocity[1]) ** 2)
                    else:
                        velocity_angle = math.atan2(self.velocity[1], self.velocity[0])
                        velocity_magnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

                    for i in range(int(10 * commons.PARTICLEDENSITY)):  # blood
                        particle_pos = (self.position[0] + random.random() * commons.PLAYER_WIDTH - commons.PLAYER_WIDTH * 0.5, self.position[1] + random.random() * commons.PLAYER_HEIGHT - commons.PLAYER_HEIGHT * 0.5)
                        entity_manager.spawn_particle(particle_pos, (230, 0, 0), life=1, size=10, angle=velocity_angle, spread=math.pi * 0.2, magnitude=random.random() * velocity_magnitude, gravity=0.15, outline=False)
            else:
                self.kill(source_name, source_velocity)

            if knockback != 0:
                remaining_knockback = max(0, knockback - self.knockback_resist)
                self.velocity = (self.velocity[0] + direction * remaining_knockback, remaining_knockback * -1.5)

        hp_float = self.hp / self.max_hp
        self.hp_text = shared_methods.outline_text(str(self.hp), ((1 - hp_float) * 255, hp_float * 255, 0), commons.DEFAULTFONT, outline_colour=((1 - hp_float) * 180, hp_float * 180, 0))
        self.hp_x_position = commons.WINDOW_WIDTH - 10 - hp_float * 100 - self.hp_text.get_width() * 0.5

    """================================================================================================================= 
        player.Player.kill -> void
        
        Kills the player, adds a death message, spawns particles, plays a sound
    -----------------------------------------------------------------------------------------------------------------"""
    def kill(self, source, source_velocity=None):
        if self.alive:
            self.alive = False
            self.respawn_tick = 5.0  # respawn delay
            self.velocity = (0, 0)

            entity_manager.add_message(get_death_message(self.name, source), (255, 255, 255))

            if commons.PARTICLES:
                if source_velocity is not None:
                    self.velocity = (self.velocity[0] + source_velocity[0], self.velocity[1] + source_velocity[1])

                velocity_angle = math.atan2(self.velocity[1], self.velocity[0])
                velocity_magnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

                for i in range(int(35 * commons.PARTICLEDENSITY)):  # more blood
                    entity_manager.spawn_particle((self.position[0] + random.random() * commons.PLAYER_WIDTH - commons.PLAYER_WIDTH * 0.5,
                                                  self.position[1] + random.random() * commons.PLAYER_HEIGHT - commons.PLAYER_HEIGHT * 0.5),
                                                  (230, 0, 0), life=1, angle=velocity_angle, size=10, spread=0.9,
                                                  magnitude=random.random() * velocity_magnitude * 0.8, gravity=0.15, outline=False)
            game_data.play_sound("fg.sound.player_death")  # death sound

    """================================================================================================================= 
        player.Player.respawn -> void
        
        Sets the player's position to the world's spawn point and resets some variables
    -----------------------------------------------------------------------------------------------------------------"""
    def respawn(self):
        self.position = tuple(world.world.spawn_position)  # set position to world.world.spawn_point
        self.velocity = (0, 0)
        self.alive = True
        self.hp = int(self.max_hp)  # reset hp
        self.hp_text = shared_methods.outline_text(str(self.hp), (0, 255, 0), commons.DEFAULTFONT, outline_colour=(0, 180, 0))
        self.hp_x_position = commons.WINDOW_WIDTH - 10 - 100 - self.hp_text.get_width() * 0.5

    """================================================================================================================= 
        player.Player.render_current_item_image -> void
        
        Renders the item that the player is currently holding to the current_item_image surface
    -----------------------------------------------------------------------------------------------------------------"""
    def render_current_item_image(self):
        if not commons.IS_HOLDING_ITEM:
            item = self.items[ItemLocation.HOTBAR][self.hotbar_index]
        else:
            item = commons.ITEM_HOLDING
        if item is not None:
            self.current_item_image = item.get_image()

            # Item swing surface
            swing_surface = self.current_item_image
            if item.has_tag(ItemTag.WEAPON):
                world_override_image = item.get_world_override_image()
                if world_override_image is not None:
                    swing_surface = world_override_image

            item_scale = item.get_scale()
            inner_dimensions = (int(swing_surface.get_width() * item_scale),
                                int(swing_surface.get_height() * item_scale))
            scaled_surface = pygame.transform.scale(swing_surface, inner_dimensions)
            scaled_surface.set_colorkey()
            padded_dimensions = (int(inner_dimensions[0] * 1.414), int(inner_dimensions[1] * 1.414))
            padded_surface = pygame.Surface(padded_dimensions)
            padded_surface.fill((255, 0, 255))
            padded_surface.blit(scaled_surface, (int(padded_dimensions[0] * 0.5 - inner_dimensions[0] * 0.5),
                                                 int(padded_dimensions[1] * 0.5 - inner_dimensions[1] * 0.5)))
            padded_surface.set_colorkey((255, 0, 255))
            self.current_item_swing_image = padded_surface
            self.current_item_swing_offset = math.sqrt((inner_dimensions[0] * 0.5) ** 2 + (inner_dimensions[1] * 0.5) ** 2) * 0.8

    """================================================================================================================= 
        player.Player.animate -> void
        
        Primarily updates the player's animation_frame and arm_animation_frame
    -----------------------------------------------------------------------------------------------------------------"""
    def animate(self):
        if self.animation_tick <= 0:  # Happens every 'animation_speed' frames
            self.animation_tick += self.animation_speed
            if self.grounded:
                if self.moving_left:  # If moving left, cycle through left frames
                    if self.animation_frame < 29:
                        self.animation_frame += 1
                    else:
                        self.animation_frame = 17
                    return
                elif self.moving_right:  # If moving right, cycle through right frames
                    if self.animation_frame < 14:
                        self.animation_frame += 1
                    else:
                        self.animation_frame = 2
                    return
                else:  # If idle put arms down
                    if self.direction == 0:
                        self.animation_frame = 15
                    elif self.direction == 1:
                        self.animation_frame = 0
            else:  # Puts arms in the air if not grounded
                if self.direction == 0:
                    self.animation_frame = 16
                elif self.direction == 1:
                    self.animation_frame = 1
        else:
            self.animation_tick -= commons.DELTA_TIME

        if self.arm_animation_tick <= 0:
            self.arm_animation_tick += self.arm_animation_speed

            if self.swinging_arm:
                if self.direction == 1:
                    self.arm_animation_frame = math.floor(min(4, 1 + self.use_delta * 4))
                else:
                    self.arm_animation_frame = math.floor(min(24, 21 + self.use_delta * 4))

            else:
                if self.grounded:
                    if self.moving_left:  # If moving left, cycle through left frames
                        if self.arm_animation_frame < 38:
                            self.arm_animation_frame += 1
                        else:
                            self.arm_animation_frame = 26
                        return
                    elif self.moving_right:  # If moving right, cycle through right frames
                        if self.arm_animation_frame < 18:
                            self.arm_animation_frame += 1
                        else:
                            self.arm_animation_frame = 6
                        return
                    else:  # If idle put arms down
                        if self.direction == 0:
                            self.arm_animation_frame = 20
                        elif self.direction == 1:
                            self.arm_animation_frame = 0
                else:  # Puts arms in the air if not grounded
                    if self.direction == 0:
                        self.arm_animation_frame = 25
                    elif self.direction == 1:
                        self.arm_animation_frame = 5
        else:
            self.arm_animation_tick -= commons.DELTA_TIME

        if self.arm_out:
            if self.direction == 1:
                self.arm_animation_frame = 19
            else:
                self.arm_animation_frame = 39

    """================================================================================================================= 
        player.Player.use_item -> void
        
        Gets the item that the player is holding and calls the correct use function
    -----------------------------------------------------------------------------------------------------------------"""

    def use_item(self, right_click=False):
        item = None

        if commons.IS_HOLDING_ITEM:
            item = commons.ITEM_HOLDING
        elif not self.inventory_open:
            item = self.items[ItemLocation.HOTBAR][self.hotbar_index]

        if item is None and not right_click:
            return

        screen_position_x = self.position[0] - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5
        screen_position_y = self.position[1] - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5

        if not right_click:
            self.should_swing_arm = False

            if item.has_tag(ItemTag.TILE):
                self.place_block(screen_position_x, screen_position_y, item, True)

            if item.has_tag(ItemTag.WALL):
                self.place_block(screen_position_x, screen_position_y, item, False)

            elif item.has_tag(ItemTag.PICKAXE) or item.has_tag(ItemTag.HAMMER) or item.has_tag(ItemTag.AXE):
                self.use_tool(screen_position_x, screen_position_y, item)

            elif item.has_tag(ItemTag.MELEE):
                self.use_melee_weapon(item)

            elif item.has_tag(ItemTag.RANGED):
                self.use_ranged_weapon(screen_position_x, screen_position_y, item)

            if self.should_swing_arm:
                if not self.swinging_arm:
                    self.swinging_arm = True
                    if self.direction == 1:
                        self.arm_animation_frame = 1
                    else:
                        self.arm_animation_frame = 20

        else:
            if math.sqrt((screen_position_x - commons.MOUSE_POS[0]) ** 2 + (screen_position_y - commons.MOUSE_POS[1]) ** 2) < commons.BLOCKSIZE * commons.PLAYER_REACH or commons.CREATIVE:
                block_position = commons.TILE_POSITION_MOUSE_HOVERING
                tile_dat = world.world.tile_data[block_position[0]][block_position[1]]
                xml_tile_data = game_data.get_tile_by_id(tile_dat[0])
                if TileTag.CHEST in xml_tile_data["@tags"] or TileTag.CYCLABLE in xml_tile_data["@tags"] or TileTag.CRAFTINGTABLE in xml_tile_data["@tags"]:
                    if TileTag.MULTITILE in xml_tile_data["@tags"]:
                        origin = block_position[0] - tile_dat[2][0], block_position[1] - tile_dat[2][1]
                    else:
                        origin = block_position
                    world.use_special_tile(origin[0], origin[1])

    """================================================================================================================= 
        player.Player.place_block -> void
        
        Uses a screen position and a block item to place a block in the world
    -----------------------------------------------------------------------------------------------------------------"""
    def place_block(self, screen_position_x, screen_position_y, block_item, is_tile):
        if math.sqrt((screen_position_x - commons.MOUSE_POS[0]) ** 2 + (screen_position_y - commons.MOUSE_POS[1]) ** 2) < commons.BLOCKSIZE * commons.PLAYER_REACH or commons.CREATIVE:
            block_position = commons.TILE_POSITION_MOUSE_HOVERING
            if world.tile_in_map(block_position[0], block_position[1]):

                block_rect = Rect(commons.BLOCKSIZE * block_position[0], commons.BLOCKSIZE * block_position[1] + 1, commons.BLOCKSIZE, commons.BLOCKSIZE)
                
                if not block_rect.colliderect(self.rect):
                    
                    block_placed = False

                    if is_tile:
                        tile_to_place = game_data.get_tile_by_id_str(block_item.get_tile_id_str())

                        if TileTag.MULTITILE in tile_to_place["@tags"]:
                            can_place = True

                            tile_dimensions = tile_to_place["@multitile_dimensions"]

                            for x in range(tile_dimensions[0]):
                                for y in range(tile_dimensions[1]):
                                    if not world.world.tile_data[block_position[0] + x][block_position[1] + y][0] == game_data.air_tile_id:
                                        can_place = False

                            required_solids = tile_to_place["@multitile_required_solids"]

                            for i in range(len(required_solids)):
                                tile_id = world.world.tile_data[block_position[0] + required_solids[i][0]][block_position[1] + required_solids[i][1]][0]
                                tile_data = game_data.get_tile_by_id(tile_id)
                                if TileTag.NOCOLLIDE in tile_data["@tags"]:
                                    can_place = False

                            if can_place:
                                world.place_multitile(block_position[0], block_position[1], tile_dimensions, tile_to_place["@id"], True)

                                if TileTag.CHEST in tile_to_place["@tags"]:
                                    world.world.chest_data.append([block_position, [None for _ in range(20)]])

                                block_placed = True

                                game_data.play_tile_place_sfx(tile_to_place["@id"])

                        else:
                            if world.world.tile_data[block_position[0]][block_position[1]][0] == game_data.air_tile_id:
                                if world.get_neighbor_count(block_position[0], block_position[1]) > 0:
                                    world.world.tile_data[block_position[0]][block_position[1]][0] = tile_to_place["@id"]

                                    if world.tile_in_map(block_position[0], block_position[1] + 1):
                                        if game_data.get_tile_by_id(world.world.tile_data[block_position[0]][block_position[1]][0])["@id_str"] == "fg.tile.grass":
                                            world.world.tile_data[block_position[0]][block_position[1]][0] = game_data.get_tile_id_by_id_str("fg.tile.dirt")

                                    world.update_terrain_surface(block_position[0], block_position[1])

                                    game_data.play_tile_place_sfx(tile_to_place["@id"])
                                    block_placed = True
                    else:
                        if world.world.tile_data[block_position[0]][block_position[1]][1] == game_data.air_wall_id:
                            if world.get_neighbor_count(block_position[0], block_position[1], tile=1) > 0:
                                wall_to_place = game_data.get_wall_by_id_str(block_item.get_wall_id_str())

                                world.world.tile_data[block_position[0]][block_position[1]][1] = int(wall_to_place["@id"])
                                world.update_terrain_surface(block_position[0], block_position[1])

                                game_data.play_wall_place_sfx(wall_to_place["@id"])

                                block_placed = True

                    if block_placed:
                        self.should_swing_arm = True
                        self.item_swing = True
                        self.use_delay = 0.2
                        self.use_tick = 0
                        self.use_delta = 0.0
                        self.can_use = False
                        if not commons.CREATIVE:
                            if not commons.IS_HOLDING_ITEM:
                                self.items[ItemLocation.HOTBAR][self.hotbar_index].amnt -= 1
                                dat = [ItemLocation.HOTBAR, self.hotbar_index]
                                if dat not in self.old_inventory_positions:
                                    self.old_inventory_positions.append(dat)
                                if self.items[ItemLocation.HOTBAR][self.hotbar_index].amnt <= 0:
                                    self.items[ItemLocation.HOTBAR][self.hotbar_index] = None
                            else:
                                commons.WAIT_TO_USE = True
                                commons.ITEM_HOLDING.amnt -= 1
                                if commons.ITEM_HOLDING.amnt <= 0:
                                    commons.ITEM_HOLDING = None
                                    commons.IS_HOLDING_ITEM = False

    """================================================================================================================= 
        player.Player.use_pickaxe -> void
        
        Uses a screen position and a pickaxe item to mine a block in the world
    -----------------------------------------------------------------------------------------------------------------"""
    def use_tool(self, screen_position_x, screen_position_y, tool_item):
        if self.can_use or commons.CREATIVE:
            self.enemies_hit = []
            self.can_use = False
            self.use_tick = 0
            self.use_delta = 0.0
            self.use_delay = tool_item.get_attack_speed() * 0.01
            self.should_swing_arm = True
            self.item_swing = True

            game_data.play_sound("fg.sound.swing")

            if math.sqrt((screen_position_x - commons.MOUSE_POS[0]) ** 2 + (screen_position_y - commons.MOUSE_POS[1]) ** 2) < commons.BLOCKSIZE * commons.PLAYER_REACH or commons.CREATIVE:
                block_position = commons.TILE_POSITION_MOUSE_HOVERING
                if world.tile_in_map(block_position[0], block_position[1]):
                    if tool_item.has_tag(ItemTag.PICKAXE):
                        tile_id = world.world.tile_data[block_position[0]][block_position[1]][0]
                        tile_dat = game_data.get_tile_by_id(tile_id)
                        if TileTag.MULTITILE in tile_dat["@tags"]:
                            multitile_origin = world.get_multitile_origin(block_position[0], block_position[1])
                            world.remove_multitile(multitile_origin, True)
                            game_data.play_tile_hit_sfx(tile_id)
                        else:
                            if tile_id != game_data.air_tile_id:
                                item_id = game_data.get_item_id_by_id_str(tile_dat["@item_id_str"])
                                # Remove Grass from dirt
                                if tile_id == game_data.grass_tile_id:
                                    world.world.tile_data[block_position[0]][block_position[1]][0] = game_data.get_tile_id_by_id_str("fg.tile.dirt")
                                else:
                                    world.world.tile_data[block_position[0]][block_position[1]][0] = game_data.air_tile_id

                                    entity_manager.spawn_physics_item(Item(item_id), ((block_position[0] + 0.5) * commons.BLOCKSIZE, (block_position[1] + 0.5) * commons.BLOCKSIZE), pickup_delay=10)
                                world.update_terrain_surface(block_position[0], block_position[1])
                                colour = tile_dat["@average_colour"]

                                game_data.play_tile_hit_sfx(tile_id)
                                if commons.PARTICLES:
                                    for i in range(int(random.randint(2, 3) * commons.PARTICLEDENSITY)):
                                        entity_manager.spawn_particle((block_position[0] * commons.BLOCKSIZE + commons.BLOCKSIZE * 0.5, block_position[1] * commons.BLOCKSIZE + commons.BLOCKSIZE * 0.5), colour, size=13, life=1, angle=-math.pi * 0.5, spread=math.pi, gravity=0.05)

                    elif tool_item.has_tag(ItemTag.HAMMER):
                        wall_id = world.world.tile_data[block_position[0]][block_position[1]][1]
                        if wall_id != game_data.air_wall_id:
                            if world.get_neighbor_count(block_position[0], block_position[1], tile=1, check_centre_tile=False, check_centre_wall=False) < 4:
                                wall_dat = game_data.get_wall_by_id(wall_id)

                                item_id = game_data.get_item_id_by_id_str(wall_dat["@item_id_str"])
                                entity_manager.spawn_physics_item(Item(item_id), ((block_position[0] + 0.5) * commons.BLOCKSIZE, (block_position[1] + 0.5) * commons.BLOCKSIZE), pickup_delay=10)

                                world.world.tile_data[block_position[0]][block_position[1]][1] = game_data.air_wall_id

                                world.update_terrain_surface(block_position[0], block_position[1])

                                game_data.play_wall_hit_sfx(wall_id)

    """================================================================================================================= 
        player.Player.use_melee_weapon -> void
        
        Swings the given melee weapon item
    -----------------------------------------------------------------------------------------------------------------"""
    def use_melee_weapon(self, melee_weapon_item):
        if self.can_use:
            self.enemies_hit = []
            self.can_use = False
            self.use_tick = 0
            self.use_delta = 0.0
            self.use_delay = melee_weapon_item.get_attack_speed() * 0.01

            game_data.play_sound("fg.sound.swing")

            self.should_swing_arm = True
            self.item_swing = True

    """================================================================================================================= 
        player.Player.use_ranged_weapon -> void
        
        Shoots the given ranged weapon item
    -----------------------------------------------------------------------------------------------------------------"""
    def use_ranged_weapon(self, screen_position_x, screen_position_y, ranged_weapon_item):
        if self.can_use:
            ammo_to_use_id = -1
            ammo_to_use_dat = None
            for item_id in ammo_type_item_lists[ranged_weapon_item.xml_item["@ranged_ammo_type"]]:
                item_ammo_slots = self.find_existing_item_stacks(item_id)
                if len(item_ammo_slots) > 0:
                    ammo_to_use_dat = item_ammo_slots[0]
                    ammo_to_use_id = item_id
                    break

            if ammo_to_use_id != -1:
                self.remove_item((ammo_to_use_dat[0], ammo_to_use_dat[1]), remove_count=1)

                game_data.play_sound(ranged_weapon_item.xml_item["@use_sound"])

                if commons.MOUSE_POS[0] < screen_position_x:
                    self.direction = 0
                else:
                    self.direction = 1

                self.can_use = False

                self.arm_out = True
                self.arm_out_angle = math.atan2(screen_position_y - commons.MOUSE_POS[1], abs(screen_position_x - commons.MOUSE_POS[0]))

                self.use_tick = 0
                self.use_delay = ranged_weapon_item.get_attack_speed() * 0.01

                angle = math.atan2(commons.MOUSE_POS[1] - screen_position_y, commons.MOUSE_POS[0] - screen_position_x)

                source = self.name

                entity_manager.spawn_projectile(self.position, angle, ranged_weapon_item, ammo_to_use_id, source)

    """================================================================================================================= 
        player.Player.give_item -> varying return info
        
        Gives the player one or several potentially prefixed items.
        
        Performs an optional search on the player's available item spaces to merge the item with pre-existing stacks or
        just place it in an empty slot
    -----------------------------------------------------------------------------------------------------------------"""
    def give_item(self, item, amnt=1, position=None):
        # No position specified
        if position is None:
            is_coin = item.has_tag(ItemTag.COIN)
            # Find all suitable slots
            existing_slots = self.find_existing_item_stacks(item.item_id)
            # Slots that already have the item
            while len(existing_slots) > 0 and amnt > 0:
                # Work out how many to add to the stack
                fill_count = existing_slots[0][2]
                amnt -= fill_count
                if amnt < 0:
                    fill_count += amnt

                # Increase the amnt of the chosen slot
                self.items[existing_slots[0][0]][existing_slots[0][1]].amnt += fill_count

                # Automatically craft new coins
                if is_coin:
                    if self.items[existing_slots[0][0]][existing_slots[0][1]].amnt == self.items[existing_slots[0][0]][existing_slots[0][1]].get_max_stack():
                        if amnt > 0:
                            self.items[existing_slots[0][0]][existing_slots[0][1]].amnt = amnt
                        else:
                            self.items[existing_slots[0][0]][existing_slots[0][1]] = None
                        self.give_item(Item(item.item_id + 1))
                        amnt = 0

                # Flag the position for a surface update
                dat = [existing_slots[0][0], existing_slots[0][1]]
                if dat not in self.old_inventory_positions:
                    self.old_inventory_positions.append(dat)
                # Remove the used data
                existing_slots.pop(0)

            # Free slots
            free_slots = self.find_free_spaces(item.xml_item["@max_stack"])

            while len(free_slots) > 0 and amnt > 0:  # No stacks left to fill so fill empty slots
                # Work out how many to add to the stack
                fill_count = free_slots[0][2]
                amnt -= fill_count
                if amnt < 0:
                    fill_count += amnt

                # Add that number to the free slot
                self.items[free_slots[0][0]][free_slots[0][1]] = item.copy(new_amnt=fill_count)

                # Flag the position for a surface update
                dat = [free_slots[0][0], free_slots[0][1]]
                if dat not in self.old_inventory_positions:
                    self.old_inventory_positions.append(dat)
                # Remove the used data
                free_slots.remove(free_slots[0])

            if amnt <= 0:
                return [ItemSlotClickResult.GAVE_ALL]
            else:
                if item.item_id not in self.un_pickupable_items:
                    self.un_pickupable_items.append(item.item_id)
                return [ItemSlotClickResult.GAVE_SOME, amnt]

        # Position specified
        else:
            # Slot is free, add
            if self.items[position[0]][position[1]] is None:
                self.items[position[0]][position[1]] = item.copy(new_amnt=amnt)
                return [ItemSlotClickResult.GAVE_ALL]

            # Slot has an item with the same Id
            elif self.items[position[0]][position[1]].item_id == item.item_id:
                max_stack = self.items[position[0]][position[1]].get_max_stack()
                # Item is already at max stack, swap
                if self.items[position[0]][position[1]].amnt == max_stack:
                    return [ItemSlotClickResult.SWAPPED, self.items[position[0]][position[1]], position[0]]

                else:
                    self.items[position[0]][position[1]].amnt += amnt
                    # Entire stack cannot be given
                    if self.items[position[0]][position[1]].amnt > max_stack:
                        amnt = self.items[position[0]][position[1]].amnt - max_stack
                        self.items[position[0]][position[1]].amnt = max_stack
                        return [ItemSlotClickResult.GAVE_SOME, amnt]

                    # Entire stack was given
                    else:
                        return [ItemSlotClickResult.GAVE_ALL]

            # Slot has an item with a different Id, swap
            elif self.items[position[0]][position[1]].item_id != item.item_id:
                return [ItemSlotClickResult.SWAPPED, self.items[position[0]][position[1]], position[0]]

    """================================================================================================================= 
        player.Player.remove_item -> item
        
        Removes all the items from a slot in one of the player's available item slots
    -----------------------------------------------------------------------------------------------------------------"""
    def remove_item(self, position, remove_count=None):
        item = self.items[position[0]][position[1]]
        if item is not None:
            if remove_count is None:
                self.items[position[0]][position[1]] = None
            else:
                self.items[position[0]][position[1]].amnt -= remove_count
                if self.items[position[0]][position[1]].amnt <= 0:
                    self.items[position[0]][position[1]] = None

            if position not in self.old_inventory_positions:
                self.old_inventory_positions.append(position)

            if remove_count is None:
                return item.copy()
            else:
                return item.copy(new_amnt=remove_count)

    """================================================================================================================= 
        player.Player.find_existing_item_stacks -> existing space list
        
        Finds any occurrences of an item in the player's inventory or hotbar
    -----------------------------------------------------------------------------------------------------------------"""
    def find_existing_item_stacks(self, item_id, search_hotbar=True, search_inventory=True):
        # [which array, position in array, amount]
        existing_spaces = []
        item_data = game_data.get_item_by_id(item_id)

        if search_hotbar:
            for hotbar_index in range(len(self.items[ItemLocation.HOTBAR])):
                item = self.items[ItemLocation.HOTBAR][hotbar_index]
                if item is not None:
                    if item.item_id == item_id:
                        available = item_data["@max_stack"] - self.items[ItemLocation.HOTBAR][hotbar_index].amnt
                        existing_spaces.append([ItemLocation.HOTBAR, hotbar_index, available])
        
        if search_inventory:
            for inventory_index in range(len(self.items[ItemLocation.INVENTORY])):
                item = self.items[ItemLocation.INVENTORY][inventory_index]
                if item is not None:
                    if item.item_id == item_id:
                        available = item_data["@max_stack"] - self.items[ItemLocation.INVENTORY][inventory_index].amnt
                        if available > 0:
                            existing_spaces.append([ItemLocation.INVENTORY, inventory_index, available])

        return existing_spaces

    """================================================================================================================= 
        player.Player.find_free_spaces -> free space list

        Finds any free spaces in the player's inventory or hotbar
    -----------------------------------------------------------------------------------------------------------------"""
    def find_free_spaces(self, max_stack=999, search_hotbar=True, search_inventory=True):
        free_spaces = []

        if search_hotbar:
            for hotbar_index in range(len(self.items[ItemLocation.HOTBAR])):
                if self.items[ItemLocation.HOTBAR][hotbar_index] is None:
                    free_spaces.append([ItemLocation.HOTBAR, hotbar_index, max_stack])

        if search_inventory:
            for inventory_index in range(len(self.items[ItemLocation.INVENTORY])):
                if self.items[ItemLocation.INVENTORY][inventory_index] is None:
                    free_spaces.append([ItemLocation.INVENTORY, inventory_index, max_stack])

        return free_spaces

    """================================================================================================================= 
        player.Player.render_hotbar -> void
        
        Fully renders the player's hotbar to the hotbar_image surface, including all the items in the hotbar 
    -----------------------------------------------------------------------------------------------------------------"""
    def render_hotbar(self):
        self.hotbar_image.fill((255, 0, 255))
        for hotbar_index in range(len(self.items[ItemLocation.HOTBAR])):
            self.hotbar_image.blit(surface_manager.misc_gui[0], (48 * hotbar_index, 0))
            item = self.items[ItemLocation.HOTBAR][hotbar_index]
            if item is not None:
                self.hotbar_image.blit(item.get_image(), (item.get_item_slot_offset_x() + 48 * hotbar_index, item.get_item_slot_offset_y()))
                if item.amnt > 1:
                    self.hotbar_image.blit(shared_methods.outline_text(str(item.amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * hotbar_index, 30))

    """================================================================================================================= 
        player.Player.render_inventory -> void
        
        Fully renders the player's inventory to the inventory_image surface, including all the items in the inventory 
    -----------------------------------------------------------------------------------------------------------------"""
    def render_inventory(self):
        self.inventory_image.fill((255, 0, 255))
        pygame.draw.rect(self.inventory_image, (150, 150, 150), Rect(5, 5, 472, 184), 0)
        for inventory_index in range(len(self.items[ItemLocation.INVENTORY])):
            slot_x = inventory_index % 10
            slot_y = inventory_index // 10
            self.inventory_image.blit(surface_manager.misc_gui[0], (48 * slot_x, 48 * slot_y))
            item = self.items[ItemLocation.INVENTORY][inventory_index]
            if item is not None:
                self.inventory_image.blit(item.get_image(), (item.get_item_slot_offset_x() + 48 * slot_x, item.get_item_slot_offset_y() + 48 * slot_y))
                if self.items[ItemLocation.INVENTORY][inventory_index].amnt > 1:
                    self.inventory_image.blit(shared_methods.outline_text(str(self.items[ItemLocation.INVENTORY][inventory_index].amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * slot_x, 30 + 48 * slot_y))

    """================================================================================================================= 
        player.Player.render_chest -> void
        
        Fully renders the chest the player has open to the chest_image surface, including all the items in the open chest 
    -----------------------------------------------------------------------------------------------------------------"""
    def render_chest(self):
        self.chest_image.fill((255, 0, 255))
        pygame.draw.rect(self.chest_image, (150, 150, 150), Rect(5, 5, 232, 184), 0)
        for chest_index in range(len(self.items[ItemLocation.CHEST])):
            slot_x = chest_index % 5
            slot_y = chest_index // 5
            self.chest_image.blit(surface_manager.misc_gui[0], (48 * slot_x, 48 * slot_y))
            item = self.items[ItemLocation.CHEST][chest_index]
            if item is not None:
                self.chest_image.blit(item.get_image(), (item.get_item_slot_offset_x() + 48 * slot_x, item.get_item_slot_offset_y() + 48 * slot_y))
                if self.items[ItemLocation.CHEST][chest_index].amnt > 1:
                    self.chest_image.blit(shared_methods.outline_text(str(self.items[ItemLocation.CHEST][chest_index].amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * slot_x, 30 + 48 * slot_y))

    """================================================================================================================= 
        player.Player.update_inventory_old_slots -> void
        
        Uses a list of outdated positions in the hotbar, inventory or an open chest to update the respective area's surfaces
    -----------------------------------------------------------------------------------------------------------------"""
    def update_inventory_old_slots(self):
        for data in self.old_inventory_positions:
            if data[0] == ItemLocation.HOTBAR:
                item = self.items[ItemLocation.HOTBAR][data[1]]
                self.hotbar_image.blit(surface_manager.misc_gui[0], (data[1] * 48, 0))
                if item is not None:
                    self.hotbar_image.blit(item.get_image(), (item.get_item_slot_offset_x() + 48 * data[1], item.get_item_slot_offset_y()))
                    if item.amnt > 1:
                        self.hotbar_image.blit(shared_methods.outline_text(str(item.amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * data[1], 30))
            elif data[0] == ItemLocation.INVENTORY:
                item = self.items[ItemLocation.INVENTORY][data[1]]
                slot_x = data[1] % 10
                slot_y = data[1] // 10
                self.inventory_image.blit(surface_manager.misc_gui[0], (slot_x * 48, slot_y * 48))
                if item is not None:
                    self.inventory_image.blit(item.get_image(), (item.get_item_slot_offset_x() + slot_x * 48, item.get_item_slot_offset_y() + slot_y * 48))
                    if item.amnt > 1:
                        self.inventory_image.blit(shared_methods.outline_text(str(item.amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * slot_x, 30 + 48 * slot_y))

            elif data[0] == ItemLocation.CHEST:
                item = self.items[ItemLocation.CHEST][data[1]]
                slot_x = data[1] % 5
                slot_y = data[1] // 5
                self.chest_image.blit(surface_manager.misc_gui[0], (slot_x * 48, slot_y * 48))
                if item is not None:
                    self.chest_image.blit(item.get_image(), (item.get_item_slot_offset_x() + slot_x * 48, item.get_item_slot_offset_y() + slot_y * 48))
                    if item.amnt > 1:
                        self.chest_image.blit(shared_methods.outline_text(str(item.amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * slot_x, 30 + 48 * slot_y))
        self.old_inventory_positions = []

    """================================================================================================================= 
        player.Player.update_craftable_items -> void
        
        Creates a list of items that can be crafted with the current materials List structure [item_id, amnt]
    -----------------------------------------------------------------------------------------------------------------"""
    def update_craftable_items(self):
        self.items[ItemLocation.CRAFTING_MENU] = [[i + 1, 1] for i in range(len(game_data.xml_item_data) - 1)]

    """================================================================================================================= 
        player.Player.render_craftable_items_surf -> void
        
        Uses the craftable_items list to create a surface that displays all the items the player can craft
    -----------------------------------------------------------------------------------------------------------------"""
    def render_craftable_items_surf(self):
        self.craftable_items_surf = pygame.Surface((48, len(self.items[ItemLocation.CRAFTING_MENU]) * 48))
        self.craftable_items_surf.fill((255, 0, 255))
        for i in range(len(self.items[ItemLocation.CRAFTING_MENU])):
            self.craftable_items_surf.blit(surface_manager.misc_gui[0], (0, i * 48))
            item_data = game_data.xml_item_data[self.items[ItemLocation.CRAFTING_MENU][i][0]]
            image = item_data["@image"]
            if image is not None:
                self.craftable_items_surf.blit(image, (item_data["@item_slot_offset_x"], item_data["@item_slot_offset_y"] + i * 48))

    """================================================================================================================= 
        player.Player.draw -> void
        
        Uses various player variables to draw the player in the world
    -----------------------------------------------------------------------------------------------------------------"""
    def draw(self):  # Draw player to screen
        hit_rect = Rect(0, 0, 1, 1)

        if self.alive:
            screen_position_x = self.position[0] - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5
            screen_position_y = self.position[1] - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5
            commons.screen.blit(self.sprites[self.animation_frame], (screen_position_x - 20, screen_position_y - 33))

            if self.arm_out:
                if not commons.IS_HOLDING_ITEM:
                    item = self.items[ItemLocation.HOTBAR][self.hotbar_index]
                else:
                    item = commons.ITEM_HOLDING
                world_override_image = item.get_world_override_image()
                if world_override_image is not None:
                    rotated_item_surf = shared_methods.rotate_surface(world_override_image, self.arm_out_angle * 180 / math.pi)
                else:
                    rotated_item_surf = shared_methods.rotate_surface(item.get_image(), self.arm_out_angle * 180 / math.pi)
                if self.direction == 1:
                    offset_x = 10
                else:
                    offset_x = -10
                    rotated_item_surf = pygame.transform.flip(rotated_item_surf, True, False)
                commons.screen.blit(rotated_item_surf, (screen_position_x - rotated_item_surf.get_width() * 0.5 + offset_x, screen_position_y - rotated_item_surf.get_height() * 0.5))
            
            elif self.item_swing:
                if not commons.IS_HOLDING_ITEM:
                    item = self.items[ItemLocation.HOTBAR][self.hotbar_index]
                else:
                    item = commons.ITEM_HOLDING

                if item is not None and item.has_tag(ItemTag.WEAPON):
                    if self.direction == 1:
                        hit_rect = Rect(self.position[0],
                                        self.position[1] - self.current_item_swing_image.get_height() * 0.5,
                                        self.current_item_swing_image.get_width(),
                                        self.current_item_swing_image.get_height())
                    else:
                        hit_rect = Rect(self.position[0] - self.current_item_swing_image.get_width(),
                                        self.position[1] - self.current_item_swing_image.get_height() * 0.5,
                                        self.current_item_swing_image.get_width(),
                                        self.current_item_swing_image.get_height())

                    if commons.HITBOXES:
                        hit_rect_screen_x = hit_rect.x - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5
                        hit_rect_screen_y = hit_rect.y - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5
                        pygame.draw.rect(commons.screen, (255, 0, 0), Rect(hit_rect_screen_x, hit_rect_screen_y, hit_rect.w, hit_rect.h), 1)

                    # Probably should be in update
                    for enemy in entity_manager.enemies:
                        if enemy.rect.colliderect(hit_rect):
                            if enemy.game_id not in self.enemies_hit:
                                if self.direction == 0:
                                    direction = -1
                                else:
                                    direction = 1
                                damage = item.get_attack_damage()
                                if random.random() <= item.get_crit_chance():
                                    crit = True
                                else:
                                    crit = False

                                to_enemy = shared_methods.normalize_vec_2((enemy.position[0] - self.position[0], enemy.position[1] - self.position[1]))

                                enemy.damage(damage, ["melee", "Player"], item.get_knockback(), direction=direction, crit=crit, source_velocity=(to_enemy[0] * 30, to_enemy[1] * 30))
                                self.enemies_hit.append(int(enemy.game_id))

                eased_use_delta = shared_methods.ease_out_zero_to_one(self.use_delta, 1)
                less_eased_delta = shared_methods.lerp_float(self.use_delta, eased_use_delta, 0.7)

                if self.direction == 1:
                    self.swing_angle = -less_eased_delta * 175 + 85
                else:
                    self.swing_angle = less_eased_delta * 175 + 5

                rotated_surface = shared_methods.rotate_surface(self.current_item_swing_image, self.swing_angle)

                if item is not None:
                    total_offset = commons.PLAYER_ARM_LENGTH + self.current_item_swing_offset * item.get_hold_offset()
                else:
                    total_offset = commons.PLAYER_ARM_LENGTH

                # Looking right
                if self.direction == 1:
                    hand_angle_global_degrees = shared_methods.lerp_float(-130, 45, less_eased_delta)
                    hand_angle_global_radians = hand_angle_global_degrees * (math.pi / 180)
                    offset_x = math.cos(hand_angle_global_radians) * total_offset - rotated_surface.get_width() * 0.5 - 5
                    offset_y = math.sin(hand_angle_global_radians) * total_offset - rotated_surface.get_height() * 0.5 + 2
                # Looking left
                else:
                    hand_angle_global_degrees = shared_methods.lerp_float(130, -45, less_eased_delta)
                    hand_angle_global_radians = hand_angle_global_degrees * (math.pi / 180)
                    offset_x = -math.cos(hand_angle_global_radians) * total_offset - rotated_surface.get_width() * 0.5 + 5
                    offset_y = -math.sin(hand_angle_global_radians) * total_offset - rotated_surface.get_height() * 0.5 + 2

                commons.screen.blit(rotated_surface, (screen_position_x + offset_x, screen_position_y + offset_y))

            commons.screen.blit(self.arm_sprites[self.arm_animation_frame], (screen_position_x - 20, screen_position_y - 33))

            if commons.HITBOXES:  # Show hitbox
                pygame.draw.rect(commons.screen,  (255, 0, 0), Rect(screen_position_x - commons.PLAYER_WIDTH * 0.5, screen_position_y - commons.PLAYER_HEIGHT * 0.5, commons.PLAYER_WIDTH, commons.PLAYER_HEIGHT), 1)

    """================================================================================================================= 
        player.Player.draw_hp -> void
        
        Draws the player's health in the top right
    -----------------------------------------------------------------------------------------------------------------"""
    def draw_hp(self):
        if self.hp > 0:
            rect = Rect(commons.WINDOW_WIDTH - 10 - self.hp * 2, 25, self.hp * 2, 20)
            hp_float = self.hp / self.max_hp
            col = ((1 - hp_float) * 255, hp_float * 255, 0)
            pygame.draw.rect(commons.screen, col, rect, 0)
            pygame.draw.rect(commons.screen, (col[0] * 0.8, col[1] * 0.8, 0), rect, 3)
            commons.screen.blit(self.hp_text, (self.hp_x_position, 45))

    """================================================================================================================= 
        player.Player.open_chest -> void
        
        Plays the chest opening sound, opens the inventory and updates the items that the player can craft
    -----------------------------------------------------------------------------------------------------------------"""
    def open_chest(self, items):
        if not self.chest_open:
            game_data.play_sound("fg.sound.menu_open")
            self.chest_open = True
        self.inventory_open = True
        self.items[ItemLocation.CHEST] = items
        self.crafting_menu_offset_y = 120
        self.update_craftable_items()
        self.render_craftable_items_surf()
        self.render_chest()

    """================================================================================================================= 
        player.Player.save -> void
        
        Packs the important player data into an array and serialises it using the pickle module
    -----------------------------------------------------------------------------------------------------------------"""
    def save(self):
        # Convert the items in the hotbar to a less data heavy format
        formatted_hotbar = []
        for item_index in range(len(self.items[ItemLocation.HOTBAR])):
            item = self.items[ItemLocation.HOTBAR][item_index]
            if item is not None:
                if item.prefix_data is None:
                    formatted_hotbar.append([item_index, item.get_id_str(), item.amnt, None])
                else:
                    formatted_hotbar.append([item_index, item.get_id_str(), item.amnt, item.get_prefix_name()])

        # Convert the items in the inventory to a less data heavy format
        formatted_inventory = []
        for item_index in range(len(self.items[ItemLocation.INVENTORY])):
            item = self.items[ItemLocation.INVENTORY][item_index]
            if item is not None:
                if item.prefix_data is None:
                    formatted_inventory.append([item_index, item.get_id_str(), item.amnt, None])
                else:
                    formatted_inventory.append([item_index, item.get_id_str(), item.amnt, item.get_prefix_name()])

        # Save the data to disk and display a message
        commons.PLAYER_DATA = [self.name, self.model, formatted_hotbar, formatted_inventory, self.hp, self.max_hp, self.play_time, self.creation_date, self.last_played_date]  # Create player array
        pickle.dump(commons.PLAYER_DATA, open("res/players/" + self.name + ".player", "wb"))  # Save player array
        entity_manager.add_message("Saved Player: " + self.name + "!", (255, 255, 255))

    """================================================================================================================= 
        player.Player.jump -> void
        
        Plays a sound, spawns particles and sets the player's y velocity
    -----------------------------------------------------------------------------------------------------------------"""
    def jump(self):
        if self.alive and self.grounded:
            game_data.play_sound("fg.sound.jump")
            if commons.PARTICLES:
                colour = shared_methods.get_block_average_colour(self.last_block_on)
                for i in range(int(random.randint(5, 8) * commons.PARTICLEDENSITY)):
                    entity_manager.spawn_particle((self.position[0], self.position[1] + commons.BLOCKSIZE * 1.5), colour, size=10, life=1, angle=-math.pi * 0.5, spread=math.pi * 0.33, gravity=0, magnitude=1.5 + random.random() * 10)
            self.velocity = (self.velocity[0], -50)
            self.grounded = False

    def get_date_created_string(self):
        return str(str(self.creation_date)[:19])

    def get_last_date_played_string(self):
        return str(str(self.last_played_date)[:19])


"""================================================================================================================= 
    player.render_sprites -> [sprites, arm_sprites]
    
    Uses a model object to render torso and arm frames to surfaces so that they can be used to draw this player
-----------------------------------------------------------------------------------------------------------------"""
def render_sprites(model, directions=2, arm_frame_count=20, torso_frame_count=15):  # create an array of surfs for the current character used for animation/blitting
    sprites = []
    arm_sprites = []
    for j in range(directions):  # for both directions
        hair = shared_methods.colour_surface(surface_manager.hair[model.hair_id], model.hair_col)

        if j == 1:  # flip if necessary
            hair = pygame.transform.flip(hair, True, False)

        torso = shared_methods.colour_surface(surface_manager.torsos[0], model.shirt_col)
        if j == 0:  # flip if necessary
            torso = pygame.transform.flip(torso, True, False)

        head = shared_methods.colour_surface(surface_manager.hair[9], model.skin_col)
        pygame.draw.rect(head, (255, 254, 255), Rect(20, 22, 4, 4), 0)
        pygame.draw.rect(head, model.eye_col, Rect(22, 22, 2, 4), 0)

        if j == 1:  # flip if necessary
            head = pygame.transform.flip(head, True, False)

        for i in range(torso_frame_count):  # all animation frames for one direction
            body_surf = pygame.Surface((44, 75))
            body_surf.fill((255, 0, 255))
            body_surf.set_colorkey(
                (255, 0, 255))  # create the surf for the whole player with a colourkey of (255, 0, 255)
            trousers = shared_methods.colour_surface(surface_manager.torsos[i + 1], model.trouser_col)
            if j == 0:  # flip if necessary
                trousers = pygame.transform.flip(trousers, True, False)
            shoes = shared_methods.colour_surface(surface_manager.torsos[i + 16], model.shoe_col)
            if j == 0:  # flip if necessary
                shoes = pygame.transform.flip(shoes, True, False)
            body_surf.blit(torso, (0, 4))
            body_surf.blit(trousers, (0, 4))
            body_surf.blit(shoes, (0, 4))
            body_surf.blit(head, (0, 0))
            body_surf.blit(hair, (0, 0))

            sprites.append(body_surf)

        for i in range(arm_frame_count):  # all animation frames for one direction
            arm_surf = pygame.Surface((44, 75))
            arm_surf.fill((255, 0, 255))
            arm_surf.set_colorkey((255, 0, 255))

            arms = shared_methods.colour_surface(surface_manager.torsos[i + 31], model.under_shirt_col)
            if j == 0:  # flip if necessary
                arms = pygame.transform.flip(arms, True, False)

            hands = shared_methods.colour_surface(surface_manager.torsos[i + 51], model.skin_col)
            if j == 0:  # flip if necessary
                hands = pygame.transform.flip(hands, True, False)

            arm_surf.blit(arms, (0, 4))
            arm_surf.blit(hands, (0, 4))

            arm_sprites.append(arm_surf)

    return [sprites, arm_sprites]
