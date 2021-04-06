# shared_methods.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame
import math
from pygame.locals import *
import math

import commons
import surface_manager
import game_data

from game_data import TileTag

"""================================================================================================================= 
    shared_methods.normalize_vec_2 -> tuple

    Performs vector normalization on the given vector (scalar tuple)
-----------------------------------------------------------------------------------------------------------------"""
def normalize_vec_2(vector):
    magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    return vector[0] / magnitude, vector[1] / magnitude


"""================================================================================================================= 
    shared_methods.get_on_off -> string

    Given a bool, returns either "on" or "off"
-----------------------------------------------------------------------------------------------------------------"""
def get_on_off(bool_var):
    if bool_var:
        return "on"
    return "off"


"""================================================================================================================= 
    shared_methods.darken_colour -> tuple

    Multiplies all three components of a colour tuple by a given float
-----------------------------------------------------------------------------------------------------------------"""
def darken_colour(colour, factor=0.6):
    return colour[0] * factor, colour[1] * factor, colour[2] * factor


"""================================================================================================================= 
    shared_methods.get_block_average_colour -> tuple

    Given a tile_id, the average colour of that tile's image is computed using the 'pygame.transform.average_color'
    function, or potentially overridden in the tile tool
-----------------------------------------------------------------------------------------------------------------"""
def get_block_average_colour(tile_id):
    tile_data = game_data.get_tile_by_id(tile_id)
    return tile_data["@average_colour"]

"""================================================================================================================= 
    shared_methods.get_tier_colour -> tuple

    Given an item tier, a colour representing that tier is returned
-----------------------------------------------------------------------------------------------------------------"""
def get_tier_colour(tier):
    if tier < 0:
        return 150, 150, 150  # Gray
    elif tier == 1:
        return 146, 146, 249  # Blue
    elif tier == 2:
        return 146, 249, 146  # Green
    elif tier == 3:
        return 233, 182, 137  # Orange
    elif tier == 4:
        return 253, 148, 148  # Light Red
    elif tier == 5:
        return 249, 146, 249  # Pink
    elif tier == 6:
        return 191, 146, 233  # Light Purple
    elif tier == 7:
        return 139, 237, 9  # Lime
    elif tier == 8:
        return 233, 233, 9  # Yellow
    elif tier == 9:
        return 3, 138, 177  # Cyan
    elif tier == 10:
        return 229, 35, 89  # Red
    elif tier > 10:
        return 170, 37, 241  # Purple
    else:
        return 255, 255, 255, 255  # White


"""================================================================================================================= 
    shared_methods.rotate_surface -> pygame.Surface

    Given a surface and an angle, a rotation preserving edges is performed on the surface and returned
-----------------------------------------------------------------------------------------------------------------"""
def rotate_surface(image, angle):
    original_rect = image.get_rect()
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = original_rect.copy()
    rotated_rect.center = rotated_image.get_rect().center
    rotated_image = rotated_image.subsurface(rotated_rect).copy()
    return rotated_image


"""================================================================================================================= 
    shared_methods.outline_text -> pygame.Surface

    Used to draw most text in the game, renders some text and draws it several times at varying offsets to create
    an outline effect
-----------------------------------------------------------------------------------------------------------------"""
def outline_text(string, colour, font, outline_colour=(0, 0, 0)):
    text1 = font.render(string, False, colour)
    if commons.FANCYTEXT:
        text2 = font.render(string, False, outline_colour)
        surf = pygame.Surface((text2.get_width() + 2, text2.get_height() + 2))
        surf.fill((255, 0, 255))
        surf.set_colorkey((255, 0, 255))
        surf.blit(text2, (0, 1))
        surf.blit(text2, (2, 1))
        surf.blit(text2, (1, 0))
        surf.blit(text2, (1, 2))
        surf.blit(text1, (1, 1))
        return surf
    else:
        return text1


"""================================================================================================================= 
    shared_methods.create_menu_surface -> pygame.Surface

    Using a few measurements, and the images in the UI image list, a bordered surface image is created, with some
    optional text (measurements in multiples of 48px)
-----------------------------------------------------------------------------------------------------------------"""
def create_menu_surface(width, height, body):
    surf = pygame.Surface((width * 48, height * 48))
    surf.fill((255, 0, 255))
    surf.set_colorkey((255, 0, 255))
    for i in range(width):
        for j in range(height):
            if i == 0:
                if j == 0:
                    index = 5
                elif j == height - 1:
                    index = 6
                else:
                    index = 2
            elif i == width-1:
                if j == 0:
                    index = 8
                elif j == height - 1:
                    index = 7
                else:
                    index = 4
            elif j == 0:
                index = 1
            elif j == height - 1:
                index = 3
            else:
                index = 9
                
            surf.blit(surface_manager.misc_gui[index], (i * 48, j * 48))
    usable_width = width * 48 - 60
    lines = [""]
    words = body.split(" ")
    line_width = 0
    for word in words:
        line_width += commons.DEFAULTFONT.size(" " + word)[0]
        if line_width > usable_width:
            line_width = 0
            lines.append(word)
        else:
            lines[-1] += " " + word
    for i in range(len(lines)):
        surf.blit(outline_text(lines[i], (255, 255, 255), commons.DEFAULTFONT), (15, 15 + i * 20))
    return surf


"""================================================================================================================= 
    shared_methods.colour_surface -> pygame.Surface

    Uses the pygame.BLEND_RGB_ADD blend flag to colour a grayscale image with the given colour
-----------------------------------------------------------------------------------------------------------------"""
def colour_surface(grey_surf, col):
    if col == ():
        col = (0, 0, 0)
    x = grey_surf.get_width()
    y = grey_surf.get_height()
    surf = pygame.Surface((x, y))
    surf.fill((255, 255, 255))
    surf.set_colorkey((255, 255, 255))  # set the colourkey to white
    surf.blit(grey_surf, (0, 0))  # create a surf with the given hair and white background
    colour = pygame.Surface((x, y))
    colour.fill(col)  # create a blank surf with the colour of the hair
    surf.blit(colour, (0, 0), None, BLEND_RGB_ADD)  # blit the new surf to the hair with an add blend flag
    return surf


"""================================================================================================================= 
    shared_methods.lerp_float -> float

    Simple linear interpolation
-----------------------------------------------------------------------------------------------------------------"""
def lerp_float(a, b, t):
    return a + (b - a) * t


def smooth_zero_to_one(zero_to_one_float, iterations):
    for _ in range(iterations):
        zero_to_one_float = math.sin(zero_to_one_float * math.pi - math.pi * 0.5)
        zero_to_one_float = zero_to_one_float * 0.5 + 0.5
    return zero_to_one_float


def ease_out_zero_to_one(zero_to_one_float, iterations):
    for _ in range(iterations):
        zero_to_one_float = math.sin(zero_to_one_float * math.pi * 0.5)
    return zero_to_one_float


def ease_in_zero_to_one(zero_to_one_float, iterations):
    for _ in range(iterations):
        zero_to_one_float = 1.0 + math.sin(zero_to_one_float * math.pi * 0.5 - math.pi * 0.5)
    return zero_to_one_float
