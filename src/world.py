#world.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, random, pickle, datetime, perlin;
from pygame.locals import *;

import commons;
import tables;
import surface_manager;
import entity_manager;
import shared_methods;
import sound_manager;

def Initialize():
    global MAP_SIZE_X, MAP_SIZE_Y, mapData, tileMaskData, wallTileMaskData, clientWorld;
    MAP_SIZE_X = 0;
    MAP_SIZE_Y = 0;

    mapData = [];
    tileMaskData = [];
    wallTileMaskData = [];

    clientWorld = None;

    global BORDER_SOUTH, BORDER_NORTH, BORDER_WEST, BORDER_EAST;
    BORDER_SOUTH = 0;
    BORDER_NORTH = 0;
    BORDER_WEST = 0;
    BORDER_EAST = 0;

    global WORLD_NAME;
    WORLD_NAME = 0;

    global NOISE, NOISE_OFFSETS;
    NOISE = perlin.SimplexNoise(); #create NOISE object
    NOISE_OFFSETS = [random.random() * 1000, random.random() * 1000, random.random() * 1000]; #randomly generate offsets

class World():
    def __init__(self, name, creationDate,  size):
        self.name = name;
        self.creationDate = creationDate;
        self.size = size;
        self.playTime = 0;
        self.spawnPosition = (0, 0);
        self.chestData = [];

def SaveWorld():
    pickle.dump(mapData, open("res/worlds/" + str(clientWorld.name) + ".wrld", "wb")); #save wrld
    pickle.dump(clientWorld, open("res/worlds/" + str(clientWorld.name) + ".dat", "wb")); #save dat
    entity_manager.AddMessage("Saved World: " + clientWorld.name + "!", (255, 255, 255));

# Used to work out if a block can be placed at a position based on neighbors
def GetNeighborCount(i, j, tile = 0):
    if commons.CREATIVE:
        return 1;
    neighborCount = 0;
    try:
        if mapData[i-1][j][tile] != -1:
            neighborCount += 1;
    except IndexError:
        None;
    try:
        if mapData[i+1][j][tile] != -1:
            neighborCount += 1;
    except IndexError:
        None;
    try:
        if mapData[i][j-1][tile]!=-1:
            neighborCount += 1;
    except IndexError:
        None;
    try:
        if mapData[i][j+1][tile] != -1:
            neighborCount += 1;
    except IndexError:
        None;
    try:
        if mapData[i][j][1] != -1:
            neighborCount += 1;
    except IndexError:
        None;
    try:
        if mapData[i][j][0] != -1:
            neighborCount += 1;
    except IndexError:
        None;
    return neighborCount;

# Which blocks should merge with each other (Could use a 2D table for faster access)
def CheckTileMerge(ID1, ID2): 
    if ID1 == ID2: return True;
    if ID1 == 0: 
        if ID2 == 1: return True;
        elif ID2 == 2: return True;
        elif ID2 == 4: return True;
        elif ID2 == 5: return True;
        elif ID2 == 8: return True;
        elif ID2 == 13: return True;
        elif ID2 >= 68: return True;
    elif ID1 == 1: 
        if ID2 == 0: return True;
        elif ID2 == 2: return True;
    elif ID1 == 2: 
        if ID2 == 0: return True;
        elif ID2 == 1: return True;
        elif ID2 == 3: return True;
        elif ID2 == 4: return True;
        elif ID2 == 8: return True;
        elif ID2 == 9: return True;
        elif ID2 == 10: return True;
    elif ID1 == 3: 
        if ID2 == 2: return True;
    elif ID1 == 4: 
        if ID2 == 0: return True;
        elif ID2 == 2: return True;
        elif ID2 == 8: return True;
        elif ID2 == 13: return True;
    elif ID1 == 5: 
        if ID2 == 0: return True;
        if ID2 == 10: return True;
    elif ID1 == 8: 
        if ID2 == 0: return True;
        elif ID2 == 2: return True;
        elif ID2 == 4: return True;
        elif ID2 == 9: return True;
    elif ID1 == 9: 
        if ID2 == 2: return True;
        elif ID2 == 8: return True;
    elif ID1 == 10: 
        if ID2 == 2: return True;
        elif ID2 == 5: return True;
        elif ID2 == 11: return True;
        elif ID2 == 12: return True;
    elif ID1 == 11: 
        if ID2 == 10: return True;
    elif ID1 == 12: 
        if ID2 == 10: return True;
    elif ID1 == 13:
        if ID2 == 0: return True;
        elif ID2 == 4: return True;
    #elif ID1>=68: return True
    else: 
        return False;

def TileInMapRange(i, j, width = 1):
   if i < -1 + width: return False;
   if j < -1 + width: return False;
   if i > MAP_SIZE_X - width: return False;
   if j > MAP_SIZE_Y - width: return False;
   return True;

# Returns the mask type given an array of the surrounding blocks
def GetMaskNameFromSurroundingBlocks(numArr):
   if numArr == [0, 0, 0, 0]: return "single";
   elif numArr == [0, 0, 0, 1]: return "single_vertical_bot";
   elif numArr == [0, 0, 1, 0]: return "single_horizontal_right";
   elif numArr == [0, 0, 1, 1]: return "corner_bot_right";
   elif numArr == [0, 1, 0, 0]: return "single_vertical_top";
   elif numArr == [0, 1, 0, 1]: return "single_vertical_mid";
   elif numArr == [0, 1, 1, 0]: return "corner_top_right";
   elif numArr == [0, 1, 1, 1]: return "right_mid";
   elif numArr == [1, 0, 0, 0]: return "single_horizontal_left";
   elif numArr == [1, 0, 0, 1]: return "corner_bot_left";
   elif numArr == [1, 0, 1, 0]: return "single_horizontal_mid";
   elif numArr == [1, 0, 1, 1]: return "bot_mid";
   elif numArr == [1, 1, 0, 0]: return "corner_top_left";
   elif numArr == [1, 1, 0, 1]: return "left_mid";
   elif numArr == [1, 0, 1, 0]: return "single_horizontal_mid";
   elif numArr == [0, 1, 1, 1]: return "left_mid";
   elif numArr == [1, 1, 1, 1]: return "mid";
   elif numArr == [1, 1, 1, 0]: return "top_mid";

# Returns a random mask index for the given type
def GetMaskIndex(name):
    if name == "top_mid": return random.randint(1, 3);
    elif name == "left_mid": return int(random.randint(0, 2) * 13);
    elif name == "bot_mid": return random.randint(27, 29);
    elif name == "right_mid": return int(random.randint(0, 2) * 13) + 4;
    elif name == "single_vertical_mid": return int(random.randint(0, 2) * 13) + 5;
    elif name == "single_horizontal_mid": return random.randint(58, 60);
    elif name == "single_vertical_top": return random.randint(6, 8);
    elif name == "single_vertical_bot": return random.randint(45, 47);
    elif name == "single_horizontal_left": return int(random.randint(0, 2) * 13) + 9;
    elif name == "single_horizontal_right": return int(random.randint(0, 2) * 13) + 12;
    elif name == "single": return random.randint(48, 50);
    elif name == "corner_top_left": return 39 + int(random.randint(0, 2) * 2);
    elif name == "corner_top_right": return 40 + int(random.randint(0, 2) * 2);
    elif name == "corner_bot_left": return 52 + int(random.randint(0, 2) * 2);
    elif name == "corner_bot_right": return 53 + int(random.randint(0, 2) * 2);
    elif name == "mid": return 14;
    
# Returns the type of a given mask index
def GetMaskNameFromIndex(index):
    if index == 1 or index == 2 or index == 3: return "top_mid";
    elif index == 0 or index == 13 or index == 26: return "left_mid";
    elif index == 27 or index == 28 or index == 29: return "bot_mid";
    elif index == 4 or index == 17 or index == 30: return "right_mid";
    elif index == 5 or index == 18 or index == 31: return "single_vertical_mid";
    elif index == 58 or index == 59 or index == 60: return "single_horizontal_mid";
    elif index == 6 or index == 7 or index == 8: return "single_vertical_top";
    elif index == 45 or index == 46 or index == 47: return "single_vertical_bot";
    elif index == 9 or index == 22 or index == 35: return "single_horizontal_left";
    elif index == 12 or index == 25 or index == 38: return "single_horizontal_right";
    elif index == 48 or index == 49 or index == 50: return "single";
    elif index == 39 or index == 41 or index == 43: return "corner_top_left";
    elif index == 40 or index == 42 or index == 44: return "corner_top_right";
    elif index == 52 or index == 54 or index == 56: return "corner_bot_left";
    elif index == 53 or index == 55 or index == 57: return "corner_bot_right";
   
# Returns the index of the mask for the wall at a given position
def GetWallMaskIndexFromPos(i, j, ID):
    sameBlocks = [1, 1, 1, 1];
    if i > 0:
        if not CheckTileMerge(mapData[i - 1][j][1], ID):
            sameBlocks[2] = 0;
    if i < MAP_SIZE_X - 1:
        if not CheckTileMerge(mapData[i + 1][j][1], ID):
            sameBlocks[0] = 0;
    if j > 0:
        if not CheckTileMerge(mapData[i][j - 1][1], ID):
            sameBlocks[3] = 0;
    if j < MAP_SIZE_Y - 1:
        if not CheckTileMerge(mapData[i][j + 1][1], ID):
            sameBlocks[1] = 0;
    return GetMaskIndex(GetMaskNameFromSurroundingBlocks(sameBlocks));


# Returns the index of the mask for the block at a given position
def GetMaskIndexFromPos(i, j, ID):
    sameBlocks = [1, 1, 1, 1];
    if i > 0:
        if not CheckTileMerge(mapData[i - 1][j][0], ID):
            sameBlocks[2] = 0;
    if i < MAP_SIZE_X - 1:
        if not CheckTileMerge(mapData[i + 1][j][0],ID):
            sameBlocks[0] = 0;
    if j > 0:
        if not CheckTileMerge(mapData[i][j - 1][0],ID):
            sameBlocks[3] = 0;
    if j < MAP_SIZE_Y - 1:
        if not CheckTileMerge(mapData[i][j + 1][0], ID):
            sameBlocks[1] = 0;
    return GetMaskIndex(GetMaskNameFromSurroundingBlocks(sameBlocks));

def BlitGenerationStage(string):
    commons.screen.blit(surface_manager.largeBackgrounds[1], (0, 0));
    #commons.screen.blit(titleText, (menuLeft1, 10));
    text1 = shared_methods.OutlineText("Generating " + WORLD_NAME + "", (255, 255, 255), commons.XLARGEFONT);
    text2 = shared_methods.OutlineText(string, (255, 255, 255), commons.LARGEFONT);
    commons.screen.blit(text1, (commons.WINDOW_WIDTH * 0.5 - text1.get_width()  * 0.5, 120));
    commons.screen.blit(text2, (commons.WINDOW_WIDTH * 0.5 - text2.get_width() * 0.5, 300));
    pygame.display.flip();

# Initializes all structures related to terrain and generates a map of thive given size using the given generation type
def GenerateTerrain(genType, blitProgress = False):
    global mapData, tileMaskData, wallTileMaskData, clientWorld;
    BIOMEBOARDER_X1 = MAP_SIZE_X * 0.333333;
    BIOMEBOARDER_X2 = MAP_SIZE_X * 0.666666;
    BORDER_WEST = int(commons.BLOCKSIZE);
    BORDER_EAST = int(MAP_SIZE_X * commons.BLOCKSIZE - commons.BLOCKSIZE);
    BORDER_NORTH = int(commons.BLOCKSIZE * 1.5);
    BORDER_SOUTH = int(MAP_SIZE_Y * commons.BLOCKSIZE - commons.BLOCKSIZE * 1.5);

    mapData = [[-1 for i in range(MAP_SIZE_Y)] for i in range(MAP_SIZE_X)];
    tileMaskData = [[-1 for i in range(MAP_SIZE_Y)] for i in range(MAP_SIZE_X)];
    wallTileMaskData = [[-1 for i in range(MAP_SIZE_Y)] for i in range(MAP_SIZE_X)];
    date = datetime.datetime.now();
    clientWorld = World(WORLD_NAME, str(str(date)[:19]), genType);

    if genType == "ice caves":
        mapData = [[[-1, 0] for i in range(MAP_SIZE_X)] for j in range(MAP_SIZE_Y)];
        backgroundID = 0;

        for i in range(MAP_SIZE_X):
            for j in range(MAP_SIZE_Y):

                val = NOISE.noise2(i / 15 + NOISE_OFFSETS[0], j / 15 + NOISE_OFFSETS[0]);
                if val > -0.2:
                    val2 = NOISE.noise2(i / 15 + NOISE_OFFSETS[1], j / 15 + NOISE_OFFSETS[1]);
                    if val2 > 0.4:
                        mapData[i][j][0] = 2;
                    else:
                        mapData[i][j][0] = 3;
                else:
                    mapData[i][j][0] = -1;

    elif genType == "DEFAULT":
        print("genType: " + genType);
        print("Worldsize: " + str(MAP_SIZE_X * MAP_SIZE_Y) + " blocks. (" + str(MAP_SIZE_X) + "x" + str(MAP_SIZE_Y) + ")\n");

        for i in range(MAP_SIZE_X):
            if blitProgress:
                BlitGenerationStage("Generating Terrain: " + str(round((i / MAP_SIZE_X) * 100, 1)) + "%");

            for j in range(MAP_SIZE_Y):
                if i < BIOMEBOARDER_X1 + random.randint(-5, 5):
                    biome = 1;
                elif i < BIOMEBOARDER_X2 + random.randint(-5, 5):
                    biome = 0;
                else:
                    biome = 2;

                wallValue = -1;
                if j > 350 + random.randint(-5, 5): # caverns layer 2
                    val = NOISE.noise2(i / 30 + NOISE_OFFSETS[2], j / 20 + NOISE_OFFSETS[2]);
                    val2 = NOISE.noise2(i / 30 + NOISE_OFFSETS[0], j / 30 + NOISE_OFFSETS[0]);
                    if val > 0.55:
                        tileValue = -1;
                        wallValue = -1;
                    elif val > 0.1:
                        tileValue = -1;
                        wallValue = int(tables.biomeTileVals[biome][1][1]);
                    else:
                        tileValue = int(tables.biomeTileVals[biome][0][2]);
                        wallValue = int(tables.biomeTileVals[biome][1][1]);
                
                elif j > 250 + random.randint(-3, 3): # caverns layer 1
                    val = NOISE.noise2(i / 30 + NOISE_OFFSETS[2], j / 20 + NOISE_OFFSETS[2]);
                    val2 = NOISE.noise2(i / 30 + NOISE_OFFSETS[0], j / 30 + NOISE_OFFSETS[0]);
                    if val > 0.5:
                        tileValue = -1;
                        wallValue = -1;
                    elif val > 0.15:
                        tileValue = -1;
                        wallValue = int(tables.biomeTileVals[biome][1][1]);
                    elif val2 > 0.5:
                        tileValue = int(tables.biomeTileVals[biome][0][1]);
                        wallValue = int(tables.biomeTileVals[biome][1][0]);
                    else:
                        tileValue = int(tables.biomeTileVals[biome][0][2]);
                        wallValue = int(tables.biomeTileVals[biome][1][1]);
                
                elif j > 200 + random.randint(-2, 2): #tier 2 small caves
                    val = NOISE.noise2(i / 30 + NOISE_OFFSETS[2], j / 20 + NOISE_OFFSETS[2]);
                    val2 = NOISE.noise2(i / 30 + NOISE_OFFSETS[0], j / 30 + NOISE_OFFSETS[0]);
                    if val > 0.3:
                        tileValue = -1;
                        wallValue = int(tables.biomeTileVals[biome][1][1]);
                    elif val2 > 0.3:
                        tileValue = int(tables.biomeTileVals[biome][0][1]);
                        wallValue = int(tables.biomeTileVals[biome][1][0]);
                    else:
                        tileValue = int(tables.biomeTileVals[biome][0][2]);
                        wallValue = int(tables.biomeTileVals[biome][1][1]);
                
                elif j > 95: #tier 1 small caves
                    val = NOISE.noise2(i / 35 + NOISE_OFFSETS[1], j / 25 + NOISE_OFFSETS[1]);
                    val2 = NOISE.noise2(i / 20 + NOISE_OFFSETS[0], j / 20 + NOISE_OFFSETS[0]);
                    if val > 0.45:
                        tileValue = -1;
                    elif val2 > 0.1:
                        tileValue = int(tables.biomeTileVals[biome][0][2]);
                    else:
                        tileValue = int(tables.biomeTileVals[biome][0][1]);
                    wallValue = int(tables.biomeTileVals[biome][1][0]);
                else: #surface
                    val = NOISE.noise2(i / 30 + NOISE_OFFSETS[1], j / 20 + NOISE_OFFSETS[1]);
                    val2 = NOISE.noise2(i / 100 + NOISE_OFFSETS[2], 0.1);
                    val3 = NOISE.noise2(i / 15 + NOISE_OFFSETS[0], j / 15 + NOISE_OFFSETS[0]);
                    val4 = NOISE.noise2(i / 35 + NOISE_OFFSETS[1], j / 25 + NOISE_OFFSETS[1]);
                    if j >= val * 5 + 60 + val2 * 30:
                        if val4 > 0.5:
                            tileValue = -1;
                            wallValue = int(tables.biomeTileVals[biome][1][0]);
                        elif val3 > -0.6:
                            tileValue = int(tables.biomeTileVals[biome][0][1]);
                            wallValue = int(tables.biomeTileVals[biome][1][0]);
                        else:
                            tileValue = int(tables.biomeTileVals[biome][0][2]);
                            wallValue = int(tables.biomeTileVals[biome][1][1]);
                        if mapData[i][j-1][0] == -1 and tileValue == int(tables.biomeTileVals[biome][0][1]):
                            tileValue = int(tables.biomeTileVals[biome][0][0]);
                            wallValue = int(tables.biomeTileVals[biome][1][0]);
                    else:
                        tileValue = -1;
                mapData[i][j] = [tileValue, wallValue];

        if blitProgress:
            BlitGenerationStage("Spawning ores");
        
        for i in range(int(MAP_SIZE_X * MAP_SIZE_Y / 1200)):
            CreateVein(random.randint(0, MAP_SIZE_X - 1), random.randint(70, 500), 7, random.randint(2, 4));
        
        for i in range(int(MAP_SIZE_X * MAP_SIZE_Y / 1200)):
            CreateVein(random.randint(0, MAP_SIZE_X - 1), random.randint(70, 500), 6, random.randint(2, 4));
        
        if blitProgress:
            BlitGenerationStage("Growing Trees");
        
        for i in range(int(MAP_SIZE_X / 5)):
            if random.randint(1, 2) == 1:
                CreateTree(i * 5, 0, random.randint(5, 15));

    elif genType == "superflat":
        mapData = [];
        backgroundID = 3;
        for i in range(MAP_SIZE_X):
            mapData.append([]);
            for j in range(MAP_SIZE_Y):
                if j > 100:
                    tileValue = 1;
                    wallValue = 1;
                else:
                    tileValue = -1;
                    wallValue = -1;
                mapData[i].append([tileValue, wallValue]);

    CreateGroundedSpawnPosition();
    
    print("Generation complete!");

# Creates the terrain surface
def CreateTerrainSurface(): 
    global terrainSurface;
    print("Creating Terrain Surface...");
    terrainSurface = pygame.Surface((MAP_SIZE_X * commons.BLOCKSIZE, MAP_SIZE_Y * commons.BLOCKSIZE));
    terrainSurface.fill((255, 0, 255));
    terrainSurface.set_colorkey((255, 0, 255));
    for i in range(MAP_SIZE_X):
        for j in range(MAP_SIZE_Y):
            UpdateTerrainSurface(i, j, affectOthers = False);

def DestroySpecialTile(i, j):
    data = tables.specialTileData[mapData[i][j][0] - 255];
    origin = (i + data[0][0], j + data[0][1]);
    destroy = True;
    if data[3] == "CHEST":
        for k in range(len(clientWorld.chestData)):
            if clientWorld.chestData[k][0] == origin:
                for f in range(5):
                    for m in range(4):
                        if clientWorld.chestData[k][1][f][m] != None:
                            destroy = False;
                break;
                #for f in range(5):
                #    for m in range(4):
                #        if clientWorld.chestData[k][1][f][m] != None:
                #        entity_manager.SpawnPhysicsItem((i * commons.BLOCKSIZE, j * commons.BLOCKSIZE), clientWorld.chestData[k][1][f][m]);

    if destroy:
        for dat in data[1]:
            mapData[i + dat[0]][j + dat[1]][0] = -1;
            UpdateTerrainSurface(i + dat[0], j + dat[1]);
        entity_manager.SpawnPhysicsItem((i * commons.BLOCKSIZE, j * commons.BLOCKSIZE), data[4], 0, pickupDelay = 10);


def UseSpecialTile(i, j):
    data = tables.specialTileData[mapData[i][j][0] - 255];
    if data[3] == "CHEST":
        for k in range(len(clientWorld.chestData)):
            if clientWorld.chestData[k][0] == (i, j):
                entity_manager.clientPlayer.OpenChest(clientWorld.chestData[k][1]);

    if data[3] == "CRAFTTABLE":
        entity_manager.clientPlayer.craftingMenuOffsetY = 120;
        entity_manager.clientPlayer.UpdateCraftableItems();
        entity_manager.clientPlayer.RenderCraftableItemsSurf();
        entity_manager.clientPlayer.inventoryOpen = True;
        entity_manager.clientPrompt = None;

    if data[2] == "CT":
        if entity_manager.clientPlayer.direction == 1:
            canOpen = True;
            for k in range(len(data[5][1])):
                if TileInMapRange(i + data[5][1][k][1], j + data[5][1][k][2]):
                    if data[5][1][k][1] != 0:
                        if not mapData[i + data[5][1][k][1]][j + data[5][1][k][2]][0]==-1:
                            canOpen = False;
            if canOpen:
                if commons.SOUND:
                    sound_manager.sounds[28].play();
                for k in range(len(data[5][1])):
                    mapData[i + data[5][1][k][1]][j + data[5][1][k][2]][0] = int(data[5][1][k][0]);
                    UpdateTerrainSurface(i + data[5][1][k][1], j + data[5][1][k][2], affectOthers = False);
        else:
            canOpen = True;
            for k in range(len(data[5][0])):
                if TileInMapRange(i + data[5][0][k][1],j + data[5][0][k][2]):
                    if data[5][0][k][1] != 0:
                        if not mapData[i + data[5][0][k][1]][j + data[5][0][k][2]][0]== -1:
                            canOpen = False;
            if canOpen:
                if commons.SOUND:
                    sound_manager.sounds[28].play();
                for k in range(len(data[5][0])):
                    mapData[i + data[5][0][k][1]][j + data[5][0][k][2]][0] = int(data[5][0][k][0]);
                    UpdateTerrainSurface(i + data[5][0][k][1], j + data[5][0][k][2], affectOthers = False);

    elif data[2]=="OLTL":
        if commons.SOUND:
            sound_manager.sounds[29].play();
        for k in range(len(data[5])):
            mapData[i + data[5][k][1]][j + data[5][k][2]][0] = int(data[5][k][0]);
            UpdateTerrainSurface(i + data[5][k][1], j + data[5][k][2], affectOthers = False);

    elif data[2] == "ORTL":
        if commons.SOUND:
            sound_manager.sounds[29].play();
        for k in range(len(data[5])):
            mapData[i + data[5][k][1]][j + data[5][k][2]][0]=int(data[5][k][0])
            UpdateTerrainSurface(i + data[5][k][1], j + data[5][k][2], affectOthers = False);

    commons.WAIT_TO_USE = True;

# Updates a tile in the terrain surface and optionally, the blocks around it.
def UpdateTerrainSurface(i, j, affectOthers = True):
    global terrainSurface;
    tilesToUpdate = [];
    if affectOthers:
        if i > 0:
            tilesToUpdate.append((i - 1, j));
        if i < MAP_SIZE_X - 1:
            tilesToUpdate.append((i + 1, j));
        if j > 0:
            tilesToUpdate.append((i, j - 1));
        if j < MAP_SIZE_Y - 1:
            tilesToUpdate.append((i, j + 1));
    tilesToUpdate.append((i, j));

    for tile in tilesToUpdate:
        pygame.draw.rect(terrainSurface, (255, 0, 255), Rect(tile[0] * commons.BLOCKSIZE, tile[1] * commons.BLOCKSIZE, commons.BLOCKSIZE, commons.BLOCKSIZE), 0);
        tileDat = mapData[tile[0]][tile[1]];
        if tileDat[0] != -1: # If there is a block at i, j
            if tileDat[0] >= 255:
                special = True;
            else:
                special = False;
            if tileDat[0] in tables.transparentBlocks:
                transparent = True;
            else:
                transparent = False;
            
            tileMaskData[tile[0]][tile[1]] = GetMaskIndexFromPos(tile[0], tile[1], tileDat[0]); # Get the mask at i, j and store it in the tileMaskData array
                        
            if special:
                tiletex = pygame.Surface((commons.BLOCKSIZE, commons.BLOCKSIZE));
                tiletex.blit(surface_manager.specialTiles[tileDat[0] - 255], (0, 0)); # Get the texture of the block at i, j
                tiletex.set_colorkey((255, 0, 255));
            else:
                tiletex = surface_manager.tiles[tileDat[0]].copy();
                tiletex.blit(surface_manager.tileMasks[tileMaskData[tile[0]][tile[1]]],  (0,  0),  None,  pygame.BLEND_RGBA_MULT); # Blit the block mask to the block texture using a multiply blend flag
                
            if (tileMaskData[tile[0]][tile[1]] != 14 or transparent) and tileDat[1] != -1: # If the block is not a centre block (and so there is some transparency in it) and there is a wall tile behind it,  blit the wall tile
                backimg = surface_manager.walls[tileDat[1]].copy(); # Get the wall texture
                wallTileMaskData[tile[0]][tile[1]] = GetWallMaskIndexFromPos(tile[0], tile[1], tileDat[1]); # Get the wall mask
                if GetMaskNameFromIndex(wallTileMaskData[tile[0]][tile[1]]) == GetMaskNameFromIndex(tileMaskData[tile[0]][tile[1]]):# If the mask of the wall and the mask of the tile are from the same type
                    wallTileMaskData[tile[0]][tile[1]] = tileMaskData[tile[0]][tile[1]]; # Set the wall mask to the tile mask
                backimg.blit(surface_manager.tileMasks[wallTileMaskData[tile[0]][tile[1]]],  (0,  0),  None,  pygame.BLEND_RGBA_MULT); # Blit the mask onto the wall texture using a multiply blend flag    
                backimg.blit(tiletex,  (0,  0)); # Blit the masked block texture to the main surface
                terrainSurface.blit(backimg,  (tile[0] * commons.BLOCKSIZE,  tile[1] * commons.BLOCKSIZE)); # Blit the masked wall surf to the main surf
            else:
                terrainSurface.blit(tiletex,  (tile[0] * commons.BLOCKSIZE,  tile[1] * commons.BLOCKSIZE)); # Blit the masked wall surf to the main surf
        elif tileDat[1] != -1: # If there is no block but there is a wall
            backimg = surface_manager.walls[tileDat[1]].copy(); # Get the wall texture
            wallTileMaskData[tile[0]][tile[1]] = GetWallMaskIndexFromPos(tile[0], tile[1], tileDat[1]); # Get the wall mask
            backimg.blit(surface_manager.tileMasks[wallTileMaskData[tile[0]][tile[1]]],  (0,  0),  None,  pygame.BLEND_RGBA_MULT); # Blit the mask onto the wall texture using a multiply blend flag
            terrainSurface.blit(backimg,  (tile[0] * commons.BLOCKSIZE,  tile[1] * commons.BLOCKSIZE)); # Blit the masked wall surf to the main surf

# Recursively creates ore at a location
def CreateVein(i, j, tileID, size):
    try:
        if mapData[i][j][0] != -1 and mapData[i][j][0] != tileID and size > 0:
            if random.randint(1, 10) == 1:
                size += 1;
            mapData[i][j][0] = tileID;
            CreateVein(i - 1, j, tileID, size - 1);
            CreateVein(i + 1, j, tileID, size - 1);
            CreateVein(i, j - 1, tileID, size - 1);
            CreateVein(i, j + 1, tileID, size - 1);
    except:
        None;
    
def CreateTree(i, j, height):
    global mapData;
    grounded = False;
    for k in range(MAP_SIZE_Y - j - 1):
        val = mapData[i][j + 1][0];
        if val == 5 or val == 2:
            block1 = 10;
            if val == 5:
                block2 = 11;
            if val == 2:
                block2 = 12;
            grounded = True;
            break;
        if val != -1:
            break;
        j += 1;
    if not grounded:
        return;
    if mapData[i - 1][j + 1][0] == 5 or mapData[i - 1][j + 1][0] == 2:
        mapData[i - 1][j][0] = int(block1);
    if mapData[i + 1][j + 1][0] == 5 or mapData[i + 1][j + 1][0] == 2:
        mapData[i + 1][j][0] = int(block1);
    h = int(height);
    for k in range(height):
        mapData[i][j][0] = int(block1);
        if h > 2 and h < height - 1:
            if random.randint(1, 5) == 1:
                if random.randint(0, 1) == 0:
                    mapData[i - 1][j][0] = int(block2);
                else:
                    mapData[i + 1][j][0] = int(block2);
        h -= 1;
        j -= 1;
    #create canopy
    for k in range(-1, 2):
        mapData[i + k][j - 2][0] = int(block2);
    for k in range(-2, 3):
        mapData[i + k][j - 1][0] = int(block2);
    for k in range(-2, 3):
        mapData[i + k][j][0] = int(block2);
    mapData[i - 1][j + 1][0] = int(block2);
    mapData[i + 1][j + 1][0] = int(block2);

#creates and grounds spawn point
def CreateGroundedSpawnPosition():
    global clientWorld;
    clientWorld.spawnPosition = (commons.BLOCKSIZE * 40, commons.BLOCKSIZE * 1.5)
    for i in range(300):
        clientWorld.spawnPosition = (clientWorld.spawnPosition[0], clientWorld.spawnPosition[1] + commons.BLOCKSIZE);
        x1 = int(clientWorld.spawnPosition[0] - commons.BLOCKSIZE * 0.5) // commons.BLOCKSIZE;
        y1 = int(clientWorld.spawnPosition[1] + commons.BLOCKSIZE) // commons.BLOCKSIZE;
        x2 = int(clientWorld.spawnPosition[0] + commons.BLOCKSIZE * 0.5) // commons.BLOCKSIZE;
        y2 = int(clientWorld.spawnPosition[1] + commons.BLOCKSIZE) // commons.BLOCKSIZE;
        if mapData[x1][y1][0] not in tables.uncollidableBlocks or mapData[x2][y2][0] not in tables.uncollidableBlocks:
            clientWorld.spawnPosition = (clientWorld.spawnPosition[0], clientWorld.spawnPosition[1] - commons.BLOCKSIZE * 1.5);
            break;