#surface_manager.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame;
from pygame.locals import *;

import commons;

def LoadTileMaskSurfaces():
    global tileMasks;
    tileMaskImage = pygame.image.load("res/images/tilemasks.png").convert_alpha();
    tileMasks = [];
    for j in range(5):
        for i in range(13):
            surf = pygame.Surface((8,8), pygame.SRCALPHA);
            surf.blit(tileMaskImage, (-i * 9, -j * 9));
            surf = pygame.transform.scale(surf, (commons.BLOCKSIZE, commons.BLOCKSIZE));
            tileMasks.append(surf);

def LoadMiscGuiSurfaces():
    global miscGUI;
    miscGUI = [];
    miscGUIImage = pygame.image.load("res/images/miscGUI.png").convert()
    for j in range(1):
        for i in range(11):
            surf = pygame.Surface((48, 48));
            surf.set_colorkey((255, 0, 255));
            surf.blit(miscGUIImage, (-i * 48, -j * 48));
            miscGUI.append(surf);

def LoadBackgroundSurfaces():
    global backgrounds;
    backgroundImage = pygame.image.load("res/images/backgroundTilesheet.png").convert()
    backgrounds = [];
    for i in range(6):
        surf = pygame.Surface((20, 20));
        surf.blit(backgroundImage, (-i * 20, 0));
        surf = pygame.transform.scale(surf, (40, 40));
        backgrounds.append(surf);

def LoadTileSurfaces():
    global tiles;
    tilesetImage = pygame.image.load("res/images/tileset.png").convert_alpha()
    tiles = [];
    for j in range(10):
        for i in range(10):
            surf = pygame.Surface((8, 8), pygame.SRCALPHA);
            surf.set_colorkey((255, 0, 255));
            surf.blit(tilesetImage, (-i * 8, -j * 8));
            surf = pygame.transform.scale(surf, (commons.BLOCKSIZE, commons.BLOCKSIZE));
            tiles.append(surf);

def LoadWallSurfaces():
    global walls;
    wallTilesetImage = pygame.image.load("res/images/wallTileset.png").convert_alpha();
    walls = [];
    for j in range(10):
        for i in range(10):
            surf = pygame.Surface((8, 8), pygame.SRCALPHA);
            surf.blit(wallTilesetImage,(-i * 8, -j * 8));
            surf = pygame.transform.scale(surf, (commons.BLOCKSIZE, commons.BLOCKSIZE));
            walls.append(surf);

def LoadProjectileSurfaces():
    global projectiles;
    projectileTilesetImage = pygame.image.load("res/images/projectileTileset.png").convert();
    projectiles = [];
    for j in range(10):
        for i in range(10):
            surf = pygame.Surface((16, 16));
            surf.blit(projectileTilesetImage, (-i * 16, -j * 16));
            surf.set_colorkey((255, 0, 255));
            projectiles.append(surf);

def LoadItemSurfaces():
    global items;
    itemTilesetImage = pygame.image.load("res/images/itemTileset.png").convert();
    items = [];
    for j in range(10):
        for i in range(10):
            surf = pygame.Surface((16, 16));
            surf.blit(itemTilesetImage, (-16 * i, -16 * j));
            surf2 = pygame.Surface((24, 24));
            surf2.fill((255, 0, 255));
            surf2.set_colorkey((255, 0, 255));
            surf2.blit(surf, (4, 4));
            surf2 = pygame.transform.scale(surf2, (48, 48));
            items.append(surf2);

def LoadHairSurfaces():
    global hair;
    hair = [];
    scale = 2;
    hairTilesetImage = pygame.transform.scale(pygame.image.load("res/images/hairsTileset.png"), (int(22 * 10 * scale), int(24 * scale)));
    for i in range(10):
        surf = pygame.Surface((int(22 * scale), int(24 * scale)));
        surf.set_colorkey((255, 0, 255));
        surf.blit(hairTilesetImage, (-i * 22 * scale, 0));
        surf = pygame.transform.scale(surf, (int(20 * scale), int(24 * scale)));
        hair.append(surf);

def LoadSpecialTileSurfaces():
    global specialTiles;
    specialTiles = [];
    scale = 2;
    specialTilesetImage = pygame.transform.scale(pygame.image.load("res/images/specialTileset.png"), (int(10 * 8 * scale), int(10 * 8 * scale)));
    for j in range(10):
        for i in range(10):
            surf = pygame.Surface((int(8 * scale), int(8 * scale)));
            surf.blit(specialTilesetImage, (-i * 8 * scale, -j * 8 * scale));
            specialTiles.append(surf);
        
def LoadTorsoSurfaces():
    global torsos;
    torsos = [];
    scale = 2;
    torsoTilesetImage = pygame.transform.scale(pygame.image.load("res/images/torsoTileset.png"), (int(20 * 19 * scale), int(30 * 4 * scale)));
    for j in range(4):
        for i in range(19):
            surf = pygame.Surface((int(20 * scale), int(30 * scale)));
            surf.set_colorkey((255, 0, 255));
            surf.blit(torsoTilesetImage, (-i * 20 * scale, -j * 30 * scale));
            torsos.append(surf);

def LoadSlimeSurfaces():
    global slimes;
    slimes = [];
    scale = 2;
    slimeTilesetImage = pygame.transform.scale(pygame.image.load("res/images/slimeTileset.png"), (int(16 * 3 * scale), int(12 * 5 * scale)));
    for j in range(5):
        for i in range(3):
            surf = pygame.Surface((int(16 * scale), int(12 * scale)));
            surf.set_colorkey((255, 0, 255));
            surf.blit(slimeTilesetImage, (-i * 16 * scale, -j * 12 * scale));
            surf.set_alpha(200);
            slimes.append(surf);
        
def CompileBackgroundImages():#creates a larger surf compiled with background surfs
    global largeBackgrounds;
    largeBackgrounds = [];
    for k in range(6):
        largeBackground = pygame.Surface((commons.WINDOW_WIDTH + 40, commons.WINDOW_HEIGHT + 40));
        for i in range(int(commons.WINDOW_WIDTH / 40 + 1)):
            for j in range(int(commons.WINDOW_HEIGHT / 40 + 1)):
                largeBackground.blit(backgrounds[k], (i * 40, j * 40));
        largeBackgrounds.append(largeBackground);
        
def Initialize():
    LoadTileMaskSurfaces();
    LoadMiscGuiSurfaces();
    LoadBackgroundSurfaces();
    LoadTileSurfaces();
    LoadWallSurfaces();
    LoadProjectileSurfaces();
    LoadItemSurfaces();
    LoadHairSurfaces();
    LoadSpecialTileSurfaces();
    LoadTorsoSurfaces();
    LoadSlimeSurfaces();
    CompileBackgroundImages();