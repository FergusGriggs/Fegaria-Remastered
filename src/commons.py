#commons.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame;
from pygame.locals import *;

def LoadConfig():
    global GRAVITY, WINDOW_WIDTH, WINDOW_HEIGHT, RUNFULLSCREEN, PARTICLES, PARTICLEDENSITY, MUSIC, CONFIG_MUSIC_VOLUME, SOUND, CONFIG_SOUND_VOLUME, CREATIVE, BACKGROUND, PARALLAXAMNT, PASSIVE, MAXENEMYSPAWNS, FANCYTEXT, HITBOXES, SPLASHSCREEN, AUTOSAVEFREQUENCY, EXPERIMENTALLIGHTING, SMOOTHCAM, DRAWUI
    
    config = open("config.txt", "r");
    configDataStr = config.readlines();
    configData = [];
    for item in configDataStr:
        item = item.split("=");
        configData.append(item[1][:-1]);
    WINDOW_WIDTH = int(configData[0].split(",")[0]);
    WINDOW_HEIGHT = int(configData[0].split(",")[1]);
    GRAVITY = 9.8 * BLOCKSIZE * 0.666 * float(configData[1]); # 3 tiles = 1 metre
    RUNFULLSCREEN = bool(int(configData[2]));
    PARTICLES = bool(int(configData[3]));
    PARTICLEDENSITY = float(configData[4]);
    MUSIC = bool(int(configData[5]));
    CONFIG_MUSIC_VOLUME = float(configData[6]);
    SOUND = bool(int(configData[7]));
    CONFIG_SOUND_VOLUME = float(configData[8]);
    CREATIVE = bool(int(configData[9]));
    BACKGROUND = bool(int(configData[10]));
    PARALLAXAMNT = float(configData[11]);
    PASSIVE = bool(int(configData[12]));
    MAXENEMYSPAWNS = int(configData[13]);
    FANCYTEXT = bool(int(configData[14]));
    HITBOXES = bool(int(configData[15]));
    SPLASHSCREEN = bool(int(configData[16]))
    AUTOSAVEFREQUENCY = float(configData[17]);
    EXPERIMENTALLIGHTING = bool(int(configData[18]));
    SMOOTHCAM = bool(int(configData[19]));
    DRAWUI = bool(int(configData[20]));

def Initialize():
    global BLOCKSIZE, TARGETFPS, MOUSE_POS, TILE_POSITION_MOUSE_HOVERING, SHIFT_ACTIVE, GAME_STATE, GAME_SUB_STATE, GAME_SUB_STATE_STACK, screen, SMALLFONT, DEFAULTFONT, LARGEFONT, XLARGEFONT;
    BLOCKSIZE = 16;
    TARGETFPS = 244;
    MOUSE_POS = (0, 0);
    TILE_POSITION_MOUSE_HOVERING = (0, 0);
    SHIFT_ACTIVE = False;

    GAME_STATE = "MAINMENU";
    GAME_SUB_STATE = "MAIN";
    GAME_SUB_STATE_STACK = [];

    LoadConfig();
    
    if RUNFULLSCREEN:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN);
    else:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT));

    fontFilePath = "res/fonts/VCR_OSD_MONO_1.001.ttf";
    SMALLFONT = pygame.font.Font(fontFilePath, 10);
    DEFAULTFONT = pygame.font.Font(fontFilePath, 16);
    LARGEFONT = pygame.font.Font(fontFilePath, 30);
    XLARGEFONT = pygame.font.Font(fontFilePath, 50);

    global WAIT_TO_USE;
    WAIT_TO_USE = False;

    global ENEMY_SPAWN_TICK, MIN_ENEMY_SPAWN_TILES_X, MAX_ENEMY_SPAWN_TILES_X, MIN_ENEMY_SPAWN_TILES_Y, MAX_ENEMY_SPAWN_TILES_Y;
    ENEMY_SPAWN_TICK = 0;
    
    MIN_ENEMY_SPAWN_TILES_X = int((WINDOW_WIDTH // BLOCKSIZE) * 0.5);
    MAX_ENEMY_SPAWN_TILES_X = int(MIN_ENEMY_SPAWN_TILES_X * 2);
    MIN_ENEMY_SPAWN_TILES_Y = int((WINDOW_HEIGHT // BLOCKSIZE) * 0.5);
    MAX_ENEMY_SPAWN_TILES_Y = int(MIN_ENEMY_SPAWN_TILES_Y * 2);

    global PLAYER_DATA;
    PLAYER_DATA = [];

    global PLAYER_WIDTH, PLAYER_HEIGHT;
    PLAYER_WIDTH = 26;
    PLAYER_HEIGHT = 48;

    global PLAYER_MODEL_DATA, PLAYER_MODEL, PLAYER_FRAMES, PLAYER_MODEL_COLOUR_INDEX, TEXT_INPUT;
    PLAYER_MODEL_DATA = [];
    PLAYER_MODEL = None;
    PLAYER_FRAMES = [];
    PLAYER_MODEL_COLOUR_INDEX = 0;
    TEXT_INPUT = "";

    global IS_HOLDING_ITEM, ITEM_HOLDING;
    IS_HOLDING_ITEM = False;
    ITEM_HOLDING = None;

    global PLAYER_SAVE_OPTIONS;
    PLAYER_SAVE_OPTIONS = [];

    global OLD_TIME_MILLISECONDS, DELTA_TIME;
    OLD_TIME_MILLISECONDS = pygame.time.get_ticks();
    DELTA_TIME = 0;