#entity_manager.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, math, random;
from pygame.locals import *;

import commons;
import tables;
import world;

import shared_methods;
import sound_manager;

from player import Player;
from enemy import Enemy;
from particle import Particle;
from projectile import Projectile;
from physics_item import PhysicsItem;
from colour_picker import ColourPicker;

def Initialize():
    global enemies, particles, projectiles, physicsItems, messages, damageNumbers, recentPickups, clientPlayer, clientPrompt, clientColourPicker, cameraPosition, oldCameraPosition, cameraPositionDifference;
    
    enemies = [];
    particles = [];
    projectiles = [];
    physicsItems = [];
    messages = [];
    damageNumbers = [];
    recentPickups = [];
    
    clientPlayer = None;
    clientPrompt = None;
    clientColourPicker = ColourPicker((int(commons.WINDOW_WIDTH * 0.5 - 155),  190),  300,  300);

    cameraPosition = (0, 0);
    oldCameraPosition = (0, 0);
    cameraPositionDifference = (0, 0);

def CreatePlayer():
    global clientPlayer;
    name = commons.PLAYER_DATA[0];
    model = commons.PLAYER_DATA[1];
    hotbar = commons.PLAYER_DATA[2];
    inventory = commons.PLAYER_DATA[3];
    HP = commons.PLAYER_DATA[4];
    maxHP = commons.PLAYER_DATA[5];
    playTime = commons.PLAYER_DATA[6];
    creationDate = commons.PLAYER_DATA[7];
    clientPlayer = Player((0,0), model, name = name, hotbar = hotbar, inventory = inventory, HP = HP, maxHP = maxHP, playTime = playTime, creationDate = creationDate);

def UpdateEnemies():
    for enemy in enemies:
        enemy.Update();
        
def DrawEnemies():
    for enemy in enemies:
        enemy.Draw();

def UpdateParticles():
    for particle in particles:
        particle.Update();
        
def DrawParticles():
    for particle in particles:
        particle.Draw();
        
def UpdatePhysicsItems():
    for physicsItem in physicsItems:
        physicsItem.Update();

def SpawnPhysicsItem(position, ID, tier, amnt = 1, pickupDelay = 100, unique = False, item = None, velocity = None):
    physicsItems.append(PhysicsItem(position, ID, tier, amnt, pickupDelay, unique, item, velocity));

def DrawPhysicsItems():
    for physicsItem in physicsItems:
        physicsItem.Draw();

def UpdateProjectiles():
    for projectile in projectiles:
        projectile.Update();

def DrawProjectiles():
    for projectile in projectiles:
        projectile.Draw();

def SpawnProjectile(position, angle, weaponDamage, weaponKnockback, weaponProjectileSpeed, ID, source, crit):
    
    angle += random.random() * 0.125 - 0.06125;
    
    damage = int(weaponDamage) + int(tables.projectileData[ID][2]);
    
    power = int(weaponProjectileSpeed) + int(tables.projectileData[ID][3]);
    velocity = (math.cos(angle) * power, math.sin(angle) * power);
    
    knockback = int(weaponKnockback) + int(tables.projectileData[ID][3]);

    if commons.SOUND:
        sound_manager.sounds[int(tables.projectileData[ID][10])].play();
    
    projectiles.append(Projectile(position, velocity, str(tables.projectileData[ID][1]), ID, source, damage, knockback, crit, int(tables.projectileData[ID][5]), str(tables.projectileData[ID][7]), GRAVITY = float(tables.projectileData[ID][8]), DRAG = float(tables.projectileData[ID][9])));

def UpdateMessages():
    global messages;
    for message in messages:
        message[1] -= commons.DELTA_TIME;
        if message[1] <= 0:
            messages.remove(message);

def DrawMessages():
    for i in range(len(messages)):
        if messages[i][1] < 1.0:
             messages[i][0].set_alpha((messages[i][1] / 1.0) * 255);
        commons.screen.blit(messages[i][0], (10, commons.WINDOW_HEIGHT - 25 - i * 20));

def AddMessage(text, colour, life = 5, outlineColour = (0, 0, 0)):
    global messages;
    text1 = commons.DEFAULTFONT.render(text, False, colour);
    text2 = commons.DEFAULTFONT.render(text, False, outlineColour);
    surf = pygame.Surface((text1.get_width() + 2, text1.get_height() + 2))
    surf.fill((255, 0, 255));
    surf.set_colorkey((255, 0, 255));
    if commons.FANCYTEXT:
        surf.blit(text2, (0, 1));
        surf.blit(text2, (2, 1));
        surf.blit(text2, (1, 0));
        surf.blit(text2, (1, 2));
    
    surf.blit(text1, (1, 1));
    messages.insert(0, [surf, life]);
    
def CheckEnemySpawn():
    if not commons.PASSIVE:
        if commons.ENEMY_SPAWN_TICK <= 0:
            commons.ENEMY_SPAWN_TICK += 1.0;
            val = int(14 - ((clientPlayer.position[1] // commons.BLOCKSIZE) // 30));
            if val < 1:
                val = 1;
            if len(enemies) < commons.MAXENEMYSPAWNS + (7 - val * 0.5) and random.randint(1, val) == 1: #reduce enemy spawns
                SpawnEnemy();
        else:
            commons.ENEMY_SPAWN_TICK -= commons.DELTA_TIME;

def SpawnEnemy(position = None, ID = None):
    if ID == None:
        if clientPlayer.position[1] < 200 * commons.BLOCKSIZE:
            ID = random.randint(0, 1);
        elif clientPlayer.position[1] < 300 * commons.BLOCKSIZE:
            ID = random.randint(1, 2);
        elif clientPlayer.position[1] >= 300 * commons.BLOCKSIZE:
            ID = random.randint(3, 4);
    if position == None:
        playerBlockPos = (int(cameraPosition[0]) // commons.BLOCKSIZE, int(cameraPosition[1]) // commons.BLOCKSIZE)  ;
        for i in range(500):
            if random.random() < 0.5:
                x = random.randint(playerBlockPos[0] - commons.MAX_ENEMY_SPAWN_TILES_X, playerBlockPos[0] - commons.MIN_ENEMY_SPAWN_TILES_X);
                if random.random() < 0.5:
                    y = random.randint(playerBlockPos[1] - commons.MAX_ENEMY_SPAWN_TILES_Y, playerBlockPos[1] - commons.MIN_ENEMY_SPAWN_TILES_Y);
                else:
                    y = random.randint(playerBlockPos[1] + commons.MIN_ENEMY_SPAWN_TILES_Y, playerBlockPos[1] + commons.MAX_ENEMY_SPAWN_TILES_Y);
            else:
                x = random.randint(playerBlockPos[0] + commons.MIN_ENEMY_SPAWN_TILES_X, playerBlockPos[0] + commons.MAX_ENEMY_SPAWN_TILES_X);
                if random.random() < 0.5:
                    y = random.randint(playerBlockPos[1] - commons.MAX_ENEMY_SPAWN_TILES_Y, playerBlockPos[1] - commons.MIN_ENEMY_SPAWN_TILES_Y);
                else:
                    y = random.randint(playerBlockPos[1] + commons.MIN_ENEMY_SPAWN_TILES_Y, playerBlockPos[1] + commons.MAX_ENEMY_SPAWN_TILES_Y);
            if world.TileInMapRange(x, y, width = 2):
                if world.mapData[x][y][0] in tables.uncollidableBlocks and world.mapData[x][y][1] != 4:
                    if world.mapData[x - 1][y][0] in tables.uncollidableBlocks:
                        if world.mapData[x][y - 1][0] in tables.uncollidableBlocks:
                            if world.mapData[x + 1][y][0] in tables.uncollidableBlocks:
                                if world.mapData[x][y + 1][0] in tables.uncollidableBlocks:
                                    enemies.append(Enemy((x * commons.BLOCKSIZE, y * commons.BLOCKSIZE), ID));
                                    return;
    else:
        enemies.append(Enemy(position, ID));

def SpawnParticle(position, colour, life = 2, magnitude = 1, size = 5, angle = None, spread = math.pi / 4, GRAV = 1, velocity = None, outline = True):
    particles.append(Particle(position, colour, life, magnitude, size, angle, spread, GRAV, velocity, outline));

def UpdateDamageNumbers():
    for damageNumber in damageNumbers:
        damageNumber[1] = (damageNumber[1][0] * 0.95, damageNumber[1][1] * 0.95);
        damageNumber[0] = (damageNumber[0][0] + damageNumber[1][0] - cameraPositionDifference[0], damageNumber[0][1] + damageNumber[1][1] - cameraPositionDifference[1])
        damageNumber[3] -= commons.DELTA_TIME;
        if damageNumber[3] <= 0:
            damageNumbers.remove(damageNumber);

def DrawDamageNumbers():
    for damageNumber in damageNumbers:
        if damageNumber[3] < 0.5:
            damageNumber[2].set_alpha(damageNumber[3] * 510);
        surf = damageNumber[2].copy();
        surf = shared_methods.RotateSurface(surf, -damageNumber[1][0] * 35);
        commons.screen.blit(surf, (damageNumber[0][0] - surf.get_width() * 0.5, damageNumber[0][1] - surf.get_height() * 0.5));

def AddDamageNumber(pos, val, crit = False, colour = None):
    global damageNumbers;

    if colour == None:
        if crit:
            colour = (246, 97, 28);
        else:
            colour = (207, 127, 63);
    
    t1 = commons.DEFAULTFONT.render(str(int(val)), False, colour);
    t2 = commons.DEFAULTFONT.render(str(int(val)), False, (colour[0] * 0.8, colour[1] * 0.8, colour[2] * 0.8));
    
    width = t1.get_width() + 2;
    height = t1.get_height() + 2;

    if width > height:
        size = width;
    else:
        size = height;
    
    surf = pygame.Surface((size, size));
    surf.fill((255, 0, 255));
    surf.set_colorkey((255, 0, 255));
    
    midx = size * 0.5 - width * 0.5;
    midy = size * 0.5 - height * 0.5;

    if commons.FANCYTEXT:
        surf.blit(t2, (midx, midy));
        surf.blit(t2, (midx + 2, midy));
        surf.blit(t2, (midx + 1, midy - 1));
        surf.blit(t2, (midx + 1, midy + 1));
    
    surf.blit(t1, (midx, midy));
    
    damageNumbers.append([(pos[0] - cameraPosition[0] + commons.WINDOW_WIDTH * 0.5, pos[1] - cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5), (random.random() * 4 - 2, -1 - random.random() * 4), surf, 3.0]);

def UpdateRecentPickups():
    global recentPickups;
    toRemove = [];
    for i in range(len(recentPickups)):
        recentPickups[i][5] -= commons.DELTA_TIME;
        if recentPickups[i][5] < 0.5:
            recentPickups[i][2].set_alpha(recentPickups[i][5] * 510);
            if recentPickups[i][5] <= 0:
                toRemove.append(recentPickups[i]);
        for j in range(0, i):
            if i != j:
                #check if it is colliding with prevoius messages, if so, move up
                if Rect(recentPickups[i][3][0], recentPickups[i][3][1], recentPickups[i][2].get_width(), recentPickups[i][2].get_height()).colliderect(Rect(recentPickups[j][3][0], recentPickups[j][3][1], recentPickups[j][2].get_width(), recentPickups[j][2].get_height())):
                    recentPickups[i][4] = (recentPickups[i][4][0], recentPickups[i][4][1] - 0.05);
                    recentPickups[i][3] = (recentPickups[i][3][0], recentPickups[i][3][1] - 1);
        recentPickups[i][4] = (recentPickups[i][4][0] * 0.9, recentPickups[i][4][1] * 0.9);
        recentPickups[i][3] = (recentPickups[i][3][0] + recentPickups[i][4][0], recentPickups[i][3][1] + recentPickups[i][4][1]);
    for item in toRemove:
        recentPickups.remove(item);

def AddRecentPickup(ID, amnt, tier, pos, unique = False, item = None):
    global recentPickups;
    if not unique:
        for recentPickup in recentPickups:
            if recentPickup[0] == ID:
                amnt += recentPickup[1];
                recentPickups.remove(recentPickup);    
    if amnt > 1:
        string = tables.itemData[ID][0] + "(" + str(amnt) + ")";
    else:
        if item != None:
            string = item.GetName();
        else:
            string = tables.itemData[ID][0];
    size = commons.DEFAULTFONT.size(string);
    size = (size[0] + 2, size[1] + 2);
    surf = pygame.Surface(size);
    surf.set_colorkey((255, 0, 255));
    surf.fill((255, 0, 255));
    surf.blit(shared_methods.OutlineText(string, shared_methods.GetTierColour(tier), commons.DEFAULTFONT), (1, 1));
    vel = (random.random() * 2 - 1, -6.5);
    recentPickups.append([ID, amnt, surf, pos, vel, 3.0]);

def DrawRecentPickups():
    for recentPickup in recentPickups:
        commons.screen.blit(recentPickup[2], (recentPickup[3][0] - recentPickup[2].get_width() * 0.5 - cameraPosition[0] + commons.WINDOW_WIDTH * 0.5, recentPickup[3][1] - cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5));

def DrawEnemyHoverText():
    mpos = (commons.MOUSE_POS[0] + clientPlayer.position[0] - commons.WINDOW_WIDTH * 0.5, commons.MOUSE_POS[1] + clientPlayer.position[1] - commons.WINDOW_HEIGHT * 0.5);
    for enemy in enemies:
        if enemy.rect.collidepoint(mpos):
            text1 = commons.DEFAULTFONT.render(enemy.name + " " + str(math.ceil(enemy.HP)) + "/" + str(enemy.maxHP), True, (255, 255, 255));
            text2 = commons.DEFAULTFONT.render(enemy.name + " " + str(math.ceil(enemy.HP)) + "/" + str(enemy.maxHP), True, (0, 0, 0));
                
            commons.screen.blit(text2, (commons.MOUSE_POS[0] - text2.get_width() * 0.5, commons.MOUSE_POS[1] - 39));
            commons.screen.blit(text2, (commons.MOUSE_POS[0] - text2.get_width() * 0.5, commons.MOUSE_POS[1] - 41));
            commons.screen.blit(text2, (commons.MOUSE_POS[0] - text2.get_width() * 0.5 - 1, commons.MOUSE_POS[1] - 40));
            commons.screen.blit(text2, (commons.MOUSE_POS[0] - text2.get_width() * 0.5 + 1, commons.MOUSE_POS[1] - 40));
                
            commons.screen.blit(text1, (commons.MOUSE_POS[0] - text1.get_width() * 0.5, commons.MOUSE_POS[1] - 40));
            break;