#prompt.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame;
from pygame.locals import *;

import commons;
import world;
import shared_methods;

import sound_manager;
import surface_manager;
import entity_manager;
import menu_manager;

class Prompt():
    def __init__(self, name, body, button1Name = None, shop = False, shopItems = None, size = (10, 3), NPC = True, pos = None):
        self.name = name;
        self.body = body;
        
        self.shop = shop;
        self.shopHover = False;
        self.shopItems = shopItems;
        
        self.button1Name = button1Name;
        self.button1Pressed = False;
        self.button1Hover = False;

        self.closeHover = False;
        self.close = False;
        
        self.bodySurf = shared_methods.CreateMenuSurface(size[0], size[1], body);
        
        self.width = self.bodySurf.get_width();
        self.height = self.bodySurf.get_height();

        if pos == None:
            self.left = commons.WINDOW_WIDTH * 0.5 - self.width * 0.5;
            self.top = commons.WINDOW_HEIGHT * 2 / 7 - self.height * 0.5;
            self.bot = self.top + self.height - 30;
        else:
            self.left = pos[0];
            self.top = pos[1];
            self.bot = pos[1] + self.height - 30;

        if commons.SOUND:
            if NPC:
                sound_manager.sounds[27].play();
            else:
                sound_manager.sounds[24].play();
        
    def Update(self):
        offsetx = 10;

        if self.shop:
            if Rect(self.left + offsetx, self.bot, 60, 20).collidepoint(commons.MOUSE_POS):
                if not self.shopHover:
                    self.shopHover = True;
                    if commons.SOUND:
                        sound_manager.sounds[26].play();
            else:
                self.shopHover = False;
            offsetx += 60;

        if self.button1Name != None:
            if Rect(self.left + offsetx, self.bot, 60, 20).collidepoint(commons.MOUSE_POS):
                if not self.button1Hover:
                    self.button1Hover = True;
                    if commons.SOUND:
                        sound_manager.sounds[26].play();
                if pygame.mouse.get_pressed()[0]:
                    self.button1Pressed = True;
            else:
                self.button1Hover = False;
            offsetx += commons.DEFAULTFONT.size(self.button1Name)[0] + 20;

        if Rect(self.left+offsetx, self.bot, 60, 20).collidepoint(commons.MOUSE_POS):
            if not self.closeHover:
                self.closeHover = True;
                if commons.SOUND:
                    sound_manager.sounds[26].play();
            if pygame.mouse.get_pressed()[0]:
                if commons.SOUND:
                    sound_manager.sounds[25].play();
                self.close = True;
        else:
            self.closeHover = False;
            
        if pygame.mouse.get_pressed()[0] and not commons.WAIT_TO_USE:
            if not Rect(self.left, self.top, self.width, self.height).collidepoint(commons.MOUSE_POS):
                if commons.SOUND:
                    sound_manager.sounds[25].play();
                self.close = True;
                
        if self.name == "Exit":
            if self.button1Pressed:
                entity_manager.clientPlayer.SavePlayer();
                world.SaveWorld();
                commons.GAME_STATE = "MAINMENU";
                commons.GAME_SUB_STATE = "MAIN";
                world.terrainSurface = pygame.Surface((1, 1));
                menu_manager.UpdateActiveMenuButtons();
                self.close = True;

    def Draw(self):
        commons.screen.blit(self.bodySurf, (self.left, self.top));
        offsetx = 20;
        if self.shop:
            shopCol = (230, 230, 10);
            if self.shopHover:
                shopCol = (255, 255, 255);
            commons.screen.blit(shared_methods.OutlineText("Shop", shopCol, commons.DEFAULTFONT), (self.left+offsetx, self.bot));
            offsetx += 60;
        if self.button1Name != None:
            button1Col = (230, 230, 10);
            if self.button1Hover:
                button1Col = (255, 255, 255);
            commons.screen.blit(shared_methods.OutlineText(self.button1Name, button1Col, commons.DEFAULTFONT), (self.left + offsetx, self.bot));
            offsetx += commons.DEFAULTFONT.size(self.button1Name)[0] + 20;
        closeCol = (230, 230, 10);
        if self.closeHover:
            closeCol = (255, 255, 255);
        commons.screen.blit(shared_methods.OutlineText("Close", closeCol, commons.DEFAULTFONT), (self.left + offsetx, self.bot));