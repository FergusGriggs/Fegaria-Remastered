#projectile.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, math, random;
from pygame.locals import *;

import commons;
import tables;
import world;

import entity_manager;
import shared_methods;
import sound_manager;
import surface_manager;

class Projectile():
    def __init__(self, position, velocity, Type, ID, source, damage, knockback, crit, bounceNum, trail, maxLife = 5, GRAVITY = commons.GRAVITY, DRAG = 0.99):
        self.position = position;
        self.velocity = velocity;
        self.angle = math.atan2(velocity[1], velocity[0]);
        self.type = Type;
        self.ID = ID;
        self.source = source;
        self.damage = damage;
        self.knockback = knockback;
        self.crit = crit;
        self.trail = trail;
        self.trailTick = 0.1;
        self.bounceNum = bounceNum;
        self.size = tables.projectileData[ID][6];
        self.rect = Rect(self.position[0] - self.size * 0.5, self.position[1] - self.size * 0.5, self.size, self.size);
        self.life = int(maxLife);
        self.GRAVITY = GRAVITY;
        self.DRAG = DRAG;

    def Update(self):

        if self.life <= 0:
            entity_manager.projectiles.remove(self);
            return;
        else:
            self.life -= commons.DELTA_TIME;

        dragFactor = 1.0 - commons.DELTA_TIME;

        self.velocity = (self.velocity[0] * dragFactor, self.velocity[1] * dragFactor + commons.GRAVITY * self.GRAVITY * commons.DELTA_TIME);
        self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE);
        self.rect.left = self.position[0] - self.size * 0.5; #updating rect
        self.rect.top = self.position[1] - self.size * 0.5;
        self.blockposition = (math.floor(self.position[1] // commons.BLOCKSIZE), math.floor(self.position[0] // commons.BLOCKSIZE));
        if self.trail != None:
            if self.trailTick <= 0:
                if self.trail == "arrow":
                    self.trailTick += 0.025;
                    if commons.PARTICLES:
                        entity_manager.SpawnParticle((self.position[0] + self.size * 0.5, self.position[1] + self.size * 0.5), (90, 90, 90), life = 0.5, size = 7, magnitude = 0, GRAV = 0);
                #elif self.trail=="bullet":
                    #self.trailTick=1
                    #Particle((self.position[0]-campositionX+commons.WINDOW_WIDTH/2+self.size/2,self.position[1]-campositionY+commons.WINDOW_HEIGHT/2+self.size/2),(235,20,20),size=6,magnitude=0,GRAV=0,outline=False)
            else:
                self.trailTick -= commons.DELTA_TIME;
        if self.velocity[1] > 0:
            if self.position[1] > world.BORDER_SOUTH:
                self.position = (self.position[0], int(world.BORDER_SOUTH));
                self.velocity = (self.velocity[0], 0);
                self.grounded = True;
                
        xcollided = False;
        ycollided = False;
        
        for j in range(-1, 2):
            for i in range(-1, 2):
                #try:
                if world.TileInMapRange(self.blockposition[1] + j, self.blockposition[0] + i):
                    val = world.mapData[self.blockposition[1] + j][self.blockposition[0] + i][0];
                    if val not in tables.uncollidableBlocks:
                        if val not in tables.platformBlocks:
                            blockrect = Rect(commons.BLOCKSIZE * (self.blockposition[1] + j), commons.BLOCKSIZE * (self.blockposition[0] + i), commons.BLOCKSIZE, commons.BLOCKSIZE);   
                            if blockrect.colliderect(self.rect):
                                blockHitVal = int(val)
                                deltaX = self.position[0] - blockrect.centerx;
                                deltaY = self.position[1] - blockrect.centery;
                                if abs(deltaX) > abs(deltaY):
                                    if deltaX > 0:
                                        self.position = (blockrect.right + self.rect.width * 0.5, self.position[1]); #move proj right
                                    else:
                                        self.position = (blockrect.left - self.rect.width * 0.5, self.position[1]); #move proj left
                                    xcollided = True;
                                else:
                                    if deltaY > 0:
                                        if self.velocity[1] < 0:
                                            self.position = (self.position[0], blockrect.bottom + self.rect.height * 0.5)#move proj down
                                    else:
                                        if self.velocity[1] > 0:
                                            self.position = (self.position[0], blockrect.top - self.rect.height * 0.5)#move proj up             
                                    ycollided = True;
                #except:
                    #None;
        if ycollided or xcollided:
            if self.bounceNum > 0:
                self.bounceNum -= 1;
                if ycollided:
                    self.velocity = (self.velocity[0], -self.velocity[1]);
                else:
                    self.velocity = (-self.velocity[0], -self.velocity[1]);
            if self.bounceNum <= 0:
                entity_manager.projectiles.remove(self);
                if commons.PARTICLES:
                    colour = shared_methods.GetBlockAverageColour(blockHitVal);
                    velocityAngle = math.atan2(self.velocity[1], self.velocity[0]);
                    velocityMagnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2);
                    for i in range(int(4 * commons.PARTICLEDENSITY)):
                        entity_manager.SpawnParticle(self.position, colour, life = 0.5, angle = velocityAngle, spread = 0.8, magnitude = velocityMagnitude * random.random() * 0.7, GRAV = 0, size = 8);
                if commons.SOUND:
                    if self.type == "Bullet":
                        sound_manager.sounds[18].play();
                    else:
                        sound_manager.sounds[random.randint(3, 5)].play();
                return
        for enemy in entity_manager.enemies:
            if enemy.rect.colliderect(self.rect):
                if enemy.position[0] > entity_manager.clientPlayer.position[0]:
                    direction = 1;
                else:
                    direction = -1;
                enemy.Damage(self.damage, crit = self.crit, knockBack = self.knockback, direction = direction);
                entity_manager.projectiles.remove(self);
                return;

    def Draw(self):
        if self.type == "Arrow":
            angle = math.atan2(self.velocity[1], -self.velocity[0]) * 180 / math.pi - 90;
            surf = surface_manager.projectiles[self.ID].copy();
            surf = shared_methods.RotateSurface(surf, angle);
            commons.screen.blit(surf, (self.rect.left - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5, self.rect.top - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5));
        elif self.type == "Bullet":
            pygame.draw.circle(commons.screen,(60, 60, 60), (int(self.rect.centerx - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5), int(self.rect.centery - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5)), 3, 0);
        if commons.HITBOXES:
            pygame.draw.rect(commons.screen, (255, 0, 0), Rect(self.rect.left - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5, self.rect.top - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5,self.rect.width, self.rect.height), 1);