# commons.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame


BLOCKSIZE = 16
TARGETFPS = 9999
MOUSE_POS = (0, 0)
TILE_POSITION_MOUSE_HOVERING = (0, 0)
SHIFT_ACTIVE = False

GAME_STATE = "MAINMENU"
GAME_SUB_STATE = "MAIN"
GAME_SUB_STATE_STACK = []

# Config loading
config = open("config.txt", "r")
configDataStr = config.readlines()
configData = []
for item in configDataStr:
    item = item.split("=")
    configData.append(item[1][:-1])
WINDOW_WIDTH = int(configData[0].split(",")[0])
WINDOW_HEIGHT = int(configData[0].split(",")[1])
GRAVITY = 9.8 * BLOCKSIZE * 0.666 * float(configData[1])  # 3 tiles = 1 metre
RUNFULLSCREEN = bool(int(configData[2]))
PARTICLES = bool(int(configData[3]))
PARTICLEDENSITY = float(configData[4])
MUSIC = bool(int(configData[5]))
CONFIG_MUSIC_VOLUME = float(configData[6])
SOUND = bool(int(configData[7]))
CONFIG_SOUND_VOLUME = float(configData[8])
CREATIVE = bool(int(configData[9]))
BACKGROUND = bool(int(configData[10]))
PARALLAXAMNT = float(configData[11])
PASSIVE = bool(int(configData[12]))
MAXENEMYSPAWNS = int(configData[13])
FANCYTEXT = bool(int(configData[14]))
HITBOXES = bool(int(configData[15]))
SPLASHSCREEN = bool(int(configData[16]))
AUTOSAVEFREQUENCY = float(configData[17])
EXPERIMENTALLIGHTING = bool(int(configData[18]))
SMOOTHCAM = bool(int(configData[19]))
DRAWUI = bool(int(configData[20]))

if RUNFULLSCREEN:
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

font_file_path = "res/fonts/VCR_OSD_MONO_1.001.ttf"
SMALLFONT = pygame.font.Font(font_file_path, 10)
DEFAULTFONT = pygame.font.Font(font_file_path, 16)
LARGEFONT = pygame.font.Font(font_file_path, 30)
XLARGEFONT = pygame.font.Font(font_file_path, 50)

WAIT_TO_USE = False

ENEMY_SPAWN_TICK = 0

MIN_ENEMY_SPAWN_TILES_X = int((WINDOW_WIDTH // BLOCKSIZE) * 0.5)
MAX_ENEMY_SPAWN_TILES_X = int(MIN_ENEMY_SPAWN_TILES_X * 2)
MIN_ENEMY_SPAWN_TILES_Y = int((WINDOW_HEIGHT // BLOCKSIZE) * 0.5)
MAX_ENEMY_SPAWN_TILES_Y = int(MIN_ENEMY_SPAWN_TILES_Y * 2)

PLAYER_DATA = []

PLAYER_WIDTH = 26
PLAYER_HEIGHT = 48
PLAYER_ARM_LENGTH = 20

PLAYER_MODEL_DATA = []
PLAYER_MODEL = None
PLAYER_FRAMES = []
PLAYER_REACH = 8
PLAYER_MODEL_COLOUR_INDEX = 0
TEXT_INPUT = ""

DEFAULT_PLAYER_MODEL = None

IS_HOLDING_ITEM = False
ITEM_HOLDING = None

PLAYER_SAVE_OPTIONS = []

OLD_TIME_MILLISECONDS = pygame.time.get_ticks()
DELTA_TIME = 0

CURRENT_SKY_LIGHTING = 255
CURRENT_TIME_STATE = None
