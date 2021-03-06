#enemy.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, math, random;
from pygame.locals import *;

import tables;
import commons;
import world;

import entity_manager;
import surface_manager;
import sound_manager;
import shared_methods;

from item import Item;

# Returns an array of coin types from an integer value
def CoinsFromValue(value):
    coins = [0, 0, 0, 0];
    coins[0] = value // 1000000;
    value -= coins[0] * 1000000;
    coins[1] = value // 10000;
    value -= coins[1] * 10000;
    coins[2] = value // 100;
    value -= coins[2] * 100;
    coins[3] = value;
    return coins;

class Enemy():
    def __init__(self, position, enemyID):
        self.position = position;
        self.velocity = (0,0);
        self.ID = enemyID;
        self.name = str(tables.enemyData[self.ID][0]);
        self.type = str(tables.enemyData[self.ID][1]);
        self.HP = int(tables.enemyData[self.ID][2]);
        self.maxHP = int(self.HP);
        self.defense = int(tables.enemyData[self.ID][3]);
        self.knockBackResist = int(tables.enemyData[self.ID][3]);
        self.attackDamage = int(tables.enemyData[self.ID][5]);
        self.bloodColour = tuple(tables.enemyData[self.ID][6]);
        self.rect = Rect(self.position[0] - commons.BLOCKSIZE, self.position[1] - commons.BLOCKSIZE / 1.5, commons.BLOCKSIZE * 2, commons.BLOCKSIZE * 1.5);
        self.grounded = False;

        self.stopLeft = False;
        self.stopRight = False;

        self.movingLeft = False;
        self.movingRight = False;

        self.damageTick = 0;
        self.jumpTick = 1;
        self.despawnTick = 5;
        self.animationFrame = 0;
        self.gameID = random.randint(1000,9999);

        self.worldInvincibleTimer = 0.0;
        self.worldInvincible = False;

        self.alive = True;

    def Update(self):
        if self.alive:
            if self.worldInvincible:
                if self.worldInvincibleTimer <= 0.0:
                    self.worldInvincible = False;
                else:
                    self.worldInvincibleTimer -= commons.DELTA_TIME;

            self.stopLeft = False;
            self.stopRight = False;

            if self.despawnTick <= 0:
                self.despawnTick += 5;
                if self.CheckDespawn():
                    return;
            else:
                self.despawnTick -= commons.DELTA_TIME;

            if self.movingLeft:#moves enemy left
                if not self.stopLeft:
                    self.velocity = (-12.5, self.velocity[1]);
            if self.movingRight:#moves enemy right
                if not self.stopRight:
                    self.velocity = (12.5, self.velocity[1]);
            if not self.grounded:
                self.velocity = (self.velocity[0], self.velocity[1] + commons.GRAVITY * commons.DELTA_TIME);
            self.runAI();

            dragFactor = 1.0 - commons.DELTA_TIME * 4;

            self.velocity = (self.velocity[0] * dragFactor, self.velocity[1] * dragFactor);
            self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE);
            self.rect.left = self.position[0] - self.rect.width * 0.5;#updating rect
            self.rect.top = self.position[1] - self.rect.height * 0.5;
            self.blockpos = (math.floor(self.position[1] // commons.BLOCKSIZE), math.floor(self.position[0] // commons.BLOCKSIZE));
            self.grounded = False;
        
            if self.velocity[0] < 0:
                if self.position[0] < world.BORDER_WEST:
                    self.position = (int(world.BORDER_WEST), self.position[1]);
            elif self.velocity[0] > 0:
                if self.position[0] > world.BORDER_EAST:
                    self.position = (int(world.BORDER_EAST), self.position[1]);
            if self.velocity[1] > 0:
                if self.position[1] > world.BORDER_SOUTH:
                    self.position = (self.position[0], int(world.BORDER_SOUTH));
                    self.velocity = (self.velocity[0], 0);
                    self.grounded = True;
                    
            if self.damageTick <= 0:
                if entity_manager.clientPlayer.rect.colliderect(self.rect):
                    if entity_manager.clientPlayer.position[0] < self.position[0]:
                        direction = -1;
                    else:
                        direction = 1;

                    #normalizedPositionDifference = shared_methods.NormalizeVector2((entity_manager.clientPlayer.position[0] - self.position[0], entity_manager.clientPlayer.position[1] - self.position[1]));
                
                    entity_manager.clientPlayer.Damage(self.attackDamage, ["enemy", self.name], knockBack = 10, direction = direction, sourceVelocity = self.velocity);#(normalizedPositionDifference[0] * 10, normalizedPositionDifference[1] * 10)
                    self.damageTick += 0.5;
            else:
                self.damageTick -= commons.DELTA_TIME;

            for j in range(-2, 3):
                for i in range(-2, 3):
                    #try:
                    if world.TileInMapRange(self.blockpos[1] + j, self.blockpos[0] + i):
                        val = world.mapData[self.blockpos[1] + j][self.blockpos[0] + i][0];
                        if val not in tables.uncollidableBlocks:
                            blockrect = Rect(commons.BLOCKSIZE * (self.blockpos[1] + j), commons.BLOCKSIZE * (self.blockpos[0] + i), commons.BLOCKSIZE, commons.BLOCKSIZE);
                            if val in tables.platformBlocks:
                                platform = True;
                            else:
                                platform = False;
                            if blockrect.colliderect(int(self.rect.left - 1), int(self.rect.top + 2), 1, int(self.rect.height - 4)):
                                self.stopLeft = True; #is there a solid block left
                            if blockrect.colliderect(int(self.rect.right + 1), int(self.rect.top + 2), 1, int(self.rect.height - 4)):
                                self.stopRight = True; #is there a solid block right
                            if blockrect.colliderect(self.rect):
                                if not self.worldInvincible and val == 258:
                                    self.Damage(5, ["spike", "World"]);
                                
                                deltaX = self.position[0] - blockrect.centerx;
                                deltaY = self.position[1] - blockrect.centery;
                                if abs(deltaX) > abs(deltaY):
                                    if deltaX > 0:
                                        if not platform:
                                            self.position = (blockrect.right + self.rect.width * 0.5, self.position[1]); #move enemy right
                                            self.velocity = (0, self.velocity[1]); #stop enemy horizontally
                                    else:
                                        if not platform:
                                            self.position=(blockrect.left - self.rect.width * 0.5, self.position[1]); #move enemy left
                                            self.velocity=(0, self.velocity[1]); #stop enemy horizontally
                                else:
                                    if deltaY > 0:
                                        if self.velocity[1] < 0:
                                            if not platform:
                                                if Rect(self.rect.left + 3, self.rect.top, self.rect.width - 6, self.rect.height).colliderect(blockrect):
                                                    self.position = (self.position[0], blockrect.bottom + self.rect.height * 0.5); #move enemy down
                                                    self.velocity = (self.velocity[0], 0); #stop enemy vertically
                                    else:
                                        if self.velocity[1] > 0:
                                            if Rect(self.rect.left + 3, self.rect.top, self.rect.width - 6, self.rect.height).colliderect(blockrect):
                                                self.position = (self.position[0], blockrect.top - self.rect.height * 0.5 + 1); #move enemy up
                                                self.velocity = (self.velocity[0] * 0.5, 0); #slow down enemy horizontally and stop player vertically
                                                self.grounded = True;
                                                self.movingRight = False;
                                                self.movingLeft = False;
                    #except:
                        #None;

            self.Animate();

    def Damage(self, val, source, knockBack = 0, direction = 0, crit = False, sourceVelocity = None):
        if self.alive:
            if source[1] == "World" and self.worldInvincible:
                return;
            else:
                self.worldInvincibleTimer = 0.35;
                self.worldInvincible = True;

            self.movingRight = False;
            self.movingLeft = False;

            val -= self.defense;
            val *= 1.0 + random.random() * 0.1 - 0.05;
            if val < 1.0:
                val = 1.0;

            if crit:
                val *= 2.0;

            self.HP -= val;

            if self.HP < 0:
                self.HP = 0;

            entity_manager.AddDamageNumber(self.position, val, crit = crit);

            if self.HP > 0: #check if the enemy has died from damage
                if commons.SOUND:
                    sound_manager.sounds[13].play();
                if commons.PARTICLES:
                    velocityAngle = 0;
                    velocityMagnitude = 0;

                    if sourceVelocity != None:
                        velocityAngle = math.atan2(sourceVelocity[1], sourceVelocity[0]);
                        velocityMagnitude = math.sqrt(sourceVelocity[0] ** 2 + sourceVelocity[1] ** 2);
                    else: 
                        velocityAngle = math.atan2(self.velocity[1], self.velocity[0]);
                        velocityMagnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2);

                    for i in range(int(5 * commons.PARTICLEDENSITY)): #blood
                        particlePos = (self.position[0] + random.random() * self.rect.width - self.rect.width * 0.5, self.position[1] + random.random() * self.rect.height - self.rect.height * 0.5);
                        entity_manager.SpawnParticle(particlePos, self.bloodColour, life = 0.5, size = 10, angle = velocityAngle, spread = math.pi * 0.2, magnitude = random.random() * velocityMagnitude * 0.5);
            else:
                self.Kill(sourceVelocity);

            if knockBack != 0:
                remainingKnockback = max(0, knockBack - self.knockBackResist);
                self.velocity = (self.velocity[0] + direction * remainingKnockback * 3.0, remainingKnockback * -5.0);
            
    def Kill(self, sourceVelocity):
        if self.alive:
            self.alive = False;

            coinRange = tables.enemyData[self.ID][8];
            coinDrops = CoinsFromValue(random.randint(coinRange[0], coinRange[1]));
            itemDrops = tables.enemyData[self.ID][7];

            for i in range(len(coinDrops)):
                if coinDrops[i] > 0:
                    entity_manager.SpawnPhysicsItem(Item(24 - i, coinDrops[i]), self.position, pickupDelay = 10);

            for item in itemDrops:
                if random.randint(0, 1) <= item[3]:
                    amnt = random.randint(item[1], item[2]);
                    entity_manager.SpawnPhysicsItem(Item(item[0], amnt), self.position, pickupDelay = 10);

            if commons.PARTICLES:
                if sourceVelocity != None:
                        self.velocity = (self.velocity[0] + sourceVelocity[0], self.velocity[1] + sourceVelocity[1]);

                velocityAngle = math.atan2(self.velocity[1], self.velocity[0]);
                velocityMagnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2);

                for i in range(int(25 * commons.PARTICLEDENSITY)): #blood
                    particlePos = (self.position[0] + random.random() * self.rect.width - self.rect.width * 0.5, self.position[1] + random.random() * self.rect.height - self.rect.height * 0.5);
                    entity_manager.SpawnParticle(particlePos, self.bloodColour, life = 0.5, size = 10, angle = velocityAngle, spread = math.pi * 0.2, magnitude = random.random() * velocityMagnitude * 0.4);
            if commons.SOUND:
                sound_manager.sounds[14].play()#death sound

            entity_manager.enemies.remove(self);
                
    def Animate(self):
        if not self.grounded:
            if self.velocity[1] > 2:
                self.animationFrame = 2;
            elif self.velocity[1] <- 2:
                self.animationFrame = 1;
            else:
                self.animationFrame = 0;
        else:
            self.animationFrame = 0;

    def CheckDespawn(self):
        if self.position[0] < entity_manager.clientPlayer.position[0] - commons.MAX_ENEMY_SPAWN_TILES_X * 1.5 * commons.BLOCKSIZE:
            entity_manager.enemies.remove(self);
            return True;
        elif self.position[0] > entity_manager.clientPlayer.position[0] + commons.MAX_ENEMY_SPAWN_TILES_X * 1.5 * commons.BLOCKSIZE:
            entity_manager.enemies.remove(self);
            return True;
        elif self.position[1] < entity_manager.clientPlayer.position[1] - commons.MAX_ENEMY_SPAWN_TILES_Y * 1.5 * commons.BLOCKSIZE:
            entity_manager.enemies.remove(self);
            return True;
        elif self.position[1] > entity_manager.clientPlayer.position[1] + commons.MAX_ENEMY_SPAWN_TILES_Y * 1.5 * commons.BLOCKSIZE:
            entity_manager.enemies.remove(self);
            return True;
        return False;
        
    def Draw(self):
        left = self.rect.left - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5;
        top = self.rect.top - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5;
        commons.screen.blit(surface_manager.slimes[self.ID * 3 + self.animationFrame], (left, top));
        if self.HP < self.maxHP:
            hpFloat = self.HP / self.maxHP;
            col = (255 * (1 - hpFloat), 255 * hpFloat, 0);
            pygame.draw.rect(commons.screen, shared_methods.DarkenColour(col), Rect(left, top + 30, self.rect.width, 10), 0);
            pygame.draw.rect(commons.screen, col, Rect(left + 2, top + 32, (self.rect.width - 4) * hpFloat, 6), 0);
        if commons.HITBOXES:
            pygame.draw.rect(commons.screen, (255, 0, 0), Rect(self.rect.left - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5, self.rect.top - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5, self.rect.width, self.rect.height), 1);
            
    def runAI(self):
        if self.type == "Slime":
            if self.grounded:
                if self.jumpTick <= 0:
                    self.jumpTick += 0.5 + random.random();
                    if entity_manager.clientPlayer.position[0] < self.position[0]:
                        if entity_manager.clientPlayer.alive:
                            self.velocity = (-10, -45 + random.random());
                            self.movingLeft = True;
                        else:
                            self.velocity = (10, -45 + random.random());
                            self.movingRight = True;
                    else:
                        if entity_manager.clientPlayer.alive:
                            self.velocity = (10, -45 + random.random());
                            self.movingRight = True;
                        else:
                            self.velocity = (-10, -45 + random.random());
                            self.movingLeft = True;
                else:
                    self.jumpTick -= commons.DELTA_TIME;
