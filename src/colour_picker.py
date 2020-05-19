#colour_picker.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import pygame, random;
from pygame.locals import *;

import commons;

class ColourPicker():
   def __init__(self, position, width, height, boarderSize = 5, surfaceResolution = 0.5):
      self.position = position;
      self.width = width;
      self.height = height;
      self.sectionWidth = width / 6;
      self.boarderSize = boarderSize;
      self.surfaceResolution = surfaceResolution;
      self.colours = [
         (255,   0, 255),
         (255,   0,   0),
         (255, 255,   0),
         (  0, 255,   0),
         (  0, 255, 255),
         (  0,   0, 255),
         (255,   0, 255)
         ]
      self.selectedColour = (0,0,0);
      self.selectedX = 0;
      self.selectedY = height;
      self.RenderSurface();
      self.rect = Rect(self.position[0] + self.boarderSize, self.position[1] + self.boarderSize, width, height);

   def RenderSurface(self):
      self.surface = pygame.Surface((self.width + self.boarderSize * 2,  self.height + self.boarderSize * 2));
      #draw border
      pygame.draw.rect(self.surface, (90, 90, 90), Rect(0, 0, self.width+self.boarderSize * 2, self.height+self.boarderSize * 2), 0);
      pygame.draw.rect(self.surface, (128, 128, 128), Rect(2, 2, self.width+self.boarderSize * 2 - 4, self.height + self.boarderSize * 2 - 4), 0);
      pygame.draw.rect(self.surface, (110, 110, 110), Rect(4, 4, self.width+self.boarderSize * 2 - 8, self.height + self.boarderSize * 2 - 8), 0);
      
      surf=pygame.Surface((int(self.width * self.surfaceResolution), int(self.height * self.surfaceResolution)));
      for j in range(int(self.height * self.surfaceResolution)):
         for i in range(int(self.width * self.surfaceResolution)):
            surf.set_at((i, j), self.GetColour(i / self.surfaceResolution, j / self.surfaceResolution));
      surf = pygame.transform.scale(surf, (self.width, self.height));
      self.surface.blit(surf, (self.boarderSize, self.boarderSize));

   def GetColour(self, i, j):
      baseCol = int(i // self.sectionWidth); #colour to the left of the point
      nextCol = (baseCol + 1); #colour to the right of the point
      blend = (i % self.sectionWidth) / self.sectionWidth;
      shade = 1 - j / self.height;

      col = [0, 0, 0];

      for index in range(3):
         baseColour = int(self.colours[baseCol][index]);
         nextColour = int(self.colours[nextCol][index]);
      
         channel = int(round(baseColour * (1 - blend) + nextColour * blend));
         if shade < 0.5:
            channel = int(channel * shade * 2);
         elif shade > 0.5:
            newShade = shade - 0.5;
            channel = int(channel * (0.5 - newShade) * 2 + 255 * newShade * 2);
            
         col[index] = channel;

      return tuple(col);

   def Update(self):
      if pygame.mouse.get_pressed()[0] and not commons.WAIT_TO_USE:
         if self.rect.collidepoint(commons.MOUSE_POS):
            self.selectedX = commons.MOUSE_POS[0] - self.position[0] - self.boarderSize;
            self.selectedY = commons.MOUSE_POS[1] - self.position[1] - self.boarderSize;
            self.selectedColour = self.GetColour(self.selectedX, self.selectedY);
            self.selectedColour = (self.selectedColour[0] * 0.5, self.selectedColour[1] * 0.5, self.selectedColour[2] * 0.5);

   def Draw(self):
      commons.screen.blit(self.surface, self.position)
      if self.selectedX != None and self.selectedY != None:
          pygame.draw.circle(commons.screen, (128, 128, 128), (self.selectedX + self.position[0], self.selectedY + self.position[1]), 5, 1);