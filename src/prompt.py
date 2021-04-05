# prompt.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame
from pygame.locals import *

import commons
import world
import shared_methods
import game_data

import entity_manager
import menu_manager


"""================================================================================================================= 
    prompt.Prompt

    Stores information necessary to update and draw a Prompt instance
-----------------------------------------------------------------------------------------------------------------"""
class Prompt:
    def __init__(self, name, body, button_1_name=None, shop=False, shop_items=None, size=(10, 3), npc=True, pos=None):
        self.name = name
        self.body = body
        
        self.shop = shop
        self.shop_hover = False
        self.shop_items = shop_items
        
        self.button_1_name = button_1_name
        self.button_1_pressed = False
        self.button_1_hover = False

        self.close_hover = False
        self.close = False
        
        self.body_surf = shared_methods.create_menu_surface(size[0], size[1], body)
        
        self.width = self.body_surf.get_width()
        self.height = self.body_surf.get_height()

        if pos is None:
            self.left = commons.WINDOW_WIDTH * 0.5 - self.width * 0.5
            self.top = commons.WINDOW_HEIGHT * 2 / 7 - self.height * 0.5
            self.bot = self.top + self.height - 30
        else:
            self.left = pos[0]
            self.top = pos[1]
            self.bot = pos[1] + self.height - 30

        if npc:
            game_data.play_sound("fg.sound.chat")
        else:
            game_data.play_sound("fg.sound.menu_open")

    """================================================================================================================= 
        prompt.Prompt.update -> void

        Handles interactions with all possible prompt buttons
    -----------------------------------------------------------------------------------------------------------------"""
    def update(self):
        offset_x = 10

        if self.shop:
            if Rect(self.left + offset_x, self.bot, 60, 20).collidepoint(commons.MOUSE_POS):
                if not self.shop_hover:
                    self.shop_hover = True
                    game_data.play_sound("fg.sound.menu_select")
            else:
                self.shop_hover = False
            offset_x += 60

        if self.button_1_name is not None:
            if Rect(self.left + offset_x, self.bot, 60, 20).collidepoint(commons.MOUSE_POS):
                if not self.button_1_hover:
                    self.button_1_hover = True
                    game_data.play_sound("fg.sound.menu_select")
                if pygame.mouse.get_pressed()[0]:
                    self.button_1_pressed = True
            else:
                self.button_1_hover = False
            offset_x += commons.DEFAULTFONT.size(self.button_1_name)[0] + 20

        if Rect(self.left + offset_x, self.bot, 60, 20).collidepoint(commons.MOUSE_POS):
            if not self.close_hover:
                self.close_hover = True
                game_data.play_sound("fg.sound.menu_select")
            if pygame.mouse.get_pressed()[0]:
                game_data.play_sound("fg.sound.menu_close")
                self.close = True
        else:
            self.close_hover = False
            
        if pygame.mouse.get_pressed()[0] and not commons.WAIT_TO_USE:
            if not Rect(self.left, self.top, self.width, self.height).collidepoint(commons.MOUSE_POS):
                game_data.play_sound("fg.sound.menu_close")
                self.close = True
                
        if self.name == "Exit":
            if self.button_1_pressed:
                entity_manager.client_player.save()
                world.save()
                commons.GAME_STATE = "MAINMENU"
                commons.GAME_SUB_STATE = "MAIN"
                world.terrain_surface = pygame.Surface((1, 1))
                menu_manager.update_active_menu_buttons()
                entity_manager.kill_all_entities()
                self.close = True

    """================================================================================================================= 
        prompt.Prompt.draw -> void

        Draws all the active prompt buttons and the prompt text
    -----------------------------------------------------------------------------------------------------------------"""
    def draw(self):
        commons.screen.blit(self.body_surf, (self.left, self.top))
        offset_x = 20

        if self.shop:
            shop_col = (230, 230, 10)
            if self.shop_hover:
                shop_col = (255, 255, 255)
            commons.screen.blit(shared_methods.outline_text("Shop", shop_col, commons.DEFAULTFONT), (self.left + offset_x, self.bot))
            offset_x += 60

        if self.button_1_name is not None:
            button_1_col = (230, 230, 10)
            if self.button_1_hover:
                button_1_col = (255, 255, 255)
            commons.screen.blit(shared_methods.outline_text(self.button_1_name, button_1_col, commons.DEFAULTFONT), (self.left + offset_x, self.bot))
            offset_x += commons.DEFAULTFONT.size(self.button_1_name)[0] + 20
        close_col = (230, 230, 10)

        if self.close_hover:
            close_col = (255, 255, 255)

        commons.screen.blit(shared_methods.outline_text("Close", close_col, commons.DEFAULTFONT), (self.left + offset_x, self.bot))