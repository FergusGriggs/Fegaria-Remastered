# enemy.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame, math, random
from pygame.locals import *

import game_data
from game_data import *

import commons
import world

import entity_manager
import surface_manager
import shared_methods

import item
from item import Item


"""================================================================================================================= 
    enemy.Enemy

    Stores all information about an enemy instance
-----------------------------------------------------------------------------------------------------------------"""


class Enemy:
    def __init__(self, position, enemy_id):
        self.position = position
        self.block_pos = (0, 0)
        self.velocity = (0, 0)
        self.enemy_id = enemy_id
        self.name = str(game_data.enemy_data[self.enemy_id][0])
        self.type = str(game_data.enemy_data[self.enemy_id][1])
        self.hp = int(game_data.enemy_data[self.enemy_id][2])
        self.max_hp = int(self.hp)
        self.defense = int(game_data.enemy_data[self.enemy_id][3])
        self.knockback_resist = int(game_data.enemy_data[self.enemy_id][3])
        self.attack_damage = int(game_data.enemy_data[self.enemy_id][5])
        self.blood_colour = tuple(game_data.enemy_data[self.enemy_id][6])
        self.rect = Rect(self.position[0] - commons.BLOCKSIZE, self.position[1] - commons.BLOCKSIZE / 1.5, commons.BLOCKSIZE * 2, commons.BLOCKSIZE * 1.5)
        self.grounded = False

        self.stop_left = False
        self.stop_right = False

        self.moving_left = False
        self.moving_right = False

        self.damage_tick = 0
        self.jump_tick = 1
        self.despawn_tick = 5
        self.animation_frame = 0
        self.game_id = random.randint(1000, 9999)

        self.world_invincible_timer = 0.0
        self.world_invincible = False

        self.alive = True

    """================================================================================================================= 
        enemy.Enemy.update -> void

        Updates the enemy instance, performing physics, AI and animation
    -----------------------------------------------------------------------------------------------------------------"""
    def update(self):
        if self.alive:
            if self.world_invincible:
                if self.world_invincible_timer <= 0.0:
                    self.world_invincible = False
                else:
                    self.world_invincible_timer -= commons.DELTA_TIME

            self.stop_left = False
            self.stop_right = False

            if self.despawn_tick <= 0:
                self.despawn_tick += 5
                if self.check_despawn():
                    return
            else:
                self.despawn_tick -= commons.DELTA_TIME

            if self.moving_left:  # Moves enemy left
                if not self.stop_left:
                    self.velocity = (-12.5, self.velocity[1])
            if self.moving_right:  # Moves enemy right
                if not self.stop_right:
                    self.velocity = (12.5, self.velocity[1])
            if not self.grounded:
                self.velocity = (self.velocity[0], self.velocity[1] + commons.GRAVITY * commons.DELTA_TIME)
            self.run_ai()

            drag_factor = 1.0 - commons.DELTA_TIME * 4

            self.velocity = (self.velocity[0] * drag_factor, self.velocity[1] * drag_factor)
            self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE)
            self.rect.left = self.position[0] - self.rect.width * 0.5  # updating rect
            self.rect.top = self.position[1] - self.rect.height * 0.5
            self.block_pos = (math.floor(self.position[1] // commons.BLOCKSIZE), math.floor(self.position[0] // commons.BLOCKSIZE))
            self.grounded = False
        
            if self.velocity[0] < 0:
                if self.position[0] < world.border_left:
                    self.position = (int(world.border_left), self.position[1])
            elif self.velocity[0] > 0:
                if self.position[0] > world.border_right:
                    self.position = (int(world.border_right), self.position[1])
            if self.velocity[1] > 0:
                if self.position[1] > world.border_down:
                    self.position = (self.position[0], int(world.border_down))
                    self.velocity = (self.velocity[0], 0)
                    self.grounded = True
                    
            if self.damage_tick <= 0:
                if entity_manager.client_player.rect.colliderect(self.rect):
                    if entity_manager.client_player.position[0] < self.position[0]:
                        direction = -1
                    else:
                        direction = 1

                    entity_manager.client_player.damage(self.attack_damage, ["enemy", self.name], knockback=10, direction=direction, source_velocity=self.velocity)  # (normalizedPositionDifference[0] * 10, normalizedPositionDifference[1] * 10)
                    self.damage_tick += 0.5
            else:
                self.damage_tick -= commons.DELTA_TIME

            for j in range(-2, 3):
                for i in range(-2, 3):
                    if world.tile_in_map(self.block_pos[1] + j, self.block_pos[0] + i):
                        tile_id = world.world.tile_data[self.block_pos[1] + j][self.block_pos[0] + i][0]
                        tile_data = game_data.get_tile_by_id(tile_id)
                        if TileTag.NOCOLLIDE not in tile_data["@tags"]:
                            block_rect = Rect(commons.BLOCKSIZE * (self.block_pos[1] + j), commons.BLOCKSIZE * (self.block_pos[0] + i), commons.BLOCKSIZE, commons.BLOCKSIZE)
                            if TileTag.PLATFORM in tile_data["@tags"]:
                                platform = True
                            else:
                                platform = False
                            if block_rect.colliderect(int(self.rect.left - 1), int(self.rect.top + 2), 1, int(self.rect.height - 4)):
                                self.stop_left = True  # Is there a solid block left
                            if block_rect.colliderect(int(self.rect.right + 1), int(self.rect.top + 2), 1, int(self.rect.height - 4)):
                                self.stop_right = True  # Is there a solid block right
                            if block_rect.colliderect(self.rect):
                                if not self.world_invincible and TileTag.DAMAGING in tile_data["@tags"]:
                                    self.damage(tile_data["@tile_damage"], [tile_data["@tile_damage_name"], "World"])
                                
                                delta_x = self.position[0] - block_rect.centerx
                                delta_y = self.position[1] - block_rect.centery
                                if abs(delta_x) > abs(delta_y):
                                    if delta_x > 0:
                                        if not platform:
                                            self.position = (block_rect.right + self.rect.width * 0.5, self.position[1])  # Move enemy right
                                            self.velocity = (0, self.velocity[1])  # Stop enemy horizontally
                                    else:
                                        if not platform:
                                            self.position = (block_rect.left - self.rect.width * 0.5, self.position[1])  # Move enemy left
                                            self.velocity = (0, self.velocity[1])  # Stop enemy horizontally
                                else:
                                    if delta_y > 0:
                                        if self.velocity[1] < 0:
                                            if not platform:
                                                if Rect(self.rect.left + 3, self.rect.top, self.rect.width - 6, self.rect.height).colliderect(block_rect):
                                                    self.position = (self.position[0], block_rect.bottom + self.rect.height * 0.5)  # Move enemy down
                                                    self.velocity = (self.velocity[0], 0)  # Stop enemy vertically
                                    else:
                                        if self.velocity[1] > 0:
                                            if Rect(self.rect.left + 3, self.rect.top, self.rect.width - 6, self.rect.height).colliderect(block_rect):
                                                self.position = (self.position[0], block_rect.top - self.rect.height * 0.5 + 1)  # Move enemy up
                                                self.velocity = (self.velocity[0] * 0.5, 0)  # Slow down enemy horizontally and stop player vertically
                                                self.grounded = True
                                                self.moving_right = False
                                                self.moving_left = False

            self.animate()

    """================================================================================================================= 
        enemy.Enemy.damage -> void

        Damages the enemy instance spawning particles and playing a sound
        
        Will call 'kill' on the enemy if it's health drops below 0 
    -----------------------------------------------------------------------------------------------------------------"""
    def damage(self, value, source, knockback=0, direction=0, crit=False, source_velocity=None):
        if self.alive:
            if source[1] == "World" and self.world_invincible:
                return
            else:
                self.world_invincible_timer = 0.35
                self.world_invincible = True

            self.moving_right = False
            self.moving_left = False

            value -= self.defense
            value *= 1.0 + random.random() * 0.1 - 0.05
            if value < 1.0:
                value = 1.0

            if crit:
                value *= 2.0

            self.hp -= value

            if self.hp < 0:
                self.hp = 0

            entity_manager.add_damage_number(self.position, value, crit=crit)

            if self.hp > 0:  # Check if the enemy has died from damage
                game_data.play_sound("fg.sound.slime_hurt")
                if commons.PARTICLES:
                    if source_velocity is not None:
                        velocity_angle = math.atan2(source_velocity[1], source_velocity[0])
                        velocity_magnitude = math.sqrt(source_velocity[0] ** 2 + source_velocity[1] ** 2)
                    else: 
                        velocity_angle = math.atan2(self.velocity[1], self.velocity[0])
                        velocity_magnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

                    for i in range(int(5 * commons.PARTICLEDENSITY)):  # Blood particles
                        particle_pos = (self.position[0] + random.random() * self.rect.width - self.rect.width * 0.5, self.position[1] + random.random() * self.rect.height - self.rect.height * 0.5)
                        entity_manager.spawn_particle(particle_pos, self.blood_colour, life=0.5, size=10, angle=velocity_angle, spread=math.pi * 0.2, magnitude=random.random() * velocity_magnitude * 0.5, outline=False)
            else:
                self.kill(source_velocity)

            if knockback != 0:
                remaining_knockback = max(0, knockback - self.knockback_resist)
                self.velocity = (self.velocity[0] + direction * remaining_knockback * 3.0, remaining_knockback * -5.0)

    """================================================================================================================= 
        enemy.Enemy.kill -> void

        Sets the enemies alive variable to false, will be removed from the entity list by the manager
        
        Plays a sound and spawns particles and loot
    -----------------------------------------------------------------------------------------------------------------"""
    def kill(self, source_velocity):
        if self.alive:
            self.alive = False

            coin_range = game_data.enemy_data[self.enemy_id][8]
            coin_drops = item.get_coins_from_int(random.randint(coin_range[0], coin_range[1]))
            item_drops = game_data.enemy_data[self.enemy_id][7]

            for coin_item in coin_drops:
                entity_manager.spawn_physics_item(coin_item, self.position, pickup_delay=10)

            total_weight = 0
            for item_drop in item_drops:
                total_weight += item_drop[3]

            random_number = random.randint(0, total_weight)

            for item_drop in item_drops:
                if random_number <= item_drop[3]:
                    amnt = random.randint(item_drop[1], item_drop[2])
                    item_id = game_data.get_item_id_by_id_str(item_drop[0])
                    entity_manager.spawn_physics_item(Item(item_id, amnt), self.position, pickup_delay=10)
                else:
                    random_number -= item_drop[3]

            if commons.PARTICLES:
                if source_velocity is not None:
                    self.velocity = (self.velocity[0] + source_velocity[0], self.velocity[1] + source_velocity[1])

                velocity_angle = math.atan2(self.velocity[1], self.velocity[0])
                velocity_magnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

                for i in range(int(25 * commons.PARTICLEDENSITY)):  # Blood particles
                    particle_pos = (self.position[0] + random.random() * self.rect.width - self.rect.width * 0.5, self.position[1] + random.random() * self.rect.height - self.rect.height * 0.5)
                    entity_manager.spawn_particle(particle_pos, self.blood_colour, life=0.5, size=10, angle=velocity_angle, spread=math.pi * 0.2, magnitude=random.random() * velocity_magnitude * 0.4, outline=False)

            game_data.play_sound("fg.sound.slime_death")  # Death sound

            entity_manager.enemies.remove(self)

    """================================================================================================================= 
        enemy.Enemy.animate -> void

        Updates the animation frame of the enemy instance
    -----------------------------------------------------------------------------------------------------------------"""
    def animate(self):
        if not self.grounded:
            if self.velocity[1] > 2:
                self.animation_frame = 2
            elif self.velocity[1] < -2:
                self.animation_frame = 1
            else:
                self.animation_frame = 0
        else:
            self.animation_frame = 0

    """================================================================================================================= 
        enemy.Enemy.check_despawn -> bool

        Checks if the enemy has gone too far beyond the player's view, if so, return true
    -----------------------------------------------------------------------------------------------------------------"""
    def check_despawn(self):
        if self.position[0] < entity_manager.client_player.position[0] - commons.MAX_ENEMY_SPAWN_TILES_X * 1.5 * commons.BLOCKSIZE:
            entity_manager.enemies.remove(self)
            return True
        elif self.position[0] > entity_manager.client_player.position[0] + commons.MAX_ENEMY_SPAWN_TILES_X * 1.5 * commons.BLOCKSIZE:
            entity_manager.enemies.remove(self)
            return True
        elif self.position[1] < entity_manager.client_player.position[1] - commons.MAX_ENEMY_SPAWN_TILES_Y * 1.5 * commons.BLOCKSIZE:
            entity_manager.enemies.remove(self)
            return True
        elif self.position[1] > entity_manager.client_player.position[1] + commons.MAX_ENEMY_SPAWN_TILES_Y * 1.5 * commons.BLOCKSIZE:
            entity_manager.enemies.remove(self)
            return True
        return False

    """================================================================================================================= 
        enemy.Enemy.draw -> void

        Draws the enemy instance at the current animation frame
    -----------------------------------------------------------------------------------------------------------------"""
    def draw(self):
        left = self.rect.left - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5
        top = self.rect.top - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5
        commons.screen.blit(surface_manager.slimes[self.enemy_id * 3 + self.animation_frame], (left, top))
        if self.hp < self.max_hp:
            hp_float = self.hp / self.max_hp
            col = (255 * (1 - hp_float), 255 * hp_float, 0)
            pygame.draw.rect(commons.screen, shared_methods.darken_colour(col), Rect(left, top + 30, self.rect.width, 10), 0)
            pygame.draw.rect(commons.screen, col, Rect(left + 2, top + 32, (self.rect.width - 4) * hp_float, 6), 0)
        if commons.HITBOXES:
            pygame.draw.rect(commons.screen, (255, 0, 0), Rect(self.rect.left - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5, self.rect.top - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5, self.rect.width, self.rect.height), 1)

    """================================================================================================================= 
        enemy.Enemy.run_ai -> void

        Runs AI specific to this type of enemy
    -----------------------------------------------------------------------------------------------------------------"""
    def run_ai(self):
        if self.type == "Slime":
            if self.grounded:
                if self.jump_tick <= 0:
                    self.jump_tick += 0.5 + random.random()
                    if entity_manager.client_player.position[0] < self.position[0]:
                        if entity_manager.client_player.alive:
                            self.velocity = (-10, -45 + random.random())
                            self.moving_left = True
                        else:
                            self.velocity = (10, -45 + random.random())
                            self.moving_right = True
                    else:
                        if entity_manager.client_player.alive:
                            self.velocity = (10, -45 + random.random())
                            self.moving_right = True
                        else:
                            self.velocity = (-10, -45 + random.random())
                            self.moving_left = True
                else:
                    self.jump_tick -= commons.DELTA_TIME
