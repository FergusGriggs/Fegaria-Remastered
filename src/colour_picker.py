# colour_picker.py
__author__ = "Fergus Griggs"
__email__ = "fbob987 at gmail dot com"

import pygame
from pygame.locals import *

import commons


"""================================================================================================================= 
    colour_picker.ColourPicker

    Stores information about a colour picker
-----------------------------------------------------------------------------------------------------------------"""
class ColourPicker:
    def __init__(self, position, width, height, border_size=5, surface_resolution=0.5):
        self.position = position
        self.width = width
        self.height = height
        self.section_width = width / 6
        self.border_size = border_size
        self.surface_resolution = surface_resolution
        self.colours = [
         (255,   0, 255),
         (255,   0,   0),
         (255, 255,   0),
         (  0, 255,   0),
         (  0, 255, 255),
         (  0,   0, 255),
         (255,   0, 255)
        ]
        self.selected_colour = (0, 0, 0)
        self.selected_x = 0
        self.selected_y = height
        self.surface = None
        self.render_surface()
        self.rect = Rect(self.position[0] + self.border_size, self.position[1] + self.border_size, width, height)

    """================================================================================================================= 
        colour_picker.ColourPicker.render_surface -> void

        Uses canvas and border size info to render the colour picker surface 
    -----------------------------------------------------------------------------------------------------------------"""
    def render_surface(self):
        self.surface = pygame.Surface((self.width + self.border_size * 2,  self.height + self.border_size * 2))
        # Draw border
        pygame.draw.rect(self.surface, (90, 90, 90), Rect(0, 0, self.width+self.border_size * 2, self.height+self.border_size * 2), 0)
        pygame.draw.rect(self.surface, (128, 128, 128), Rect(2, 2, self.width+self.border_size * 2 - 4, self.height + self.border_size * 2 - 4), 0)
        pygame.draw.rect(self.surface, (110, 110, 110), Rect(4, 4, self.width+self.border_size * 2 - 8, self.height + self.border_size * 2 - 8), 0)
        surf = pygame.Surface((int(self.width * self.surface_resolution), int(self.height * self.surface_resolution)))
        for j in range(int(self.height * self.surface_resolution)):
            for i in range(int(self.width * self.surface_resolution)):
                surf.set_at((i, j), self.get_colour(i / self.surface_resolution, j / self.surface_resolution))
        surf = pygame.transform.scale(surf, (self.width, self.height))
        self.surface.blit(surf, (self.border_size, self.border_size))

    """================================================================================================================= 
        colour_picker.ColourPicker.get_colour -> tuple

        Generates the colour of the surface at a given location
    -----------------------------------------------------------------------------------------------------------------"""
    def get_colour(self, i, j):
        base_colour_index = int(i // self.section_width)  # Colour to the left of the point
        next_colour_index = (base_colour_index + 1)  # Colour to the right of the point
        blend = (i % self.section_width) / self.section_width
        shade = 1 - j / self.height

        col = [0, 0, 0]

        for index in range(3):
            base_colour_channel = int(self.colours[base_colour_index][index])
            next_colour_channel = int(self.colours[next_colour_index][index])

            channel = int(round(base_colour_channel * (1 - blend) + next_colour_channel * blend))
            if shade < 0.5:
                channel = int(channel * shade * 2)
            elif shade > 0.5:
                new_shade = shade - 0.5
                channel = int(channel * (0.5 - new_shade) * 2 + 255 * new_shade * 2)

            col[index] = channel
        return tuple(col)

    """================================================================================================================= 
        colour_picker.ColourPicker.update -> void

        If the mouse is clicked over the colour picker, update the selected colour and location
    -----------------------------------------------------------------------------------------------------------------"""
    def update(self):
        if pygame.mouse.get_pressed()[0] and not commons.WAIT_TO_USE:
            if self.rect.collidepoint(commons.MOUSE_POS):
                self.selected_x = commons.MOUSE_POS[0] - self.position[0] - self.border_size
                self.selected_y = commons.MOUSE_POS[1] - self.position[1] - self.border_size
                self.selected_colour = self.get_colour(self.selected_x, self.selected_y)
                self.selected_colour = (self.selected_colour[0] * 0.5, self.selected_colour[1] * 0.5, self.selected_colour[2] * 0.5)

    """================================================================================================================= 
        colour_picker.ColourPicker.draw -> void

        Draws the colour picker's surface and draws the location of the selected colour
    -----------------------------------------------------------------------------------------------------------------"""
    def draw(self):
        commons.screen.blit(self.surface, self.position)

        if self.selected_x is not None and self.selected_y is not None:
            pygame.draw.circle(commons.screen, (128, 128, 128), (self.selected_x + self.position[0] + self.border_size, self.selected_y + self.position[1] + self.border_size), 5, 1)
