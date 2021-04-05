# projectile.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame
import math
import random
from pygame.locals import *

import commons
import game_data
from game_data import *
import world

import entity_manager
import shared_methods
import surface_manager


"""================================================================================================================= 
    projectile.Projectile

    Stores information required to update and draw a single Projectile instance
-----------------------------------------------------------------------------------------------------------------"""
class Projectile:
    def __init__(self, position, velocity, projectile_type, projectile_id, source, damage, knockback, crit, bounce_num, trail, max_life=5, gravity=commons.GRAVITY, drag=0.99):
        self.position = position
        self.velocity = velocity
        self.angle = math.atan2(velocity[1], velocity[0])
        self.projectile_type = projectile_type
        self.projectile_id = projectile_id
        self.source = source
        self.damage = damage
        self.knockback = knockback
        self.crit = crit
        self.trail = trail
        self.trail_tick = 0.1
        self.bounce_num = bounce_num
        self.size = game_data.projectile_data[projectile_id][5]
        self.rect = Rect(self.position[0] - self.size * 0.5, self.position[1] - self.size * 0.5, self.size, self.size)
        self.life = int(max_life)
        self.gravity = gravity
        self.drag = drag
        self.grounded = True

    """================================================================================================================= 
        projectile.Projectile.update -> void

        Updates the life of the Projectile instance, performs physics (including optional bounces) and
        spawns trail particles if necessary
    -----------------------------------------------------------------------------------------------------------------"""
    def update(self):
        if self.life <= 0:
            entity_manager.projectiles.remove(self)
            return
        else:
            self.life -= commons.DELTA_TIME

        drag_factor = 1 + self.drag * commons.DELTA_TIME
        self.velocity = (self.velocity[0] / drag_factor, self.velocity[1] / drag_factor + commons.GRAVITY * self.gravity * commons.DELTA_TIME)

        self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE)
        self.rect.left = self.position[0] - self.size * 0.5
        self.rect.top = self.position[1] - self.size * 0.5
        block_position = (math.floor(self.position[1] // commons.BLOCKSIZE), math.floor(self.position[0] // commons.BLOCKSIZE))
        if self.trail is not None:
            if self.trail_tick <= 0:
                if self.trail == "arrow":
                    self.trail_tick += 0.025
                    if commons.PARTICLES:
                        entity_manager.spawn_particle((self.position[0] + self.size * 0.5, self.position[1] + self.size * 0.5), (90, 90, 90), life=0.5, size=7, magnitude=0, gravity=0)
            else:
                self.trail_tick -= commons.DELTA_TIME
        if self.velocity[1] > 0:
            if self.position[1] > world.border_down:
                self.position = (self.position[0], int(world.border_down))
                self.velocity = (self.velocity[0], 0)
                self.grounded = True
                
        x_collided = False
        y_collided = False

        block_hit_tile_id = -1

        for j in range(-1, 2):
            for i in range(-1, 2):
                if world.tile_in_map(block_position[1] + j, block_position[0] + i):
                    tile_id = world.world.tile_data[block_position[1] + j][block_position[0] + i][0]
                    tile_data = game_data.get_tile_by_id(tile_id)
                    if TileTag.NOCOLLIDE not in tile_data["@tags"]:
                        if TileTag.PLATFORM not in tile_data["@tags"]:
                            block_rect = Rect(commons.BLOCKSIZE * (block_position[1] + j), commons.BLOCKSIZE * (block_position[0] + i), commons.BLOCKSIZE, commons.BLOCKSIZE)
                            if block_rect.colliderect(self.rect):
                                delta_x = self.position[0] - block_rect.centerx
                                delta_y = self.position[1] - block_rect.centery
                                if abs(delta_x) > abs(delta_y):
                                    if delta_x > 0:
                                        self.position = (block_rect.right + self.rect.width * 0.5, self.position[1])  # Move proj right
                                    else:
                                        self.position = (block_rect.left - self.rect.width * 0.5, self.position[1])  # Move proj left
                                    block_hit_tile_id = tile_id
                                    x_collided = True
                                else:
                                    if delta_y > 0:
                                        if self.velocity[1] < 0:
                                            self.position = (self.position[0], block_rect.bottom + self.rect.height * 0.5)  # Move proj down
                                    else:
                                        if self.velocity[1] > 0:
                                            self.position = (self.position[0], block_rect.top - self.rect.height * 0.5)  # Move proj up
                                    block_hit_tile_id = tile_id
                                    y_collided = True

        if x_collided or y_collided:
            if self.bounce_num > 0:
                self.bounce_num -= 1
                if y_collided:
                    self.velocity = (self.velocity[0], -self.velocity[1])
                else:
                    self.velocity = (-self.velocity[0], -self.velocity[1])
            if self.bounce_num <= 0:
                entity_manager.projectiles.remove(self)
                if commons.PARTICLES:
                    colour = shared_methods.get_block_average_colour(block_hit_tile_id)
                    velocity_angle = math.atan2(self.velocity[1], self.velocity[0])
                    velocity_magnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
                    for i in range(int(4 * commons.PARTICLEDENSITY)):
                        entity_manager.spawn_particle(self.position, colour, life=0.5, angle=velocity_angle, spread=0.8, magnitude=velocity_magnitude * random.random() * 0.7, gravity=0, size=8)
                if self.projectile_type == "Bullet":
                    game_data.play_sound("fg.sound.bullet")
                else:
                    game_data.play_sound("fg.sound.dig")
                return

        for enemy in entity_manager.enemies:
            if enemy.rect.colliderect(self.rect):
                if enemy.position[0] > entity_manager.client_player.position[0]:
                    direction = 1
                else:
                    direction = -1
                enemy.damage(self.damage, ["projectile", "Player"], crit=self.crit, knockback=self.knockback, direction=direction, source_velocity=self.velocity)
                entity_manager.projectiles.remove(self)
                return

    """================================================================================================================= 
        projectile.Projectile.draw -> void

        Draws the Projectile instance, using the type to chose the image/shape
    -----------------------------------------------------------------------------------------------------------------"""
    def draw(self):
        if self.projectile_type == "Arrow":
            angle = math.atan2(self.velocity[1], -self.velocity[0]) * 180 / math.pi - 90
            surf = surface_manager.projectiles[self.projectile_id].copy()
            surf = shared_methods.rotate_surface(surf, angle)
            commons.screen.blit(surf, (self.rect.left - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5, self.rect.top - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5))
        elif self.projectile_type == "Bullet":
            pygame.draw.circle(commons.screen, (60, 60, 60), (int(self.rect.centerx - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5), int(self.rect.centery - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5)), 3, 0)
        if commons.HITBOXES:
            pygame.draw.rect(commons.screen, (255, 0, 0), Rect(self.rect.left - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5, self.rect.top - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5, self.rect.width, self.rect.height), 1)
