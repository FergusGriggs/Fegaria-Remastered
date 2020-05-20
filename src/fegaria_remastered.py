#fegaria_remastered.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";
__version__ = "0.1.1";

# External module importing
import pygame, sys, math, time, os, random, pickle, datetime, webbrowser, _thread
from pygame.locals import *

#set to 8000 for creepy mode (48000 norm)
pygame.mixer.pre_init(48000, -16, 2, 1024);
pygame.init();

# Loads config file and common variables
import commons;
import shared_methods;
commons.Initialize();

import sound_manager;
sound_manager.Initialize();

import surface_manager;
surface_manager.Initialize();

import entity_manager;
entity_manager.Initialize();

import world;
world.Initialize();

import menu_manager;
menu_manager.Initialize();

from player import Player;
import player;

from item import Item;

import tables;
import prompt;

from colour_picker import ColourPicker;

def DrawTerrainMultiThreadedFunc(threadName, threadID, position, quadrant):
    global blitThreadOneActive, blitThreadTwoActive, blitThreadThreeActive;

    if quadrant == 0:
        commons.screen.blit(world.terrainSurface, position, Rect(-position[0], -position[1], commons.WINDOW_WIDTH * 0.5, commons.WINDOW_HEIGHT));
        blitThreadOneActive = False;
    elif quadrant == 1:
        commons.screen.blit(world.terrainSurface, position, Rect(-position[0] + commons.WINDOW_WIDTH * 0.5, -position[1], commons.WINDOW_WIDTH * 0.5, commons.WINDOW_HEIGHT));
        blitThreadTwoActive = False;
    elif quadrant == 2:
        commons.screen.blit(world.terrainSurface, position, Rect(-position[0], -position[1] + commons.WINDOW_HEIGHT * 0.5, commons.WINDOW_WIDTH * 0.5, commons.WINDOW_HEIGHT));
        blitThreadThreeActive = False;
    else:
        commons.screen.blit(world.terrainSurface, position, Rect(-position[0] + commons.WINDOW_WIDTH * 0.5, -position[1] + commons.WINDOW_HEIGHT * 0.5, commons.WINDOW_WIDTH * 0.5, commons.WINDOW_HEIGHT));

def DrawTerrainMultiThreaded(position):
    global blitThreadOneActive, blitThreadTwoActive, blitThreadThreeActive;
    blitThreadOneActive = True;
    blitThreadTwoActive = True;
    blitThreadThreeActive = True;

    _thread.start_new_thread(DrawTerrainMultiThreadedFunc, ("Blit Thread One", 2, position, 0));
    _thread.start_new_thread(DrawTerrainMultiThreadedFunc, ("Blit Thread One", 3, position, 1));
    _thread.start_new_thread(DrawTerrainMultiThreadedFunc, ("Blit Thread One", 4, position, 2));
    DrawTerrainMultiThreadedFunc("Main Thread", 0, position, 3);

    i = 0;
    while blitThreadOneActive or blitThreadTwoActive or blitThreadThreeActive:
        i += 1;



def MoveParallax(val):
    global parallaxPos
    parallaxPos = (parallaxPos[0] + val[0], parallaxPos[1] + val[1])
    if parallaxPos[0] > 0:
        parallaxPos = (-40 + parallaxPos[0], parallaxPos[1])
    elif parallaxPos[0] < -39: parallaxPos = (parallaxPos[0] + 40, parallaxPos[1])
    if parallaxPos[1] > 0:
        parallaxPos = (parallaxPos[0], -40 + parallaxPos[1])
    elif parallaxPos[1] < -39:
        parallaxPos = (parallaxPos[0], parallaxPos[1] + 40)

def FadeBackground(ID):
    global fadeBackgroundID, fadeBack, fadeFloat;
    fadeBackgroundID = ID;
    fadeBack = True;
    fadeFloat = 0;

# Check if player has moved biome and change background
def CheckChangeBackground(): 
    global backgroundTick;
    if backgroundTick <= 0:
        backgroundTick += 0.25;
        if entity_manager.cameraPosition[1] > 200 * commons.BLOCKSIZE:
            if entity_manager.cameraPosition[0] < BIOMEBOARDER_X1 * commons.BLOCKSIZE:
                if fadeBackgroundID != 0:
                    FadeBackground(0);
            elif entity_manager.cameraPosition[0] < BIOMEBOARDER_X2 * commons.BLOCKSIZE:
                if fadeBackgroundID != 2:
                    FadeBackground(2);
            else:
                if fadeBackgroundID != 2:
                    FadeBackground(2);
            backgroundScrollVel = 0;
        if entity_manager.cameraPosition[1] > 110 * commons.BLOCKSIZE:
            if entity_manager.cameraPosition[0] < BIOMEBOARDER_X1 * commons.BLOCKSIZE:
                if fadeBackgroundID != 0:
                    FadeBackground(0);
            elif entity_manager.cameraPosition[0] < BIOMEBOARDER_X2 * commons.BLOCKSIZE:
                if fadeBackgroundID != 1:
                    FadeBackground(1);
            else:
                if fadeBackgroundID != 4:
                    FadeBackground(4);
            backgroundScrollVel = 0;

        elif entity_manager.cameraPosition[1] > 15 * commons.BLOCKSIZE:
            if fadeBackgroundID != 3:
                FadeBackground(3);

        else:
            if fadeBackgroundID != 5:
                FadeBackground(5);
            backgroundScrollVel = 0.1;
    else:
        backgroundTick -= commons.DELTA_TIME;
        
# Message shown on death
def DrawDeathMessage():
    text = shared_methods.OutlineText("You Were Slain", (255, 255, 255), commons.LARGEFONT)
    val = (1 - (entity_manager.clientPlayer.respawnTick / 5.0)) * 255;
    if val > 255:
        val = 255;
    text.set_alpha(val);
    commons.screen.blit(text, (commons.WINDOW_WIDTH * 0.5 - text.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.5));
       
def RenderHandText():
    global handText;
    item = entity_manager.clientPlayer.hotbar[entity_manager.clientPlayer.hotbarIndex];
    if item != None:
        colour = shared_methods.GetTierColour(item.tier);
        handText = shared_methods.OutlineText(item.GetName(), colour, commons.DEFAULTFONT);
    else:
        handText = shared_methods.OutlineText("", (255, 255, 255), commons.DEFAULTFONT);
        

def RunSplashScreen():
    done = False;
    age = 0;
    text = shared_methods.OutlineText("A Fergus Griggs game...", (255, 255, 255), commons.LARGEFONT);
    blackSurf = pygame.Surface((commons.WINDOW_WIDTH, commons.WINDOW_HEIGHT));
    sprites = Player.RenderSprites(defaultModel, directions = 1);

    torsoFrame = 2;
    armFrame = 6;

    xpos = -30;

    slowTick = 0;
    fastTick = 0;

    commons.OLD_TIME_MILLISECONDS = pygame.time.get_ticks();
    
    splashScreenRunning = True

    while splashScreenRunning:
        commons.DELTA_TIME = (pygame.time.get_ticks() - commons.OLD_TIME_MILLISECONDS) * 0.001;
        commons.OLD_TIME_MILLISECONDS = pygame.time.get_ticks();

        commons.screen.blit(surface_manager.largeBackgrounds[1], (0, 0));
        entity_manager.DrawParticles();

        if age < 0.5:
            blackSurf.set_alpha(255);

        elif age < 1.5 and age > 0.5:
            alpha = (1.5 - age) * 255;
            blackSurf.set_alpha(alpha);

        elif age > 1.5 and age < 4.5:
            entity_manager.UpdateParticles();
            if slowTick <= 0:
                slowTick += 0.2;
                if commons.SOUND:
                    sound_manager.sounds[random.randint(20, 22)].play();
            else:
                slowTick -= commons.DELTA_TIME;

            if fastTick <= 0:
                fastTick += 0.025;
                if torsoFrame < 14:
                    torsoFrame += 1;
                else:
                    torsoFrame = 2;

                if armFrame < 18:
                    armFrame += 1;
                else:
                    armFrame = 6;

                if commons.PARTICLES:
                    for i in range(int(4 * commons.PARTICLEDENSITY)):
                        entity_manager.SpawnParticle((xpos + commons.PLAYER_WIDTH - commons.WINDOW_WIDTH * 0.5, commons.WINDOW_HEIGHT * 0.25 + commons.PLAYER_HEIGHT * 1.15), (255, 255, 255), life = 0.5, GRAV = -0.4, size = 10, angle = math.pi, spread = math.pi, magnitude = random.random() * 8);

            else:
                fastTick -= commons.DELTA_TIME;

            xpos += commons.WINDOW_WIDTH * commons.DELTA_TIME * 0.35;

            commons.screen.blit(sprites[0][torsoFrame], (xpos, commons.WINDOW_HEIGHT * 0.75));
            commons.screen.blit(sprites[1][armFrame], (xpos, commons.WINDOW_HEIGHT * 0.75));

        elif age > 4.5 and age < 5.5:
            entity_manager.UpdateParticles();
            alpha = (age - 4.5) * 255;
            blackSurf.set_alpha(alpha);

        elif age > 6.0:
            splashScreenRunning = False;
        commons.screen.blit(text, (commons.WINDOW_WIDTH * 0.5 - text.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.5));
        commons.screen.blit(blackSurf, (0, 0));

        age += commons.DELTA_TIME;

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit();
                sys.exit();
            if event.type == KEYDOWN:
                splashScreenRunning = False;
        pygame.display.flip();

        clock.tick(commons.TARGETFPS);

def RenderStatsText(pos):
    global statsText, lastHoveredItem;

    if pos[0] == "H":
        item = entity_manager.clientPlayer.hotbar[pos[1]];

    elif pos[0] == "I":
        item = entity_manager.clientPlayer.inventory[pos[1][0]][pos[1][1]];

    elif pos[0] == "C":
        item = entity_manager.clientPlayer.chestItems[pos[1][0]][pos[1][1]];

    elif pos[0] == "CM":
        item = Item(entity_manager.clientPlayer.craftableItems[pos[1]][0], forceNoPrefix = True);

    if item != None:
        if item != lastHoveredItem: 
            lastHoveredItem = item;
            statsText = pygame.Surface((340, 200));
            statsText.fill((255, 0, 255));
            statsText.set_colorkey((255, 0, 255));
            
            stats = [];
            stats.append(shared_methods.OutlineText(item.GetName(), shared_methods.GetTierColour(item.tier), commons.DEFAULTFONT));
            if "weapon" in item.tags or "tool" in item.tags:
                stats.append(shared_methods.OutlineText(str(round(item.attackDamage, 1)).rstrip('0').rstrip('.') + " damage", (255,255,255), commons.DEFAULTFONT));
                stats.append(shared_methods.OutlineText(str(round(item.critStrikeChance * 100, 1)).rstrip('0').rstrip('.') + "% critical strike chance", (255, 255, 255), commons.DEFAULTFONT));
                stats.append(shared_methods.OutlineText(GetSpeedText(item.attackSpeed), (255, 255, 255), commons.DEFAULTFONT))
                stats.append(shared_methods.OutlineText(GetKnockbackText(item.knockback), (255, 255, 255), commons.DEFAULTFONT))
            
            if "ammo" in item.tags:
                stats.append(shared_methods.OutlineText("Ammunition", (255, 255, 255), commons.DEFAULTFONT));
                stats.append(shared_methods.OutlineText(str(tables.projectileData[tables.itemData[item.ID][6]][2]) + " damage", (255, 255, 255), commons.DEFAULTFONT));
                stats.append(shared_methods.OutlineText(GetKnockbackText(tables.projectileData[tables.itemData[item.ID][6]][3]), (255, 255, 255), commons.DEFAULTFONT));
                stats.append(shared_methods.OutlineText(str(round(tables.projectileData[tables.itemData[item.ID][6]][7] * 100, 1)) + "% gravity", (255, 255, 255), commons.DEFAULTFONT));
                stats.append(shared_methods.OutlineText(str(round(tables.projectileData[tables.itemData[item.ID][6]][8] * 100, 1)) + "% drag", (255, 255, 255), commons.DEFAULTFONT));

            if "material" in item.tags:
                stats.append(shared_methods.OutlineText("Material", (255, 255, 255), commons.DEFAULTFONT));
            
            if "block" in item.tags:
                stats.append(shared_methods.OutlineText("Can be placed", (255, 255, 255), commons.DEFAULTFONT));

            if item.description != "None":
                stats.append(shared_methods.OutlineText(item.description, (255, 255, 255), commons.DEFAULTFONT));
            if item.hasPrefix:
                if item.prefixData[1][1] != 0:
                    if item.prefixData[1][1] > 0:
                        colour = tuple(goodColour);
                    else:
                        colour = tuple(badColour);
                    stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][1] * 100))) + "% damage", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
                if item.prefixData[0] != "universal":
                    if item.prefixData[1][2] != 0:
                        if item.prefixData[1][2] > 0:
                            colour = tuple(goodColour);
                        else:
                            colour = tuple(badColour);
                        stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][2] * 100))) + "% speed", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
                else:
                    if item.prefixData[1][2] != 0:
                        if item.prefixData[1][2] > 0:
                            colour = tuple(goodColour);
                        else:
                            colour = tuple(badColour);
                        stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][2] * 100))) + "% critical strike chance", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
                    if item.prefixData[1][3] != 0:
                        if item.prefixData[1][3] > 0:
                            colour = tuple(goodColour);
                        else:
                            colour = tuple(badColour);
                        stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][3] * 100))) + "% knockback", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
                if item.prefixData[0] != "universal":
                    if item.prefixData[1][3] != 0:
                        if item.prefixData[1][3] > 0:
                            colour = tuple(goodColour);
                        else:
                            colour = tuple(badColour);
                        stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][3] * 100))) + "% critical strike chance", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
                if item.prefixData[0] == "common":
                    if item.prefixData[1][4] != 0:
                        if item.prefixData[1][4] > 0:
                            colour = tuple(goodColour);
                        else:
                            colour = tuple(badColour);
                        stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][4] * 100))) + "% knockback", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
                if item.prefixData[0] == "melee":
                    if item.prefixData[1][4] != 0:
                        if item.prefixData[1][4] > 0:
                            colour = tuple(goodColour);
                        else:
                            colour = tuple(badColour);
                        stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][4] * 100))) + "% size", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
                elif item.prefixData[0]=="ranged":
                    if item.prefixData[1][4]!=0:
                        if item.prefixData[1][4]>0:
                            colour = tuple(goodColour);
                        else:
                            colour = tuple(badColour);
                        stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][4] * 100))) + "% projectile velocity", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
                elif item.prefixData[0] == "magic":
                    if item.prefixData[1][4] != 0:
                        if item.prefixData[1][4] < 0:
                            colour = tuple(goodColour);
                        else:
                            colour = tuple(badColour);
                        stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][4] * 100))) + "% size", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
                if item.prefixData[0]=="melee" or item.prefixData[0]=="ranged" or item.prefixData[0]=="magic":
                    if item.prefixData[1][5] != 0:
                        if item.prefixData[1][5] > 0:
                            colour = tuple(goodColour);
                        else:
                            colour = tuple(badColour);
                        stats.append(shared_methods.OutlineText(AddPlus(str(int(item.prefixData[1][5] * 100))) + "% knockback", colour, commons.DEFAULTFONT, outlineColour = shared_methods.DarkenColour(colour)));
            for i in range(len(stats)):
                statsText.blit(stats[i], (0, i * 15));
        return True;
    return False;

def UpdateLight(threadName, threadID):
    global lightSurf, mapLight, XMIN, XMAX, YMIN, YMAX, threadActive, newestLightSurf, newestLightSurfPos, threadUpdatingData, lastThreadTime;
    threadActive = True;

    targetPosition = (entity_manager.cameraPosition[0] + (entity_manager.cameraPositionDifference[0] / commons.DELTA_TIME) * lastThreadTime, entity_manager.cameraPosition[1] + (entity_manager.cameraPositionDifference[1] / commons.DELTA_TIME) * lastThreadTime);

    XMIN = int(targetPosition[0] // commons.BLOCKSIZE - LIGHTRENDERDISTANCEX);
    XMAX = int(targetPosition[0] // commons.BLOCKSIZE + LIGHTRENDERDISTANCEX);
    YMIN = int(targetPosition[1] // commons.BLOCKSIZE - LIGHTRENDERDISTANCEY);
    YMAX = int(targetPosition[1] // commons.BLOCKSIZE + LIGHTRENDERDISTANCEY);

    XMINCHANGE = 0;
    YMINCHANGE = 0;

    if XMIN < 0:
        XMINCHANGE = -XMIN;
        XMIN = 0;
    if YMIN < 0:
        YMINCHANGE = -YMIN;
        YMIN = 0;

    if XMIN >= world.WORLD_SIZE_X or  YMIN >= world.WORLD_SIZE_Y or XMAX < 0 or YMAX < 0:
        threadActive = False;
        return;

    tempPos = ((targetPosition[0] // commons.BLOCKSIZE - LIGHTRENDERDISTANCEX + XMINCHANGE) * commons.BLOCKSIZE, (targetPosition[1] // commons.BLOCKSIZE - LIGHTRENDERDISTANCEY + YMINCHANGE) * commons.BLOCKSIZE);
    
    if XMAX > world.WORLD_SIZE_X:
        XMAX = world.WORLD_SIZE_X;
    if YMAX > world.WORLD_SIZE_Y:
        YMAX = world.WORLD_SIZE_Y;

    #timeBefore = pygame.time.get_ticks();

    for i in range(XMIN, XMAX):
        for j in range(YMIN, YMAX):
            mapLight[i][j] = max(0, mapLight[i][j] - 4);

    #mapLight = [[0 for i in range(world.WORLD_SIZE_Y)] for j in range(world.WORLD_SIZE_X)];
    

    for i in range(XMIN, XMAX):
        for j in range(YMIN, YMAX):
            if world.mapData[i][j][1] == -1 and world.mapData[i][j][0] == -1:
                if j < 110:
                    FillLight(i, j, globalLighting);
                #else:
                    #FillLight(i, j, 4);
            elif world.mapData[i][j][0] == 264:
                FillLight(i, j, 14);
    
    #print("Fill Light MS: ", pygame.time.get_ticks() - timeBefore);

    rangeX = XMAX - XMIN;
    rangeY = YMAX - YMIN;

    #timeBefore = pygame.time.get_ticks();

    lightSurf = pygame.Surface((rangeX, rangeY), pygame.SRCALPHA);

    for i in range(rangeX):
        for j in range(rangeY):
            lightSurf.set_at((i, j), (0, 0, 0, (15 - mapLight[i + XMIN][j + YMIN]) * 17));

    lightSurf = pygame.transform.scale(lightSurf, (rangeX * commons.BLOCKSIZE, rangeY * commons.BLOCKSIZE));

    threadUpdatingData = True;
    newestLightSurfPos = tempPos;
    newestLightSurf = lightSurf;
    threadUpdatingData = False;
    threadActive = False;

    #print("Scale Copy MS: ", pygame.time.get_ticks() - timeBefore);

def FillLight(i, j, lightValue):
    global mapLight;
    if i >= XMIN and i < XMAX and j >= YMIN and j < YMAX:
        newlightValue = max(0, lightValue - tables.tileData[world.mapData[i][j][0]][1]);
        if newlightValue > mapLight[i][j]:
            mapLight[i][j] = int(newlightValue);
            FillLight(i - 1, j, newlightValue);
            FillLight(i + 1, j, newlightValue);
            FillLight(i, j - 1, newlightValue);
            FillLight(i, j + 1, newlightValue);
        else:
            return;
    else:
        return;

def GetSpeedText(speed):
    if speed < 2:
        return "Insanely fast speed";
    elif speed < 10:
        return "Extremely fast speed";
    elif speed < 25:
        return "Very fast speed";
    elif speed < 40:
        return "Fast speed";
    elif speed < 60:
        return "Normal speed";
    elif speed < 80:
        return "Slow speed";
    else:
        return "Very Slow Speed";

def GetKnockbackText(knockback):
    if knockback == 0:
        return "No knockback";
    elif knockback < 2:
        return "Very weak knockback";
    elif knockback < 5:
        return "Weak knockback";
    elif knockback < 7:
        return "Average knockback";
    elif knockback < 9:
        return "Strong knockback";
    else:
        return "Very strong knockback";

def GetBouncesText(bounces):
    if bounces == 0:
        return "No bounces";
    else:
        return str(bounces) + " bounces";

def AddPlus(string):
    if string[0]!="-":
        string="+"+string
    return string

def DrawInventoryHoverText():
    global canDropHolding, canPickupItem, itemDropTick, itemDropRate;
    found = False;

    if Rect(5, 20, 480, 244).collidepoint(commons.MOUSE_POS):
        for i in range(10):
            if Rect(5 + 48 * i, 20, 48, 48).collidepoint(commons.MOUSE_POS):
                found = True;
                pos = ["H", i];
                break;

        for j in range(4):
            for i in range(10):
                if Rect(5 + 48 * i, 67 + 48 * j, 48, 48).collidepoint(commons.MOUSE_POS):
                    found = True;
                    pos = ["I", (i, j)];
                    break;

    elif Rect(245, 265, 384, 192).collidepoint(commons.MOUSE_POS) and entity_manager.clientPlayer.chestOpen:
        for j in range(4):
            for i in range(5):
                if Rect(245 + 48 * i, 265 + j * 48, 48, 48).collidepoint(commons.MOUSE_POS):
                    found = True;
                    pos = ["C", (i, j)];
                    break;
    
    elif Rect(5, 270, 48, 288).collidepoint(commons.MOUSE_POS):
        arrpos = (commons.MOUSE_POS[1] - 270 - int(entity_manager.clientPlayer.craftingMenuOffsetY)) // 48;
        if arrpos >= 0 and arrpos < len(entity_manager.clientPlayer.craftableItems):
            if pygame.mouse.get_pressed()[0]:  
                if not commons.IS_HOLDING_ITEM:
                    commons.ITEM_HOLDING = Item(entity_manager.clientPlayer.craftableItems[arrpos][0], amnt = entity_manager.clientPlayer.craftableItems[arrpos][1]);
                    commons.IS_HOLDING_ITEM = True;
                    canPickupItem = False;
                    canDropHolding = False;
                    sound_manager.sounds[19].play();
                elif canDropHolding:
                    if commons.ITEM_HOLDING.ID == entity_manager.clientPlayer.craftableItems[arrpos][0]:
                        if commons.ITEM_HOLDING.amnt < tables.itemData[commons.ITEM_HOLDING.ID][3][10]:
                            commons.ITEM_HOLDING.amnt += entity_manager.clientPlayer.craftableItems[arrpos][1];
                            sound_manager.sounds[19].play();
            
            if RenderStatsText(["CM", arrpos]) and not commons.IS_HOLDING_ITEM:
                commons.screen.blit(statsText, (commons.MOUSE_POS[0] + 10, commons.MOUSE_POS[1] + 10));
    if found:
        mouseButtons = pygame.mouse.get_pressed();

        if mouseButtons[0] or mouseButtons[2]:
            if canDropHolding and commons.ITEM_HOLDING!=None:
                unique = False;

                if commons.ITEM_HOLDING.hasPrefix:
                    unique = True;

                if mouseButtons[0]:
                    amnt = commons.ITEM_HOLDING.amnt;
                else:
                    amnt = 1;
                itemAddData = None;

                if mouseButtons[0] or itemDropTick <= 0:
                    itemAddData = entity_manager.clientPlayer.GiveItem(commons.ITEM_HOLDING.ID, amnt, position = pos, unique = unique, item = commons.ITEM_HOLDING);

                if itemAddData != None:
                    canDropHolding = False;

                    if itemAddData[0] == 0:
                        if commons.SOUND:
                            if commons.ITEM_HOLDING.ID >= 21 and commons.ITEM_HOLDING.ID <= 24:
                                sound_manager.sounds[23].play();
                            else:
                                sound_manager.sounds[19].play();
                        if mouseButtons[0]:
                            commons.ITEM_HOLDING = None;
                            commons.IS_HOLDING_ITEM = False;
                        else:
                            commons.ITEM_HOLDING.amnt -= 1;
                            
                    elif itemAddData[0] == 1:
                        commons.ITEM_HOLDING.amnt = itemAddData[1];

                    elif itemAddData[0] == 2:
                        if commons.ITEM_HOLDING.ID >= 21 and commons.ITEM_HOLDING.ID <= 24:
                            sound_manager.sounds[23].play();
                        else:
                            sound_manager.sounds[19].play();

                        if itemAddData[2] == "I":
                            entity_manager.clientPlayer.inventory[pos[1][0]][pos[1][1]] = commons.ITEM_HOLDING;
                        elif itemAddData[2] == "C":
                            entity_manager.clientPlayer.chestItems[pos[1][0]][pos[1][1]] = commons.ITEM_HOLDING;
                        else:
                            entity_manager.clientPlayer.hotbar[pos[1]] = commons.ITEM_HOLDING;
                        commons.ITEM_HOLDING = itemAddData[1];

                    if pos not in entity_manager.clientPlayer.oldInventoryPositions:
                        entity_manager.clientPlayer.oldInventoryPositions.append(pos);

                if itemDropTick <= 0:
                    itemDropRate -= 1;
                    if itemDropRate <= 0:
                        itemDropRate = 0;
                    itemDropTick = int(itemDropRate);
                    if commons.ITEM_HOLDING != None and commons.ITEM_HOLDING.amnt <= 0:
                        commons.ITEM_HOLDING = None;
                        commons.IS_HOLDING_ITEM = False;
                else:
                    itemDropTick -= 1;

            elif canPickupItem and not mouseButtons[2]:
                canPickupItem = False;
                commons.ITEM_HOLDING = entity_manager.clientPlayer.RemoveItem(pos);
                if commons.ITEM_HOLDING != None:
                    if commons.SOUND:
                        if commons.ITEM_HOLDING.ID >= 21 and commons.ITEM_HOLDING.ID <= 24:
                            sound_manager.sounds[23].play();
                        else:
                            sound_manager.sounds[19].play();
                    commons.IS_HOLDING_ITEM = True;
                entity_manager.clientPlayer.RenderCurrentItemImage();

        if RenderStatsText(pos) and not commons.IS_HOLDING_ITEM:
            commons.screen.blit(statsText, (commons.MOUSE_POS[0] + 10, commons.MOUSE_POS[1] + 10));

    elif pygame.mouse.get_pressed()[2] and commons.IS_HOLDING_ITEM:
        unique = False;
        if commons.ITEM_HOLDING.hasPrefix:
            unique = True;
        if entity_manager.clientPlayer.direction == 1:
            velocity = (4, -random.random());
        else:
            velocity = (-4, -random.random());

        entity_manager.SpawnPhysicsItem(commons.ITEM_HOLDING, entity_manager.clientPlayer.position, pickupDelay = 250, velocity = velocity);
        
        commons.IS_HOLDING_ITEM = False;
        canDropHolding = False;
        commons.ITEM_HOLDING = None;
        
def DrawItemHolding():
    if commons.IS_HOLDING_ITEM:
        commons.screen.blit(surface_manager.items[commons.ITEM_HOLDING.ID], (commons.MOUSE_POS[0] + 10, commons.MOUSE_POS[1] + 10));
        if commons.ITEM_HOLDING.amnt > 1:
            commons.screen.blit(shared_methods.OutlineText(str(commons.ITEM_HOLDING.amnt), (255, 255, 255), commons.SMALLFONT), (commons.MOUSE_POS[0] + 34, commons.MOUSE_POS[1] + 40));

def DrawExitButton():
    global quitButtonHover;
    top = commons.WINDOW_HEIGHT - 20;
    left = commons.WINDOW_WIDTH - 50;
    if Rect(left, top, 50, 20).collidepoint(commons.MOUSE_POS):
        if not quitButtonHover:
            quitButtonHover = True;
            if commons.SOUND:
                sound_manager.sounds[26].play();
        colour = (230, 230, 0);
        if pygame.mouse.get_pressed()[0]:
            entity_manager.clientPlayer.inventoryOpen=False
            entity_manager.clientPlayer.chestOpen=False
            entity_manager.clientPrompt = prompt.Prompt("Exit", tables.exitMessages[random.randint(0, len(tables.exitMessages) - 1)], button1Name = "Yep", size = (6, 2));
            commons.WAIT_TO_USE = True;
    else:
        colour = (255, 255, 255);
        quitButtonHover = False;
    text = shared_methods.OutlineText("Quit", colour, commons.DEFAULTFONT);
    commons.screen.blit(text, (left, top));

def RenderInteractableBlockHover():
    if world.TileInMapRange(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1]):
        val = world.mapData[commons.TILE_POSITION_MOUSE_HOVERING[0]][commons.TILE_POSITION_MOUSE_HOVERING[1]][0];
        if val >= 255:
            ID = tables.tileData[val][0];
            if "interactable" in tables.itemData[ID][1]:
                commons.screen.blit(surface_manager.items[ID], commons.MOUSE_POS);

goodColour = (10, 230, 10);
badColour = (230, 10, 10);

#MAX SURF WIDTH IS 16383

defaultModel = player.Model(0, 0, (127, 72, 36), 
                   (62, 22, 0), 
                   (0, 0, 0), 
                   (95, 125, 127), 
                   (48, 76, 127), 
                   (129, 113, 45), 
                   (80,  100,  45));

pygame.display.set_caption("fegaria remastered " + __version__);

SONG_END = pygame.USEREVENT + 1;
pygame.mixer.music.set_endevent(SONG_END);

ICON = pygame.image.load("res/images/icon.png");
pygame.display.set_icon(ICON);

clock = pygame.time.Clock();

if commons.SPLASHSCREEN:
    RunSplashScreen();
    
fpsText = shared_methods.OutlineText(str(0), (255, 255, 255), commons.DEFAULTFONT);

fadeBack = False;
fadeFloat = 0;
fadeBackgroundID = -1;
backgroundTick = 0;
backgroundScrollVel = 0;
autoSaveTick = 0;
fpsTick = 0;
lastHoveredItem = None;
parallaxPos = (0,0);
canDropHolding = False;
canPickupItem = False;
quitButtonHover = False;
threadActive = False;
threadUpdatingData = False;
itemDropTick = 0;
itemDropRate = 0;

blitThreadOneActive = False;
blitThreadTwoActive = False;
blitThreadThreeActive = False;

newestLightSurf = pygame.Surface((0,0));
newestLightSurfPos = (0,0);

globalLighting = 16;
LIGHTRENDERDISTANCEX = int((commons.WINDOW_WIDTH * 0.5) / commons.BLOCKSIZE) + 9;#38;
LIGHTRENDERDISTANCEY = int((commons.WINDOW_HEIGHT * 0.5) / commons.BLOCKSIZE) + 9;#34;

lastThreadTime = 0.2;
lastThreadStart = pygame.time.get_ticks();

saveSelectSurf = pygame.Surface((315, 360));
saveSelectSurf.set_colorkey((255, 0, 255));
saveSelectYOffset = 0;
saveSelectYVel = 0;

loadMenuSurf = shared_methods.CreateMenuSurface(7, 8, "");
loadMenuBoxLeft1 = commons.WINDOW_WIDTH * 0.5 - 336 * 0.5;
loadMenuBoxLeft2 = commons.WINDOW_WIDTH * 0.5 - 315 * 0.5;

screenshotImg = pygame.image.load("res/images/screenshots/" + str(random.randint(1, 24)) + ".png");
scale = 280 / screenshotImg.get_height();
screenshotImg = pygame.transform.scale(screenshotImg, (int(scale * screenshotImg.get_width()), 280));
boarderImg = shared_methods.CreateMenuSurface(screenshotImg.get_width() // 48 + 2, 7, "");
        
oldTimeMilliseconds = pygame.time.get_ticks();

gameRunning = True;

while gameRunning:
    commons.MOUSE_POS = pygame.mouse.get_pos();
    commons.TILE_POSITION_MOUSE_HOVERING = (int((entity_manager.cameraPosition[0] + commons.MOUSE_POS[0] - commons.WINDOW_WIDTH * 0.5) // commons.BLOCKSIZE), int((entity_manager.cameraPosition[1] + commons.MOUSE_POS[1] - commons.WINDOW_HEIGHT * 0.5) // commons.BLOCKSIZE));
    
    commons.DELTA_TIME = (pygame.time.get_ticks() - oldTimeMilliseconds) * 0.001;
    oldTimeMilliseconds = pygame.time.get_ticks();

    #If framerate is less than 30, simulate at a slower speed
    if commons.DELTA_TIME > 0.033333:
        commons.DELTA_TIME = 0.033333;

    if pygame.key.get_mods() & KMOD_LSHIFT:
        commons.SHIFT_ACTIVE = True;
    else:
        commons.SHIFT_ACTIVE = False;

    if commons.GAME_STATE == "PLAYING":
        world.clientWorld.playTime += commons.DELTA_TIME;
        entity_manager.clientPlayer.playTime += commons.DELTA_TIME;

        evenOlderCamPos = entity_manager.oldCameraPosition;

        entity_manager.oldCameraPosition = (entity_manager.cameraPosition[0], entity_manager.cameraPosition[1]);
        
        entity_manager.UpdateEnemies();
        entity_manager.UpdateProjectiles();
        entity_manager.UpdateParticles();
        entity_manager.UpdateMessages();
        entity_manager.UpdatePhysicsItems();
        entity_manager.CheckEnemySpawn();

        entity_manager.clientPlayer.Update();
        entity_manager.clientPlayer.Animate();

        entity_manager.UpdateDamageNumbers();
        entity_manager.UpdateRecentPickups();
        
        world.CheckGrowGrass();

        tempCamPosX = entity_manager.cameraPosition[0];
        tempCamPosY = entity_manager.cameraPosition[1];

        if commons.SMOOTHCAM:
            needToMoveX = (entity_manager.clientPlayer.position[0] - tempCamPosX) * commons.DELTA_TIME * 4;
            needToMoveY = (entity_manager.clientPlayer.position[1] - tempCamPosY) * commons.DELTA_TIME * 4;

            needToMoveMagnitude = math.sqrt(needToMoveX ** 2 + needToMoveY ** 2);
            needToMoveAngle = math.atan2(needToMoveY, needToMoveX);

            camDiffMagnitude = math.sqrt(entity_manager.cameraPositionDifference[0] ** 2 + entity_manager.cameraPositionDifference[1] ** 2);

            if camDiffMagnitude < 1:
                camDiffMagnitude = 1;

            canMoveMagnitude = camDiffMagnitude * (1 + commons.DELTA_TIME * 8);

            # Make sure it does not exceed a max camera speed
            canMoveMagnitude = min(canMoveMagnitude, 200 * commons.BLOCKSIZE * commons.DELTA_TIME);

            if needToMoveMagnitude > canMoveMagnitude:
                tempCamPosX = tempCamPosX + math.cos(needToMoveAngle) * canMoveMagnitude;
                tempCamPosY = tempCamPosY + math.sin(needToMoveAngle) * canMoveMagnitude;
            else:
                tempCamPosX = tempCamPosX + math.cos(needToMoveAngle) * needToMoveMagnitude;
                tempCamPosY = tempCamPosY + math.sin(needToMoveAngle) * needToMoveMagnitude;

        else:
            tempCamPosX = entity_manager.clientPlayer.position[0];
            tempCamPosY = entity_manager.clientPlayer.position[1];

        if tempCamPosX > world.BORDER_EAST + commons.BLOCKSIZE - commons.WINDOW_WIDTH * 0.5:
            tempCamPosX = world.BORDER_EAST + commons.BLOCKSIZE - commons.WINDOW_WIDTH * 0.5;
        elif tempCamPosX < commons.WINDOW_WIDTH * 0.5:
            tempCamPosX = commons.WINDOW_WIDTH * 0.5;
        if tempCamPosY > world.BORDER_SOUTH + commons.BLOCKSIZE * 1.5 - commons.WINDOW_HEIGHT * 0.5:
            tempCamPosY = world.BORDER_SOUTH + commons.BLOCKSIZE * 1.5 - commons.WINDOW_HEIGHT * 0.5
        elif tempCamPosY < commons.WINDOW_HEIGHT * 0.5:
            tempCamPosY = commons.WINDOW_HEIGHT * 0.5;
        
        entity_manager.cameraPosition = (tempCamPosX, tempCamPosY);

        entity_manager.cameraPositionDifference = (entity_manager.cameraPosition[0] - entity_manager.oldCameraPosition[0], entity_manager.cameraPosition[1] - entity_manager.oldCameraPosition[1]);

        MoveParallax((-entity_manager.cameraPositionDifference[0] * commons.PARALLAXAMNT, -entity_manager.cameraPositionDifference[1] * commons.PARALLAXAMNT)); #move parallax based on vel
        
        if entity_manager.clientPrompt != None:
            entity_manager.clientPrompt.Update();
            if entity_manager.clientPrompt.close == True:
                entity_manager.clientPrompt = None;
                commons.WAIT_TO_USE = True;
        
        if commons.BACKGROUND:
            if fadeBack:
                if fadeFloat < 1:
                    fadeSurf = surface_manager.largeBackgrounds[fadeBackgroundID].copy();
                    fadeSurf.set_alpha(fadeFloat * 255);
                    fadeFloat += 0.1;
                else:
                    fadeBack = False;
                    backgroundID = int(fadeBackgroundID);
            commons.screen.blit(surface_manager.largeBackgrounds[backgroundID], parallaxPos);
            if fadeBack:
                commons.screen.blit(fadeSurf, parallaxPos);
        else:
            commons.screen.fill((153, 217, 234));
        
        terrainPosition = (commons.WINDOW_WIDTH * 0.5 - entity_manager.cameraPosition[0], commons.WINDOW_HEIGHT * 0.5 - entity_manager.cameraPosition[1]);
        #DrawTerrainMultiThreaded(terrainPosition);
        commons.screen.blit(world.terrainSurface, terrainPosition);
        entity_manager.DrawProjectiles();
        entity_manager.clientPlayer.Draw();
        entity_manager.DrawParticles();
        entity_manager.DrawEnemies();
        entity_manager.DrawPhysicsItems();
                
        if commons.EXPERIMENTALLIGHTING:
            if not threadActive:
                lastThreadTime = (pygame.time.get_ticks() - lastThreadStart) * 0.001;
                _thread.start_new_thread(UpdateLight, ("Lighting Thread", 1));
                lastThreadStart = pygame.time.get_ticks();

            commons.screen.blit(newestLightSurf, (newestLightSurfPos[0] - entity_manager.cameraPosition[0] + commons.WINDOW_WIDTH * 0.5, newestLightSurfPos[1] - entity_manager.cameraPosition[1] + commons.WINDOW_HEIGHT * 0.5));

##            if newestLightSurf.get_width()<(10+LIGHTRENDERDISTANCEX*2)*commons.BLOCKSIZE:
##                if entity_manager.cameraPosition[0]<world.WORLD_SIZE_X*commons.BLOCKSIZE/2:
##                    lightOffsetX=-(10+LIGHTRENDERDISTANCEX*2)*commons.BLOCKSIZE-newestLightSurf.get_width()
##                else:
##                    lightOffsetX=(10+LIGHTRENDERDISTANCEX*2)*commons.BLOCKSIZE-newestLightSurf.get_width()
##            if newestLightSurf.get_height()<(10+LIGHTRENDERDISTANCEY*2)*commons.BLOCKSIZE:
##                if entity_manager.cameraPosition[1]<world.WORLD_SIZE_Y*commons.BLOCKSIZE/2:
##                    lightOffsetY=-(10+LIGHTRENDERDISTANCEY*2)*commons.BLOCKSIZE-newestLightSurf.get_height()
##                else:
##                    lightOffsetY=(10+LIGHTRENDERDISTANCEY*2)*commons.BLOCKSIZE-newestLightSurf.get_height()

        
        if commons.DRAWUI:
            entity_manager.clientPlayer.DrawHP();
            commons.screen.blit(entity_manager.clientPlayer.hotbarImage, (5, 20));
            entity_manager.DrawMessages();
            
        entity_manager.DrawDamageNumbers();
        entity_manager.DrawEnemyHoverText();
        entity_manager.DrawRecentPickups();
        RenderInteractableBlockHover();

        if entity_manager.clientPrompt != None:
            entity_manager.clientPrompt.Draw();

        if not entity_manager.clientPlayer.alive:
            DrawDeathMessage();

        if commons.DRAWUI:
            if entity_manager.clientPlayer.inventoryOpen:
                commons.screen.blit(entity_manager.clientPlayer.inventoryImage, (5, 70));
                entity_manager.clientPlayer.blitCraftSurf.fill((255, 0, 255));
                entity_manager.clientPlayer.blitCraftSurf.blit(entity_manager.clientPlayer.craftableItemsSurf, (0, entity_manager.clientPlayer.craftingMenuOffsetY));
                commons.screen.blit(entity_manager.clientPlayer.blitCraftSurf, (5, 270));
            
            if entity_manager.clientPlayer.chestOpen:
                commons.screen.blit(entity_manager.clientPlayer.chestImage, (245, 265));

            pygame.draw.rect(commons.screen, (230, 230, 10), Rect(5 + entity_manager.clientPlayer.hotbarIndex * 48, 20, 48, 48), 3);

            if entity_manager.clientPlayer.inventoryOpen:
                DrawInventoryHoverText();
                DrawExitButton();

            commons.screen.blit(handText, (242 - handText.get_width() * 0.5, 0));
            DrawItemHolding();
        
        if commons.BACKGROUND:
            CheckChangeBackground();
            MoveParallax((backgroundScrollVel, 0));
            
        if autoSaveTick <= 0:
            autoSaveTick += commons.AUTOSAVEFREQUENCY;
            entity_manager.clientPlayer.SavePlayer();
            world.SaveWorld();
        else:
            autoSaveTick -= commons.DELTA_TIME;
                
    elif commons.GAME_STATE == "MAINMENU":
        parallaxPos = (parallaxPos[0] - commons.DELTA_TIME * 20, 0);
        if parallaxPos[0] < -40:
            parallaxPos = (0, 0);
        commons.screen.blit(surface_manager.largeBackgrounds[1], parallaxPos);

        menu_manager.UpdateMenuButtons();
        menu_manager.DrawMenuButtons();

        if commons.GAME_SUB_STATE == "MAIN":
            commons.screen.blit(boarderImg, (commons.WINDOW_WIDTH * 0.5 - boarderImg.get_width() * 0.5, 95));
            commons.screen.blit(screenshotImg, (commons.WINDOW_WIDTH * 0.5 - screenshotImg.get_width() * 0.5, 120));
            commons.screen.blit(menu_manager.titleMessageText, (menu_manager.titleMessageTextLeft, 65));

        elif commons.GAME_SUB_STATE ==  "PLAYERSELECTION":
            if pygame.mouse.get_pressed()[0] and not commons.WAIT_TO_USE:
                if Rect(loadMenuBoxLeft1, 120, 336, 384).collidepoint(commons.MOUSE_POS):
                    for i in range(len(commons.PLAYER_SAVE_OPTIONS)):
                        if Rect(loadMenuBoxLeft2, 132 + i * 62 + saveSelectYOffset, 315, 60).collidepoint(commons.MOUSE_POS):
                            commons.WAIT_TO_USE = True;
                            commons.PLAYER_DATA = commons.PLAYER_SAVE_OPTIONS[i][0];
                            menu_manager.LoadMenuWorldData();
                            if commons.SOUND:
                                sound_manager.sounds[24].play();
                            commons.GAME_SUB_STATE = "WORLDSELECTION";
                            commons.GAME_SUB_STATE_STACK.append("PLAYERSELECTION");
                            menu_manager.UpdateActiveMenuButtons();
                            saveSelectYOffset = 0;
                            
            saveSelectYVel *= 0.9;
            if len(commons.PLAYER_SAVE_OPTIONS) > 5:
                saveSelectYOffset += saveSelectYVel;
                if saveSelectYOffset < -61 * len(commons.PLAYER_SAVE_OPTIONS) + 350:
                    saveSelectYOffset = -61 * len(commons.PLAYER_SAVE_OPTIONS) + 350;
                if saveSelectYOffset > 0:
                    saveSelectYOffset = 0;

            commons.screen.blit(loadMenuSurf, (loadMenuBoxLeft1, 120))
            saveSelectSurf.fill((255, 0, 255))
            for i in range(len(commons.PLAYER_SAVE_OPTIONS)): 
                saveSelectSurf.blit(commons.PLAYER_SAVE_OPTIONS[i][1], (0, i*62+saveSelectYOffset))
            commons.screen.blit(saveSelectSurf, (loadMenuBoxLeft2,  132))

        elif commons.GAME_SUB_STATE == "PLAYERCREATION":
            commons.screen.blit(commons.PLAYER_FRAMES[0][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[0][0].get_width() * 0.5, 100));
            commons.screen.blit(commons.PLAYER_FRAMES[1][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[1][0].get_width() * 0.5, 100));

        elif commons.GAME_SUB_STATE == "WORLDSELECTION":
            Break = False;
            if pygame.mouse.get_pressed()[0] and not commons.WAIT_TO_USE:
                if Rect(loadMenuBoxLeft1, 120, 336, 384).collidepoint(commons.MOUSE_POS):
                    for i in range(len(commons.WORLD_SAVE_OPTIONS)):
                        if Rect(loadMenuBoxLeft2, 132 + i * 60 + saveSelectYOffset, 315, 60).collidepoint(commons.MOUSE_POS):
                            if commons.SOUND:
                                sound_manager.sounds[24].play();

                            world.mapData = pickle.load(open("res/worlds/" + commons.WORLD_SAVE_OPTIONS[i][0] + ".wrld","rb")); #open selected save wrld file
                            world.clientWorld = pickle.load(open("res/worlds/" + commons.WORLD_SAVE_OPTIONS[i][0] + ".dat","rb")); #open selected save dat file
                            
                            world.WORLD_SIZE_X, world.WORLD_SIZE_Y = len(world.mapData), len(world.mapData[0]);

                            BIOMEBOARDER_X1 = world.WORLD_SIZE_X * 0.333333;
                            BIOMEBOARDER_X2 = world.WORLD_SIZE_X * 0.666666;
                            world.BORDER_WEST = int(commons.BLOCKSIZE);
                            world.BORDER_EAST = int(world.WORLD_SIZE_X * commons.BLOCKSIZE - commons.BLOCKSIZE);
                            world.BORDER_NORTH = int(commons.BLOCKSIZE*1.5);
                            world.BORDER_SOUTH = int(world.WORLD_SIZE_Y * commons.BLOCKSIZE - commons.BLOCKSIZE * 1.5);

                            world.tileMaskData = [[-1 for i in range(world.WORLD_SIZE_Y)] for i in range(world.WORLD_SIZE_X)];
                            world.wallTileMaskData = [[-1 for i in range(world.WORLD_SIZE_Y)] for i in range(world.WORLD_SIZE_X)];
                            backgroundID = 3;

                            entity_manager.CreatePlayer();

                            commons.screen.fill((0,0,0));

                            text0 = shared_methods.OutlineText("Greetings " + entity_manager.clientPlayer.name + ", bear with us while", (255, 255, 255), commons.LARGEFONT);
                            text1 = shared_methods.OutlineText("we load up '" + world.clientWorld.name + "'", (255, 255, 255), commons.LARGEFONT);
                            text2 = shared_methods.OutlineText(tables.helpfulTips[random.randint(0, len(tables.helpfulTips) - 1)], (255, 255, 255), commons.DEFAULTFONT);

                            commons.screen.blit(text0, (commons.WINDOW_WIDTH * 0.5 - text0.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.5 - 30));
                            commons.screen.blit(text1, (commons.WINDOW_WIDTH * 0.5 - text1.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.5));
                            commons.screen.blit(text2, (commons.WINDOW_WIDTH * 0.5 - text2.get_width() * 0.5, commons.WINDOW_HEIGHT * 0.75));

                            pygame.display.flip();
                            world.CreateTerrainSurface();

                            entity_manager.cameraPosition = (world.clientWorld.spawnPosition[0], 0);
                            entity_manager.clientPlayer.position = tuple(world.clientWorld.spawnPosition);
                            entity_manager.clientPlayer.RenderCurrentItemImage();
                            entity_manager.clientPlayer.RenderHotbar();
                            entity_manager.clientPlayer.RenderInventory();

                            RenderHandText();
                            
                            mapLight = [[0 for i in range(world.WORLD_SIZE_Y)]for j in range(world.WORLD_SIZE_X)];
                            for i in range(world.WORLD_SIZE_X - 1):
                                for j in range(world.WORLD_SIZE_Y - 1):
                                    if world.mapData[i][j][0] == -1 and world.mapData[i][j][1] == -1 and j < 110:
                                        mapLight[i][j] = globalLighting;
                                    else:
                                        mapLight[i][j] = 0;
                            
                            commons.GAME_STATE = "PLAYING";
                            Break = True;
                            break;
            if not Break:
                saveSelectYVel *= 0.9;
                if len(commons.WORLD_SAVE_OPTIONS) > 5:
                    saveSelectYOffset += saveSelectYVel;
                    if saveSelectYOffset < -61 * len(commons.WORLD_SAVE_OPTIONS) + 350:
                        saveSelectYOffset = -61 * len(commons.WORLD_SAVE_OPTIONS) + 350;
                    if saveSelectYOffset > 0:
                        saveSelectYOffset = 0;
                        
                commons.screen.blit(loadMenuSurf, (loadMenuBoxLeft1, 120));
                saveSelectSurf.fill((255, 0, 255));
                for i in range(len(commons.WORLD_SAVE_OPTIONS)): 
                    saveSelectSurf.blit(commons.WORLD_SAVE_OPTIONS[i][1], (0, i * 62 + saveSelectYOffset));
                commons.screen.blit(saveSelectSurf, (loadMenuBoxLeft2, 132));

        elif commons.GAME_SUB_STATE == "CLOTHES":
            commons.screen.blit(commons.PLAYER_FRAMES[0][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[0][0].get_width() * 0.5, 100));
            commons.screen.blit(commons.PLAYER_FRAMES[1][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[1][0].get_width() * 0.5, 100));

        elif commons.GAME_SUB_STATE == "WORLDNAMING":
            text = shared_methods.OutlineText(commons.TEXT_INPUT + "|", (255, 255, 255), commons.LARGEFONT);
            commons.screen.blit(text, (commons.WINDOW_WIDTH * 0.5 - text.get_width() * 0.5, 175));

        elif commons.GAME_SUB_STATE == "PLAYERNAMING":
            text = shared_methods.OutlineText(commons.TEXT_INPUT + "|", (255, 255, 255), commons.LARGEFONT);
            commons.screen.blit(text, (commons.WINDOW_WIDTH * 0.5 - text.get_width() * 0.5, 175));
            commons.screen.blit(commons.PLAYER_FRAMES[0][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[0][0].get_width() * 0.5, 100));
            commons.screen.blit(commons.PLAYER_FRAMES[1][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[1][0].get_width() * 0.5, 100));

        elif commons.GAME_SUB_STATE == "COLOURPICKER":

            entity_manager.clientColourPicker.Update();

            if entity_manager.clientColourPicker.selectedX != None and entity_manager.clientColourPicker.selectedY != None:
                commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][1] = entity_manager.clientColourPicker.selectedX;
                commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][2] = entity_manager.clientColourPicker.selectedY;
                commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][0] = tuple(entity_manager.clientColourPicker.selectedColour);
                player.UpdatePlayerModelUsingModelData();
                commons.PLAYER_FRAMES = Player.RenderSprites(commons.PLAYER_MODEL, directions = 1, armFrameCount = 1, torsoFrameCount = 1);
            
            commons.screen.blit(commons.PLAYER_FRAMES[0][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[0][0].get_width() * 0.5, 100));
            commons.screen.blit(commons.PLAYER_FRAMES[1][0], (commons.WINDOW_WIDTH * 0.5 - commons.PLAYER_FRAMES[1][0].get_width() * 0.5, 100));
            entity_manager.clientColourPicker.Draw();
            
    # Draw a prompt if there is one
    if entity_manager.clientPrompt != None:
        entity_manager.clientPrompt.Update();
        entity_manager.clientPrompt.Draw();
        if entity_manager.clientPrompt.close == True:
            entity_manager.clientPrompt = None;
            
    # Update fps text
    if commons.DRAWUI:
        if fpsTick <= 0:
            fpsTick += 0.5;
            if commons.DELTA_TIME > 0:
                fpsText = shared_methods.OutlineText(str(int(1.0 / commons.DELTA_TIME)), (255, 255, 255), commons.DEFAULTFONT);
        else:
            fpsTick -= commons.DELTA_TIME;
        commons.screen.blit(fpsText,(commons.WINDOW_WIDTH - fpsText.get_width(), 0));

    # Reset some variables when the mousebutton is lifted
    if not pygame.mouse.get_pressed()[0]:
        if commons.WAIT_TO_USE and not pygame.mouse.get_pressed()[2]:
            commons.WAIT_TO_USE = False;
        if commons.IS_HOLDING_ITEM:
            canDropHolding = True;
        elif not commons.IS_HOLDING_ITEM:
            canPickupItem = True;

    if not pygame.mouse.get_pressed()[2]:
        itemDropRate = 25;
        itemDropTick = 0;
            
    for event in pygame.event.get():
        if event.type == QUIT:
            if commons.GAME_STATE == "PLAYING":
                entity_manager.clientPlayer.inventoryOpen = False;
                entity_manager.clientPlayer.chestOpen = False;
                entity_manager.clientPrompt = prompt.Prompt("Exit", tables.exitMessages[random.randint(0, len(tables.exitMessages) - 1)], button1Name = "Yep", size = (6, 2));
            else:
                pygame.quit();
                sys.exit();
            commons.WAIT_TO_USE = True;
        
        if event.type == SONG_END:
            pygame.mixer.music.load("res/sounds/day.mp3");
            pygame.mixer.music.set_volume(sound_manager.musicVolume);
            pygame.mixer.music.play();
        

            #if event.key == K_CAPSLOCK:
            #    if commons.SHIFT_ACTIVE:
            #        commons.SHIFT_ACTIVE = False;
            #    else:
            #        commons.SHIFT_ACTIVE = True;

        
        if commons.GAME_STATE == "PLAYING":
            if event.type == KEYDOWN:
                # Toggle Inventory
                if event.key == K_ESCAPE:
                    if entity_manager.clientPlayer.inventoryOpen:
                        if commons.SOUND:
                            sound_manager.sounds[25].play();
                            entity_manager.clientPlayer.RenderCurrentItemImage();
                        entity_manager.clientPlayer.inventoryOpen = False;
                        entity_manager.clientPlayer.chestOpen = False;
                    else:
                        if commons.SOUND:
                            sound_manager.sounds[24].play();
                        entity_manager.clientPlayer.inventoryOpen = True;
                        entity_manager.clientPlayer.craftingMenuOffsetY = 120;
                        entity_manager.clientPlayer.UpdateCraftableItems();
                        entity_manager.clientPlayer.RenderCraftableItemsSurf();
                        entity_manager.clientPrompt = None;
                
                # Player Move Left
                if event.key == K_a:
                    entity_manager.clientPlayer.movingLeft = True;
                    entity_manager.clientPlayer.animationFrame = random.randint(17, 29);
                    if not entity_manager.clientPlayer.swingingArm:
                        entity_manager.clientPlayer.armAnimationFrame = random.randint(26, 39);
                    if entity_manager.clientPlayer.direction == 1:
                        entity_manager.clientPlayer.itemSwing = False;
                    entity_manager.clientPlayer.direction = 0;
                
                # Player Move Right
                if event.key == K_d:
                    entity_manager.clientPlayer.movingRight = True;
                    entity_manager.clientPlayer.animationFrame = random.randint(2, 15);
                    if not entity_manager.clientPlayer.swingingArm:
                        entity_manager.clientPlayer.armAnimationFrame = random.randint(6, 19);
                    if entity_manager.clientPlayer.direction == 0:
                        entity_manager.clientPlayer.itemSwing = False;
                    entity_manager.clientPlayer.direction = 1;

                # Player Walk
                if event.key == K_s:
                    entity_manager.clientPlayer.movingDown = True;
                    entity_manager.clientPlayer.animationSpeed = 0.05;

                # Player Jump
                if event.key == K_SPACE:
                    entity_manager.clientPlayer.Jump();

                # Kill All Enemies Cheat
                if event.key == K_x:
                    if commons.SHIFT_ACTIVE:
                        while len(entity_manager.enemies) > 0:
                            entity_manager.enemies[0].Kill((0, -50));
                        entity_manager.AddMessage("All enemies killed", (255, 223, 10), outlineColour = (80, 70, 3));
                
                # Spawn Enemy Cheat
                if event.key == K_f:
                    if commons.SHIFT_ACTIVE:
                        entity_manager.SpawnEnemy((entity_manager.cameraPosition[0] - commons.WINDOW_WIDTH * 0.5 + commons.MOUSE_POS[0], entity_manager.cameraPosition[1] - commons.WINDOW_HEIGHT * 0.5 + commons.MOUSE_POS[1]));
                        entity_manager.AddMessage("Spawned enemy", (255, 223, 10), outlineColour = (80, 70, 3));

                # Respawn Cheats
                if event.key == K_r:
                    if commons.SHIFT_ACTIVE:
                        world.clientWorld.spawnPosition = tuple(entity_manager.clientPlayer.position);
                        entity_manager.AddMessage("Spawn point moved to " + str(world.clientWorld.spawnPosition), (255, 223, 10), outlineColour = (80, 70, 3));
                    else:
                        if commons.PARTICLES:
                            for i in range(int(20 * commons.PARTICLEDENSITY)):
                                entity_manager.SpawnParticle(entity_manager.clientPlayer.position, (230, 230, 255), magnitude = 1 + random.random() * 6, size = 15, GRAV = 0);

                        if commons.SOUND:
                            sound_manager.sounds[12].play();

                        entity_manager.clientPlayer.Respawn();
                        entity_manager.AddMessage("Player respawned", (255, 223, 10), outlineColour = (80, 70, 3));

                        if commons.PARTICLES:
                            for i in range(int(40 * commons.PARTICLEDENSITY)):
                                entity_manager.SpawnParticle(entity_manager.clientPlayer.position, (230, 230, 255), magnitude = 1 + random.random() * 6, size = 15, GRAV = 0);
                
                # Gravity Reverse Cheat
                if event.key == K_g:
                    if commons.SHIFT_ACTIVE:
                        commons.GRAVITY = -commons.GRAVITY;
                        entity_manager.AddMessage("Gravity reversed", (255, 223, 10), outlineColour = (80, 70, 3));

                # Random Item Prefix Cheat
                if event.key == K_c:
                    if commons.SHIFT_ACTIVE:
                        if entity_manager.clientPlayer.hotbar[entity_manager.clientPlayer.hotbarIndex] != None:
                            entity_manager.clientPlayer.hotbar[entity_manager.clientPlayer.hotbarIndex] = Item(entity_manager.clientPlayer.hotbar[entity_manager.clientPlayer.hotbarIndex].ID);
                            entity_manager.AddMessage("Item prefix randomized", (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), life = 2.5);
                            entity_manager.clientPlayer.RenderCurrentItemImage();
                            RenderHandText();
                
                # Test Prompt Cheat
                if event.key == K_v:
                    if commons.SHIFT_ACTIVE:
                        entity_manager.clientPrompt = prompt.Prompt("test","My name's the guide, I can help you around this awfully crafted world. It's basically just a rip off of terraria so this should be child's play");
                        entity_manager.AddMessage("Random prompt delpoyed", (255, 223, 10), outlineColour = (80, 70, 3));

                # Get Tile and Wall IDS
                if event.key == K_p:
                    if commons.SHIFT_ACTIVE: 
                        if world.TileInMapRange(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1]):
                            wallID = world.mapData[commons.TILE_POSITION_MOUSE_HOVERING[0]][commons.TILE_POSITION_MOUSE_HOVERING[1]][1];
                            entity_manager.AddMessage("Wall at (" + str(commons.TILE_POSITION_MOUSE_HOVERING[0]) + ", " + str(commons.TILE_POSITION_MOUSE_HOVERING[1]) + ") has ID: " + str(wallID), (255, 223, 10), outlineColour = (80, 70, 3));
                    else:
                        if world.TileInMapRange(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1]):
                            tileID = world.mapData[commons.TILE_POSITION_MOUSE_HOVERING[0]][commons.TILE_POSITION_MOUSE_HOVERING[1]][0];
                            entity_manager.AddMessage("Tile at (" + str(commons.TILE_POSITION_MOUSE_HOVERING[0]) + ", " + str(commons.TILE_POSITION_MOUSE_HOVERING[1]) + ") has ID: " + str(tileID), (255, 223, 10), outlineColour = (80, 70, 3));
                
                # Spawn loot chest at mouse
                if event.key == K_m:
                    if world.TileInMapRange(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1]):
                        world.SpawnLootChest(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1]);

                        world.UpdateTerrainSurface(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1], affectOthers = False);
                        world.UpdateTerrainSurface(commons.TILE_POSITION_MOUSE_HOVERING[0] + 1, commons.TILE_POSITION_MOUSE_HOVERING[1], affectOthers = False);
                        world.UpdateTerrainSurface(commons.TILE_POSITION_MOUSE_HOVERING[0], commons.TILE_POSITION_MOUSE_HOVERING[1] + 1, affectOthers = False);
                        world.UpdateTerrainSurface(commons.TILE_POSITION_MOUSE_HOVERING[0] + 1, commons.TILE_POSITION_MOUSE_HOVERING[1] + 1, affectOthers = False);

                # Toggle UI
                if event.key == K_u:
                    commons.DRAWUI = not commons.DRAWUI;
                    entity_manager.AddMessage("UI " + shared_methods.GetOnOff(commons.DRAWUI), (255, 223, 10), outlineColour = (80, 70, 3));

                # Toggle SMOOTHCAM
                if event.key == K_j:
                    commons.SMOOTHCAM = not commons.SMOOTHCAM;
                    entity_manager.AddMessage("Smooth camera " + shared_methods.GetOnOff(commons.SMOOTHCAM), (255, 223, 10), outlineColour = (80, 70, 3));

                # Toggle HITBOXES
                if event.key == K_h:
                    commons.HITBOXES = not commons.HITBOXES;
                    entity_manager.AddMessage("Hitboxes " + shared_methods.GetOnOff(commons.HITBOXES), (255, 223, 10), outlineColour = (80, 70, 3));

                # Hotbar Item Selection
                if event.key==K_1: entity_manager.clientPlayer.hotbarIndex = 0; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                if event.key==K_2: entity_manager.clientPlayer.hotbarIndex = 1; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                if event.key==K_3: entity_manager.clientPlayer.hotbarIndex = 2; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                if event.key==K_4: entity_manager.clientPlayer.hotbarIndex = 3; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                if event.key==K_5: entity_manager.clientPlayer.hotbarIndex = 4; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                if event.key==K_6: entity_manager.clientPlayer.hotbarIndex = 5; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                if event.key==K_7: entity_manager.clientPlayer.hotbarIndex = 6; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                if event.key==K_8: entity_manager.clientPlayer.hotbarIndex = 7; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                if event.key==K_9: entity_manager.clientPlayer.hotbarIndex = 8; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                if event.key==K_0: entity_manager.clientPlayer.hotbarIndex = 9; entity_manager.clientPlayer.RenderCurrentItemImage(); entity_manager.clientPlayer.itemSwing = False; RenderHandText();
                
                if commons.SOUND:
                    if event.key == K_1 or event.key == K_2 or event.key == K_3 or event.key == K_4 or event.key == K_5 or event.key == K_6 or event.key == K_7 or event.key == K_8 or event.key == K_9 or event.key == K_0:
                        sound_manager.sounds[26].play();
                
                # Toggle Lighting
                if event.key == K_l:
                    #if commons.SHIFT_ACTIVE:
                        commons.EXPERIMENTALLIGHTING = not commons.EXPERIMENTALLIGHTING;
                        entity_manager.AddMessage("Experimental lighting "  + shared_methods.GetOnOff(commons.EXPERIMENTALLIGHTING), (255, 223, 10), outlineColour = (80, 70, 3));

                # Toggle Background
                if event.key == K_b:
                    if commons.SHIFT_ACTIVE:
                        commons.BACKGROUND = not commons.BACKGROUND;
                        entity_manager.AddMessage("Background " + shared_methods.GetOnOff(commons.BACKGROUND), (255, 223, 10), outlineColour = (80, 70, 3));

                # Music Volume Up
                if event.key == K_UP and commons.SHIFT_ACTIVE:
                    sound_manager.ChangeMusicVolume(0.05);
                
                # Music Volume Down
                if event.key == K_DOWN and commons.SHIFT_ACTIVE:
                    sound_manager.ChangeMusicVolume(-0.05);
                
                # Sound Volume Up
                if event.key == K_RIGHT and commons.SHIFT_ACTIVE:
                    sound_manager.ChangeSoundVolume(0.05);

                # Sound Volume Down
                if event.key == K_LEFT and commons.SHIFT_ACTIVE:
                    sound_manager.ChangeSoundVolume(-0.05);
                
            # Keyup Events
            if event.type == KEYUP:
                if event.key == K_a:
                    entity_manager.clientPlayer.movingLeft = False;
                if event.key == K_d:
                    entity_manager.clientPlayer.movingRight = False;
                if event.key == K_s:
                    entity_manager.clientPlayer.movingDownTick = 5;
                    entity_manager.clientPlayer.stopMovingDown = True;
                    entity_manager.clientPlayer.animationSpeed = 0.025;
                    
            # Hotbar Item and Crafting Scrolling
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    if entity_manager.clientPlayer.inventoryOpen:
                        entity_manager.clientPlayer.craftingMenuOffsetVelocityY += 3;
                    else:
                        if entity_manager.clientPlayer.hotbarIndex > 0:
                            entity_manager.clientPlayer.hotbarIndex -= 1;
                            entity_manager.clientPlayer.RenderCurrentItemImage();
                            entity_manager.clientPlayer.itemSwing = False;
                            RenderHandText();
                            if commons.SOUND:
                                sound_manager.sounds[26].play();
                        else:
                            entity_manager.clientPlayer.hotbarIndex = 9;

                if event.button == 5:
                    if entity_manager.clientPlayer.inventoryOpen:
                        entity_manager.clientPlayer.craftingMenuOffsetVelocityY -= 3;
                    else:
                        if entity_manager.clientPlayer.hotbarIndex < 9:
                            entity_manager.clientPlayer.hotbarIndex += 1;
                            entity_manager.clientPlayer.RenderCurrentItemImage();
                            entity_manager.clientPlayer.itemSwing = False;
                            RenderHandText();
                            if commons.SOUND:
                                sound_manager.sounds[26].play();
                        else:
                            entity_manager.clientPlayer.hotbarIndex = 0;

        elif commons.GAME_STATE == "MAINMENU":

            if commons.GAME_SUB_STATE == "PLAYERSELECTION" or commons.GAME_SUB_STATE == "WORLDSELECTION":
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 4:
                        saveSelectYVel += 3;
                    if event.button == 5:
                        saveSelectYVel -= 3;

            elif commons.GAME_SUB_STATE == "PLAYERNAMING" or commons.GAME_SUB_STATE == "WORLDNAMING":
                if event.type == KEYDOWN:
                    if event.key == K_a:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "A";
                        else:
                            commons.TEXT_INPUT += "a";
                    elif event.key==K_b:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "B";
                        else:
                            commons.TEXT_INPUT += "b";
                    elif event.key == K_c:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "C";
                        else:
                            commons.TEXT_INPUT += "c";
                    elif event.key == K_d:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "D";
                        else:
                            commons.TEXT_INPUT += "d";
                    elif event.key == K_e:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "E";
                        else:
                            commons.TEXT_INPUT += "e";
                    elif event.key == K_f:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "F";
                        else:
                            commons.TEXT_INPUT += "f";
                    elif event.key == K_g:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "G";
                        else:
                            commons.TEXT_INPUT += "g";
                    elif event.key == K_h:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "H";
                        else:
                            commons.TEXT_INPUT += "h";
                    elif event.key == K_i:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "I";
                        else:
                            commons.TEXT_INPUT += "i";
                    elif event.key == K_j:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "J";
                        else:
                            commons.TEXT_INPUT += "j";
                    elif event.key == K_k:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "K";
                        else:
                            commons.TEXT_INPUT += "k";
                    elif event.key == K_l:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "L";
                        else:
                            commons.TEXT_INPUT += "l";
                    elif event.key == K_m:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "M";
                        else:
                            commons.TEXT_INPUT += "m";
                    elif event.key == K_n:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "N";
                        else:
                            commons.TEXT_INPUT += "n";
                    elif event.key == K_o:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "O";
                        else:
                            commons.TEXT_INPUT += "o";
                    elif event.key == K_p:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "P";
                        else:
                            commons.TEXT_INPUT += "p";
                    elif event.key == K_q:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "Q";
                        else:
                            commons.TEXT_INPUT += "q";
                    elif event.key == K_r:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "R";
                        else:
                            commons.TEXT_INPUT += "r";
                    elif event.key == K_s:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "S";
                        else:
                            commons.TEXT_INPUT += "s";
                    elif event.key == K_t:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "T";
                        else:
                            commons.TEXT_INPUT += "t";
                    elif event.key == K_u:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "U";
                        else:
                            commons.TEXT_INPUT += "u";
                    elif event.key == K_v:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "V";
                        else:
                            commons.TEXT_INPUT += "v";
                    elif event.key == K_w:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "W";
                        else:
                            commons.TEXT_INPUT += "w";
                    elif event.key == K_x:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "X";
                        else:
                            commons.TEXT_INPUT += "x";
                    elif event.key == K_y:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "Y";
                        else:
                            commons.TEXT_INPUT += "y";
                    elif event.key == K_z:
                        if commons.SHIFT_ACTIVE:
                            commons.TEXT_INPUT += "Z";
                        else:
                            commons.TEXT_INPUT += "z";
                    elif event.key == K_0:
                        commons.TEXT_INPUT += "0";
                    elif event.key == K_1:
                        commons.TEXT_INPUT += "1";
                    elif event.key == K_2:
                        commons.TEXT_INPUT += "2";
                    elif event.key == K_3:
                        commons.TEXT_INPUT += "3";
                    elif event.key == K_4:
                        commons.TEXT_INPUT += "4";
                    elif event.key == K_5:
                        commons.TEXT_INPUT += "5";
                    elif event.key == K_6:
                        commons.TEXT_INPUT += "6";
                    elif event.key == K_7:
                        commons.TEXT_INPUT += "7";
                    elif event.key == K_8:
                        commons.TEXT_INPUT += "8";
                    elif event.key == K_9:
                        commons.TEXT_INPUT += "9";
                    elif event.key == K_SPACE:
                            commons.TEXT_INPUT += " ";
                    elif event.key == K_BACKSPACE:
                            commons.TEXT_INPUT = commons.TEXT_INPUT[:-1];
                    if len(commons.TEXT_INPUT) > 12:
                        commons.TEXT_INPUT = commons.TEXT_INPUT[:-1];
                    
    pygame.display.flip();
    clock.tick(commons.TARGETFPS);
