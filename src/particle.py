#particle.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, random, math;
from pygame.locals import *;

import commons;
import entity_manager;

class Particle():
    def __init__(self, position, colour, life, magnitude, size, angle, spread, GRAV, velocity = None, outline = True):
        self.position = position;
        self.life = life + (random.random() * life * 0.1 - life * 0.05); #how long it lasts for (randomized slightly)
        self.initLife = self.life;
        self.colour = colour;
        self.size = size + random.random() * size * 0.1 - size * 0.05; #how large it will be (randomized slightly)
        self.initSize = self.size;
        self.outline = outline;
        if velocity == None:
            if angle == None:
                angle = random.random() * math.pi * 2 - math.pi; #random angle
            else:
                angle += random.random() * spread - spread * 0.5; #set angle + random spread in set range
            self.velocity = (math.cos(angle) * magnitude, math.sin(angle) * magnitude); #velocity from angle and magnitude
        else:
            self.velocity = velocity;
        self.GRAV = GRAV; #gravity
        
    def Update(self):
        dragFactor = 1.0 - commons.DELTA_TIME * 2;

        self.velocity = (self.velocity[0] * dragFactor, self.velocity[1] * dragFactor + self.GRAV * commons.DELTA_TIME);
        self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE);

        self.life -= commons.DELTA_TIME; #change life

        self.size = self.initSize * self.life / self.initLife; #change size based on life and initial size

        if self.life <= 0: #if life<=0 remove the particle
            entity_manager.particles.remove(self);

    def Draw(self):
        rect = Rect(self.position[0] - self.size * 0.5 - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5, self.position[1] - self.size * 0.5  - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5, self.size, self.size);
        pygame.draw.rect(commons.screen, self.colour, rect, 0); #draw 2 rects for each particle (fill and outine)
        if self.outline:
            pygame.draw.rect(commons.screen, (0, 0, 0), rect, 1);