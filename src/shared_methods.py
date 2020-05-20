#shared_methods.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, math;
from pygame.locals import *;

import commons;
import surface_manager;
import tables;

def NormalizeVector2(vector):
    magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2);
    return (vector[0] / magnitude, vector[1] / magnitude);

def GetOnOff(booleanVariable):
    if booleanVariable:
        return "on";
    return "off";

def DarkenColour(colour, factor = 0.6):
    return (colour[0] * factor, colour[1] * factor, colour[2] * factor);

def GetBlockAverageColour(val):
    if val in tables.platformBlocks:  
        colour = pygame.transform.average_color(surface_manager.specialTiles[val - 255],Rect(commons.BLOCKSIZE / 8, commons.BLOCKSIZE / 8, commons.BLOCKSIZE * 3 / 4, commons.BLOCKSIZE / 4));
    else:
        if val >= 255:
            colour = pygame.transform.average_color(surface_manager.specialTiles[val - 255]);
        else:
            colour = pygame.transform.average_color(surface_manager.tiles[val]);
    return colour;

def GetTierColour(tier):
    if tier < 0: return(150, 150, 150)#Gray
    elif tier == 1: return(146, 146, 249)#Blue
    elif tier == 2: return(146, 249, 146)#Green
    elif tier == 3: return(233, 182, 137)#Orange
    elif tier == 4: return(253, 148, 148)#Light Red
    elif tier == 5: return(249, 146, 249)#Pink
    elif tier == 6: return(191, 146, 233)#Light Purple
    elif tier == 7: return(139, 237, 9)#Lime
    elif tier == 8: return(233, 233, 9)#Yellow
    elif tier == 9: return(3, 138, 177)#Cyan
    elif tier == 10: return(229, 35, 89)#Red
    elif tier > 10: return(170, 37, 241)#Purple
    else:
        return(255, 255, 255, 255); #White

def RotateSurface(image, angle):
    originalRect = image.get_rect();
    rotatedImage = pygame.transform.rotate(image, angle);
    rotatedRect = originalRect.copy();
    rotatedRect.center = rotatedImage.get_rect().center;
    rotatedImage = rotatedImage.subsurface(rotatedRect).copy();
    return rotatedImage;

def OutlineText(string, colour, font, outlineColour = (0, 0, 0)):
    text1 = font.render(string, False, colour);
    if commons.FANCYTEXT:
        text2 = font.render(string, False, outlineColour);
        surf = pygame.Surface((text2.get_width() + 2, text2.get_height() + 2));
        surf.fill((255, 0, 255));
        surf.set_colorkey((255, 0, 255));
        surf.blit(text2, (0, 1));
        surf.blit(text2, (2, 1));
        surf.blit(text2, (1, 0))
        surf.blit(text2, (1, 2))
        surf.blit(text1, (1, 1))
        return surf;
    else:
        return text1;

#measurements in multiples of 48px
def CreateMenuSurface(width, height, body):
    surf = pygame.Surface((width * 48, height * 48));
    surf.fill((255, 0, 255));
    surf.set_colorkey((255,0,255));
    for i in range(width):
        for j in range(height):
            if i == 0:
                if j == 0:
                    index = 5;
                elif j == height - 1:
                    index = 6;
                else:
                    index = 2;
            elif i == width-1:
                if j == 0:
                    index = 8;
                elif j == height - 1:
                    index = 7;
                else:
                    index = 4;
            elif j == 0:
                index = 1;
            elif j == height - 1:
                index = 3;
            else:
                index = 9;
                
            surf.blit(surface_manager.miscGUI[index], (i * 48, j * 48));
    usableWidth = width * 48 - 60;
    lines = [""];
    words = body.split(" ");
    lineWidth = 0;
    for word in words:
        lineWidth += commons.DEFAULTFONT.size(" " + word)[0];
        if lineWidth > usableWidth:
            lineWidth = 0;
            lines.append(word);
        else:
            lines[-1] += " " + word;
    for i in range(len(lines)):
        surf.blit(OutlineText(lines[i], (255, 255, 255), commons.DEFAULTFONT), (15, 15 + i * 20));
    return surf;

def ColourSurface(greySurf, col):
    if col == ():
        col = (0, 0, 0);
    x = greySurf.get_width();
    y = greySurf.get_height();
    surf = pygame.Surface((x, y)); 
    surf.fill((255, 255, 255));
    surf.set_colorkey((255, 255, 255)); #set the colourkey to white
    surf.blit(greySurf, (0, 0)); #create a surf with the given hair and white background
    colour = pygame.Surface((x, y));
    colour.fill(col); #create a blank surf with the colour of the hair
    surf.blit(colour, (0, 0), None, BLEND_RGB_ADD); #blit the new surf to the hair with an add blend flag
    return surf;
