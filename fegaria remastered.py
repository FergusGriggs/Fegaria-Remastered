#fegaria remastered
import pygame, sys, math, time, os, random, perlin, pickle, datetime
from pygame.locals import *

def moveParallax(val):
    global parallaxPos
    parallaxPos=(parallaxPos[0]+val[0],parallaxPos[1]+val[1])
    if parallaxPos[0]>0:parallaxPos=(-40+parallaxPos[0],parallaxPos[1])
    elif parallaxPos[0]<-39:parallaxPos=(parallaxPos[0]+40,parallaxPos[1])
    if parallaxPos[1]>0:parallaxPos=(parallaxPos[0],-40+parallaxPos[1])
    elif parallaxPos[1]<-39:parallaxPos=(parallaxPos[0],parallaxPos[1]+40)
    
def loadTileMasks():
    global tilemasks
    tilemaskimg=pygame.image.load("Textures/tilemasks.png").convert_alpha()
    tilemasks=[]
    for j in range(5):
        for i in range(13):
            surf=pygame.Surface((8,8),pygame.SRCALPHA)
            surf.blit(tilemaskimg,(-i*9,-j*9))
            surf=pygame.transform.scale(surf,(BLOCKSIZE,BLOCKSIZE))
            tilemasks.append(surf)
            
def loadBackgroundImages():
    global backgroundImages
    backgroundimg=pygame.image.load("Textures/backgroundTilesheet.png").convert()
    backgroundImages=[]
    for i in range(5):
        surf=pygame.Surface((20,20))
        surf.blit(backgroundimg,(-i*20,0))
        surf=pygame.transform.scale(surf,(40,40))
        backgroundImages.append(surf)
            
def loadTiles():
    global tileImages
    tilesetimg=pygame.image.load("Textures/tileset.png").convert_alpha()
    tileImages=[]
    for j in range(10):
        for i in range(10):
            surf=pygame.Surface((8,8),pygame.SRCALPHA)
            surf.set_colorkey((255,0,255))
            surf.blit(tilesetimg,(-i*8,-j*8))
            surf=pygame.transform.scale(surf,(BLOCKSIZE,BLOCKSIZE))
            tileImages.append(surf)
            
def loadWallTiles():
    global wallTileImages
    walltilesetimg=pygame.image.load("Textures/wallTileset.png").convert_alpha()
    wallTileImages=[]
    for j in range(10):
        for i in range(10):
            surf=pygame.Surface((8,8),pygame.SRCALPHA)
            surf.blit(walltilesetimg,(-i*8,-j*8))
            surf=pygame.transform.scale(surf,(BLOCKSIZE,BLOCKSIZE))
            wallTileImages.append(surf)
            
def loadHairStyles():
    global hairStyles
    hairStyles=[]
    scale=2
    img=pygame.transform.scale(pygame.image.load("Textures/hairsTileset.png"),(int(22*9*scale),int(24*scale)))
    for i in range(9):
        surf=pygame.Surface((int(22*scale),int(24*scale)))
        surf.set_colorkey((255,0,255))
        surf.blit(img,(-i*22*scale,0))
        surf=pygame.transform.scale(surf,(int(20*scale),int(24*scale)))
        hairStyles.append(surf)
        
def loadTorsoFrames():
    global torsoFrames
    torsoFrames=[]
    scale=2
    img=pygame.transform.scale(pygame.image.load("Textures/torsoTileset.png"),(int(20*19*scale),int(30*scale)))
    for i in range(19):
        surf=pygame.Surface((int(20*scale),int(30*scale)))
        surf.set_colorkey((255,0,255))
        surf.blit(img,(-i*20*scale,0))
        torsoFrames.append(surf)
        
def compileBackgroundImages():#creates a larger surf compiled with background surfs
    global backsurfs
    backsurfs=[]
    for k in range(5):
        backsurf=pygame.Surface((screenW+40,screenH+40))
        for i in range(int(screenW/40+1)):
            for j in range(int(screenH/40+1)):
                backsurf.blit(backgroundImages[k],(i*40,j*40))
        backsurfs.append(backsurf)
        
class Model():#used to store info about the player's looks (fairly useless atm)
    def __init__(self,sex,hairID,hairCol,eyeCol,shirtCol,underShirtCol,trouserCol,shoeCol):
        self.sex=sex
        self.hairID=hairID
        self.hairCol=hairCol
        self.eyeCol=eyeCol
        self.shirtCol=shirtCol
        self.underShirtCol=underShirtCol
        self.trouserCol=trouserCol
        self.shoeCol=shoeCol
        
class Player():#stores all info about a player
    def __init__(self,pos,model):
        self.pos=pos
        self.oldpos=pos
        self.rect=Rect(self.pos[0]-playerWidth/2,self.pos[1]-playerHeight/2,playerWidth,playerHeight)#hitbox
        self.vel=(0,0)
        self.model=model#model class
        self.renderSprites()
        self.animationTick=0
        self.animationTick2=0
        self.animationFrame=5#which frame to blit
        self.alive=True
        self.respawnTick=0#how long till respawn
        self.HP=100
        self.maxHP=self.HP
        self.grounded=True
        self.movingLeft=False
        self.movingRight=False
        self.movingDown=False#is player walking
        self.direction=1
        self.armSwing=False
        self.stopLeft=False#stop movement left
        self.stopRight=False#stop movement right
        self.animationSpeed=1
        self.movingDownTick=0
        self.stopMovingDown=False
        self.lastBlockOn=0
    def update(self):
        if self.alive:
            if self.movingLeft:#moves player left
                if not self.stopLeft:
                    if self.movingDown:self.vel=(-1,self.vel[1])
                    else:self.vel=(-3,self.vel[1])
            if self.movingRight:#moves player right
                if not self.stopRight:
                    if self.movingDown:self.vel=(1,self.vel[1])
                    else:self.vel=(3,self.vel[1])
            oldpos=tuple(self.pos)#used to work out how much parallax and particles need to move
            self.vel=(self.vel[0]*0.9,self.vel[1]*0.99+GRAVITY)
            self.pos=(self.pos[0]+self.vel[0],self.pos[1]+self.vel[1])
            self.rect.left=self.pos[0]-playerWidth/2#updating rect
            self.rect.top=self.pos[1]-playerHeight/2
            self.blockpos=(math.floor(self.pos[1]//BLOCKSIZE),math.floor(self.pos[0]//BLOCKSIZE))
            self.grounded=False
            self.stopLeft=False
            self.stopRight=False
            fallDamaged=False#so fall damage is only applied once     
            
            if self.vel[0]<0:
                if self.pos[0]<WORLDBOARDER_WEST:self.pos=(int(WORLDBOARDER_WEST),self.pos[1])
            elif self.vel[0]>0:
                if self.pos[0]>WORLDBOARDER_EAST:self.pos=(int(WORLDBOARDER_EAST),self.pos[1])
            if self.vel[1]<0:
                if self.pos[1]<WORLDBOARDER_NORTH:
                    self.pos=(self.pos[0],int(WORLDBOARDER_NORTH))
                    self.vel=(self.vel[0],0)
            elif self.vel[1]>0:
                if self.pos[1]>WORLDBOARDER_SOUTH:
                    self.pos=(self.pos[0],int(WORLDBOARDER_SOUTH))
                    self.vel=(self.vel[0],0)
                    self.grounded=True
            
            
            for j in range(-2,3):
                for i in range(-2,3):
                    try:
                        val=mapData[self.blockpos[1]+j][self.blockpos[0]+i][0]
                        if val not in uncollidableBlocks:
                            blockrect=Rect(BLOCKSIZE*(self.blockpos[1]+j),BLOCKSIZE*(self.blockpos[0]+i),BLOCKSIZE,BLOCKSIZE) 
                            if val in platformBlocks:platform=True
                            else:
                                platform=False
                                if blockrect.colliderect(int(self.rect.left-1),int(self.rect.top+2),1,int(self.rect.height-4)):self.stopLeft=True#is there a solid block left
                                if blockrect.colliderect(int(self.rect.right+1),int(self.rect.top+2),1,int(self.rect.height-4)):self.stopRight=True#is there a solid block right        
                            if blockrect.colliderect(self.rect):
                                deltaX = self.pos[0]-blockrect.centerx
                                deltaY = self.pos[1]-blockrect.centery
                                if abs(deltaX) > abs(deltaY):
                                    if deltaX > 0:
                                        if not platform:
                                            self.pos=(blockrect.right+playerWidth/2,self.pos[1])#move player right
                                            self.vel=(0,self.vel[1])#stop player horizontally
                                    else:
                                        if not platform:
                                            self.pos=(blockrect.left-playerWidth/2,self.pos[1])#move player left
                                            self.vel=(0,self.vel[1])#stop player horizontally
                                else:
                                    if deltaY > 0:
                                        if self.vel[1]<0:
                                            if not platform:
                                                if Rect(self.rect.left+3,self.rect.top,self.rect.width-6,self.rect.height).colliderect(blockrect):
                                                    self.pos=(self.pos[0],blockrect.bottom+playerHeight/2)#move player down
                                                    self.vel=(self.vel[0],0)#stop player vertically
                                    else:
                                        if self.vel[1]>0:
                                            if Rect(self.rect.left+3,self.rect.top,self.rect.width-6,self.rect.height).colliderect(blockrect):
                                                if platform:
                                                    if self.movingDown:
                                                        collide=False
                                                    else:
                                                        if self.vel[1]<5:
                                                            if self.pos[1]+BLOCKSIZE<blockrect.top:
                                                                collide=True
                                                        else:
                                                            collide=True
                                                else:collide=True
                                                if collide:
                                                    if not fallDamaged:
                                                        if self.vel[1]>8:
                                                            damage=int(((self.vel[1]-7.5)*5)**1.5)#work out fall damage
                                                            self.damage(damage)#apply fall damage once
                                                            fallDamaged=True
                                                    self.lastBlockOn=int(val)
                                                    self.movingDownTick=-1
                                                    self.pos=(self.pos[0],blockrect.top-playerHeight/2+1)#move player up
                                                    self.vel=(self.vel[0]*0.5,0)#slow down player horizontally and stop player vertically
                                                    self.grounded=True
                                            
                                                
                    except:None
            if self.stopMovingDown:#wait before setting movingdown to false based on player y vel
                if self.movingDownTick<0:
                    self.movingDown=False
                    self.stopMovingDown=False
                else:
                    self.movingDownTick-=self.vel[1]
            if self.alive:
                self.posDiff=(self.pos[0]-oldpos[0],self.pos[1]-oldpos[1])
                moveParallax((-self.posDiff[0]*PARALLAXAMNT,-self.posDiff[1]*PARALLAXAMNT))#move parallax based on vel
            
        else:# if player is not alive, wait to respawn
            if self.respawnTick>0:
                self.respawnTick-=1
            else:
                self.respawn()
                
    def damage(self,val):
        if not CREATIVE:
            print(str(val)+" damage from falling, clumsy.")
            self.HP-=val
            if self.HP<0:self.HP=0
            renderHpText()
            if self.HP>0:#check if the player has died from damage
                if SFX:
                    sounds[random.randint(7,9)].play()#random hurt sound
                if PARTICLES:
                    for i in range(int(5*PARTICLEDENSITY)):#blood
                        Particle((screenW/2,screenH/2),(230,0,0),life=100,GRAV=0.02,angle=-math.pi/2,spread=math.pi,magnitude=random.random()*2)
            else:
                self.kill()
            
    def kill(self):
        self.respawnTick=500#respawn delay
        self.alive=False
        self.vel=(0,0)
        self.posDiff=(0,0)
        if PARTICLES:
            for i in range(int(25*PARTICLEDENSITY)):#more blood
                Particle((screenW/2,screenH/2),(230,0,0),life=100,GRAV=0.02,angle=-math.pi/2,spread=math.pi,magnitude=random.random()*4)
        if SFX:
            sounds[11].play()#death sound
        
    def respawn(self):
        self.pos=tuple(clientWorld.spawnPoint)#set pos to clientWorld.spawnPoint
        self.vel=(0,0)
        self.alive=True
        self.HP=self.maxHP#reset hp
        renderHpText()
        
    def animate(self):
            if not self.armSwing:#arm swing overrides other animations (sometimes causes sliding)
                if self.animationTick<=0:#happens every 'animationSpeed' frames
                    self.animationTick=self.animationSpeed
                    if self.grounded:
                        if self.movingLeft:#if moving left, cycle through left frames
                            if  self.animationFrame<37:
                                 self.animationFrame+=1
                            else:
                                self.animationFrame=25
                            return
                        elif self.movingRight:#if moving right, cycle through right frames
                            if  self.animationFrame<18:
                                 self.animationFrame+=1
                            else:
                                self.animationFrame=6
                            return
                        else:#if idle put arms down
                            if self.direction==0:
                                self.animationFrame=19
                            elif self.direction==1:
                                self.animationFrame=0  
                    else:#puts arms in the air if not grounded
                        if self.direction==0:
                            self.animationFrame=24
                        elif self.direction==1:
                            self.animationFrame=5
                else:
                    self.animationTick-=1
            else:#cycle through arm swing animation frames
                if self.animationTick<=0:
                    self.animationTick=2
                    if self.direction==1:
                        if self.animationFrame<3:
                            self.animationFrame+=1
                        else:
                            self.animationFrame=0
                            self.armSwing=False
                    else:
                        if self.animationFrame<22:
                            self.animationFrame+=1
                        else:
                            self.animationFrame=19
                            self.armSwing=False
                else:
                    self.animationTick-=1
                    
    def renderSprites(self):#create an array of surfs for the current character used for animation/blitting
        self.sprites=[]
        for j in range(2):#for both directions
            hair=pygame.Surface((44,48))   
            hair.fill((255,255,255))
            hair.blit(hairStyles[self.model.hairID],(0,0))#create a surf with the given hair and white background
            if j==1:#flip if necessary
                hair=pygame.transform.flip(hair,True,False)
            hair.set_colorkey((255,255,255))#set the colourkey to white
            colour=pygame.Surface((44,48))
            colour.fill(self.model.hairCol)#create a blank surf with the colour of the hair
            hair.blit(colour,(0,0),None,BLEND_RGB_ADD)#blit the new surf to the hair with an add blend flag
            for i in range(19):#all animation frames for one direction
                surf=pygame.Surface((44,75))
                surf.fill((255,0,255))
                surf.set_colorkey((255,0,255))#create the surf for the whole player with a colourkey of (255,0,255)
                if j==0:#if right blit this
                    surf.blit(hairStyles[8],(0,0))
                    surf.blit(hair,(0,0))
                    surf.blit(pygame.transform.flip(torsoFrames[i],True,False),(0,4))
                else:#if left blit this
                    surf.blit(pygame.transform.flip(hairStyles[8],True,False),(0,0))
                    surf.blit(hair,(-4,0))
                    surf.blit(torsoFrames[i],(0,4))
                self.sprites.append(surf)
    def useItem(self,ID,alt=False):
        global mapData, miningTick
        swing=False
        if not alt:
            blockpos=(int((m[0]+clientPlayer.pos[0]-screenW/2)//BLOCKSIZE),int((m[1]+clientPlayer.pos[1]-screenH/2)//BLOCKSIZE))
            blockrect=Rect(BLOCKSIZE*blockpos[0],BLOCKSIZE*blockpos[1]+1,BLOCKSIZE,BLOCKSIZE)
            if not blockrect.colliderect(clientPlayer.rect):
                if shift:
                    if mapData[blockpos[0]][blockpos[1]][1]==-1:
                        if getNeighborCount(blockpos[0],blockpos[1],tile=1)>0:
                            mapData[blockpos[0]][blockpos[1]][1]=ID
                            updateSurface(blockpos[0],blockpos[1])
                            if SFX:
                                playHitSfx(ID)
                            swing=True
                else:
                    if mapData[blockpos[0]][blockpos[1]][0]==-1:
                        if getNeighborCount(blockpos[0],blockpos[1])>0:
                            mapData[blockpos[0]][blockpos[1]][0]=ID
                            updateSurface(blockpos[0],blockpos[1])
                            if SFX:
                                playHitSfx(ID)
                            swing=True

        else:
            if CREATIVE:#delay to destroy another block
                miningTick=0
            else:
                miningTick=10
                
            if shift:datIndex=1#wall or block being clicked
            else:datIndex=0
            
            tile=mapData[int((m[0]+clientPlayer.pos[0]-screenW/2)//BLOCKSIZE)][int((m[1]+clientPlayer.pos[1]-screenH/2)//BLOCKSIZE)][datIndex]
            if tile!=-1:
                if tile==5:
                    mapData[int((m[0]+clientPlayer.pos[0]-screenW/2)//BLOCKSIZE)][int((m[1]+clientPlayer.pos[1]-screenH/2)//BLOCKSIZE)][datIndex]=0
                else:
                    mapData[int((m[0]+clientPlayer.pos[0]-screenW/2)//BLOCKSIZE)][int((m[1]+clientPlayer.pos[1]-screenH/2)//BLOCKSIZE)][datIndex]=-1
                updateSurface(int((m[0]+clientPlayer.pos[0]-screenW/2)//BLOCKSIZE),int((m[1]+clientPlayer.pos[1]-screenH/2)//BLOCKSIZE))
                if tile in platformBlocks:  
                    colour=pygame.transform.average_color(tileImages[tile],Rect(BLOCKSIZE/8,BLOCKSIZE/8,BLOCKSIZE*3/4,BLOCKSIZE/4))
                else:colour=pygame.transform.average_color(tileImages[tile])
                
                if SFX:
                    playHitSfx(tile)
                if PARTICLES:
                    for i in range(int(random.randint(2,3)*PARTICLEDENSITY)):
                        Particle(m,colour,size=10,life=100,angle=-math.pi/2,spread=math.pi,GRAV=0.05)
                swing=True
        if swing:
            if not clientPlayer.armSwing:
                clientPlayer.armSwing=True
                if clientPlayer.direction==0:
                    clientPlayer.animationFrame=20
                else:
                    clientPlayer.animationFrame=1
    def draw(self):#draw player to screen
        if self.alive:
            screen.blit(self.sprites[self.animationFrame],(screenW/2-20,screenH/2-33))
        if hitboxDebug:#show hitbox
            pygame.draw.rect(screen,(255,0,0),self.rect,1)
            
class Particle():
    def __init__(self,pos,colour,life=75,magnitude=2,size=5,angle=None,spread=math.pi/4,GRAV=0.2,vel=None):
        self.pos=pos 
        self.life=life+random.random()*life/10-life/20#how long it lasts for (randomized slightly)
        self.initLife=self.life
        self.colour=colour
        self.size=size+random.random()*size/10-size/20#how large it will be (randomized slightly)
        self.initSize=self.size
        if vel==None:
            if angle==None:
                angle=random.random()*math.pi*2-math.pi#random angle
            else:
                angle+=random.random()*spread-spread/2#set angle + random spread in set range
            self.vel=(math.cos(angle)*magnitude,math.sin(angle)*magnitude)#vel from angle and magnitude
        else:
            self.vel=vel
        self.GRAV=GRAV#gravity
        particles.append(self)
        
    def update(self):
        self.vel=(self.vel[0]*0.95,self.vel[1]*0.95+self.GRAV)
        self.pos=(self.pos[0]+self.vel[0]-clientPlayer.posDiff[0],self.pos[1]+self.vel[1]-clientPlayer.posDiff[1])
        self.life-=1#change life
        self.size=self.initSize*self.life/self.initLife#change size based on life and initial size
        if self.life<=0:#if life<=0 remove the particle
            particles.remove(self)
            
    def draw(self):
        rect=Rect(self.pos[0]-self.size/2,self.pos[1]-self.size/2,self.size,self.size)
        pygame.draw.rect(screen,self.colour,rect,0)#draw 2 rects for each particle (fill and outine)
        pygame.draw.rect(screen,(0,0,0),rect,1)
        
def updateParticles():
    for particle in particles:
        particle.update()
        
def drawParticles():
    for particle in particles:
        particle.draw()
        
def getMaskIndex(name):#returns a random mask index for the given type
    if name=="top_mid":return random.randint(1,3)
    elif name=="left_mid":return int(random.randint(0,2)*13)
    elif name=="bot_mid":return random.randint(27,29)
    elif name=="right_mid":return int(random.randint(0,2)*13)+4
    elif name=="single_vertical_mid":return int(random.randint(0,2)*13)+5
    elif name=="single_horizontal_mid":return random.randint(58,60)
    elif name=="single_vertical_top":return random.randint(6,8)
    elif name=="single_vertical_bot":return random.randint(45,47)
    elif name=="single_horizontal_left":return int(random.randint(0,2)*13)+9
    elif name=="single_horizontal_right":return int(random.randint(0,2)*13)+12
    elif name=="single":return random.randint(48,50)
    elif name=="corner_top_left":return 39+int(random.randint(0,2)*2)
    elif name=="corner_top_right":return 40+int(random.randint(0,2)*2)
    elif name=="corner_bot_left":return 52+int(random.randint(0,2)*2)
    elif name=="corner_bot_right":return 53+int(random.randint(0,2)*2)
    elif name=="mid":return 14
    
def getMaskNameFromIndex(index):#returns the type of a given mask index
    if index==1 or index==2 or index==3:return "top_mid"
    elif index==0 or index==13 or index==26:return "left_mid"
    elif index==27 or index==28 or index==29:return "bot_mid"
    elif index==4 or index==17 or index==30:return "right_mid"
    elif index==5 or index==18 or index==31:return "single_vertical_mid"
    elif index==58 or index==59 or index==60:return "single_horizontal_mid"
    elif index==6 or index==7 or index==8:return "single_vertical_top"
    elif index==45 or index==46 or index==47:return "single_vertical_bot"
    elif index==9 or index==22 or index==35:return "single_horizontal_left"
    elif index==12 or index==25 or index==38:return "single_horizontal_right"
    elif index==48 or index==49 or index==50:return "single"
    elif index==39 or index==41 or index==43:return "corner_top_left"
    elif index==40 or index==42 or index==44:return "corner_top_right"
    elif index==52 or index==54 or index==56:return "corner_bot_left"
    elif index==53 or index==55 or index==57:return "corner_bot_right"
    
def getWallMaskIndexFromPos(i,j,ID):#returns the index of the mask for the wall at a given position
    sameBlocks=[1,1,1,1]
    if i>0:
        if not checkMerge(mapData[i-1][j][1],ID):sameBlocks[2]=0
    if i<MAPSIZEX-1:
        if not checkMerge(mapData[i+1][j][1],ID):sameBlocks[0]=0
    if j>0:
        if not checkMerge(mapData[i][j-1][1],ID):sameBlocks[3]=0
    if j<MAPSIZEY-1:
        if not checkMerge(mapData[i][j+1][1],ID):sameBlocks[1]=0
    return getMaskIndex(getMaskNameFromSurroundingBlocks(sameBlocks))

def getMaskIndexFromPos(i,j,ID):#returns the index of the mask for the block at a given position
    sameBlocks=[1,1,1,1]
    if i>0:
        if not checkMerge(mapData[i-1][j][0],ID):sameBlocks[2]=0
    if i<MAPSIZEX-1:
        if not checkMerge(mapData[i+1][j][0],ID):sameBlocks[0]=0
    if j>0:
        if not checkMerge(mapData[i][j-1][0],ID):sameBlocks[3]=0
    if j<MAPSIZEY-1:
        if not checkMerge(mapData[i][j+1][0],ID):sameBlocks[1]=0
    return getMaskIndex(getMaskNameFromSurroundingBlocks(sameBlocks))

def getMaskNameFromSurroundingBlocks(numArr):#returns the mask type given an array of the surrounding blocks
    if numArr==[0,0,0,0]:return "single"
    elif numArr==[0,0,0,1]:return "single_vertical_bot"
    elif numArr==[0,0,1,0]:return "single_horizontal_right"
    elif numArr==[0,0,1,1]:return "corner_bot_right"
    elif numArr==[0,1,0,0]:return "single_vertical_top"
    elif numArr==[0,1,0,1]:return "single_vertical_mid"
    elif numArr==[0,1,1,0]:return "corner_top_right"
    elif numArr==[0,1,1,1]:return "right_mid"
    elif numArr==[1,0,0,0]:return "single_horizontal_left"
    elif numArr==[1,0,0,1]:return "corner_bot_left"
    elif numArr==[1,0,1,0]:return "single_horizontal_mid"
    elif numArr==[1,0,1,1]:return "bot_mid"
    elif numArr==[1,1,0,0]:return "corner_top_left"
    elif numArr==[1,1,0,1]:return "left_mid"
    elif numArr==[1,0,1,0]:return "single_horizontal_mid"
    elif numArr==[0,1,1,1]:return "left_mid"
    elif numArr==[1,1,1,1]:return "mid"
    elif numArr==[1,1,1,0]:return "top_mid"
    
def createSurface():#creates the main surface
    global mainSurf
    print("Creating Surface...")
    mainSurf=pygame.Surface((MAPSIZEX*BLOCKSIZE,MAPSIZEY*BLOCKSIZE))
    mainSurf.fill((255,0,255))
    mainSurf.set_colorkey((255,0,255))
    for i in range(MAPSIZEX):
        for j in range(MAPSIZEY):
            updateSurface(i,j,affectOthers=False)
            
def updateSurface(i,j,affectOthers=True):
    global mainSurf
    tilesToUpdate=[]
    if affectOthers:
        if i>0:tilesToUpdate.append((i-1,j))
        if i<MAPSIZEX-1:tilesToUpdate.append((i+1,j))
        if j>0:tilesToUpdate.append((i,j-1))
        if j<MAPSIZEY:tilesToUpdate.append((i,j+1))
    tilesToUpdate.append((i,j))
    for tile in tilesToUpdate:
        pygame.draw.rect(mainSurf,(255,0,255),Rect(tile[0]*BLOCKSIZE,tile[1]*BLOCKSIZE,BLOCKSIZE,BLOCKSIZE),0)
        tileDat=mapData[tile[0]][tile[1]]
        if tileDat[0]!=-1:#if there is a block at i,j
            if tileDat[0] in specialBlocks:special=True
            else:special=False
            if tileDat[0] in transparentBlocks:transparent=True
            else:transparent=False
            
            tileMaskData[tile[0]][tile[1]]=getMaskIndexFromPos(tile[0],tile[1],tileDat[0])#get the mask at i,j and store it in the tileMaskData array
                        
            if special:
                tiletex = pygame.Surface((BLOCKSIZE,BLOCKSIZE))
                tiletex.blit(tileImages[tileDat[0]],(0,0))#get the texture of the block at i,j
                tiletex.set_colorkey((255,0,255))
            else:
                tiletex = tileImages[tileDat[0]].copy()
                tiletex.blit(tilemasks[tileMaskData[tile[0]][tile[1]]], (0, 0), None, pygame.BLEND_RGBA_MULT)#blit the block mask to the block texture using a multiply blend flag
                
            if (tileMaskData[tile[0]][tile[1]]!=14 or transparent) and tileDat[1]!=-1:#if the block is not a centre block (and so there is some transparency in it) and there is a wall tile behind it, blit the wall tile
                backimg=wallTileImages[tileDat[1]].copy()#get the wall texture
                wallTileMaskData[tile[0]][tile[1]]=getWallMaskIndexFromPos(tile[0],tile[1],tileDat[1])#get the wall mask
                if getMaskNameFromIndex(wallTileMaskData[tile[0]][tile[1]])==getMaskNameFromIndex(tileMaskData[tile[0]][tile[1]]):#if the mask of the wall and the mask of the tile are from the same type
                    wallTileMaskData[tile[0]][tile[1]]=tileMaskData[tile[0]][tile[1]]#set the wall mask to the tile mask
                backimg.blit(tilemasks[wallTileMaskData[tile[0]][tile[1]]], (0, 0), None, pygame.BLEND_RGBA_MULT)#blit the mask onto the wall texture using a multiply blend flag    
                backimg.blit(tiletex, (0, 0))#blit the masked block texture to the main surface
                mainSurf.blit(backimg, (tile[0]*BLOCKSIZE, tile[1]*BLOCKSIZE))#blit the masked wall surf to the main surf
            else:
                mainSurf.blit(tiletex, (tile[0]*BLOCKSIZE, tile[1]*BLOCKSIZE))#blit the masked wall surf to the main surf
        elif tileDat[1]!=-1:#if there is no block but there is a wall
            backimg=wallTileImages[tileDat[1]].copy()#get the wall texture
            wallTileMaskData[tile[0]][tile[1]]=getWallMaskIndexFromPos(tile[0],tile[1],tileDat[1])#get the wall mask
            backimg.blit(tilemasks[wallTileMaskData[tile[0]][tile[1]]], (0, 0), None, pygame.BLEND_RGBA_MULT)#blit the mask onto the wall texture using a multiply blend flag
            mainSurf.blit(backimg, (tile[0]*BLOCKSIZE, tile[1]*BLOCKSIZE))#blit the masked wall surf to the main surf
            
def playHitSfx(tile):
    if tile ==0 or tile==2 or tile==4 or tile==8 or tile==9 or tile==10 or tile==13:
        sounds[random.randint(3,5)].play()
    elif tile==1 or tile==3 or tile==6 or tile==7:
        sounds[random.randint(0,2)].play()
    elif tile==5 or tile==11 or tile==12:
        sounds[10].play()
        
def generateTerrain(genType):
    global mapData, tileMaskData, wallTileMaskData, backgroundID, worldName, clientWorld
    print("WARNING: Using the same name as an existing world will overwrite it!\n")
    worldName=str(input("Enter new world name: "))
    tileMaskData=[[-1 for i in range(MAPSIZEY)] for i in range(MAPSIZEX)]
    wallTileMaskData=[[-1 for i in range(MAPSIZEY)] for i in range(MAPSIZEX)]
    date=datetime.datetime.now()
    clientWorld=World(worldName,str(str(date)[:19]),genType)
    if genType=="ice caves":
        mapData=[[[-1,0] for i in range(MAPSIZEX)] for j in range(MAPSIZEY)]
        backgroundID=0
        for i in range(MAPSIZEX):
            for j in range(MAPSIZEY):
                val=noise.noise2(i/15+OFFSETS[0],j/15+OFFSETS[0])
                if val>-0.2:
                    val2=noise.noise2(i/15+OFFSETS[1],j/15+OFFSETS[1])
                    if val2>0.4:mapData[i][j][0]=2
                    else:mapData[i][j][0]=3
                else:mapData[i][j][0]=-1
    elif genType=="DEFAULT":
        print("genType: "+genType)
        print("Worldsize: "+str(MAPSIZEX*MAPSIZEY)+" blocks. ("+str(MAPSIZEX)+"x"+str(MAPSIZEY)+")\n")
        print("Generating Terrain...")
        mapData=[]
        backgroundID=3
        for i in range(MAPSIZEX):
            mapData.append([])
            for j in range(MAPSIZEY):
                if i<BIOMEBOARDER_X1+random.randint(-5,5):biome=0
                elif i<BIOMEBOARDER_X2+random.randint(-5,5):biome=1
                else:biome=2
                wval=-1
                if j>350+random.randint(-5,5): # caverns layer 2
                    val=noise.noise2(i/30+OFFSETS[2],j/20+OFFSETS[2])
                    val2=noise.noise2(i/30+OFFSETS[0],j/30+OFFSETS[0])
                    if val>0.55:bval=-1;wval=-1
                    elif val>0.1:bval=-1;wval=int(biomeTileVals[biome][1][1])
                    else:bval=int(biomeTileVals[biome][0][2]);wval=int(biomeTileVals[biome][1][1])
                elif j>250+random.randint(-3,3):# caverns layer 1
                    val=noise.noise2(i/30+OFFSETS[2],j/20+OFFSETS[2])
                    val2=noise.noise2(i/30+OFFSETS[0],j/30+OFFSETS[0])
                    if val>0.5:bval=-1;wval=-1
                    elif val>0.15:bval=-1;wval=int(biomeTileVals[biome][1][1])
                    elif val2>0.5:bval=int(biomeTileVals[biome][0][1]);wval=int(biomeTileVals[biome][1][0])
                    else:bval=int(biomeTileVals[biome][0][2]);wval=int(biomeTileVals[biome][1][1])
                elif j>200+random.randint(-2,2):#tier 2 small caves
                    val=noise.noise2(i/30+OFFSETS[2],j/20+OFFSETS[2])
                    val2=noise.noise2(i/30+OFFSETS[0],j/30+OFFSETS[0])
                    if val>0.3:bval=-1;wval=int(biomeTileVals[biome][1][1])
                    elif val2>0.3:bval=int(biomeTileVals[biome][0][1]);wval=int(biomeTileVals[biome][1][0])
                    else:bval=int(biomeTileVals[biome][0][2]);wval=int(biomeTileVals[biome][1][1])
                elif j>95:#tier 1 small caves
                    val=noise.noise2(i/35+OFFSETS[1],j/25+OFFSETS[1])
                    val2=noise.noise2(i/20+OFFSETS[0],j/20+OFFSETS[0])
                    if val>0.45:bval=-1;wval=int(biomeTileVals[biome][1][0])
                    elif val2>0.1:bval=int(biomeTileVals[biome][0][2])
                    else:bval=int(biomeTileVals[biome][0][1])
                    wval=int(biomeTileVals[biome][1][0])
                else:#surface
                    val=noise.noise2(i/30+OFFSETS[1],j/20+OFFSETS[1])
                    val2=noise.noise2(i/100+OFFSETS[2],0.1)
                    val3=noise.noise2(i/15+OFFSETS[0],j/15+OFFSETS[0])
                    val4=noise.noise2(i/35+OFFSETS[1],j/25+OFFSETS[1])
                    if j>=val*5+60+val2*30:
                        if val4>0.5:bval=-1;wval=int(biomeTileVals[biome][1][0])
                        elif val3>-0.6:bval=bval=int(biomeTileVals[biome][0][1]);wval=int(biomeTileVals[biome][1][0])
                        else:bval=int(biomeTileVals[biome][0][2]);wval=int(biomeTileVals[biome][1][1])
                        if mapData[i][j-1][0]==-1 and bval==int(biomeTileVals[biome][0][1]):bval=int(biomeTileVals[biome][0][0]);wval=int(biomeTileVals[biome][1][0])
                    else:bval=-1
                mapData[i].append([bval,wval])
    print("Spawning ores...")
    for i in range(int(MAPSIZEX*MAPSIZEY/1200)):
        createVein(random.randint(0,MAPSIZEX-1),random.randint(70,500),7,random.randint(2,4))
    for i in range(int(MAPSIZEX*MAPSIZEY/1200)):
        createVein(random.randint(0,MAPSIZEX-1),random.randint(70,500),6,random.randint(2,4))
    print("Growing Trees...")
    for i in range(int(MAPSIZEX/5)):
        if random.randint(1,2)==1:
            createTree(i*5,0,random.randint(5,15))
    makeSpawnPoint()
    print("Generation complete!")
def fadeBackground(ID):
    global fadeBackgroundID, fadeBack, fadeFloat
    fadeBackgroundID=ID
    fadeBack=True
    fadeFloat=0
    
def checkMerge(ID1,ID2):#which blocks should merge with each other
    if ID1==ID2:return True
    if ID1>=68:return True
    if ID1==0:
        if ID2==5:return True
        elif ID2==2:return True
        elif ID2==1:return True
        elif ID2==4:return True
        elif ID2>=68:return True
    elif ID1==1:
        if ID2==0:return True
        elif ID2==2:return True
    elif ID1==2:
        if ID2==0:return True
        elif ID2==1:return True
        elif ID2==3:return True
        elif ID2==4:return True
        elif ID2==8:return True
        elif ID2==9:return True
        elif ID2==10:return True
    elif ID1==3:
        if ID2==2:return True
    elif ID1==4:
        if ID2==0:return True
        elif ID2==2:return True
    elif ID1==5:
        if ID2==0:return True
        if ID2==10:return True
    elif ID1==8:
        if ID2==2:return True
        elif ID2==9:return True
    elif ID1==9:
        if ID2==2:return True
        elif ID2==8:return True
    elif ID1==10:
        if ID2==2:return True
        elif ID2==5:return True
        elif ID2==11:return True
        elif ID2==12:return True
    elif ID1==11:
        if ID2==10:return True
    elif ID1==12:
        if ID2==10:return True
    else:return False
    
def drawDeathMessage():#message shown on death
    font=pygame.font.Font(None,50)
    text=font.render("You Were Slain",False,(255,255,255))
    val=(1-(clientPlayer.respawnTick/500))*500
    if val>255:val=255
    text.set_alpha(val)
    screen.blit(text,(screenW/2-text.get_width()/2,screenH/2))
    
def makeSpawnPoint():#creates and grounds spawn point
    clientWorld.spawnPoint=(BLOCKSIZE*40,BLOCKSIZE*1.5)
    for i in range(300):
        clientWorld.spawnPoint=(clientWorld.spawnPoint[0],clientWorld.spawnPoint[1]+BLOCKSIZE)
        x1=int(clientWorld.spawnPoint[0]-BLOCKSIZE/2)//BLOCKSIZE
        y1=int(clientWorld.spawnPoint[1]+BLOCKSIZE)//BLOCKSIZE
        x2=int(clientWorld.spawnPoint[0]+BLOCKSIZE/2)//BLOCKSIZE
        y2=int(clientWorld.spawnPoint[1]+BLOCKSIZE)//BLOCKSIZE
        if mapData[x1][y1][0] not in uncollidableBlocks or mapData[x2][y2][0] not in uncollidableBlocks:
            clientWorld.spawnPoint=(clientWorld.spawnPoint[0],clientWorld.spawnPoint[1]-BLOCKSIZE*1.5)
            break

def loadSaves(forceWorldGen=False):#loads all possible saves, giving options to load them or create a new save
    global mapData, tileMaskData, wallTileMaskData, backgroundID, worldName, MAPSIZEX, MAPSIZEY, clientWorld
    possibleLoads=os.listdir("Saves")#get filenames
    choice="n"
    if len(possibleLoads)>0:
        for i in range(len(possibleLoads)):
            if possibleLoads[i][-3:]=="dat":#if it's a dat file
                dat=pickle.load(open("Saves/"+possibleLoads[i],"rb"))
                possibleLoads[i]=possibleLoads[i][:-4]
                string="Slot "+str(math.ceil((i+1)/2))+": Name: "+dat.name+", created: "+dat.creationDate+", playtime: "+str(int((dat.playTime/60)//60))+":"+str(int(dat.playTime//60%60)).zfill(2)+":"+str(int(dat.playTime%60)).zfill(2)
                print(string)
        choice=str(input("\nWhich slot do you want to load? (slot number or 'n' to create a new save)\n"))
    if choice=="n":
        forceWorldGen=True
        
    if not forceWorldGen:
        mapData=pickle.load(open("Saves/"+possibleLoads[int((int(choice)-1)*2)]+".wrld","rb"))#open selected save wrld file
        clientWorld=pickle.load(open("Saves/"+possibleLoads[int((int(choice)-1)*2)]+".dat","rb"))#open selected save dat file
        MAPSIZEX,MAPSIZEY=len(mapData),len(mapData[0])
        tileMaskData=[[-1 for i in range(MAPSIZEY)] for i in range(MAPSIZEX)]
        wallTileMaskData=[[-1 for i in range(MAPSIZEY)] for i in range(MAPSIZEX)]
        backgroundID=3
        worldName=clientWorld.name
        print(worldName+" successfully loaded!")
    else:generateTerrain("DEFAULT")
    
class World():
    def __init__(self,name,creationDate,size):
        self.name=name
        self.creationDate=creationDate
        self.size=size
        self.playTime=0
        self.spawnPoint=(0,0)
        
def Exit():
    Save()
    pygame.quit()
    print("\nRunning slowly? try turning off the particles, \nbackground or lowering the resolution")
    sys.exit()
    
    
def Save():
    pickle.dump(mapData,open("Saves/"+str(worldName)+".wrld","wb"))#save wrld
    pickle.dump(clientWorld,open("Saves/"+str(worldName)+".dat","wb"))#save dat
    print("Saved!")
    
def createVein(i,j,val,size):
    try:
        if mapData[i][j][0]!=-1 and mapData[i][j][0]!=val and size>0:
            if random.randint(1,10)==1:size+=1
            mapData[i][j][0]=val
            createVein(i-1,j,val,size-1)
            createVein(i+1,j,val,size-1)
            createVein(i,j-1,val,size-1)
            createVein(i,j+1,val,size-1)
        else:return
    except:None
    
def createTree(i,j,height):
    global mapData
    grounded=False
    for k in range(MAPSIZEY-j-1):
        val=mapData[i][j+1][0]
        if val==5 or val==2:
            block1=10
            if val==5:block2=11
            if val==2:block2=12
            grounded=True
            break
        if val !=-1:break
        j+=1
    if not grounded:return
    if mapData[i-1][j+1][0]==5 or mapData[i-1][j+1][0]==2:mapData[i-1][j][0]=int(block1)
    if mapData[i+1][j+1][0]==5 or mapData[i+1][j+1][0]==2:mapData[i+1][j][0]=int(block1)
    h=int(height)
    for k in range(height):
        mapData[i][j][0]=int(block1)
        if h>2 and h<height-1:
            if random.randint(1,5)==1:
                if random.randint(0,1)==0:
                    mapData[i-1][j][0]=int(block2)
                else:
                    mapData[i+1][j][0]=int(block2)
        h-=1
        j-=1
    #create canopy
    for k in range(-1,2):
        mapData[i+k][j-2][0]=int(block2)
    for k in range(-2,3):
        mapData[i+k][j-1][0]=int(block2)
    for k in range(-2,3):
        mapData[i+k][j][0]=int(block2)
    mapData[i-1][j+1][0]=int(block2)
    mapData[i+1][j+1][0]=int(block2)
    
def loadConfig():#get all settings from config file
    global MAPSIZEX, MAPSIZEY, GRAVITY, screenW, screenH, RUNFULLSCREEN, PARTICLES, PARTICLEDENSITY, MUSIC, SFX, CREATIVE, BACKGROUND, PARALLAXAMNT
    config=open("CONFIG.txt","r")
    configDataStr=config.readlines()
    configData=[]
    for item in configDataStr:
        item=item.split("=")
        configData.append(item[1][:-1])
    screenW=int(configData[0].split(",")[0])
    screenH=int(configData[0].split(",")[1])
    MAPSIZEX=int(configData[1].split(",")[0])
    MAPSIZEY=int(configData[1].split(",")[1])
    GRAVITY=float(configData[2])
    RUNFULLSCREEN=bool(int(configData[3]))
    PARTICLES=bool(int(configData[4]))
    PARTICLEDENSITY=float(configData[5])
    MUSIC=bool(int(configData[6]))
    SFX=bool(int(configData[7]))
    CREATIVE=bool(int(configData[8]))
    BACKGROUND=bool(int(configData[9]))
    PARALLAXAMNT=float(configData[10])

def changeBackground():#check if player has moved biome and change background
    global backgroundTick
    if backgroundTick<=0:#every 100 ticks is checks again
        backgroundTick=100
        if clientPlayer.pos[1]>200*BLOCKSIZE:
            if clientPlayer.pos[0]>BIOMEBOARDER_X1*BLOCKSIZE and clientPlayer.pos[0]<BIOMEBOARDER_X2*BLOCKSIZE:
                if fadeBackgroundID!=0:
                    fadeBackground(0)
            else:
                if fadeBackgroundID!=2:
                    fadeBackground(2)
            backgroundScrollVel=0
        elif clientPlayer.pos[1]>110*BLOCKSIZE:
            if clientPlayer.pos[0]>BIOMEBOARDER_X1*BLOCKSIZE and clientPlayer.pos[0]<BIOMEBOARDER_X2*BLOCKSIZE:
                if fadeBackgroundID!=0:
                    fadeBackground(0)
            else:
                if fadeBackgroundID!=1:
                    fadeBackground(1)
            backgroundScrollVel=0
        else:
            if fadeBackgroundID!=3:
                fadeBackground(3)
            backgroundScrollVel=0.1
    else:
        backgroundTick-=1
def renderHandText():
    global handText
    handText=inventoryFont.render("Hand: "+itemData[blockInHand][0],True,(255,0,0))
def renderHpText():
    global hpText
    hpText=inventoryFont.render("HP: "+str(clientPlayer.HP),True,(255,0,0))
def getNeighborCount(i,j,tile=0):#used to work out if a block can be placed at a position based on neighbors
    if CREATIVE:return 1
    neighborCount=0
    if mapData[i-1][j][tile]!=-1:neighborCount+=1
    if mapData[i+1][j][tile]!=-1:neighborCount+=1
    if mapData[i][j-1][tile]!=-1:neighborCount+=1
    if mapData[i][j+1][tile]!=-1:neighborCount+=1  
    if mapData[i][j][1]!=-1:neighborCount+=1
    if mapData[i][j][0]!=-1:neighborCount+=1
    return neighborCount
    
noise=perlin.SimplexNoise()#create noise object
OFFSETS=[random.random()*1000,random.random()*1000,random.random()*1000]#randomly generate offsets

biomeTileVals=[[[5,0,1],[0,1]],[[2,2,3],[2,2]],[[8,8,9],[8,9]]]#tiles used in biome generation eg: [[surface tile,base tile, alt tile],[wall tile, alt wall tile]]

uncollidableBlocks=[-1,10,11,12]#blocks voided in collisions
specialBlocks=[13]#blocks drawn without masks
transparentBlocks=[13]#blocks that always have background/walls drawn behind them
platformBlocks=[13]#platforms

itemData=[["Dirt"],
          ["Stone"],
          ["Snow"],
          ["Ice"],
          ["Wood"],
          ["Grass"],
          ["Copper"],
          ["Silver"],
          ["Sand"],
          ["Sandstone"],
          ["Trunk"],
          ["Leaves"],
          ["Snow Leaves"],
          ["Platform"],
          ]#info on tiles

particles=[]

#MAX SURF WIDTH IS 16383

loadConfig()#(1920,1080),(1280, 720), (1152, 864), (1024, 768), (800, 600)
BLOCKSIZE=16
BIOMEBOARDER_X1=MAPSIZEX/3
BIOMEBOARDER_X2=MAPSIZEX*2/3

WORLDBOARDER_WEST=int(BLOCKSIZE)
WORLDBOARDER_EAST=int(MAPSIZEX*BLOCKSIZE-BLOCKSIZE)
WORLDBOARDER_NORTH=int(BLOCKSIZE*1.5)
WORLDBOARDER_SOUTH=int(MAPSIZEY*BLOCKSIZE-BLOCKSIZE*1.5)

loadSaves()

VERSION="0.0.2"

if RUNFULLSCREEN:screen=pygame.display.set_mode((screenW,screenH),FULLSCREEN)
else:screen=pygame.display.set_mode((screenW,screenH))

pygame.display.set_caption("fegaria remastered "+VERSION)

pygame.mixer.pre_init(48000, -16, 2, 1024)
pygame.init()
musicVolume=0.2
if MUSIC:
    pygame.mixer.music.load("Sound/day.mp3")
    pygame.mixer.music.set_volume(musicVolume)
    pygame.mixer.music.play()
    


playerWidth=26
playerHeight=48
if SFX:
    sounds=[]
    sounds.append(pygame.mixer.Sound("Sound/Tink_0.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Tink_1.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Tink_2.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Dig_0.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Dig_1.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Dig_2.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Jump_0.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Player_Hit_0.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Player_Hit_1.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Player_Hit_2.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Grass.wav"))
    sounds.append(pygame.mixer.Sound("Sound/Player_Killed.wav"))

hitboxDebug=False
blockInHand=13

parallaxPos=(0,0)
loadTorsoFrames()
loadHairStyles() 
loadTileMasks()
loadTiles()
loadBackgroundImages()
compileBackgroundImages()
loadWallTiles()

createSurface()

clock=pygame.time.Clock()
        
defaultModel=Model(0,random.randint(0,7),(random.randint(0,128),random.randint(0,128),random.randint(0,128)),(0,0,200),(),(),(),())
clientPlayer=Player(clientWorld.spawnPoint,defaultModel)

fadeBack=False
shift=False
fadeFloat=0
fadeBackgroundID=-1
miningTick=0
backgroundTick=0
backgroundScrollVel=0
autoSaveTick=0
autoSaveDelay=3600#every minute
gameAge=0

inventoryFont=pygame.font.Font(None,20)
renderHandText()
renderHpText()
while 1:
    fps=clock.get_fps()
    try:
        clientWorld.playTime+=1/fps
        gameAge+=1/fps
    except:None#fps is zero
    m=pygame.mouse.get_pos()
    
    updateParticles()
    clientPlayer.update()
    clientPlayer.animate()
        
    if BACKGROUND:
        if fadeBack:
            if fadeFloat<1:
                fadeSurf=backsurfs[fadeBackgroundID].copy()
                fadeSurf.set_alpha(fadeFloat*255)
                fadeFloat+=0.1
            else:
                fadeBack=False
                backgroundID=int(fadeBackgroundID)
        screen.blit(backsurfs[backgroundID],parallaxPos)
        if fadeBack:
            screen.blit(fadeSurf,parallaxPos)
    else:
        screen.fill((135,206,250))
    screen.blit(mainSurf,(screenW/2-clientPlayer.pos[0],screenH/2-clientPlayer.pos[1]))
    
    clientPlayer.draw()
    drawParticles()
    screen.blit(handText,(0,0))
    screen.blit(hpText,(0,20))
    if BACKGROUND:
        changeBackground()
        moveParallax((backgroundScrollVel,0))
        
    if autoSaveTick<=0:
        autoSaveTick=autoSaveDelay
        Save()
    else:autoSaveTick-=1
    
    if clientPlayer.alive:
        if miningTick<=0:
            if pygame.mouse.get_pressed()[0]:
                clientPlayer.useItem(blockInHand)
            elif pygame.mouse.get_pressed()[2]:
                clientPlayer.useItem(blockInHand,alt=True)
        else:
            miningTick-=1
    else:
        drawDeathMessage()
    
    for event in pygame.event.get():
        if event.type==QUIT:
            Exit()      
        if event.type==KEYDOWN:
            if event.key==K_LSHIFT:
                shift=True
            if event.key==K_ESCAPE:
                Exit()
            if event.key==K_a:
                clientPlayer.movingLeft=True
                clientPlayer.animationFrame=random.randint(25,36)
                clientPlayer.direction=0
            if event.key==K_d:
                clientPlayer.movingRight=True
                clientPlayer.animationFrame=random.randint(5,17)
                clientPlayer.direction=1
            if pygame.key.get_mods() & KMOD_LSHIFT:
                if event.key==K_s:
                    clientWorld.spawnPoint=tuple(clientPlayer.pos)
                    print("Spawn point moved to "+str(clientWorld.spawnPoint))
            if event.key==K_s:
                clientPlayer.movingDown=True
                clientPlayer.animationSpeed=4
            if event.key==K_SPACE:
                if clientPlayer.alive:
                    if clientPlayer.grounded:
                        if SFX:
                            sounds[6].play()
                        if PARTICLES:
                            if clientPlayer.lastBlockOn in platformBlocks:  
                                colour=pygame.transform.average_color(tileImages[clientPlayer.lastBlockOn],Rect(BLOCKSIZE/8,BLOCKSIZE/8,BLOCKSIZE*3/4,BLOCKSIZE/4))
                            else:colour=pygame.transform.average_color(tileImages[clientPlayer.lastBlockOn])
                            
                            for i in range(int(random.randint(4,6)*PARTICLEDENSITY)):
                                Particle((screenW/2,screenH/2+BLOCKSIZE*1.5),colour,size=10,life=100,angle=-math.pi/2,spread=math.pi/4,GRAV=0,magnitude=1+random.random()*3)
                        clientPlayer.vel=(clientPlayer.vel[0],-8.5)
                        clientPlayer.grounded=False
            if event.key==K_r:
                clientPlayer.model.hairCol=(random.randint(0,128),random.randint(0,128),random.randint(0,128))
                clientPlayer.model.hairID=random.randint(0,7)
                clientPlayer.renderSprites()
            if event.key==K_j:
                clientPlayer.respawn()
            if event.key==K_g:
                GRAVITY=-GRAVITY;print("Gravity Reversed")
                
##            if event.key==K_KP0:backgroundID=0
##            if event.key==K_KP1:backgroundID=1
##            if event.key==K_KP2:backgroundID=2
##            
            if event.key==K_1:blockInHand=0;print("Hand: Dirt");renderHandText()
            if event.key==K_2:blockInHand=1;print("Hand: Stone");renderHandText()
            if event.key==K_3:blockInHand=2;print("Hand: Snow");renderHandText()
            if event.key==K_4:blockInHand=3;print("Hand: Ice");renderHandText()
            if event.key==K_5:blockInHand=4;print("Hand: Wood");renderHandText()
            if event.key==K_6:blockInHand=5;print("Hand: Grass");renderHandText()
            if event.key==K_7:blockInHand=6;print("Hand: Copper");renderHandText()
            if event.key==K_8:blockInHand=7;print("Hand: Silver");renderHandText()
            if event.key==K_9:blockInHand=8;print("Hand: Sand");renderHandText()
            if event.key==K_0:blockInHand=13;print("Hand: Platform");renderHandText()

            if event.key==K_UP and shift:
                musicVolume+=0.05
                if musicVolume>1:musicVolume=1
                pygame.mixer.music.set_volume(musicVolume)
            if event.key==K_DOWN and shift:
                musicVolume-=0.05
                if musicVolume<0:musicVolume=0
                pygame.mixer.music.set_volume(musicVolume)
##            if event.key==K_a:blockInHand=74
##            if event.key==K_b:blockInHand=75
##            if event.key==K_c:blockInHand=76
##            if event.key==K_d:blockInHand=77
##            if event.key==K_e:blockInHand=78
##            if event.key==K_f:blockInHand=79
##            if event.key==K_g:blockInHand=80
##            if event.key==K_h:blockInHand=81
##            if event.key==K_i:blockInHand=82
##            if event.key==K_j:blockInHand=83
##            if event.key==K_k:blockInHand=84
##            if event.key==K_l:blockInHand=85
##            if event.key==K_m:blockInHand=86
##            if event.key==K_n:blockInHand=87
##            if event.key==K_o:blockInHand=88
##            if event.key==K_p:blockInHand=89
##            if event.key==K_q:blockInHand=90
##            if event.key==K_r:blockInHand=91
##            if event.key==K_s:blockInHand=92
##            if event.key==K_t:blockInHand=93
##            if event.key==K_u:blockInHand=94
##            if event.key==K_v:blockInHand=95
##            if event.key==K_w:blockInHand=96
##            if event.key==K_x:blockInHand=97
##            if event.key==K_y:blockInHand=98
##            if event.key==K_z:blockInHand=99
##            if event.key==K_SLASH:blockInHand=73
##            if event.key==K_1:blockInHand=72
##            if event.key==K_PERIOD:blockInHand=71
##            if event.key==K_COMMA:blockInHand=70
##            if event.key==K_RIGHTBRACKET:blockInHand=68
##            if event.key==K_LEFTBRACKET:blockInHand=69
            
        if event.type==KEYUP:
            if event.key==K_a:
                clientPlayer.movingLeft=False
            if event.key==K_d:
                clientPlayer.movingRight=False
            if event.key==K_s:
                clientPlayer.movingDownTick=5
                clientPlayer.stopMovingDown=True
                clientPlayer.animationSpeed=1
            if event.key==K_LSHIFT:
                shift=False
    pygame.display.flip()
    clock.tick(80)
