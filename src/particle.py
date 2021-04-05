# particle.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame, random, math
from pygame.locals import *

import commons
import entity_manager


"""================================================================================================================= 
    particle.Particle

    Holds all the information required to update and draw a single particle
-----------------------------------------------------------------------------------------------------------------"""
class Particle:
    def __init__(self, position, colour, life, magnitude, size, angle, spread, gravity, velocity=None, outline=True):
        self.position = position
        self.life = life + (random.random() * life * 0.1 - life * 0.05)  # How long it lasts for (randomized slightly)
        self.initLife = self.life
        self.colour = colour
        self.size = size + random.random() * size * 0.1 - size * 0.05  # How large it will be (randomized slightly)
        self.initSize = self.size
        self.outline = outline
        if velocity is None:
            if angle is None:
                angle = random.random() * math.pi * 2 - math.pi  # Random angle
            else:
                angle += random.random() * spread - spread * 0.5  # Set angle + random spread in set range
            self.velocity = (math.cos(angle) * magnitude, math.sin(angle) * magnitude)  # Velocity from angle and magnitude
        else:
            self.velocity = velocity
        self.gravity = gravity

    """================================================================================================================= 
        particle.Particle.update -> void

        Moves the particle, updates it's time remaining and uses this time remaining to calculate it's size
    -----------------------------------------------------------------------------------------------------------------"""
    def update(self):
        drag_factor = 1.0 - commons.DELTA_TIME * 2

        self.velocity = (self.velocity[0] * drag_factor, self.velocity[1] * drag_factor + self.gravity * commons.GRAVITY * commons.DELTA_TIME)
        self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE)

        self.life -= commons.DELTA_TIME  # Change life

        self.size = self.initSize * self.life / self.initLife  # Change size based on life and initial size

        if self.life <= 0:  # Remove the particle
            entity_manager.particles.remove(self)

    """================================================================================================================= 
        particle.Particle.draw -> void

        Draws the particle instance, optionally with an outline
    -----------------------------------------------------------------------------------------------------------------"""
    def draw(self):
        rect = Rect(self.position[0] - self.size * 0.5 - entity_manager.camera_position[0] + commons.WINDOW_WIDTH * 0.5,
                    self.position[1] - self.size * 0.5 - entity_manager.camera_position[1] + commons.WINDOW_HEIGHT * 0.5, self.size, self.size)
        pygame.draw.rect(commons.screen, self.colour, rect, 0)  # Draw 2 rects for each particle (fill and outline)
        if self.outline:
            pygame.draw.rect(commons.screen, (0, 0, 0), rect, 1)
