#menu_manager.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, random, os, sys, pickle, webbrowser, datetime;
from pygame.locals import *;

from player import Player;
import player;

import commons;
import tables;
import prompt;
import world;

import sound_manager;
import entity_manager;
import surface_manager;
import shared_methods;

def Initialize():
	global titleMessageText, titleMessageTextLeft;
	titleMessageText = None;
	titleMessageTextLeft = 0;

	global menuButtons;
	menuButtons = [];

	menuButtons.append(MenuButton("Fegaria Remastered", (commons.WINDOW_WIDTH * 0.5, 30), commons.XLARGEFONT, 25, False, (110, 147, 43), (50, 80, 7)));

	menuButtons.append(MenuButton("Back", (commons.WINDOW_WIDTH * 0.5, 570), commons.LARGEFONT, 25, True));

	menuButtons.append(MenuButton("Play", (commons.WINDOW_WIDTH * 0.5, 450), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Settings", (commons.WINDOW_WIDTH * 0.5, 480), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Changes", (commons.WINDOW_WIDTH * 0.5, 510), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Credits", (commons.WINDOW_WIDTH * 0.5, 540), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Quit", (commons.WINDOW_WIDTH * 0.5, 570), commons.LARGEFONT, 25, True));

	menuButtons.append(MenuButton("Settings", (commons.WINDOW_WIDTH * 0.5, 120), commons.XLARGEFONT, 25, False));
	menuButtons.append(MenuButton("Coming soon", (commons.WINDOW_WIDTH * 0.5, 300), commons.LARGEFONT, 25, False));

	menuButtons.append(MenuButton("Credits", (commons.WINDOW_WIDTH * 0.5, 120), commons.XLARGEFONT, 25, False));
	menuButtons.append(MenuButton("Design: Fergus Griggs", (commons.WINDOW_WIDTH * 0.5, 270), commons.LARGEFONT, 25, False));
	menuButtons.append(MenuButton("Programming: Fergus Griggs", (commons.WINDOW_WIDTH * 0.5, 310), commons.LARGEFONT, 25, False));
	menuButtons.append(MenuButton("Anything but audio: Fergus Griggs", (commons.WINDOW_WIDTH * 0.5, 350), commons.LARGEFONT, 25, False));
	menuButtons.append(MenuButton("Music and sounds: Re-Logic", (commons.WINDOW_WIDTH * 0.5, 390), commons.LARGEFONT, 25, False));

	menuButtons.append(MenuButton("Select Player", (commons.WINDOW_WIDTH * 0.5, 90), commons.LARGEFONT, 24, False));
	menuButtons.append(MenuButton("New Player", (commons.WINDOW_WIDTH * 0.5, 530), commons.LARGEFONT, 24, True));

	menuButtons.append(MenuButton("Hair Type", (commons.WINDOW_WIDTH * 0.5, 200), commons.LARGEFONT, 26, True));
	menuButtons.append(MenuButton("Hair Colour", (commons.WINDOW_WIDTH * 0.5, 240), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Eye Colour", (commons.WINDOW_WIDTH * 0.5, 280), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Skin Colour", (commons.WINDOW_WIDTH * 0.5, 320), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Clothes", (commons.WINDOW_WIDTH * 0.5, 360), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Create", (commons.WINDOW_WIDTH * 0.5, 450), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Randomize", (commons.WINDOW_WIDTH * 0.5, 490), commons.LARGEFONT, 26, True));

	menuButtons.append(MenuButton("Shirt Colour", (commons.WINDOW_WIDTH * 0.5, 240), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Undershirt Colour", (commons.WINDOW_WIDTH * 0.5, 280), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Trouser Colour", (commons.WINDOW_WIDTH * 0.5, 320), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Shoe Colour", (commons.WINDOW_WIDTH * 0.5, 360), commons.LARGEFONT, 24, True));

	menuButtons.append(MenuButton("Set Player Name", (commons.WINDOW_WIDTH * 0.5, 450), commons.LARGEFONT, 24, True));

	menuButtons.append(MenuButton("Select World", (commons.WINDOW_WIDTH * 0.5, 90), commons.LARGEFONT, 24, False));
	menuButtons.append(MenuButton("New World", (commons.WINDOW_WIDTH * 0.5, 530), commons.LARGEFONT, 24, True));
	
	menuButtons.append(MenuButton("World Size", (commons.WINDOW_WIDTH * 0.5, 120), commons.XLARGEFONT, 24, False));

	menuButtons.append(MenuButton("Tiny (100x350)", (commons.WINDOW_WIDTH * 0.5, 240), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Small (200x550)", (commons.WINDOW_WIDTH * 0.5, 280), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Medium (400x700)", (commons.WINDOW_WIDTH * 0.5, 320), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("Large (700x1000)", (commons.WINDOW_WIDTH * 0.5, 360), commons.LARGEFONT, 24, True, (200, 0, 0), (100, 0, 0)));

	menuButtons.append(MenuButton("Set World Name", (commons.WINDOW_WIDTH * 0.5, 450), commons.LARGEFONT, 24, True));

	menuButtons.append(MenuButton("Changes", (commons.WINDOW_WIDTH * 0.5, 120), commons.XLARGEFONT, 25, False));

	menuButtons.append(MenuButton("PyGame Page", (commons.WINDOW_WIDTH * 0.5, 280), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("GitHub Page", (commons.WINDOW_WIDTH * 0.5, 320), commons.LARGEFONT, 24, True));
	menuButtons.append(MenuButton("YouTube Page", (commons.WINDOW_WIDTH * 0.5, 360), commons.LARGEFONT, 24, True));

	UpdateActiveMenuButtons();

def UpdateActiveMenuButtons():
	for menuButton in menuButtons:
		menuButton.active = False;

	for i in range(len(tables.activeMenuButtons)):
		if commons.GAME_SUB_STATE == tables.activeMenuButtons[i][0]:
			for j in range(len(tables.activeMenuButtons[i]) - 1): 
				menuButtons[tables.activeMenuButtons[i][j + 1]].active = True;
			break;

	if commons.GAME_SUB_STATE == "MAIN":
		NewTitleMessage();

def UpdateMenuButtons():
	for menuButton in menuButtons:
		if menuButton.active:
			menuButton.Update();

			if menuButton.clicked:
				menuButton.clicked = False;

				tempGameSubState = commons.GAME_SUB_STATE;

				if menuButton.text == "Play":
					commons.GAME_SUB_STATE = "PLAYERSELECTION";
					LoadMenuPlayerData();

				elif menuButton.text == "Settings":
					commons.GAME_SUB_STATE = "SETTINGS";

				elif menuButton.text == "Changes":
					commons.GAME_SUB_STATE = "CHANGES";
					
				elif menuButton.text == "PyGame Page":
					entity_manager.clientPrompt = prompt.Prompt("browser opened", "PyGame page opened in a new tab.", size = (5, 2));
					webbrowser.open("https://www.pygame.org/project/3451");

				elif menuButton.text == "GitHub Page":
					entity_manager.clientPrompt = prompt.Prompt("browser opened", "GitHub page opened in a new tab.", size = (5, 2));
					webbrowser.open("https://github.com/FergusGriggs/Fegaria-Remastered");

				elif menuButton.text == "YouTube Page":
					entity_manager.clientPrompt = prompt.Prompt("browser opened", "YouTube page opened in a new tab.", size = (5, 2));
					webbrowser.open("https://www.youtube.com/channel/UC_7e1qyqA39URIlV89MByug");

				elif menuButton.text == "Credits":
					commons.GAME_SUB_STATE = "CREDITS";

				elif menuButton.text == "Quit":
					pygame.quit();
					sys.exit();

				elif menuButton.text == "Back":
					commons.GAME_SUB_STATE = commons.GAME_SUB_STATE_STACK.pop();

				elif menuButton.text == "New Player":
					commons.GAME_SUB_STATE = "PLAYERCREATION";
					commons.PLAYER_MODEL_DATA = [0,  0,  [(127,  72,  36),  None, None], [(62, 22, 0), None, None], [(0, 0, 0), None, None], [(95, 125, 127), None, None], [(48, 76, 127), None, None], [(129, 113, 45), None, None], [(80,  100,  45), None, None]];
					commons.PLAYER_MODEL = player.Model(commons.PLAYER_MODEL_DATA[0], commons.PLAYER_MODEL_DATA[1], commons.PLAYER_MODEL_DATA[2][0], commons.PLAYER_MODEL_DATA[3][0], commons.PLAYER_MODEL_DATA[4][0], commons.PLAYER_MODEL_DATA[5][0], commons.PLAYER_MODEL_DATA[6][0], commons.PLAYER_MODEL_DATA[7][0], commons.PLAYER_MODEL_DATA[8][0]);
					commons.PLAYER_FRAMES = Player.RenderSprites(commons.PLAYER_MODEL,  directions = 1,  armFrameCount = 1,  torsoFrameCount = 1);

				elif menuButton.text == "Hair Type":
					if commons.PLAYER_MODEL.hairID < 8:
						commons.PLAYER_MODEL.hairID += 1;
					else:
						commons.PLAYER_MODEL.hairID = 0;
					commons.PLAYER_MODEL_DATA[1] = commons.PLAYER_MODEL.hairID;
					commons.PLAYER_FRAMES = Player.RenderSprites(commons.PLAYER_MODEL, directions = 1, armFrameCount = 1, torsoFrameCount = 1);

				elif menuButton.text == "Hair Colour":
					commons.GAME_SUB_STATE = "COLOURPICKER";
					commons.PLAYER_MODEL_COLOUR_INDEX = 3;

				elif menuButton.text == "Eye Colour":
					commons.GAME_SUB_STATE = "COLOURPICKER";
					commons.PLAYER_MODEL_COLOUR_INDEX = 4;

				elif menuButton.text == "Skin Colour":
					commons.GAME_SUB_STATE = "COLOURPICKER";
					commons.PLAYER_MODEL_COLOUR_INDEX = 2;

				elif menuButton.text == "Clothes":
					 commons.GAME_SUB_STATE = "CLOTHES";

				elif menuButton.text == "Shirt Colour":
					commons.GAME_SUB_STATE = "COLOURPICKER";
					commons.PLAYER_MODEL_COLOUR_INDEX = 5;

				elif menuButton.text == "Undershirt Colour":
					commons.GAME_SUB_STATE = "COLOURPICKER";
					commons.PLAYER_MODEL_COLOUR_INDEX = 6;

				elif menuButton.text == "Trouser Colour":
					commons.GAME_SUB_STATE = "COLOURPICKER";
					commons.PLAYER_MODEL_COLOUR_INDEX = 7;

				elif menuButton.text == "Shoe Colour":
					commons.GAME_SUB_STATE = "COLOURPICKER";
					commons.PLAYER_MODEL_COLOUR_INDEX = 8;

				elif menuButton.text == "Randomize":
					commons.PLAYER_MODEL_DATA = [0, random.randint(0, 8),
                                     [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                     [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                     [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                     [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                     [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                     [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                     [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                     [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None]];
					player.UpdatePlayerModelUsingModelData();
					commons.PLAYER_FRAMES = Player.RenderSprites(commons.PLAYER_MODEL, directions = 1, armFrameCount = 1, torsoFrameCount = 1);
				
				elif menuButton.text == "Create":
					commons.GAME_SUB_STATE = "PLAYERNAMING";
					commons.TEXT_INPUT = "";

				elif menuButton.text == "Set Player Name":
					date = datetime.datetime.now();
					creationDate = str(str(date)[:19]);
					commons.PLAYER_DATA = [commons.TEXT_INPUT, commons.PLAYER_MODEL, None, None, 100, 100, 0, creationDate]; #create player array
					pickle.dump(commons.PLAYER_DATA, open("res/players/" + commons.TEXT_INPUT + ".player", "wb")); #save player array
					commons.GAME_SUB_STATE = "PLAYERSELECTION";
					LoadMenuPlayerData();

				elif menuButton.text == "New World":
					commons.GAME_SUB_STATE = "WORLDCREATION";

				elif menuButton.text == "Tiny (100x350)":
					commons.GAME_SUB_STATE = "WORLDNAMING";
					commons.TEXT_INPUT = "";
					world.WORLD_SIZE_X = 100;
					world.WORLD_SIZE_Y = 350;

				elif menuButton.text == "Small (200x550)":
					commons.GAME_SUB_STATE = "WORLDNAMING";
					commons.TEXT_INPUT = "";
					world.WORLD_SIZE_X = 200;
					world.WORLD_SIZE_Y = 550;

				elif menuButton.text == "Medium (400x700)":
					commons.GAME_SUB_STATE = "WORLDNAMING";
					commons.TEXT_INPUT = "";
					world.WORLD_SIZE_X = 400;
					world.WORLD_SIZE_Y = 700;

				elif menuButton.text == "Large (700x1000)":
					commons.GAME_SUB_STATE = "WORLDNAMING";
					commons.TEXT_INPUT = "";
					world.WORLD_SIZE_X = 700;
					world.WORLD_SIZE_Y = 1000;

				elif menuButton.text == "Set World Name":
					world.WORLD_NAME = commons.TEXT_INPUT;
					world.GenerateTerrain("DEFAULT", blitProgress = True);
					pickle.dump(world.mapData, open("res/worlds/" + str(world.clientWorld.name) + ".wrld", "wb")); #save wrld
					pickle.dump(world.clientWorld, open("res/worlds/" + str(world.clientWorld.name) + ".dat", "wb")); #save dat
					commons.GAME_SUB_STATE = "WORLDSELECTION";
					LoadMenuWorldData();

				if commons.GAME_SUB_STATE == "COLOURPICKER":
					if commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][1] != None:
						entity_manager.clientColourPicker.selectedColour = tuple(commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][0]);
					entity_manager.clientColourPicker.selectedX = commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][1];
					entity_manager.clientColourPicker.selectedY = commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][2];

				# Update last game sub state variable is the sub state changed
				if tempGameSubState != commons.GAME_SUB_STATE:
					if menuButton.text != "Back":
						commons.GAME_SUB_STATE_STACK.append(tempGameSubState); 

					if menuButton.text == "Set Player Name":
						commons.GAME_SUB_STATE_STACK = commons.GAME_SUB_STATE_STACK[:1];

					if menuButton.text == "Set World Name":
						commons.GAME_SUB_STATE_STACK = commons.GAME_SUB_STATE_STACK[:2];

				UpdateActiveMenuButtons();
					

def DrawMenuButtons():
	for menuButton in menuButtons:
		if menuButton.active:
			menuButton.Draw();


def LoadMenuPlayerData():
    path = "res/players";
    if not os.path.exists(path):
        os.makedirs(path);
    possibleLoads = os.listdir(path); #get filenames
    commons.PLAYER_SAVE_OPTIONS = [];

    for i in range(len(possibleLoads)):
        dat = pickle.load(open("res/players/" + possibleLoads[i], "rb"));
        possibleLoads[i] = possibleLoads[i][:-7];
        playerDataSurf = pygame.Surface((315, 60));
        playerDataSurf.fill((50, 50, 50));
        pygame.draw.rect(playerDataSurf, (60, 60, 60), Rect(0, 0, 315, 60), 4);
        playerDataSurf.blit(shared_methods.OutlineText(dat[0], (255, 255, 255), commons.DEFAULTFONT),(5, 3)); #name
        playerDataSurf.blit(shared_methods.OutlineText("Created: ", (255, 255, 255), commons.DEFAULTFONT), (5, 20)); #creation date
        playerDataSurf.blit(shared_methods.OutlineText("Playtime: ", (255, 255, 255), commons.DEFAULTFONT), (5, 40)); #playtime
        playerDataSurf.blit(shared_methods.OutlineText(dat[7], (230, 230, 0), commons.DEFAULTFONT), (80, 20)); #creation date
        playerDataSurf.blit(shared_methods.OutlineText(str(dat[5]) + " HP", (230, 10, 10), commons.DEFAULTFONT, outlineColour = (128, 5, 5)), (120, 3)); #hp
        playerDataSurf.blit(shared_methods.OutlineText(str(int((dat[6] / 60) // 60)) + ":" + str(int(dat[6] // 60 % 60)).zfill(2) + ":" + str(int(dat[6] % 60)).zfill(2), (230, 230, 0), commons.DEFAULTFONT), (90, 40)); #playtime
        sprites = Player.RenderSprites(dat[1], directions = 1, armFrameCount = 1, torsoFrameCount = 1);
        playerDataSurf.blit(sprites[0][0], (270, 0));
        playerDataSurf.blit(sprites[1][0], (270, 0));
        commons.PLAYER_SAVE_OPTIONS.append([dat, playerDataSurf]);

def LoadMenuWorldData():
    path = "res/worlds";
    if not os.path.exists(path):
        os.makedirs(path);
    possibleLoads = os.listdir(path); #get filenames
    commons.WORLD_SAVE_OPTIONS = [];
    for i in range(len(possibleLoads)):
        if possibleLoads[i][-3:] == "dat": #if it's a dat file
            dat=pickle.load(open("res/worlds/" + possibleLoads[i], "rb"));

            worldDataSurf=pygame.Surface((315, 60));
            worldDataSurf.fill((50, 50, 50));
            pygame.draw.rect(worldDataSurf, (60, 60, 60), Rect(0, 0, 315, 60), 4);
            
            worldDataSurf.blit(shared_methods.OutlineText(dat.name, (255, 255, 255), commons.DEFAULTFONT), (5, 3)); #name
            worldDataSurf.blit(shared_methods.OutlineText("Created: ", (255, 255, 255), commons.DEFAULTFONT), (5, 20)); #creation date
            worldDataSurf.blit(shared_methods.OutlineText("Playtime: ", (255, 255, 255), commons.DEFAULTFONT), (5, 40)); #playtime
            worldDataSurf.blit(shared_methods.OutlineText(dat.creationDate, (230, 230, 0), commons.DEFAULTFONT), (80, 20)); #creation date
            worldDataSurf.blit(shared_methods.OutlineText(str(int((dat.playTime / 60) // 60)) + ":" + str(int(dat.playTime // 60 % 60)).zfill(2) + ":" + str(int(dat.playTime % 60)).zfill(2), (230, 230, 0), commons.DEFAULTFONT), (90, 40)); #playtime

            worldDataSurf.blit(surface_manager.miscGUI[10], (260, 7));
            
            commons.WORLD_SAVE_OPTIONS.append([dat.name, worldDataSurf]);

def NewTitleMessage():
	global titleMessageText, titleMessageTextLeft;
	titleMessageText = shared_methods.OutlineText(tables.titleMessages[random.randint(0, len(tables.titleMessages) - 1)], (255, 255, 255), commons.DEFAULTFONT);
	titleMessageTextLeft = commons.WINDOW_WIDTH * 0.5 - titleMessageText.get_width() * 0.5;

class MenuButton():
	def __init__(self, text, position, font, clickSoundID, isButton, colour = (255, 255, 255), outlineColour = (0, 0, 0)):
		self.text = text;
		self.position = position; #(position[0] + 100, position[1]);

		self.isButton = isButton;

		self.colour = colour;

		self.textSurface = shared_methods.OutlineText(text, self.colour, font, outlineColour);

		if self.isButton:
			self.altTextSurface = shared_methods.OutlineText(text, (230, 230, 15), font);

		self.rect = Rect(self.position[0] - self.textSurface.get_width() * 0.5, self.position[1] - self.textSurface.get_height() * 0.5, self.textSurface.get_width(), self.textSurface.get_height());

		self.hovered = False;
		self.clicked = False;

		self.clickSoundID = clickSoundID;

		self.active = False;

	def Update(self):
		if self.isButton:
			if self.rect.collidepoint(commons.MOUSE_POS):
				if not self.hovered:
					if commons.SOUND:
						sound_manager.sounds[26].play();
					self.hovered = True;
				if pygame.mouse.get_pressed()[0] and commons.WAIT_TO_USE == False:
					commons.WAIT_TO_USE = True;
					self.clicked = True;
					if commons.SOUND:
						sound_manager.sounds[self.clickSoundID].play();
			else:
				self.hovered = False;
				self.clicked = False;

	def Draw(self):
		if not self.hovered:
			if self.text == "Fegaria Remastered":
				commons.screen.blit(self.textSurface, (self.rect.left, self.rect.top + 3));
			commons.screen.blit(self.textSurface, (self.rect.left, self.rect.top));
		else:
			commons.screen.blit(self.altTextSurface, (self.rect.left, self.rect.top));