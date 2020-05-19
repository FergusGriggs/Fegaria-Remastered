#player.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, math, random, pickle;
from pygame.locals import *;

import tables;
import commons;
import world;

import shared_methods;
import surface_manager;
import entity_manager;
import sound_manager;

from item import Item;

def GetDeathMessage(name,source):
    string = tables.deathLines[source[0]][random.randint(0, len(tables.deathLines[source[0]]) - 1)];
    string = string.replace("<p>", name);
    string = string.replace("<w>", world.clientWorld.name);
    string = string.replace("<e>", source[1]);
    return string;   

def UpdatePlayerModelUsingModelData():
    commons.PLAYER_MODEL.sex = commons.PLAYER_MODEL_DATA[0];
    commons.PLAYER_MODEL.hairID = commons.PLAYER_MODEL_DATA[1];
    commons.PLAYER_MODEL.skinCol = commons.PLAYER_MODEL_DATA[2][0];
    commons.PLAYER_MODEL.hairCol = commons.PLAYER_MODEL_DATA[3][0];
    commons.PLAYER_MODEL.eyeCol = commons.PLAYER_MODEL_DATA[4][0];
    commons.PLAYER_MODEL.shirtCol = commons.PLAYER_MODEL_DATA[5][0];
    commons.PLAYER_MODEL.underShirtCol = commons.PLAYER_MODEL_DATA[6][0];
    commons.PLAYER_MODEL.trouserCol = commons.PLAYER_MODEL_DATA[7][0];
    commons.PLAYER_MODEL.shoeCol = commons.PLAYER_MODEL_DATA[8][0];

# Stores information about a players appearance
class Model():
    def __init__(self, sex, hairID, skinCol, hairCol, eyeCol, shirtCol, underShirtCol, trouserCol, shoeCol):
        self.sex = sex;
        self.skinCol = skinCol;
        self.hairID = hairID;
        self.hairCol = hairCol;
        self.eyeCol = eyeCol;
        self.shirtCol = shirtCol;
        self.underShirtCol = underShirtCol;
        self.trouserCol = trouserCol;
        self.shoeCol = shoeCol;
        

class Player():
    def __init__(self, position, model, name = "unassigned", HP = 100, maxHP = 100, hotbar = None, inventory = None, playTime = 0, creationDate = None):
        self.position = position;
        self.rect = Rect(self.position[0] - commons.PLAYER_WIDTH * 0.5, self.position[1] - commons.PLAYER_HEIGHT * 0.5, commons.PLAYER_WIDTH, commons.PLAYER_HEIGHT); #hitbox
        self.velocity = (0,0);
        self.model = model;
        self.name = name;

        if creationDate == None: 
            date = datetime.datetime.now();
            self.creationDate = str(str(date)[:19]);
        else:
            self.creationDate = creationDate;

        if hotbar == None:
            self.hotbar = [Item(25), Item(15), Item(19), Item(17), Item(4, amnt = 999), Item(28), None, None, None, None];
        else:
            self.hotbar = hotbar;
        self.hotbarIndex = 0;

        if inventory == None:
            self.inventory = [[None for i in range(4)]for j in range(10)];
        else:
            self.inventory = inventory;

        self.playTime = playTime;

        sprites = Player.RenderSprites(self.model);

        self.sprites = sprites[0];
        self.armSprites = sprites[1];

        self.animationTick = 0;
        self.animationFrame = 5;
        self.animationSpeed = 0.025;

        self.armAnimationFrame = 0;
        self.armAnimationTick = 0;
        self.armAnimationSpeed = 0.015;
        
        self.alive = True;
        self.respawnTick = 0;

        if HP == 0:
            self.HP = maxHP;
        else:
            self.HP = HP;

        self.maxHP = maxHP;

        hpcol = (255 * (1 - self.HP / self.maxHP), 255 * (self.HP / self.maxHP), 0);

        self.hpText = shared_methods.OutlineText(str(self.HP), hpcol, commons.DEFAULTFONT, outlineColour = (hpcol[0] * 0.5, hpcol[1] * 0.5, hpcol[2] * 0.5));
        self.hpXposition = commons.WINDOW_WIDTH - 10 - self.HP - self.hpText.get_width() * 0.5;

        self.grounded = True;

        self.movingLeft = False;
        self.movingRight = False;

        self.movingDown = False;
        self.movingDownTick = 0;
        self.stopMovingDown = False;

        self.stopLeft = False;
        self.stopRight = False;

        self.direction = 1;

        self.armSwing = False;
        
        self.lastBlockOn = 0;

        self.knockBackResist = 0;
        self.defense = 0;

        self.useTick = 0;
        self.canUse = False;
        self.armHold = False;
        self.holdAngle = 0;
        self.swingAngle = 0;
        self.itemSwing = False;
        self.currentItemImage = None;
        self.enemiesHit = [];

        self.unPickupableItems = [];

        self.hotbarImage = pygame.Surface((480, 48));
        self.hotbarImage.set_colorkey((255, 0, 255));

        self.inventoryImage = pygame.Surface((480, 192));
        self.inventoryImage.set_colorkey((255, 0, 255));

        self.chestImage = pygame.Surface((240, 192));
        self.chestImage.set_colorkey((255, 0, 255));

        self.blitCraftSurf = pygame.Surface((48, 288));
        self.blitCraftSurf.set_colorkey((255, 0, 255));

        self.craftableItemsSurf = pygame.Surface((48, 0));

        self.craftingMenuOffsetY = 120;
        self.craftingMenuOffsetVelocityY = 0;

        self.inventoryOpen = False;
        self.chestOpen = False;
        self.chestItems = None;

        self.oldInventoryPositions = [];

    def Update(self):
        if self.alive:
            if self.movingLeft:#moves player left
                if not self.stopLeft:
                    if self.movingDown:
                        self.velocity = (-5, self.velocity[1]);
                    else:
                        self.velocity = (-15, self.velocity[1]);
            if self.movingRight:#moves player right
                if not self.stopRight:
                    if self.movingDown:
                        self.velocity = (5, self.velocity[1]);
                    else:
                        self.velocity = (15, self.velocity[1]);

            dragFactor = 1.0 - commons.DELTA_TIME;

            self.velocity = (self.velocity[0] * dragFactor, self.velocity[1] * dragFactor + commons.GRAVITY * commons.DELTA_TIME );
            self.position = (self.position[0] + self.velocity[0] * commons.DELTA_TIME * commons.BLOCKSIZE, self.position[1] + self.velocity[1] * commons.DELTA_TIME * commons.BLOCKSIZE);

            self.rect.left = self.position[0] - commons.PLAYER_WIDTH * 0.5; #updating rect
            self.rect.top = self.position[1] - commons.PLAYER_HEIGHT * 0.5;

            self.blockPosition = (math.floor(self.position[1] // commons.BLOCKSIZE), math.floor(self.position[0] // commons.BLOCKSIZE));

            self.grounded = False;

            self.stopLeft = False;
            self.stopRight = False;

            fallDamaged = False; #so fall damage is only applied once
            
            if not self.canUse:
                if self.useTick <= 0:
                    self.armHold = False;
                    self.canUse = True;
                else:
                    self.useTick -= commons.DELTA_TIME;
            
            if self.velocity[0] < 0:
                if self.position[0] < world.BORDER_WEST:
                    self.position = (int(world.BORDER_WEST), self.position[1]);
            elif self.velocity[0] > 0:
                if self.position[0] > world.BORDER_EAST:
                    self.position = (int(world.BORDER_EAST), self.position[1]);
            if self.velocity[1] < 0:
                if self.position[1] < world.BORDER_NORTH:
                    self.position = (self.position[0], int(world.BORDER_NORTH));
                    self.velocity = (self.velocity[0], 0);
            elif self.velocity[1] > 0:
                if self.position[1] > world.BORDER_SOUTH:
                    self.position = (self.position[0], int(world.BORDER_SOUTH));
                    self.velocity = (self.velocity[0], 0);
                    self.grounded = True;

            if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                use = False;
                if self.inventoryOpen:
                    if not Rect(5, 5, 480, 244).collidepoint(commons.MOUSE_POS) and not Rect(commons.WINDOW_WIDTH - 50,commons.WINDOW_HEIGHT - 20, 50, 20).collidepoint(commons.MOUSE_POS) and not Rect(5, 270, 48, 288).collidepoint(commons.MOUSE_POS):
                        if self.chestOpen:
                            if not Rect(245, 265, 240, 192).collidepoint(commons.MOUSE_POS):
                                use = True;
                        else:
                            use = True;
                else:
                    use = True;
                if use and entity_manager.clientPrompt == None and commons.WAIT_TO_USE == False:
                    if pygame.mouse.get_pressed()[0]:
                        self.UseItem();
                    elif pygame.mouse.get_pressed()[2]:
                        self.UseItem(alt = True);

            collide = False;

            for j in range(-2,3):
                for i in range(-2,3):
                    #try:
                    if world.TileInMapRange(self.blockPosition[1] + j, self.blockPosition[0] + i):
                        if self.blockPosition[1] + j >= 0:
                            val = world.mapData[self.blockPosition[1] + j][self.blockPosition[0] + i][0];
                            if val not in tables.uncollidableBlocks:
                                blockrect = Rect(commons.BLOCKSIZE * (self.blockPosition[1] + j), commons.BLOCKSIZE * (self.blockPosition[0] + i), commons.BLOCKSIZE, commons.BLOCKSIZE);
                                
                                if val in tables.platformBlocks:
                                    platform = True;
                                else:
                                    platform = False;
                                    if blockrect.colliderect(int(self.rect.left - 1), int(self.rect.top + 2), 1, int(self.rect.height - 4)):
                                        self.stopLeft = True; #is there a solid block left
                                    if blockrect.colliderect(int(self.rect.right + 1), int(self.rect.top + 2), 1, int(self.rect.height - 4)):
                                        self.stopRight = True; #is there a solid block right        
                                if blockrect.colliderect(self.rect):
                                    deltaX = self.position[0] - blockrect.centerx;
                                    deltaY = self.position[1] - blockrect.centery;
                                    if abs(deltaX) > abs(deltaY):
                                        if deltaX > 0:
                                            if not platform:
                                                self.position = (blockrect.right + commons.PLAYER_WIDTH * 0.5, self.position[1]); #move player right
                                                self.velocity = (0, self.velocity[1]); #stop player horizontally
                                        else:
                                            if not platform:
                                                self.position = (blockrect.left - commons.PLAYER_WIDTH * 0.5,self.position[1]); #move player left
                                                self.velocity = (0, self.velocity[1]); #stop player horizontally
                                    else:
                                        if deltaY > 0:
                                            if self.velocity[1] < 0:
                                                if not platform:
                                                    if Rect(self.rect.left + 3, self.rect.top, self.rect.width - 6, self.rect.height).colliderect(blockrect):
                                                        self.position = (self.position[0], blockrect.bottom + commons.PLAYER_HEIGHT * 0.5); #move player down
                                                        self.velocity = (self.velocity[0], 0); #stop player vertically
                                        else:
                                            if self.velocity[1] > 0:
                                                if Rect(self.rect.left + 3, self.rect.top, self.rect.width - 6, self.rect.height).colliderect(blockrect):
                                                    if platform:
                                                        if self.movingDown:
                                                            collide = False;
                                                        else:
                                                            if self.velocity[1] < 5:
                                                                if self.position[1] + commons.BLOCKSIZE < blockrect.top:
                                                                    collide = True;
                                                            else:
                                                                collide = True;
                                                    else:
                                                        collide = True;
                                                    if collide:
                                                        if not fallDamaged:
                                                            if self.velocity[1] > 58:
                                                                damage = int((self.velocity[1] - 57) ** 2); #work out fall damage
                                                                self.Damage(damage, ["falling","World"]); #apply fall damage once
                                                                fallDamaged = True;
                                                        self.lastBlockOn = int(val);
                                                        self.movingDownTick = -1;
                                                        self.position = (self.position[0], blockrect.top - commons.PLAYER_HEIGHT * 0.5 + 1); #move player up
                                                        self.velocity = (self.velocity[0] * 0.5, 0); #slow down player horizontally and stop player vertically
                                                        self.grounded = True;     
                    #except:
                        #None;
            if self.stopMovingDown: #wait before setting movingdown to false based on player y velocity
                if self.movingDownTick < 0:
                    self.movingDown = False;
                    self.stopMovingDown = False;
                else:
                    self.movingDownTick -= self.velocity[1];

            if self.inventoryOpen:
                self.craftingMenuOffsetVelocityY *= 0.9;
                self.craftingMenuOffsetY += self.craftingMenuOffsetVelocityY;
                if self.craftingMenuOffsetY < -len(self.craftableItems) * 48 + 168:
                    self.craftingMenuOffsetY = -len(self.craftableItems) * 48 + 168;
                elif self.craftingMenuOffsetY > 120:
                    self.craftingMenuOffsetY = 120;

        else: # if player is not alive, wait to respawn
            if self.respawnTick > 0:
                self.respawnTick -= commons.DELTA_TIME;
            else:
                self.Respawn();

        self.UpdateInventoryOldSlots();

    def Damage(self, value, source, knockBack = 0, direction = None):
        if not commons.CREATIVE and self.alive:
            value -= self.defense;
            value += random.randint(-1, 1);
            if value < 1:
                value = 1;
            self.HP -= value;

            entity_manager.AddDamageNumber(self.position, value, colour = (240, 20, 20));

            if self.HP < 0:
                self.HP = 0;
            if knockBack != 0:
                valx = knockBack*(1-self.knockBackResist);
                valy = -3 * (1 - self.knockBackResist);
                self.velocity = (direction * valx, valy);
            if self.HP > 0: #check if the player has died from damage
                if commons.SOUND:
                    sound_manager.sounds[random.randint(7, 9)].play(); #random hurt sound
                if commons.PARTICLES:
                    velocityAngle = math.atan2(self.velocity[1], self.velocity[0]);
                    velocityMagnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2);
                    for i in range(int(10 * commons.PARTICLEDENSITY)): #blood
                        entity_manager.SpawnParticle((self.position[0] + random.random() * commons.PLAYER_WIDTH - commons.PLAYER_WIDTH * 0.5, self.position[1] + random.random() * commons.PLAYER_HEIGHT- commons.PLAYER_HEIGHT * 0.5), (230, 0, 0), life = 1, angle = velocityAngle, size = 10, spread = math.pi * 0.2, magnitude = random.random() * velocityMagnitude);
            else:
                self.Kill(source);
        hpFloat = self.HP / self.maxHP;
        self.hpText = shared_methods.OutlineText(str(self.HP), ((1 - hpFloat) * 255, hpFloat * 255, 0), commons.DEFAULTFONT, outlineColour = ((1 - hpFloat) * 180, hpFloat * 180, 0));
        self.hpXposition = commons.WINDOW_WIDTH - 10 - hpFloat * 100 - self.hpText.get_width() * 0.5;
            
    def Kill(self, source):
        if self.alive:
            entity_manager.AddMessage(GetDeathMessage(self.name, source), (255, 255, 255));
            self.respawnTick = 5.0; #respawn delay
            self.alive = False;
            self.positionDiff = (0, 0);
            if commons.PARTICLES:
                velocityAngle = math.atan2(self.velocity[1], self.velocity[0]);
                velocityMagnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2);
                for i in range(int(35 * commons.PARTICLEDENSITY)): #more blood
                    entity_manager.SpawnParticle((self.position[0] + random.random() * commons.PLAYER_WIDTH - commons.PLAYER_WIDTH * 0.5, self.position[1] + random.random() * commons.PLAYER_HEIGHT- commons.PLAYER_HEIGHT * 0.5), (230, 0, 0), life = 1, angle = velocityAngle, size = 10, spread = 0.9, magnitude = random.random() * velocityMagnitude * 0.8);
            if commons.SOUND:
                sound_manager.sounds[11].play(); #death sound
            self.velocity = (0, 0);
        
    def Respawn(self):
        self.position = tuple(world.clientWorld.spawnPosition); #set position to world.clientWorld.spawnPoint
        self.velocity = (0, 0);
        self.alive = True;
        self.HP = int(self.maxHP); #reset hp
        self.hpText = shared_methods.OutlineText(str(self.HP), (0, 255, 0), commons.DEFAULTFONT, outlineColour = (0, 180, 0));
        self.hpXposition = commons.WINDOW_WIDTH - 10 - 100 - self.hpText.get_width() * 0.5;

    def RenderCurrentItemImage(self):
        if not commons.IS_HOLDING_ITEM:
            item = self.hotbar[self.hotbarIndex];
        else:
            item = commons.ITEM_HOLDING;
        if item != None:
            self.currentItemImage = surface_manager.items[item.ID].copy();
            scale = item.size / tables.itemData[item.ID][3][3];
            self.currentItemImage = pygame.transform.scale(self.currentItemImage, (int(self.currentItemImage.get_width() * scale), int(self.currentItemImage.get_height() * scale)));

    def Animate(self):
        if self.animationTick <= 0: #happens every 'animationSpeed' frames
            self.animationTick += self.animationSpeed;
            if self.grounded:
                if self.movingLeft: #if moving left, cycle through left frames
                    if  self.animationFrame < 29:
                         self.animationFrame += 1;
                    else:
                        self.animationFrame = 17;
                    return
                elif self.movingRight:#if moving right, cycle through right frames
                    if  self.animationFrame < 14:
                         self.animationFrame += 1;
                    else:
                        self.animationFrame = 2;
                    return
                else:#if idle put arms down
                    if self.direction == 0:
                        self.animationFrame = 15;
                    elif self.direction == 1:
                        self.animationFrame = 0; 
            else:#puts arms in the air if not grounded
                if self.direction == 0:
                    self.animationFrame = 16;
                elif self.direction == 1:
                    self.animationFrame = 1;
        else:
            self.animationTick -= commons.DELTA_TIME;

        if self.armAnimationTick <= 0:
            self.armAnimationTick += self.armAnimationSpeed;

            if self.armSwing:
                if self.direction == 1:
                    if self.armAnimationFrame < 3:
                        self.armAnimationFrame += 1;
                    else:
                        if self.movingRight:
                            self.armAnimationFrame = 6;
                        else:
                            self.armAnimationFrame = 26;
                        self.armSwing = False;
                else:
                    if self.armAnimationFrame < 23 and self.armAnimationFrame >= 20:
                        self.armAnimationFrame += 1;
                    else:
                        if self.movingRight:
                            self.armAnimationFrame = 6;
                        else:
                            self.armAnimationFrame = 26;
                        self.armSwing = False;
            else:
                if self.grounded:
                    if self.movingLeft: #if moving left, cycle through left frames
                        if  self.armAnimationFrame < 38:
                             self.armAnimationFrame += 1;
                        else:
                            self.armAnimationFrame = 26;
                        return
                    elif self.movingRight: #if moving right, cycle through right frames
                        if  self.armAnimationFrame < 18:
                             self.armAnimationFrame += 1;
                        else:
                            self.armAnimationFrame = 6;
                        return
                    else:#if idle put arms down
                        if self.direction == 0:
                            self.armAnimationFrame = 20;
                        elif self.direction == 1:
                            self.armAnimationFrame = 0  ;
                else:#puts arms in the air if not grounded
                    if self.direction == 0:
                        self.armAnimationFrame = 25;
                    elif self.direction == 1:
                        self.armAnimationFrame = 5;
        else:
            self.armAnimationTick -= commons.DELTA_TIME;

        if self.armHold:
            if self.direction == 1:
                self.armAnimationFrame = 19;
            else:
                self.armAnimationFrame = 39;

                    
    def RenderSprites(model, directions = 2, armFrameCount = 20, torsoFrameCount = 15): #create an array of surfs for the current character used for animation/blitting
        sprites = [];
        armSprites = [];
        for j in range(directions): #for both directions
            hair = shared_methods.ColourSurface(surface_manager.hair[model.hairID], model.hairCol);
            if j == 1: #flip if necessary
                hair = pygame.transform.flip(hair, True, False);
            torso = shared_methods.ColourSurface(surface_manager.torsos[0], model.shirtCol);
            if j == 0: #flip if necessary
                torso = pygame.transform.flip(torso, True, False);
            head = shared_methods.ColourSurface(surface_manager.hair[9], model.skinCol);
            pygame.draw.rect(head, (255, 254, 255), Rect(20, 22, 4, 4), 0);
            pygame.draw.rect(head, model.eyeCol, Rect(22, 22, 2, 4), 0);
            if j == 1: #flip if necessary
                head = pygame.transform.flip(head, True, False);
            for i in range(torsoFrameCount): #all animation frames for one direction
                bodySurf=pygame.Surface((44, 75));
                bodySurf.fill((255, 0, 255));
                bodySurf.set_colorkey((255, 0, 255)); #create the surf for the whole player with a colourkey of (255, 0, 255)
                trousers=shared_methods.ColourSurface(surface_manager.torsos[i + 1], model.trouserCol)
                if j == 0: #flip if necessary
                    trousers = pygame.transform.flip(trousers, True, False);
                shoes = shared_methods.ColourSurface(surface_manager.torsos[i + 16], model.shoeCol);
                if j == 0:#flip if necessary
                    shoes = pygame.transform.flip(shoes, True, False);
                bodySurf.blit(torso, (0, 4));
                bodySurf.blit(trousers, (0, 4));
                bodySurf.blit(shoes, (0, 4));
                bodySurf.blit(head, (0, 0));
                bodySurf.blit(hair, (0, 0));
                
                sprites.append(bodySurf);
            for i in range(armFrameCount): #all animation frames for one direction
                armSurf = pygame.Surface((44, 75));
                armSurf.fill((255, 0, 255));
                armSurf.set_colorkey((255, 0, 255));

                arms = shared_methods.ColourSurface(surface_manager.torsos[i + 31], model.underShirtCol);
                if j == 0: #flip if necessary
                    arms = pygame.transform.flip(arms, True, False);
                    
                hands = shared_methods.ColourSurface(surface_manager.torsos[i + 51], model.skinCol);
                if j == 0: #flip if necessary
                    hands = pygame.transform.flip(hands, True, False);
                
                armSurf.blit(arms, (0, 4));
                armSurf.blit(hands, (0, 4));

                armSprites.append(armSurf);
        return [sprites, armSprites];
                
    def UseItem(self, alt = False):
        swing = False;
        if not commons.IS_HOLDING_ITEM:
            item = self.hotbar[self.hotbarIndex];
        else:
            item=commons.ITEM_HOLDING
        screenpositionx = self.position[0] - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5;
        screenpositiony = self.position[1] - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5;
        if not alt:
            if item != None:
                if "block" in item.tags:
                    if math.sqrt((screenpositionx - commons.MOUSE_POS[0]) ** 2 + (screenpositiony - commons.MOUSE_POS[1]) ** 2) < commons.BLOCKSIZE * 6 or commons.CREATIVE:
                        blockPosition = commons.TILE_POSITION_MOUSE_HOVERING;
                        if world.TileInMapRange(blockPosition[0], blockPosition[1]):
                            blockrect = Rect(commons.BLOCKSIZE*blockPosition[0], commons.BLOCKSIZE*blockPosition[1]+1, commons.BLOCKSIZE, commons.BLOCKSIZE);
                            if not blockrect.colliderect(self.rect):
                                if "special" in item.tags:
                                    canPlace = True;
                                    relativeData = tables.itemData[item.ID][5];
                                    for i in range(len(relativeData)):
                                        if not world.mapData[blockPosition[0] + relativeData[i][1]][blockPosition[1] + relativeData[i][2]][0] == -1:
                                            canPlace = False;
                                    requiredSolids = tables.itemData[item.ID][6];
                                    for i in range(len(requiredSolids)):
                                        if world.mapData[blockPosition[0] + requiredSolids[i][0]][blockPosition[1] + requiredSolids[i][1]][0] in tables.uncollidableBlocks:
                                            canPlace = False;
                                    if canPlace:
                                        for i in range(len(relativeData)):
                                            world.mapData[blockPosition[0] + relativeData[i][1]][blockPosition[1] + relativeData[i][2]][0] =+ relativeData[i][0];
                                            world.UpdateTerrainSurface(blockPosition[0] + relativeData[i][1], blockPosition[1] + relativeData[i][2]);
                                        if not commons.IS_HOLDING_ITEM:
                                            self.hotbar[self.hotbarIndex].amnt -= 1;
                                            dat = ["H", self.hotbarIndex];
                                            if dat not in self.oldInventoryPositions:
                                                self.oldInventoryPositions.append(dat);
                                            if self.hotbar[self.hotbarIndex].amnt <= 0:
                                                self.hotbar[self.hotbarIndex] = None;
                                        else:
                                            commons.WAIT_TO_USE = True;
                                            commons.ITEM_HOLDING.amnt -= 1;
                                            if commons.ITEM_HOLDING.amnt <= 0:
                                                commons.ITEM_HOLDING = None;
                                                commons.IS_HOLDING_ITEM = False;
                                        if "chest" in item.tags:
                                            world.clientWorld.chestData.append([blockPosition, [[None for j in range(4)] for i in range(5)]]);
                                        if commons.SOUND:
                                            sound_manager.PlayHitSfx(item.ID);
                                        swing = True;

                                else:
                                    if commons.SHIFT_ACTIVE:
                                        if world.mapData[blockPosition[0]][blockPosition[1]][1] == -1:
                                            if world.GetNeighborCount(blockPosition[0], blockPosition[1], tile = 1) > 0:
                                                if not commons.CREATIVE:
                                                    self.hotbar[self.hotbarIndex].amnt -= 1;
                                                    dat = ["H", self.hotbarIndex];
                                                    if dat not in self.oldInventoryPositions:
                                                        self.oldInventoryPositions.append(dat);
                                                    if self.hotbar[self.hotbarIndex].amnt <= 0:
                                                        self.hotbar[self.hotbarIndex] = None;
                                                tileID = tables.itemData[item.ID][5];
                                                world.mapData[blockPosition[0]][blockPosition[1]][1] = tileID;
                                                world.UpdateTerrainSurface(blockPosition[0], blockPosition[1]);
                                                if commons.SOUND:
                                                    sound_manager.PlayHitSfx(item.ID);
                                                swing = True;
                                    else:
                                        if world.mapData[blockPosition[0]][blockPosition[1]][0] == -1:
                                            if world.GetNeighborCount(blockPosition[0], blockPosition[1]) > 0:
                                                if not commons.CREATIVE:
                                                    if not commons.IS_HOLDING_ITEM:
                                                        self.hotbar[self.hotbarIndex].amnt -= 1;
                                                        dat = ["H", self.hotbarIndex];
                                                        if dat not in self.oldInventoryPositions:
                                                            self.oldInventoryPositions.append(dat);
                                                        if self.hotbar[self.hotbarIndex].amnt <= 0:
                                                            self.hotbar[self.hotbarIndex] = None;
                                                    else:
                                                        commons.WAIT_TO_USE = True;
                                                        commons.ITEM_HOLDING.amnt -= 1;
                                                        if commons.ITEM_HOLDING.amnt <= 0:
                                                            commons.ITEM_HOLDING = None;
                                                            commons.IS_HOLDING_ITEM = False;
                                                world.mapData[blockPosition[0]][blockPosition[1]][0] = tables.itemData[item.ID][5];
                                                world.UpdateTerrainSurface(blockPosition[0], blockPosition[1]);
                                                if commons.SOUND:
                                                    sound_manager.PlayHitSfx(item.ID);
                                                swing = True;

                elif "pickaxe" in item.tags:
                    if self.canUse or commons.CREATIVE:
                        self.enemiesHit = [];
                        self.canUse = False;
                        self.useTick = int(item.attackSpeed) * 0.01;
                        swing = True;
                        self.itemSwing = True;
                        if self.direction == 1:
                            self.swingAngle = 10;
                        else:
                            self.swingAngle = 65;
                        if commons.SOUND:
                            sound_manager.sounds[15].play();
                        if math.sqrt((screenpositionx - commons.MOUSE_POS[0]) ** 2 +(screenpositiony - commons.MOUSE_POS[1]) ** 2) < commons.BLOCKSIZE * 6 or commons.CREATIVE:
                            if commons.SHIFT_ACTIVE:
                                datIndex = 1; #wall or block being clicked
                            else:
                                datIndex = 0;
                            blockPosition = commons.TILE_POSITION_MOUSE_HOVERING;
                            if world.TileInMapRange(blockPosition[0], blockPosition[1]):
                                tileID = world.mapData[blockPosition[0]][blockPosition[1]][datIndex];
                                if tileID >= 255:
                                    world.DestroySpecialTile(blockPosition[0], blockPosition[1]);
                                    if commons.SOUND:
                                        sound_manager.PlayHitSfx(0);
                                else:
                                    if tileID != -1:
                                        itemID = tables.tileData[tileID][0];
                                        # Remove Grass from dirt
                                        if tileID == 5:
                                            world.mapData[blockPosition[0]][blockPosition[1]][datIndex] = 0;
                                        else:
                                            world.mapData[blockPosition[0]][blockPosition[1]][datIndex] = -1;
                                            
                                            entity_manager.SpawnPhysicsItem(((blockPosition[0] + 0.5) * commons.BLOCKSIZE, (blockPosition[1] + 0.5) * commons.BLOCKSIZE), itemID, tables.itemData[itemID][3][7], pickupDelay = 10);
                                        world.UpdateTerrainSurface(blockPosition[0], blockPosition[1]);
                                        if tileID in tables.platformBlocks:  
                                            colour = pygame.transform.average_color(surface_manager.tiles[tileID], Rect(commons.BLOCKSIZE / 8, commons.BLOCKSIZE / 8, commons.BLOCKSIZE * 3 / 4, commons.BLOCKSIZE / 4));
                                        else:
                                            colour = pygame.transform.average_color(surface_manager.tiles[tileID]);
                                        
                                        if commons.SOUND:
                                            sound_manager.PlayHitSfx(tileID);
                                        if commons.PARTICLES:
                                            for i in range(int(random.randint(2, 3) * commons.PARTICLEDENSITY)):
                                                entity_manager.SpawnParticle((blockPosition[0] * commons.BLOCKSIZE, blockPosition[1] * commons.BLOCKSIZE), colour, size = 10, life = 1, angle = -math.pi * 0.5, spread = math.pi, GRAV = 0.05);
                elif "melee" in item.tags:
                    if self.canUse:
                        self.enemiesHit = [];
                        self.canUse = False;
                        self.useTick = int(item.attackSpeed) * 0.01;
                        if commons.SOUND:
                            sound_manager.sounds[15].play();
                        swing = True;
                        self.itemSwing = True;
                        if self.direction == 1:
                            self.swingAngle = 10;
                        else:
                            self.swingAngle = 65;
                        
                if swing:
                    if not self.armSwing:
                        self.armSwing = True;
                        if self.direction == 1:
                            self.armAnimationFrame = 1;
                        else:
                            self.armAnimationFrame = 20;
                elif "ranged" in item.tags:
                    if self.canUse:
                        if commons.MOUSE_POS[0] < screenpositionx:
                            self.direction = 0;
                        else:self.direction = 1;
                        self.canUse = False;
                        self.armHold = True;
                        self.holdAngle = math.atan2(-commons.MOUSE_POS[1] + commons.WINDOW_HEIGHT * 0.5, abs(commons.MOUSE_POS[0] - commons.WINDOW_WIDTH * 0.5));
                        self.useTick = int(item.attackSpeed) * 0.01;
                        angle = math.atan2(commons.MOUSE_POS[1] - screenpositiony, commons.MOUSE_POS[0] - screenpositionx);
                        weaponDamage = item.attackDamage;
                        weaponKnockback = item.knockback;
                        weaponvelocity = item.velocity;
                        if "gun" in item.tags:
                            ammoID = 1;
                        elif "bow" in item.tags:
                            ammoID = 0;
                        source = self.name;
                        crit = False;
                        if random.random() < item.critStrikeChance:
                            crit = True;
                        entity_manager.SpawnProjectile(self.position, angle, weaponDamage, weaponKnockback, weaponvelocity, ammoID, source, crit);
        else:
            if math.sqrt((screenpositionx - commons.MOUSE_POS[0]) ** 2 + (screenpositiony - commons.MOUSE_POS[1]) ** 2) < commons.BLOCKSIZE * 6 or commons.CREATIVE:
                blockPosition = commons.TILE_POSITION_MOUSE_HOVERING;
                val = world.mapData[blockPosition[0]][blockPosition[1]][0];
                if val >= 255:
                    origin = tables.specialTileData[val - 255][0];
                    world.UseSpecialTile(blockPosition[0] + origin[0], blockPosition[1] + origin[1]);
                
    def GiveItem(self, ID, amnt = 1, position = None, unique = False, item = None):
        if position==None:
            coin = False;
            if ID >= 21 and ID <= 23:
                coin = True;
            searchData = self.FindExistingItemStacks(ID); #find all suitable slots
            while len(searchData[0]) > 0 and amnt > 0: #fill all stacks of the same item first
                fillCount = searchData[0][0][2]; #work out how many to add to the stack
                amnt -= fillCount;
                if amnt < 0:
                    fillCount += amnt;
                if searchData[0][0][0] == "H": #if item in hotbar increase the amnt by the calculated fillcount
                    self.hotbar[searchData[0][0][1]].amnt += fillCount;
                    if coin:
                        if self.hotbar[searchData[0][0][1]].amnt == tables.itemData[ID][3][10]:
                            if amnt > 0:
                                self.hotbar[searchData[0][0][1]].amnt = amnt;
                            else:
                                self.hotbar[searchData[0][0][1]] = None;
                            self.GiveItem(ID + 1);
                            amnt = 0;
                elif searchData[0][0][0] == "I": #if item in inventory increase the amnt by the calculated fillcount
                    self.inventory[searchData[0][0][1][0]][searchData[0][0][1][1]].amnt += fillCount;
                    if coin:
                        if self.inventory[searchData[0][0][1][0]][searchData[0][0][1][1]].amnt == tables.itemData[ID][3][10]:
                            if amnt > 0:
                                self.inventory[searchData[0][0][1][0]][searchData[0][0][1][1]].amnt = amnt;
                            else:
                                self.inventory[searchData[0][0][1][0]][searchData[0][0][1][1]] = None;
                            self.GiveItem(ID + 1);
                            amnt = 0;
                elif searchData[0][0][0]=="C": #if item in inventory increase the amnt by the calculated fillcount
                    self.chestItems[searchData[0][0][1][0]][searchData[0][0][1][1]].amnt += fillCount;
                    if coin:
                        if self.chestItems[searchData[0][0][1][0]][searchData[0][0][1][1]].amnt == tables.itemData[ID][3][10]:
                            if amnt > 0:
                                self.chestItems[searchData[0][0][1][0]][searchData[0][0][1][1]].amnt = amnt;
                            else:
                                self.chestItems[searchData[0][0][1][0]][searchData[0][0][1][1]] = None;
                            self.GiveItem(ID + 1);
                            amnt = 0;
                dat = [searchData[0][0][0], searchData[0][0][1]];
                if dat not in self.oldInventoryPositions:
                    self.oldInventoryPositions.append(dat); #flag the position for a surface update
                searchData[0].remove(searchData[0][0]); #remove the used data
            while len(searchData[1]) > 0 and amnt > 0: #no stacks left to fill so fill empty slots
                fillCount = searchData[1][0][2]; #work out how many to add to the stack
                amnt -= fillCount;
                if amnt < 0:
                    fillCount += amnt;
                if searchData[1][0][0] == "H": #if item in hotbar increase the amnt by the calculated fillcount
                    if unique:
                        self.hotbar[searchData[1][0][1]] = item;
                    else:
                        self.hotbar[searchData[1][0][1]] = Item(ID, amnt = fillCount);
                elif searchData[1][0][0] == "I": #if item in inventory increase the amnt by the calculated fillcount
                    if unique:
                        self.inventory[searchData[1][0][1][0]][searchData[1][0][1][1]] = item;
                    else:
                        self.inventory[searchData[1][0][1][0]][searchData[1][0][1][1]] = Item(ID, amnt = fillCount);
                elif searchData[1][0][0] == "C": #if item in chest increase the amnt by the calculated fillcount
                    if unique:
                        self.chestItems[searchData[1][0][1][0]][searchData[1][0][1][1]] = item;
                    else:
                        self.chestItems[searchData[1][0][1][0]][searchData[1][0][1][1]] = Item(ID, amnt = fillCount);
                dat = [searchData[1][0][0], searchData[1][0][1]];
                if dat not in self.oldInventoryPositions:
                    self.oldInventoryPositions.append(dat); #flag the position for a surface update
                searchData[1].remove(searchData[1][0]); #remove the used data
            if amnt <= 0:
                return [True];
            else:
                if ID not in self.unPickupableItems:
                    self.unPickupableItems.append(ID);
                return [False, amnt];
        else:
            if position[0] == "H":
                if self.hotbar[position[1]] == None:
                    if unique:
                        self.hotbar[position[1]] = item;
                    else:
                        self.hotbar[position[1]] = Item(ID, amnt = amnt);
                    return [0];
                elif self.hotbar[position[1]].ID == ID:
                    if not unique:
                        self.hotbar[position[1]].amnt += amnt;
                        if self.hotbar[position[1]].amnt > tables.itemData[ID][3][10]:
                            amnt = self.hotbar[position[1]].amnt - tables.itemData[ID][3][10];
                            self.hotbar[position[1]].amnt = tables.itemData[ID][3][10];
                            return [1, amnt];
                        else:
                            return [0];
                    else:
                        item = self.hotbar[position[1]];
                        return [2, item, "H"];
                elif self.hotbar[position[1]].ID != ID:
                    item = self.hotbar[position[1]];
                    return [2, item, "H"];
            elif position[0] == "I":
                if self.inventory[position[1][0]][position[1][1]] == None:
                    if unique:
                        self.inventory[position[1][0]][position[1][1]] = item;
                    else:
                        self.inventory[position[1][0]][position[1][1]] = Item(ID, amnt = amnt);
                    return [0]
                elif self.inventory[position[1][0]][position[1][1]].ID == ID:
                    if not unique:
                        self.inventory[position[1][0]][position[1][1]].amnt += amnt
                        if self.inventory[position[1][0]][position[1][1]].amnt > tables.itemData[ID][3][10]:
                            amnt = self.inventory[position[1][0]][position[1][1]].amnt - tables.itemData[ID][3][10];
                            self.inventory[position[1][0]][position[1][1]].amnt = tables.itemData[ID][3][10];
                            return [1, amnt];
                        else:
                            return [0];
                    else:
                        item = self.inventory[position[1][0]][position[1][1]];
                        return [2, item, "I"];
                elif self.inventory[position[1][0]][position[1][1]].ID != ID:
                    item = self.inventory[position[1][0]][position[1][1]];
                    return [2, item, "I"];
            elif position[0]=="C":
                if self.chestItems[position[1][0]][position[1][1]] == None:
                    if unique:
                        self.chestItems[position[1][0]][position[1][1]] = item;
                    else:
                        self.chestItems[position[1][0]][position[1][1]] = Item(ID, amnt = amnt);
                    return [0];
                elif self.chestItems[position[1][0]][position[1][1]].ID == ID:
                    if not unique:
                        self.chestItems[position[1][0]][position[1][1]].amnt += amnt;
                        if self.chestItems[position[1][0]][position[1][1]].amnt > tables.itemData[ID][3][10]:
                            amnt = self.chestItems[position[1][0]][position[1][1]].amnt - tables.itemData[ID][3][10];
                            self.chestItems[position[1][0]][position[1][1]].amnt = tables.itemData[ID][3][10];
                            return [1, amnt];
                        else:
                            return [0];
                    else:
                        item = self.chestItems[position[1][0]][position[1][1]];
                        return [2, item, "C"];
                elif self.chestItems[position[1][0]][position[1][1]].ID != ID:
                    item = self.chestItems[position[1][0]][position[1][1]];
                    return [2, item, "C"];      
            
    def RemoveItem(self, position):
        if position[0] == "H":
            item = self.hotbar[position[1]];
            self.hotbar[position[1]] = None;
        elif position[0] == "I":
            item = self.inventory[position[1][0]][position[1][1]];
            self.inventory[position[1][0]][position[1][1]] = None;
        elif position[0] == "C":
            item = self.chestItems[position[1][0]][position[1][1]];
            self.chestItems[position[1][0]][position[1][1]] = None;
        if position not in self.oldInventoryPositions:
            self.oldInventoryPositions.append(position);
        return item;
        
    def FindExistingItemStacks(self, ID, searchHotbar = True, searchInventory = True): #finds existing item stacks and free spaces
        #[which array, position in array, amount]
        existingSpaces = [];
        freeSpaces = [];
        
        if searchHotbar: #search hotbar
            for i in range(10):
                if self.hotbar[i] == None:
                    freeSpaces.append(["H", i, int(tables.itemData[ID][3][10])]);
                elif self.hotbar[i].ID == ID:
                    available = int(tables.itemData[ID][3][10]) - self.hotbar[i].amnt;
                    if available > 0:
                        existingSpaces.append(["H", i, available]);
        
        if searchInventory: #search inventory
            for j in range(4):
                for i in range(10):
                    if self.inventory[i][j] == None:
                        freeSpaces.append(["I", (i, j), int(tables.itemData[ID][3][10])]);
                    elif self.inventory[i][j].ID == ID:
                        available = int(tables.itemData[ID][3][10])-self.inventory[i][j].amnt;
                        if available > 0:
                            existingSpaces.append(["I", (i, j), available]);
        return [existingSpaces, freeSpaces];

    def RenderHotbar(self, full = False):
        self.hotbarImage.fill((255, 0, 255))
        for i in range(10):
            self.hotbarImage.blit(surface_manager.miscGUI[0], (48 * i, 0));
            if self.hotbar[i] != None:
                self.hotbarImage.blit(surface_manager.items[self.hotbar[i].ID], (48 * i, 0));
                if self.hotbar[i].amnt > 1:
                    self.hotbarImage.blit(shared_methods.OutlineText(str(self.hotbar[i].amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * i, 30));

    def UpdateInventoryOldSlots(self):
        for data in self.oldInventoryPositions:
            if data[0] == "H":
                item = self.hotbar[data[1]];
                self.hotbarImage.blit(surface_manager.miscGUI[0], (data[1] * 48, 0));
                if item != None:
                    self.hotbarImage.blit(surface_manager.items[item.ID], (48 * data[1], 0));
                    if item.amnt > 1:
                        self.hotbarImage.blit(shared_methods.OutlineText(str(item.amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * data[1], 30));
            elif data[0] == "I":
                item = self.inventory[data[1][0]][data[1][1]];
                self.inventoryImage.blit(surface_manager.miscGUI[0], (data[1][0] * 48, data[1][1] * 48));
                if item != None:
                    self.inventoryImage.blit(surface_manager.items[item.ID], (data[1][0] * 48, data[1][1] * 48));
                    if item.amnt > 1:
                        self.inventoryImage.blit(shared_methods.OutlineText(str(item.amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * data[1][0], 30 + 48 * data[1][1]));

            elif data[0] == "C":
                item = self.chestItems[data[1][0]][data[1][1]];
                self.chestImage.blit(surface_manager.miscGUI[0], (data[1][0] * 48, data[1][1] * 48));
                if item != None:
                    self.chestImage.blit(surface_manager.items[item.ID], (data[1][0] * 48, data[1][1] * 48));
                    if item.amnt > 1:
                        self.chestImage.blit(shared_methods.OutlineText(str(item.amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * data[1][0], 30 + 48 * data[1][1]));
        self.oldInventoryPositions = [];

    def RenderInventory(self):
        self.inventoryImage.fill((255, 0, 255));
        pygame.draw.rect(self.inventoryImage, (150, 150, 150), Rect(5, 5, 472, 184), 0);
        for j in range(4):
            for i in range(10):
                self.inventoryImage.blit(surface_manager.miscGUI[0], (48 * i, 48 * j));
                if self.inventory[i][j] != None:
                    self.inventoryImage.blit(surface_manager.items[self.inventory[i][j].ID], (48 * i, 48 * j));
                    if self.inventory[i][j].amnt > 1:
                        self.inventoryImage.blit(shared_methods.OutlineText(str(self.inventory[i][j].amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * i, 30 + 48 * j));

    def RenderChest(self):
        self.chestImage.fill((255, 0, 255));
        pygame.draw.rect(self.chestImage, (150, 150, 150), Rect(5, 5, 232, 184), 0);
        for j in range(4):
            for i in range(5):
                self.chestImage.blit(surface_manager.miscGUI[0], (48 * i, 48 * j));
                if self.chestItems[i][j] != None:
                    self.chestImage.blit(surface_manager.items[self.chestItems[i][j].ID], (48 * i, 48 * j));
                    if self.chestItems[i][j].amnt > 1:
                        self.chestImage.blit(shared_methods.OutlineText(str(self.chestItems[i][j].amnt), (255, 255, 255), commons.SMALLFONT), (24 + 48 * i, 30 + 48 * j));

    def UpdateCraftableItems(self):
        self.craftableItems = [[i, 1] for i in range(31)];

    def RenderCraftableItemsSurf(self):
        self.craftableItemsSurf = pygame.Surface((48, len(self.craftableItems) * 48));
        self.craftableItemsSurf.fill((255, 0, 255));
        for i in range(len(self.craftableItems)):
            self.craftableItemsSurf.blit(surface_manager.miscGUI[0], (0, i * 48));
            self.craftableItemsSurf.blit(surface_manager.items[self.craftableItems[i][0]], (0, i * 48));

    def Draw(self): #draw player to screen
        if self.alive:
            screenpositionx = self.position[0] - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5;
            screenpositiony = self.position[1] - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5;
            commons.screen.blit(self.sprites[self.animationFrame], (screenpositionx - 20, screenpositiony - 33));
            img = self.currentItemImage.copy();
            if self.armHold:
                if not commons.IS_HOLDING_ITEM:
                    item = self.hotbar[self.hotbarIndex];
                else:
                    item = commons.ITEM_HOLDING;
                img = shared_methods.RotateSurface(surface_manager.items[item.ID].copy(), self.holdAngle * 180 / math.pi);
                if self.direction == 1:
                    offsetx = 10;
                else:
                    offsetx = -10;
                    img = pygame.transform.flip(img, True, False);
                commons.screen.blit(img, (screenpositionx - img.get_width() * 0.5 + offsetx, screenpositiony - img.get_height() * 0.5));
            elif self.itemSwing:
                if not commons.IS_HOLDING_ITEM:
                    item = self.hotbar[self.hotbarIndex];
                else:
                    item = commons.ITEM_HOLDING;
                if self.direction == 1:  
                    hitRect = Rect(self.position[0], self.position[1] - img.get_height() * 0.5, img.get_width(), img.get_height());
                else:
                    hitRect = Rect(self.position[0] - img.get_width(), self.position[1] - img.get_height() * 0.5, img.get_width(), img.get_height());

                # Probably should be in update
                for enemy in entity_manager.enemies:
                    if enemy.rect.colliderect(hitRect):
                        if enemy.gameID not in self.enemiesHit:
                            if self.direction == 0:
                                direction = -1;
                            else:
                                direction = 1;
                            val = int(item.attackDamage);
                            if random.random() < item.critStrikeChance:
                                crit = True;
                            else:
                                crit = False;
                            enemy.Damage(val, item.knockback, direction = direction, crit = crit);
                            self.enemiesHit.append(int(enemy.gameID));
                try:
                    if self.direction == 1:
                        self.swingAngle -= (100 - item.attackSpeed) / 5;
                        if self.swingAngle < -80:
                            self.itemSwing = False;
                    else:
                        self.swingAngle += (100 - item.attackSpeed) / 5;
                        if self.swingAngle > 155:
                            self.itemSwing = False;
                except:
                    self.itemSwing = False;
                
                angle1 = self.swingAngle;
                angle2 = (self.swingAngle) * math.pi / 180;
                if self.direction == 1:
                    offsetx = img.get_width() * 0.5;
                else:
                    offsetx = -img.get_width() * 0.5;
                if self.direction == 1:
                    offsety = -math.sin(angle2 + 0.2) * img.get_height() * 2 / 3 - img.get_height() / 4;
                else:
                    offsety = -math.sin(angle2 + 0.3) * img.get_width() * 2 / 3 +img.get_height() * 0.5;
                commons.screen.blit(shared_methods.RotateSurface(img, angle1), (screenpositionx - 20 + offsetx, screenpositiony - 33 + offsety));
                
            commons.screen.blit(self.armSprites[self.armAnimationFrame], (screenpositionx - 20, screenpositiony - 33));
        
        if commons.HITBOXES and self.alive: # Show hitbox
            pygame.draw.rect(commons.screen,  (255, 0, 0), Rect(screenpositionx - commons.PLAYER_WIDTH * 0.5, screenpositiony - commons.PLAYER_HEIGHT * 0.5, commons.PLAYER_WIDTH, commons.PLAYER_HEIGHT), 1);

    def DrawHP(self):
        if self.HP > 0:
            rect = Rect(commons.WINDOW_WIDTH - 10 - self.HP * 2, 25, self.HP * 2, 20);
            hpFloat = self.HP / self.maxHP;
            col = ((1 - hpFloat) * 255, hpFloat * 255, 0);
            pygame.draw.rect(commons.screen, col, rect, 0);
            pygame.draw.rect(commons.screen, (col[0] * 0.8, col[1] * 0.8, 0), rect, 3);
            commons.screen.blit(self.hpText, (self.hpXposition, 45));
        
    def OpenChest(self, items):
        if not self.chestOpen:
            if commons.SOUND:
                sound_manager.sounds[24].play();
            self.chestOpen = True;
        self.chestItems = items;
        self.inventoryOpen = True;
        self.craftingMenuOffsetY = 120;
        self.UpdateCraftableItems();
        self.RenderCraftableItemsSurf();
        self.RenderChest();

    def SavePlayer(self):
        commons.PLAYER_DATA = [self.name, self.model, self.hotbar, self.inventory, self.HP, self.maxHP, self.playTime, self.creationDate]; #create player array
        pickle.dump(commons.PLAYER_DATA, open("res/players/" + self.name + ".player", "wb")); #save player array
        entity_manager.AddMessage("Saved Player: " + self.name + "!", (255, 255, 255));

    def Jump(self):
        if self.alive and self.grounded:
            if commons.SOUND:
                sound_manager.sounds[6].play();
            if commons.PARTICLES:
                colour = shared_methods.GetBlockAverageColour(self.lastBlockOn);
                for i in range(int(random.randint(5, 8) * commons.PARTICLEDENSITY)):
                    entity_manager.SpawnParticle((self.position[0], self.position[1] + commons.BLOCKSIZE * 1.5), colour, size = 10, life = 1, angle = -math.pi * 0.5, spread = math.pi * 0.33, GRAV = 0, magnitude = 1.5 + random.random() * 10);
            self.velocity = (self.velocity[0], -50);
            self.grounded = False;