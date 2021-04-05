# physics_item.py
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

import surface_manager
import entity_manager
import shared_methods

from item import *


"""================================================================================================================= 
    physics_item.PhysicsItem

    Holds all the information required to update and draw a single PhysicsItem (An item that can collide with tiles)
-----------------------------------------------------------------------------------------------------------------"""
class PhysicsItem:
    def __init__(self, item, position, velocity=None, pickup_delay=100):
        
        self.item = item

        self.position = position
        self.block_position = (0, 0)

        if velocity is None:
            #angle = -random.random() * math.pi
            #init_speed = random.random() * 10 + 10
            #self.velocity = (math.cos(angle) * init_speed, math.sin(angle) * init_speed)
            self.velocity = (random.random() * 20 - 10, -random.random() * 10 - 15)
        else:
            self.velocity = velocity

        self.item_scale = 1.25
        self.image = None
        self.rotated_surf = None
        self.half_image_size = 0
        self.render_image()

        self.despawn_check_tick = 60

        self.pickup_delay = pickup_delay
        self.grounded = False

        self.rect = Rect(position[0] - commons.BLOCKSIZE * 0.5 * self.item_scale, position[1] - commons.BLOCKSIZE * 0.5 * self.item_scale, commons.BLOCKSIZE * self.item_scale * 0.8, commons.BLOCKSIZE * self.item_scale * 0.8)
        
        self.stationary = False
        self.time_stationary = 0

    """================================================================================================================= 
        physics_item.PhysicsItem.render_image -> void

        Gives the image an invisible border so that it can be rotated without clipping
    -----------------------------------------------------------------------------------------------------------------"""
    def render_image(self):
        self.image = pygame.transform.scale(self.item.get_image(), (int(commons.BLOCKSIZE * 1.414 * self.item_scale), int(commons.BLOCKSIZE * 1.414 * self.item_scale)))
        self.half_image_size = self.image.get_width() * 0.5

    """================================================================================================================= 
        physics_item.PhysicsItem.check_despawn -> void

        Checks to see if the PhysicsItem is off screen, if it is then remove it from the physics items list
    -----------------------------------------------------------------------------------------------------------------"""
    def check_despawn(self):
        if self.position[0] < entity_manager.client_player.position[0] - commons.WINDOW_WIDTH * 0.5:
            entity_manager.physics_items.remove(self)
        elif self.position[0] > entity_manager.client_player.position[0] + commons.WINDOW_WIDTH * 0.5:
            entity_manager.physics_items.remove(self)
        elif self.position[1] < entity_manager.client_player.position[1] - commons.WINDOW_HEIGHT * 0.5:
            entity_manager.physics_items.remove(self)
        elif self.position[1] > entity_manager.client_player.position[1] + commons.WINDOW_HEIGHT * 0.5:
            entity_manager.physics_items.remove(self)

    """================================================================================================================= 
        physics_item.PhysicsItem.update -> void

        Runs the despawn logic and physics for the PhysicsItem instance
    -----------------------------------------------------------------------------------------------------------------"""
    def update(self):
        if self.despawn_check_tick <= 0:
            self.despawn_check_tick += 10
            self.check_despawn()
        else:
            self.despawn_check_tick -= commons.DELTA_TIME
        
        if not self.stationary:
            if math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2) < 1:
                self.time_stationary += commons.DELTA_TIME

                if self.time_stationary > 1:
                    self.stationary = True
            else:
                self.time_stationary = 0

            if not self.grounded:
                self.velocity = (self.velocity[0], self.velocity[1] + commons.GRAVITY * commons.DELTA_TIME)
        
            drag_factor = 1.0 - commons.DELTA_TIME * 2
            self.velocity = (self.velocity[0] * drag_factor, self.velocity[1] * drag_factor)
            self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE)
            self.rect.center = tuple(self.position)
            self.block_position = (math.floor(self.position[1] // commons.BLOCKSIZE), math.floor(self.position[0] // commons.BLOCKSIZE))
            
            self.grounded = False

        collide = not self.stationary
        
        if self.item.item_id not in entity_manager.client_player.un_pickupable_items:
            if self.pickup_delay <= 0:
                if abs(self.position[0] - entity_manager.client_player.position[0]) < commons.BLOCKSIZE * 3.5 and abs(self.position[1] - entity_manager.client_player.position[1]) < commons.BLOCKSIZE * 3.5:
                    collide = False
                    self.stationary = False
                    self.time_stationary = 0

                    angle = math.atan2(entity_manager.client_player.position[1] - self.position[1], entity_manager.client_player.position[0] - self.position[0])
                    self.velocity = (self.velocity[0] + math.cos(angle) * 1000 * commons.DELTA_TIME, self.velocity[1] + math.sin(angle) * 1000 * commons.DELTA_TIME)
                    
                    if entity_manager.client_player.rect.colliderect(self.rect):
                        item_add_data = entity_manager.client_player.give_item(self.item, amnt=self.item.amnt)
                            
                        if item_add_data[0] == ItemSlotClickResult.GAVE_ALL:
                            entity_manager.physics_items.remove(self)
                            entity_manager.add_recent_pickup(self.item.item_id, self.item.amnt, self.item.get_tier(), entity_manager.client_player.position, unique=self.item.has_prefix, item=self.item)

                            game_data.play_sound(self.item.get_pickup_sound_id_str())
                            return
                        elif item_add_data[0] == ItemSlotClickResult.GAVE_SOME:
                            self.item.amnt = item_add_data[1]
                        return
            else:
                self.pickup_delay -= 1

        if collide:
            for j in range(-2, 3):
                for i in range(-2, 3):
                    if world.tile_in_map(self.block_position[1] + j, self.block_position[0] + i):
                        tile_id = world.world.tile_data[self.block_position[1] + j][self.block_position[0] + i][0]
                        tile_data = game_data.get_tile_by_id(tile_id)
                        if TileTag.NOCOLLIDE not in tile_data["@tags"]:
                            block_rect = Rect(commons.BLOCKSIZE * (self.block_position[1] + j), commons.BLOCKSIZE * (self.block_position[0] + i), commons.BLOCKSIZE, commons.BLOCKSIZE)
                            if block_rect.colliderect(self.rect):
                                delta_x = self.position[0] - block_rect.centerx
                                delta_y = self.position[1] - block_rect.centery
                                if abs(delta_x) > abs(delta_y):
                                    if delta_x > 0:
                                        self.position = (block_rect.right + self.rect.width * 0.5, self.position[1])  # Move item right
                                        self.velocity = (0, self.velocity[1])  # Stop item horizontally
                                    else:
                                        self.position = (block_rect.left - self.rect.width * 0.5, self.position[1])  # Move item left
                                        self.velocity = (0, self.velocity[1])  # Stop item horizontally
                                else:
                                    if delta_y > 0:
                                        if self.velocity[1] < 0:
                                            self.position = (self.position[0], block_rect.bottom + self.rect.height * 0.5)  # Move item down
                                            self.velocity = (self.velocity[0], 0)  # Stop item vertically
                                    else:
                                        if self.velocity[1] > 0:
                                            self.position = (self.position[0], block_rect.top - self.rect.height * 0.5 + 1)  # Move item up
                                            self.velocity = (self.velocity[0], 0)  # Stop item vertically
                                            self.grounded = True

    """================================================================================================================= 
        physics_item.PhysicsItem.draw -> void

        Draws the PhysicsItem instance, rotating using the x velocity
    -----------------------------------------------------------------------------------------------------------------"""
    def draw(self):
        if self.velocity[0] < 0:
            velocity_angle = int(max(self.velocity[0], -10) * 50)
        else:
            velocity_angle = int(min(self.velocity[0], 10) * 50)

        if not self.stationary or self.rotated_surf is None:
            self.rotated_surf = shared_methods.rotate_surface(self.image.copy(), velocity_angle)
            commons.screen.blit(self.rotated_surf, (self.rect.centerx - self.half_image_size - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5,
                                      self.rect.centery - self.half_image_size - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5))
        else:
            commons.screen.blit(self.rotated_surf, (self.rect.centerx - self.half_image_size - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5,
                                             self.rect.centery - self.half_image_size - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5))
        
        if commons.HITBOXES:
            pygame.draw.rect(commons.screen, (255, 0, 0), Rect(self.rect.left - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5,
                                                               self.rect.top - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5,
                                                               self.rect.width, self.rect.height), 1)
