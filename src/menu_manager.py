# menu_manager.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame
import random
import os
import sys
import pickle
import webbrowser
import datetime
from pygame.locals import *

from player import Player
import player

import commons
import game_data
import prompt
import world

import entity_manager
import surface_manager
import shared_methods

title_message_text = None
title_message_text_left = 0

menu_buttons = []


"""================================================================================================================= 
    menu_manager.MenuButton

    Stores information about a single button, the visibility of a given button is set by the active_menu_buttons
    table
-----------------------------------------------------------------------------------------------------------------"""
class MenuButton:
    def __init__(self, text, position, font, click_sound_id, is_button, colour=(255, 255, 255), outline_colour=(0, 0, 0)):
        self.text = text
        self.position = position

        self.is_button = is_button

        self.colour = colour

        self.text_surface = shared_methods.outline_text(text, self.colour, font, outline_colour)

        if self.is_button:
            self.alt_text_surface = shared_methods.outline_text(text, (230, 230, 15), font)

        self.rect = Rect(self.position[0] - self.text_surface.get_width() * 0.5, self.position[1] - self.text_surface.get_height() * 0.5, self.text_surface.get_width(), self.text_surface.get_height())

        self.hovered = False
        self.clicked = False

        self.click_sound_id = click_sound_id

        self.active = False

    """================================================================================================================= 
        menu_manager.MenuButton.update -> void

        Checks to see if the mouse is interacting with the button instance, performing all the related logic
    -----------------------------------------------------------------------------------------------------------------"""
    def update(self):
        if self.is_button:
            if self.rect.collidepoint(commons.MOUSE_POS):
                if not self.hovered:
                    game_data.play_sound("fg.sound.menu_select")
                    self.hovered = True
                if pygame.mouse.get_pressed()[0] and not commons.WAIT_TO_USE:
                    commons.WAIT_TO_USE = True
                    self.clicked = True
                    if self.text == "Back":
                        game_data.play_sound("fg.sound.menu_close")
                    else:
                        game_data.play_sound("fg.sound.menu_open")
            else:
                self.hovered = False
                self.clicked = False

    """================================================================================================================= 
        menu_manager.MenuButton.draw -> void

        Draws the button's text surface or alt_text_surface depending on the hover state of the button
    -----------------------------------------------------------------------------------------------------------------"""
    def draw(self):
        if not self.hovered:
            if self.text == "Fegaria Remastered":
                commons.screen.blit(self.text_surface, (self.rect.left, self.rect.top + 3))
            commons.screen.blit(self.text_surface, (self.rect.left, self.rect.top))
        else:
            commons.screen.blit(self.alt_text_surface, (self.rect.left, self.rect.top))


"""================================================================================================================= 
    menu_manager.new_title_message -> void
    
    Randomizes the message displayed on the main menu
-----------------------------------------------------------------------------------------------------------------"""
def new_title_message():
    global title_message_text, title_message_text_left
    title_message_text = shared_methods.outline_text(game_data.title_messages[random.randint(0, len(game_data.title_messages) - 1)], (255, 255, 255), commons.DEFAULTFONT)
    title_message_text_left = commons.WINDOW_WIDTH * 0.5 - title_message_text.get_width() * 0.5


"""================================================================================================================= 
    menu_manager.update_active_menu_buttons -> void

    Sets the active state of all buttons to false and then re-adds buttons based on the current game sub state 
    and data in the 'active_menu_buttons' table
-----------------------------------------------------------------------------------------------------------------"""
def update_active_menu_buttons():
    for menuButton in menu_buttons:
        menuButton.active = False

    for i in range(len(game_data.active_menu_buttons)):
        if commons.GAME_SUB_STATE == game_data.active_menu_buttons[i][0]:
            for j in range(len(game_data.active_menu_buttons[i]) - 1):
                menu_buttons[game_data.active_menu_buttons[i][j + 1]].active = True
            break

    if commons.GAME_SUB_STATE == "MAIN":
        new_title_message()


"""================================================================================================================= 
    menu_manager.update_menu_buttons -> void

    Calls update on all active button instances, handles unique button press logic
-----------------------------------------------------------------------------------------------------------------"""
def update_menu_buttons():
    for menu_button in menu_buttons:
        if menu_button.active:
            menu_button.update()

            if menu_button.clicked:
                menu_button.clicked = False

                temp_game_sub_state = commons.GAME_SUB_STATE

                if menu_button.text == "Play":
                    commons.GAME_SUB_STATE = "PLAYERSELECTION"
                    load_menu_player_data()

                elif menu_button.text == "Settings":
                    commons.GAME_SUB_STATE = "SETTINGS"

                elif menu_button.text == "Changes":
                    commons.GAME_SUB_STATE = "CHANGES"

                elif menu_button.text == "PyGame Page":
                    entity_manager.client_prompt = prompt.Prompt("browser opened", "PyGame page opened in a new tab.", size=(5, 2))
                    webbrowser.open("https://www.pygame.org/project/3451")

                elif menu_button.text == "GitHub Repo":
                    entity_manager.client_prompt = prompt.Prompt("browser opened", "GitHub page opened in a new tab.", size=(5, 2))
                    webbrowser.open("https://github.com/FergusGriggs/Fegaria-Remastered")

                elif menu_button.text == "YouTube Channel":
                    entity_manager.client_prompt = prompt.Prompt("browser opened", "YouTube page opened in a new tab.", size=(5, 2))
                    webbrowser.open("https://www.youtube.com/channel/UC_7e1qyqA39URIlV89MByug")

                elif menu_button.text == "Trello Board":
                    entity_manager.client_prompt = prompt.Prompt("browser opened", "Trello board opened in a new tab.", size=(5, 2))
                    webbrowser.open("https://trello.com/b/FS1rej7y/fegaria-remastered")

                elif menu_button.text == "Credits":
                    commons.GAME_SUB_STATE = "CREDITS"

                elif menu_button.text == "Quit":
                    pygame.quit()
                    sys.exit()

                elif menu_button.text == "Back":
                    commons.GAME_SUB_STATE = commons.GAME_SUB_STATE_STACK.pop()

                elif menu_button.text == "New Player":
                    commons.GAME_SUB_STATE = "PLAYERCREATION"
                    commons.PLAYER_MODEL_DATA = [0, 0, [(127, 72, 36), None, None],
                                                 [(62, 22, 0), None, None],
                                                 [(0, 0, 0), None, None],
                                                 [(95, 125, 127), None, None],
                                                 [(48, 76, 127), None, None],
                                                 [(129, 113, 45), None, None],
                                                 [(80, 100, 45), None, None]]
                    commons.PLAYER_MODEL = player.Model(commons.PLAYER_MODEL_DATA[0], commons.PLAYER_MODEL_DATA[1],
                                                        commons.PLAYER_MODEL_DATA[2][0],
                                                        commons.PLAYER_MODEL_DATA[3][0],
                                                        commons.PLAYER_MODEL_DATA[4][0],
                                                        commons.PLAYER_MODEL_DATA[5][0],
                                                        commons.PLAYER_MODEL_DATA[6][0],
                                                        commons.PLAYER_MODEL_DATA[7][0],
                                                        commons.PLAYER_MODEL_DATA[8][0])
                    commons.PLAYER_FRAMES = player.render_sprites(commons.PLAYER_MODEL, directions=1, arm_frame_count=1, torso_frame_count=1)

                elif menu_button.text == "Hair Type":
                    if commons.PLAYER_MODEL.hair_id < 8:
                        commons.PLAYER_MODEL.hair_id += 1
                    else:
                        commons.PLAYER_MODEL.hair_id = 0
                    commons.PLAYER_MODEL_DATA[1] = commons.PLAYER_MODEL.hair_id
                    commons.PLAYER_FRAMES = player.render_sprites(commons.PLAYER_MODEL, directions=1, arm_frame_count=1, torso_frame_count=1)

                elif menu_button.text == "Hair Colour":
                    commons.GAME_SUB_STATE = "COLOURPICKER"
                    commons.PLAYER_MODEL_COLOUR_INDEX = 3

                elif menu_button.text == "Eye Colour":
                    commons.GAME_SUB_STATE = "COLOURPICKER"
                    commons.PLAYER_MODEL_COLOUR_INDEX = 4

                elif menu_button.text == "Skin Colour":
                    commons.GAME_SUB_STATE = "COLOURPICKER"
                    commons.PLAYER_MODEL_COLOUR_INDEX = 2

                elif menu_button.text == "Clothes":
                    commons.GAME_SUB_STATE = "CLOTHES"

                elif menu_button.text == "Shirt Colour":
                    commons.GAME_SUB_STATE = "COLOURPICKER"
                    commons.PLAYER_MODEL_COLOUR_INDEX = 5

                elif menu_button.text == "Undershirt Colour":
                    commons.GAME_SUB_STATE = "COLOURPICKER"
                    commons.PLAYER_MODEL_COLOUR_INDEX = 6

                elif menu_button.text == "Trouser Colour":
                    commons.GAME_SUB_STATE = "COLOURPICKER"
                    commons.PLAYER_MODEL_COLOUR_INDEX = 7

                elif menu_button.text == "Shoe Colour":
                    commons.GAME_SUB_STATE = "COLOURPICKER"
                    commons.PLAYER_MODEL_COLOUR_INDEX = 8

                elif menu_button.text == "Randomize":
                    commons.PLAYER_MODEL_DATA = [0, random.randint(0, 8),
                                                 [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                                 [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                                 [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                                 [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                                 [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                                 [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                                 [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None],
                                                 [(random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)), None, None]]
                    player.update_player_model_using_model_data()
                    commons.PLAYER_FRAMES = player.render_sprites(commons.PLAYER_MODEL, directions=1, arm_frame_count=1, torso_frame_count=1)

                elif menu_button.text == "Create":
                    commons.GAME_SUB_STATE = "PLAYERNAMING"
                    commons.TEXT_INPUT = ""

                elif menu_button.text == "Set Player Name":
                    date = datetime.datetime.now()
                    commons.PLAYER_DATA = [commons.TEXT_INPUT, commons.PLAYER_MODEL, None, None, 100, 100, 0, date, date]  # Create player array
                    pickle.dump(commons.PLAYER_DATA, open("res/players/" + commons.TEXT_INPUT + ".player", "wb"))  # Save player array
                    commons.GAME_SUB_STATE = "PLAYERSELECTION"
                    load_menu_player_data()

                elif menu_button.text == "New World":
                    commons.GAME_SUB_STATE = "WORLDCREATION"

                elif menu_button.text == "Tiny (100x350)":
                    commons.GAME_SUB_STATE = "WORLDNAMING"
                    commons.TEXT_INPUT = ""
                    world.WORLD_SIZE_X = 100
                    world.WORLD_SIZE_Y = 350

                elif menu_button.text == "Small (200x400)":
                    commons.GAME_SUB_STATE = "WORLDNAMING"
                    commons.TEXT_INPUT = ""
                    world.WORLD_SIZE_X = 200
                    world.WORLD_SIZE_Y = 400

                elif menu_button.text == "Medium (400x450)":
                    commons.GAME_SUB_STATE = "WORLDNAMING"
                    commons.TEXT_INPUT = ""
                    world.WORLD_SIZE_X = 400
                    world.WORLD_SIZE_Y = 450

                elif menu_button.text == "Large (700x550)":
                    commons.GAME_SUB_STATE = "WORLDNAMING"
                    commons.TEXT_INPUT = ""
                    world.WORLD_SIZE_X = 700
                    world.WORLD_SIZE_Y = 550

                elif menu_button.text == "Set World Name":
                    world.WORLD_NAME = commons.TEXT_INPUT
                    world.generate_terrain("DEFAULT", blit_progress=True)
                    world.save()
                    commons.GAME_SUB_STATE = "WORLDSELECTION"
                    load_menu_player_data()

                if commons.GAME_SUB_STATE == "COLOURPICKER":
                    if commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][1] is not None:
                        entity_manager.client_colour_picker.selected_colour = tuple(commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][0])
                    entity_manager.client_colour_picker.selected_x = commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][1]
                    entity_manager.client_colour_picker.selected_y = commons.PLAYER_MODEL_DATA[commons.PLAYER_MODEL_COLOUR_INDEX][2]

                # Update last game sub state variable is the sub state changed
                if temp_game_sub_state != commons.GAME_SUB_STATE:
                    if menu_button.text != "Back":
                        commons.GAME_SUB_STATE_STACK.append(temp_game_sub_state)

                    if menu_button.text == "Set Player Name":
                        commons.GAME_SUB_STATE_STACK = commons.GAME_SUB_STATE_STACK[:1]

                    if menu_button.text == "Set World Name":
                        commons.GAME_SUB_STATE_STACK = commons.GAME_SUB_STATE_STACK[:2]

                update_active_menu_buttons()


"""================================================================================================================= 
    menu_manager.draw_menu_buttons -> void

    Calls draw on all active button instances
-----------------------------------------------------------------------------------------------------------------"""
def draw_menu_buttons():
    for menuButton in menu_buttons:
        if menuButton.active:
            menuButton.draw()


"""================================================================================================================= 
    menu_manager.load_menu_player_data -> void

    Loads all player save metadata and creates a surface for each one
-----------------------------------------------------------------------------------------------------------------"""
def load_menu_player_data():
    path = "res/players"
    if not os.path.exists(path):
        os.makedirs(path)
    possible_loads = os.listdir(path)  # Get filenames
    commons.PLAYER_SAVE_OPTIONS = []

    for i in range(len(possible_loads)):
        dat = pickle.load(open("res/players/" + possible_loads[i], "rb"))
        possible_loads[i] = possible_loads[i][:-7]
        player_data_surf = pygame.Surface((315, 60))
        player_data_surf.fill((50, 50, 50))
        pygame.draw.rect(player_data_surf, (60, 60, 60), Rect(0, 0, 315, 60), 4)
        player_data_surf.blit(shared_methods.outline_text(dat[0], (255, 255, 255), commons.DEFAULTFONT), (5, 3))  # Name
        player_data_surf.blit(shared_methods.outline_text("Created: ", (255, 255, 255), commons.DEFAULTFONT), (5, 20))  # Creation date
        player_data_surf.blit(shared_methods.outline_text("Playtime: ", (255, 255, 255), commons.DEFAULTFONT), (5, 40))  # Playtime
        player_data_surf.blit(shared_methods.outline_text(str(dat[7])[:19], (230, 230, 0), commons.DEFAULTFONT), (80, 20))  # Creation date
        player_data_surf.blit(shared_methods.outline_text(str(dat[5]) + "HP", (230, 10, 10), commons.DEFAULTFONT, outline_colour=(128, 5, 5)), (155, 3))  # hp
        player_data_surf.blit(shared_methods.outline_text("100MNA", (80, 102, 244), commons.DEFAULTFONT, outline_colour=(30, 41, 122)), (205, 3))  # mana
        player_data_surf.blit(shared_methods.outline_text(str(int((dat[6] / 60) // 60)) + ":" + str(int(dat[6] // 60 % 60)).zfill(2) + ":" + str(int(dat[6] % 60)).zfill(2), (230, 230, 0), commons.DEFAULTFONT), (90, 40))  # playtime
        sprites = player.render_sprites(dat[1], directions=1, arm_frame_count=1, torso_frame_count=1)
        player_data_surf.blit(sprites[0][0], (270, 0))
        player_data_surf.blit(sprites[1][0], (270, 0))
        commons.PLAYER_SAVE_OPTIONS.append([dat, player_data_surf])


"""================================================================================================================= 
    menu_manager.load_menu_world_data -> void

    Loads all world save metadata and creates a surface for each one
-----------------------------------------------------------------------------------------------------------------"""
def load_menu_world_data():
    path = "res/worlds"
    if not os.path.exists(path):
        os.makedirs(path)
    possible_loads = os.listdir(path)  # Get filenames
    commons.WORLD_SAVE_OPTIONS = []
    for i in range(len(possible_loads)):
        if possible_loads[i][-3:] == "dat":  # if it's a dat file
            world.load(possible_loads[i][:-4], load_all=False)

            world_data_surf = pygame.Surface((315, 60))
            world_data_surf.fill((50, 50, 50))
            pygame.draw.rect(world_data_surf, (60, 60, 60), Rect(0, 0, 315, 60), 4)

            world_data_surf.blit(shared_methods.outline_text(world.world.name, (255, 255, 255), commons.DEFAULTFONT), (5, 3))  # name
            world_data_surf.blit(shared_methods.outline_text("Created: ", (255, 255, 255), commons.DEFAULTFONT), (5, 20))  # Creation date
            world_data_surf.blit(shared_methods.outline_text("Playtime: ", (255, 255, 255), commons.DEFAULTFONT), (5, 40))  # Playtime
            world_data_surf.blit(shared_methods.outline_text(world.world.get_creation_date_string(), (230, 230, 0), commons.DEFAULTFONT), (80, 20))  # Creation date
            world_data_surf.blit(shared_methods.outline_text(str(int((world.world.play_time / 60) // 60)) + ":" + str(int(world.world.play_time // 60 % 60)).zfill(2) + ":" + str(int(world.world.play_time % 60)).zfill(2), (230, 230, 0), commons.DEFAULTFONT), (90, 40))  # playtime

            world_data_surf.blit(surface_manager.misc_gui[10], (260, 7))

            commons.WORLD_SAVE_OPTIONS.append([world.world.name, world_data_surf])


"""================================================================================================================= 
    Constructing all buttons used in the game, order in the list matters here
-----------------------------------------------------------------------------------------------------------------"""
menu_buttons.append(MenuButton("Fegaria Remastered", (commons.WINDOW_WIDTH * 0.5, 30), commons.XLARGEFONT, 25, False, (110, 147, 43), (50, 80, 7)))

menu_buttons.append(MenuButton("Back", (commons.WINDOW_WIDTH * 0.5, 570), commons.LARGEFONT, 25, True))

menu_buttons.append(MenuButton("Play", (commons.WINDOW_WIDTH * 0.5, 450), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Settings", (commons.WINDOW_WIDTH * 0.5, 480), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Changes", (commons.WINDOW_WIDTH * 0.5, 510), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Credits", (commons.WINDOW_WIDTH * 0.5, 540), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Quit", (commons.WINDOW_WIDTH * 0.5, 570), commons.LARGEFONT, 25, True))

menu_buttons.append(MenuButton("Settings", (commons.WINDOW_WIDTH * 0.5, 120), commons.XLARGEFONT, 25, False))
menu_buttons.append(MenuButton("Coming soon", (commons.WINDOW_WIDTH * 0.5, 300), commons.LARGEFONT, 25, False))

menu_buttons.append(MenuButton("Credits", (commons.WINDOW_WIDTH * 0.5, 120), commons.XLARGEFONT, 25, False))
menu_buttons.append(MenuButton("Design: Fergus Griggs", (commons.WINDOW_WIDTH * 0.5, 270), commons.LARGEFONT, 25, False))
menu_buttons.append(MenuButton("Programming: Fergus Griggs", (commons.WINDOW_WIDTH * 0.5, 310), commons.LARGEFONT, 25, False))
menu_buttons.append(MenuButton("Anything but audio: Fergus Griggs", (commons.WINDOW_WIDTH * 0.5, 350), commons.LARGEFONT, 25, False))
menu_buttons.append(MenuButton("Music and sounds: Re-Logic", (commons.WINDOW_WIDTH * 0.5, 390), commons.LARGEFONT, 25, False))

menu_buttons.append(MenuButton("Select Player", (commons.WINDOW_WIDTH * 0.5, 90), commons.LARGEFONT, 24, False))
menu_buttons.append(MenuButton("New Player", (commons.WINDOW_WIDTH * 0.5, 530), commons.LARGEFONT, 24, True))

menu_buttons.append(MenuButton("Hair Type", (commons.WINDOW_WIDTH * 0.5, 200), commons.LARGEFONT, 26, True))
menu_buttons.append(MenuButton("Hair Colour", (commons.WINDOW_WIDTH * 0.5, 240), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Eye Colour", (commons.WINDOW_WIDTH * 0.5, 280), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Skin Colour", (commons.WINDOW_WIDTH * 0.5, 320), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Clothes", (commons.WINDOW_WIDTH * 0.5, 360), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Create", (commons.WINDOW_WIDTH * 0.5, 450), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Randomize", (commons.WINDOW_WIDTH * 0.5, 490), commons.LARGEFONT, 26, True))

menu_buttons.append(MenuButton("Shirt Colour", (commons.WINDOW_WIDTH * 0.5, 240), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Undershirt Colour", (commons.WINDOW_WIDTH * 0.5, 280), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Trouser Colour", (commons.WINDOW_WIDTH * 0.5, 320), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Shoe Colour", (commons.WINDOW_WIDTH * 0.5, 360), commons.LARGEFONT, 24, True))

menu_buttons.append(MenuButton("Set Player Name", (commons.WINDOW_WIDTH * 0.5, 450), commons.LARGEFONT, 24, True))

menu_buttons.append(MenuButton("Select World", (commons.WINDOW_WIDTH * 0.5, 90), commons.LARGEFONT, 24, False))
menu_buttons.append(MenuButton("New World", (commons.WINDOW_WIDTH * 0.5, 530), commons.LARGEFONT, 24, True))

menu_buttons.append(MenuButton("World Size", (commons.WINDOW_WIDTH * 0.5, 120), commons.XLARGEFONT, 24, False))

menu_buttons.append(MenuButton("Tiny (100x350)", (commons.WINDOW_WIDTH * 0.5, 240), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Small (200x400)", (commons.WINDOW_WIDTH * 0.5, 280), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Medium (400x450)", (commons.WINDOW_WIDTH * 0.5, 320), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Large (700x550)", (commons.WINDOW_WIDTH * 0.5, 360), commons.LARGEFONT, 24, True, (200, 0, 0), (100, 0, 0)))

menu_buttons.append(MenuButton("Set World Name", (commons.WINDOW_WIDTH * 0.5, 450), commons.LARGEFONT, 24, True))

menu_buttons.append(MenuButton("Changes", (commons.WINDOW_WIDTH * 0.5, 120), commons.XLARGEFONT, 25, False))

menu_buttons.append(MenuButton("PyGame Page", (commons.WINDOW_WIDTH * 0.5, 280), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("GitHub Repo", (commons.WINDOW_WIDTH * 0.5, 320), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("YouTube Channel", (commons.WINDOW_WIDTH * 0.5, 360), commons.LARGEFONT, 24, True))
menu_buttons.append(MenuButton("Trello Board", (commons.WINDOW_WIDTH * 0.5, 400), commons.LARGEFONT, 24, True))

update_active_menu_buttons()
