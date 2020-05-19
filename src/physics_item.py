#physics_item.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, math, random;
from pygame.locals import *;

import commons;
import tables;
import world;

import surface_manager;
import entity_manager;
import shared_methods;
import sound_manager;

class PhysicsItem():
    def __init__(self, position, ID, tier, amnt = 1, pickupDelay = 100, unique = False, item = None, velocity = None):
        global physicsItems;
        self.position = position;
        if velocity == None:
            angle = random.random() * math.pi * 2 - math.pi;
            initSpeed = random.random() * 3 + 1;
            self.velocity = (math.cos(angle) * initSpeed, math.sin(angle) * initSpeed);
        else:
            self.velocity = velocity;
        self.ID = ID;
        self.tier = tier;
        self.amnt = amnt;
        self.itemScale = 1.25;
        self.RenderImage();
        self.tiltAngle = 0;
        self.despawnCheckTick = 60;
        self.pickupDelay = pickupDelay;
        self.grounded = False;
        self.unique = unique;
        self.item = item;
        self.rect = Rect(position[0] - commons.BLOCKSIZE * 0.5 * self.itemScale, position[1] - commons.BLOCKSIZE * 0.5 * self.itemScale * 0.8, commons.BLOCKSIZE * self.itemScale * 0.8, commons.BLOCKSIZE * self.itemScale);
        
        self.stationary = False;
        self.timeStationary = 0;

    def RenderImage(self):
        self.image = pygame.transform.scale(surface_manager.items[self.ID].copy(), (int(commons.BLOCKSIZE * 1.414 * self.itemScale), int(commons.BLOCKSIZE * 1.414 * self.itemScale)));
        self.spacing = int((self.image.get_width() - commons.BLOCKSIZE) * 0.5);

    def CheckDespawn(self):
        if self.position[0] < entity_manager.clientPlayer.position[0] - commons.WINDOW_WIDTH * 0.5:
            entity_manager.physicsItems.remove(self);
        elif self.position[0] > entity_manager.clientPlayer.position[0] + commons.WINDOW_WIDTH * 0.5:
            entity_manager.physicsItems.remove(self);
        elif self.position[1] < entity_manager.clientPlayer.position[1] - commons.WINDOW_HEIGHT * 0.5:
            entity_manager.physicsItems.remove(self);
        elif self.position[1] > entity_manager.clientPlayer.position[1] + commons.WINDOW_HEIGHT * 0.5:
            entity_manager.physicsItems.remove(self);

    def Update(self):
        if self.despawnCheckTick <= 0:
            self.despawnCheckTick += 10;
            self.CheckDespawn();
        else:
            self.despawnCheckTick -= commons.DELTA_TIME;
        
        if not self.stationary:
            if math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2) < 1:
                self.timeStationary += commons.DELTA_TIME;

                if self.timeStationary > 1:
                    self.stationary = True;
            else:
                self.timeStationary = 0;

            if not self.grounded:
                self.velocity = (self.velocity[0], self.velocity[1] + commons.GRAVITY * commons.DELTA_TIME);
        
            dragFactor = 1.0 - commons.DELTA_TIME * 2;
            self.velocity = (self.velocity[0] * dragFactor, self.velocity[1] * dragFactor);
            self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE);
            self.rect.center = tuple(self.position);
            self.blockposition = (math.floor(self.position[1] // commons.BLOCKSIZE), math.floor(self.position[0] // commons.BLOCKSIZE));
            self.grounded = False;

        collide = not self.stationary;
        
        if self.ID not in entity_manager.clientPlayer.unPickupableItems:
            if self.pickupDelay <= 0:
                if abs(self.position[0] - entity_manager.clientPlayer.position[0]) < commons.BLOCKSIZE * 4 and abs(self.position[1] - entity_manager.clientPlayer.position[1]) < commons.BLOCKSIZE * 4:
                    collide = False;
                    self.stationary = False;
                    self.timeStationary = 0;

                    angle = math.atan2(entity_manager.clientPlayer.position[1] - self.position[1], entity_manager.clientPlayer.position[0] - self.position[0]);
                    self.velocity = (self.velocity[0] + math.cos(angle) * 1000 * commons.DELTA_TIME, self.velocity[1] + math.sin(angle) * 1000 * commons.DELTA_TIME);
                    if entity_manager.clientPlayer.rect.colliderect(self.rect):
                        entity_manager.physicsItems.remove(self);
                        itemAddData = entity_manager.clientPlayer.GiveItem(self.ID, amnt = self.amnt, unique = self.unique, item = self.item);
                            
                        if itemAddData[0]:
                            entity_manager.AddRecentPickup(self.ID, self.amnt, self.tier, entity_manager.clientPlayer.position, unique = self.unique, item = self.item);
                            if commons.SOUND:
                                if self.ID >= 21 and self.ID <= 24:
                                    sound_manager.sounds[23].play();
                                else:
                                    sound_manager.sounds[19].play();
                            return
                        else:
                            if self.unique:
                                entity_manager.SpawnPhysicsItem(entity_manager.clientPlayer.position, self.ID, self.tier, amnt = itemAddData[1], unique = True, item = self.item);
                            else:
                                entity_manager.SpawnPhysicsItem(entity_manager.clientPlayer.position, self.ID, self.tier, amnt = itemAddData[1]);
                            return;
            else:
                self.pickupDelay -= 1;

        if collide:
            for j in range(-2, 3):
                for i in range(-2, 3):
                    #try:
                    if world.TileInMapRange(self.blockposition[1] + j, self.blockposition[0] + i):
                        val = world.mapData[self.blockposition[1] + j][self.blockposition[0] + i][0];
                        if val not in tables.uncollidableBlocks:
                            blockrect = Rect(commons.BLOCKSIZE * (self.blockposition[1] + j), commons.BLOCKSIZE * (self.blockposition[0] + i), commons.BLOCKSIZE, commons.BLOCKSIZE);
                            if blockrect.colliderect(self.rect):
                                deltaX = self.position[0] - blockrect.centerx;
                                deltaY = self.position[1] - blockrect.centery;
                                if abs(deltaX) > abs(deltaY):
                                    if deltaX > 0:
                                        self.position = (blockrect.right + self.rect.width * 0.5,self.position[1]); #move item right
                                        self.velocity = (0, self.velocity[1]); #stop item horizontally
                                    else:
                                        self.position = (blockrect.left - self.rect.width * 0.5,self.position[1]); #move item left
                                        self.velocity = (0, self.velocity[1]); #stop item horizontally
                                else:
                                    if deltaY > 0:
                                        if self.velocity[1] < 0:
                                            self.position = (self.position[0], blockrect.bottom + self.rect.height * 0.5); #move item down
                                            self.velocity = (self.velocity[0], 0); #stop item vertically
                                    else:
                                        if self.velocity[1] > 0:
                                            self.position = (self.position[0], blockrect.top - self.rect.height * 0.5 + 1); #move item up
                                            self.velocity = (self.velocity[0], 0); #stop item vertically
                                            self.grounded = True;
                    #except:
                        #None;

    def Draw(self):
        newAngle = -int(self.velocity[0] * 10)
        if newAngle != self.tiltAngle:
            self.tiltAngle = newAngle;
            img = self.image.copy();
            img = shared_methods.RotateSurface(img, self.tiltAngle);
            commons.screen.blit(img, (self.rect.left - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5 - self.spacing * 0.5, self.rect.top - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5 - self.spacing * 0.5));
        else:
            commons.screen.blit(self.image, (self.rect.left - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5 - self.spacing * 0.5, self.rect.top - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5 - self.spacing * 0.5));
        
        if commons.HITBOXES:
            pygame.draw.rect(commons.screen, (255, 0, 0),Rect(self.rect.left - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5, self.rect.top - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5, self.rect.width, self.rect.height), 1);