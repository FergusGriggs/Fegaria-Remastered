#fegaria remastered
__author__="Fergus Griggs"
__email__="fbob987 at gmail dot com"
__version__="0.0.5"


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
def loadMiscGui():
    global miscGuiImages
    miscGuiImages=[]
    miscTilesetimg=pygame.image.load("Textures/miscTileset.png").convert()
    for j in range(1):
        for i in range(1):
            surf=pygame.Surface((48,48))
            surf.set_colorkey((255,0,255))
            surf.blit(miscTilesetimg,(-i*48,-j*48))
            miscGuiImages.append(surf)
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

def loadProjectileImages():
    global projectileImages
    projectileimg=pygame.image.load("Textures/projectileTileset.png").convert()
    projectileImages=[]
    for j in range(10):
        for i in range(10):
            surf=pygame.Surface((16,16))
            surf.blit(projectileimg,(-i*16,-j*16))
            surf.set_colorkey((255,0,255))
            projectileImages.append(surf)

def loadItemTiles():
    global itemImages
    itemimg=pygame.image.load("Textures/itemTileset.png").convert()
    itemImages=[]
    for j in range(10):
        for i in range(10):
            surf=pygame.Surface((16,16))
            surf.blit(itemimg,(-16*i,-16*j))
            surf2=pygame.Surface((24,24))
            surf2.fill((255,0,255))
            surf2.set_colorkey((255,0,255))
            surf2.blit(surf,(4,4))
            surf2=pygame.transform.scale(surf2,(48,48))
            itemImages.append(surf2)
            
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
def loadSlimeFrames():
    global slimeFrames
    slimeFrames=[]
    scale=2
    img=pygame.transform.scale(pygame.image.load("Textures/slimeTileset.png"),(int(16*3*scale),int(12*5*scale)))
    for j in range(5):
        for i in range(3):
            surf=pygame.Surface((int(16*scale),int(12*scale)))
            surf.set_colorkey((255,0,255))
            surf.blit(img,(-i*16*scale,-j*12*scale))
            surf.set_alpha(200)
            slimeFrames.append(surf)
        
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

class Enemy():
    def __init__(self,pos,enemyID):
        self.pos=pos
        self.vel=(0,0)
        self.ID=enemyID
        self.name=str(enemyData[self.ID][0])
        self.type=str(enemyData[self.ID][1])
        self.HP=int(enemyData[self.ID][2])
        self.maxHP=int(self.HP)
        self.defense=int(enemyData[self.ID][3])
        self.knockBackResist=int(enemyData[self.ID][4])
        self.attackDamage=int(enemyData[self.ID][5])
        self.bloodColour=tuple(enemyData[self.ID][6])
        self.rect=Rect(self.pos[0]-BLOCKSIZE,self.pos[1]-BLOCKSIZE/1.5,BLOCKSIZE*2,BLOCKSIZE*1.5)
        self.grounded=False
        self.stopLeft=False
        self.stopRight=False
        self.movingLeft=False
        self.movingRight=False
        self.damageTick=0
        self.jumpTick=100
        self.despawnTick=0
        self.animationFrame=0
        self.gameID=random.randint(1000,9999)
        enemies.append(self)
    def update(self):
        self.stopLeft=False
        self.stopRight=False
        if self.despawnTick<=0:
            self.despawnTick=100
            self.checkDespawn()
        else:self.despawnTick-=1
        if self.movingLeft:#moves player left
            if not self.stopLeft:
                self.vel=(-3,self.vel[1])
        if self.movingRight:#moves player right
            if not self.stopRight:
                self.vel=(3,self.vel[1])
        if not self.grounded:
            self.vel=(self.vel[0],self.vel[1]+GRAVITY)
        self.runAI()
        self.vel=(self.vel[0]*0.95,self.vel[1]*0.95)
        self.pos=(self.pos[0]+self.vel[0],self.pos[1]+self.vel[1])
        self.rect.left=self.pos[0]-self.rect.width/2#updating rect
        self.rect.top=self.pos[1]-self.rect.height/2
        self.blockpos=(math.floor(self.pos[1]//BLOCKSIZE),math.floor(self.pos[0]//BLOCKSIZE))
        self.grounded=False
        
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
                    
        if self.damageTick<=0:
            if clientPlayer.rect.colliderect(self.rect):
                if clientPlayer.pos[0]<self.pos[0]:
                    direction=-1
                else:direction=1
                clientPlayer.damage(self.attackDamage,["enemy",self.name],knockBack=10,direction=direction)
                self.damageTick=100
        else:self.damageTick-=1
        for j in range(-2,3):
            for i in range(-2,3):
                try:
                    val=mapData[self.blockpos[1]+j][self.blockpos[0]+i][0]
                    if val not in uncollidableBlocks:
                        blockrect=Rect(BLOCKSIZE*(self.blockpos[1]+j),BLOCKSIZE*(self.blockpos[0]+i),BLOCKSIZE,BLOCKSIZE) 
                        if val in platformBlocks:platform=True
                        else:platform=False
                        if blockrect.colliderect(int(self.rect.left-1),int(self.rect.top+2),1,int(self.rect.height-4)):self.stopLeft=True#is there a solid block left
                        if blockrect.colliderect(int(self.rect.right+1),int(self.rect.top+2),1,int(self.rect.height-4)):self.stopRight=True#is there a solid block right
                        if blockrect.colliderect(self.rect):
                            deltaX = self.pos[0]-blockrect.centerx
                            deltaY = self.pos[1]-blockrect.centery
                            if abs(deltaX) > abs(deltaY):
                                if deltaX > 0:
                                    if not platform:
                                        self.pos=(blockrect.right+self.rect.width/2,self.pos[1])#move enemy right
                                        self.vel=(0,self.vel[1])#stop enemy horizontally
                                else:
                                    if not platform:
                                        self.pos=(blockrect.left-self.rect.width/2,self.pos[1])#move enemy left
                                        self.vel=(0,self.vel[1])#stop enemy horizontally
                            else:
                                if deltaY > 0:
                                    if self.vel[1]<0:
                                        if not platform:
                                            if Rect(self.rect.left+3,self.rect.top,self.rect.width-6,self.rect.height).colliderect(blockrect):
                                                self.pos=(self.pos[0],blockrect.bottom+self.rect.height/2)#move enemy down
                                                self.vel=(self.vel[0],0)#stop enemy vertically
                                else:
                                    if self.vel[1]>0:
                                        if Rect(self.rect.left+3,self.rect.top,self.rect.width-6,self.rect.height).colliderect(blockrect):
                                            self.pos=(self.pos[0],blockrect.top-self.rect.height/2+1)#move enemy up
                                            self.vel=(self.vel[0]*0.5,0)#slow down enemy horizontally and stop player vertically
                                            self.grounded=True
                                            self.movingRight=False
                                            self.movingLeft=False
                except:None
        self.animate()
    def damage(self,val,knockBack=0,direction=0,crit=False):
        self.movingRight=False
        self.movingLeft=False
        val-=self.defense
        val+=random.randint(-1,1)
        if val<1:val=1
        if crit:val*=2
        self.HP-=val
        if self.HP<0:self.HP=0
        if knockBack!=0:
            valx=knockBack*(1-self.knockBackResist)
            valy=-3*(1-self.knockBackResist)
            self.vel=(direction*valx,valy)
        damageNumber(self.pos,val,crit=crit)
        if self.HP>0:#check if the enemy has died from damage
            if SFX:
                sounds[13].play()
            if PARTICLES:
                for i in range(int(5*PARTICLEDENSITY)):#blood
                    Particle((self.pos[0]-clientPlayer.pos[0]+screenW/2,self.pos[1]-clientPlayer.pos[1]+screenH/2),self.bloodColour,life=100,GRAV=0.02,angle=-math.pi/2,spread=math.pi,magnitude=random.random()*2)
        else:
            self.kill()
            
    def kill(self):
        coinRange=enemyData[self.ID][8]
        coinDrops=coinsFromVal(random.randint(coinRange[0],coinRange[1]))
        for i in range(len(coinDrops)):
            if coinDrops[i]>0:
                PhysicsItem(self.pos,24-i,amnt=coinDrops[i],pickupDelay=0)
        if PARTICLES:
            for i in range(int(25*PARTICLEDENSITY)):#more blood
                Particle((self.pos[0]-clientPlayer.pos[0]+screenW/2,self.pos[1]-clientPlayer.pos[1]+screenH/2),self.bloodColour,life=100,GRAV=0.02,angle=-math.pi/2,spread=math.pi,magnitude=random.random()*4)
        if SFX:
            sounds[14].play()#death sound
        enemies.remove(self)
                
    def animate(self):
        if not self.grounded:
            if self.vel[1]>2:
                self.animationFrame=2
            elif self.vel[1]<-2:
                self.animationFrame=1
            else:
                self.animationFrame=0
        else:
            self.animationFrame=0
    def checkDespawn(self):
        if self.pos[0]<clientPlayer.pos[0]-screenW:enemies.remove(self)
        elif self.pos[0]>clientPlayer.pos[0]+screenW:enemies.remove(self)
        elif self.pos[1]<clientPlayer.pos[1]-screenH:enemies.remove(self)
        elif self.pos[1]>clientPlayer.pos[1]+screenH:enemies.remove(self)
        
    def draw(self):
        left=self.rect.left-clientPlayer.pos[0]+screenW/2
        top=self.rect.top-clientPlayer.pos[1]+screenH/2
        screen.blit(slimeFrames[self.ID*3+self.animationFrame],(left,top))
        if self.HP<self.maxHP:
            hpFloat=self.HP/self.maxHP
            col=(255*(1-hpFloat),255*hpFloat,0)
            pygame.draw.rect(screen,darkenCol(col),Rect(left,top+30,self.rect.width,10),0)
            pygame.draw.rect(screen,col,Rect(left+2,top+32,(self.rect.width-4)*hpFloat,6),0)
        if HITBOXES:
            pygame.draw.rect(screen,(255,0,0),Rect(self.rect.left-clientPlayer.pos[0]+screenW/2,self.rect.top-clientPlayer.pos[1]+screenH/2,self.rect.width,self.rect.height),1)
            
    def runAI(self):
        if self.type=="Slime":
            if self.grounded:
                if self.jumpTick<=0:
                    self.jumpTick=random.randint(40,50)
                    if clientPlayer.pos[0]<self.pos[0]:
                        if clientPlayer.alive:
                            self.vel=(-3,-8.5+random.random())
                            self.movingLeft=True
                        else:
                            self.vel=(3,-8.5+random.random())
                            self.movingRight=True
                    else:
                        if clientPlayer.alive:
                            self.vel=(3,-8.5+random.random())
                            self.movingRight=True
                        else:
                            self.vel=(-3,-8.5+random.random())
                            self.movingLeft=True
                else:
                    self.jumpTick-=1
def updateEnemies():
    for enemy in enemies:
        enemy.update()
        
def drawEnemies():
    for enemy in enemies:
        enemy.draw()
def coinsFromVal(val):
    coins=[0,0,0,0]
    coins[0] = val//1000000
    val-=coins[0]*1000000
    coins[1] = val//10000
    val-=coins[1]*10000
    coins[2] = val//100
    val-=coins[2]*100
    coins[3] = val
    return coins
    
class Player():#stores all info about a player
    def __init__(self,pos,model,name="unassigned",HP=100,maxHP=100,hotbar=None,inventory=None,playTime=0,creationDate=None):
        self.pos=pos
        self.oldpos=pos
        self.rect=Rect(self.pos[0]-playerWidth/2,self.pos[1]-playerHeight/2,playerWidth,playerHeight)#hitbox
        self.vel=(0,0)
        
        self.model=model#model class
        self.name=name
        if creationDate==None: 
            date=datetime.datetime.now()
            self.creationDate=str(str(date)[:19])
        else:self.creationDate=creationDate
        if hotbar==None:self.hotbar=[Item(25),Item(15),Item(19),Item(17),Item(0,amnt=100),Item(1,amnt=100),Item(2,amnt=100),Item(3,amnt=100),Item(4,amnt=100),Item(13,amnt=100)]
        else:self.hotbar=hotbar
        if inventory==None:self.inventory=[[None for i in range(4)]for j in range(10)]
        else:self.inventory=inventory
        self.miningTick=0
        self.playTime=playTime
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
        self.knockBackResist=0
        self.defense=0
        self.hotbarIndex=0
        self.useTick=0
        self.canUse=False
        self.armHold=False
        self.holdAngle=0
        self.currentItemImage=None
        self.swingAngle=0
        self.itemSwing=False
        self.enemiesHit=[]
        self.unPickupableItems=[]
        self.hotbarImage=pygame.Surface((480,48));self.hotbarImage.set_colorkey((255,0,255))
        self.inventoryImage=pygame.Surface((480,192));self.inventoryImage.set_colorkey((255,0,255))
        self.inventoryOpen=False
        self.oldInventoryPositions=[]
        self.posDiff=(0,0)
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
            
            if not self.canUse:
                if self.useTick<=0:
                    self.armHold=False
                    self.canUse=True
                else:self.useTick-=1
            
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

            if self.miningTick<=0:
                use=False
                if clientPlayer.inventoryOpen:
                    if not Rect(5,5,480,244).collidepoint(m):
                        use=True
                else:use=True
                if use:
                    if pygame.mouse.get_pressed()[0]:
                        self.useItem()
                    elif pygame.mouse.get_pressed()[2]:
                        self.useItem(alt=True)
            else:
                self.miningTick-=1
                
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
                                                            self.damage(damage,["falling","World"])#apply fall damage once
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
        self.updateInventoryOldSlots()
    def damage(self,val,source,knockBack=0,direction=None):
        if not CREATIVE and self.alive:
            val-=self.defense
            val+=random.randint(-1,1)
            if val<1:
                val=1
            self.HP-=val
            damageNumber(self.pos,val,colour=(240,20,20))
            if self.HP<0:self.HP=0
            if knockBack!=0:
                valx=knockBack*(1-self.knockBackResist)
                valy=-3*(1-self.knockBackResist)
                self.vel=(direction*valx,valy)
            if self.HP>0:#check if the player has died from damage
                if SFX:
                    sounds[random.randint(7,9)].play()#random hurt sound
                if PARTICLES:
                    for i in range(int(5*PARTICLEDENSITY)):#blood
                        Particle((screenW/2,screenH/2),(230,0,0),life=100,GRAV=0.02,angle=-math.pi/2,spread=math.pi,magnitude=random.random()*2)
            else:
                self.kill(source)
            
    def kill(self,source):
        if self.alive:
            message(getDeathMessage(clientPlayer.name,source),(255,255,255))
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
        self.HP=int(self.maxHP)#reset hp
    def renderCurrentItemImage(self):
        item=self.hotbar[self.hotbarIndex]
        if item!=None:
            self.currentItemImage=itemImages[item.ID].copy()
            scale=item.size/itemData[item.ID][4][3]
            self.currentItemImage=pygame.transform.scale(self.currentItemImage,(int(self.currentItemImage.get_width()*scale),int(self.currentItemImage.get_height()*scale)))
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
                    self.animationTick-=0.5
                    
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
    def useItem(self,alt=False):
        global mapData
        swing=False
        item=self.hotbar[self.hotbarIndex]
        if item!=None:
            if "block" in item.tags:
                if math.sqrt((screenW/2-m[0])**2+(screenH/2-m[1])**2)<BLOCKSIZE*6 or CREATIVE:
                    blockpos=(int((m[0]+clientPlayer.pos[0]-screenW/2)//BLOCKSIZE),int((m[1]+clientPlayer.pos[1]-screenH/2)//BLOCKSIZE))
                    blockrect=Rect(BLOCKSIZE*blockpos[0],BLOCKSIZE*blockpos[1]+1,BLOCKSIZE,BLOCKSIZE)
                    if not blockrect.colliderect(clientPlayer.rect):
                        if shift:
                            if mapData[blockpos[0]][blockpos[1]][1]==-1:
                                if getNeighborCount(blockpos[0],blockpos[1],tile=1)>0:
                                    if not CREATIVE:
                                        self.hotbar[self.hotbarIndex].amnt-=1
                                        dat=["H",self.hotbarIndex]
                                        if dat not in self.oldInventoryPositions:
                                            self.oldInventoryPositions.append(dat)
                                        if self.hotbar[self.hotbarIndex].amnt<=0:
                                            self.hotbar[self.hotbarIndex]=None
                                    mapData[blockpos[0]][blockpos[1]][1]=item.ID
                                    updateSurface(blockpos[0],blockpos[1])
                                    if SFX:
                                        playHitSfx(item.ID)
                                    swing=True
                        else:
                            if mapData[blockpos[0]][blockpos[1]][0]==-1:
                                if getNeighborCount(blockpos[0],blockpos[1])>0:
                                    if not CREATIVE:
                                        self.hotbar[self.hotbarIndex].amnt-=1
                                        dat=["H",self.hotbarIndex]
                                        if dat not in self.oldInventoryPositions:
                                            self.oldInventoryPositions.append(dat)
                                        if self.hotbar[self.hotbarIndex].amnt<=0:
                                            self.hotbar[self.hotbarIndex]=None
                                    mapData[blockpos[0]][blockpos[1]][0]=item.ID
                                    updateSurface(blockpos[0],blockpos[1])
                                    if SFX:
                                        playHitSfx(item.ID)
                                    swing=True

            elif "pickaxe" in item.tags:
                if self.canUse and math.sqrt((screenW/2-m[0])**2+(screenH/2-m[1])**2)<BLOCKSIZE*6 or CREATIVE:
                    self.enemiesHit=[]
                    self.canUse=False
                    self.useTick=int(item.attackSpeed)
                    swing=True
                    self.itemSwing=True
                    if self.direction==1:self.swingAngle=10
                    else:self.swingAngle=65
                    
                    if shift:datIndex=1#wall or block being clicked
                    else:datIndex=0
                    blockpos=(int((m[0]+clientPlayer.pos[0]-screenW/2)//BLOCKSIZE),int((m[1]+clientPlayer.pos[1]-screenH/2)//BLOCKSIZE))
                    tile=mapData[blockpos[0]][blockpos[1]][datIndex]
                    if tile!=-1:
                        if tile==5:
                            mapData[blockpos[0]][blockpos[1]][datIndex]=0
                        else:
                            mapData[blockpos[0]][blockpos[1]][datIndex]=-1
                            PhysicsItem(((blockpos[0]+0.5)*BLOCKSIZE,(blockpos[1]+0.5)*BLOCKSIZE),tile,pickupDelay=0)
                        updateSurface(blockpos[0],blockpos[1])
                        if tile in platformBlocks:  
                            colour=pygame.transform.average_color(tileImages[tile],Rect(BLOCKSIZE/8,BLOCKSIZE/8,BLOCKSIZE*3/4,BLOCKSIZE/4))
                        else:colour=pygame.transform.average_color(tileImages[tile])
                        
                        if SFX:
                            playHitSfx(tile)
                        if PARTICLES:
                            for i in range(int(random.randint(2,3)*PARTICLEDENSITY)):
                                Particle(m,colour,size=10,life=100,angle=-math.pi/2,spread=math.pi,GRAV=0.05)
                    
            elif "melee" in item.tags:
                if self.canUse:
                    self.enemiesHit=[]
                    self.canUse=False
                    self.useTick=int(item.attackSpeed)
                    if SFX:
                        sounds[15].play()
                    swing=True
                    self.itemSwing=True
                    if self.direction==1:self.swingAngle=10
                    else:self.swingAngle=65
                    
            if swing:
                if not self.armSwing:
                    self.armSwing=True
                    if self.direction==1:
                        self.animationFrame=0
                    else:
                        self.animationFrame=19
            elif "ranged" in item.tags:
                if self.canUse:
                    if m[0]<screenW/2:
                        self.direction=0
                    else:self.direction=1
                    self.canUse=False
                    self.armHold=True
                    self.holdAngle=math.atan2(-m[1]+screenH/2,abs(m[0]-screenW/2))
                    self.useTick=int(item.attackSpeed)
                    angle=math.atan2(m[1]-screenH/2,m[0]-screenW/2)
                    pos=(clientPlayer.pos[0],clientPlayer.pos[1])
                    weaponDamage=item.attackDamage
                    weaponKnockback=item.knockback
                    weaponVel=item.velocity
                    if "gun" in item.tags:
                        ammoID=1
                    elif "bow" in item.tags:
                        ammoID=0
                    source=self.name
                    crit=False
                    if random.random()<item.critStrikeChance:
                        crit=True
                    fireProjectile(pos,angle,weaponDamage,weaponKnockback,weaponVel,ammoID,source,crit)
    def giveItem(self,ID,amnt=1,pos=None,unique=False,item=None):
        if pos==None:
            coin=False
            if ID>=21 and ID<=23:
                coin=True
            searchData=self.findExistingItemStacks(ID)#find all suitable slots
            while len(searchData[0])>0 and amnt>0:#fill all stacks of the same item first
                fillCount=searchData[0][0][2]#work out how many to add to the stack
                amnt-=fillCount
                if amnt<0:
                    fillCount+=amnt
                if searchData[0][0][0]=="H":#if item in hotbar increase the amnt by the calculated fillcount
                    self.hotbar[searchData[0][0][1]].amnt+=fillCount
                    if coin:
                        if self.hotbar[searchData[0][0][1]].amnt==itemData[ID][4][10]:
                            if amnt>0:
                                self.hotbar[searchData[0][0][1]].amnt=amnt
                            else:
                                self.hotbar[searchData[0][0][1]]=None
                            self.giveItem(ID+1)
                            amnt=0
                elif searchData[0][0][0]=="I":#if item in inventory increase the amnt by the calculated fillcount
                    self.inventory[searchData[0][0][1][0]][searchData[0][0][1][1]].amnt+=fillCount
                    if coin:
                        if self.inventory[searchData[0][0][1][0]][searchData[0][0][1][1]].amnt==itemData[ID][4][10]:
                            if amnt>0:
                                self.inventory[searchData[0][0][1][0]][searchData[0][0][1][1]].amnt=amnt
                            else:
                                self.inventory[searchData[0][0][1][0]][searchData[0][0][1][1]]=None
                            self.giveItem(ID+1)
                            amnt=0
                dat=[searchData[0][0][0],searchData[0][0][1]]
                if dat not in self.oldInventoryPositions:
                    self.oldInventoryPositions.append(dat)#flag the position for a surface update
                searchData[0].remove(searchData[0][0])#remove the used data
            while len(searchData[1])>0 and amnt>0:#no stacks left to fill so fill empty slots
                fillCount=searchData[1][0][2]#work out how many to add to the stack
                amnt-=fillCount
                if amnt<0:
                    fillCount+=amnt
                if searchData[1][0][0]=="H":#if item in hotbar increase the amnt by the calculated fillcount
                    self.hotbar[searchData[1][0][1]]=Item(ID,amnt=fillCount)
                elif searchData[1][0][0]=="I":#if item in inventory increase the amnt by the calculated fillcount
                    self.inventory[searchData[1][0][1][0]][searchData[1][0][1][1]]=Item(ID,amnt=fillCount,prefixData=prefixData)
                dat=[searchData[1][0][0],searchData[1][0][1]]
                if dat not in self.oldInventoryPositions:
                    self.oldInventoryPositions.append(dat)#flag the position for a surface update
                searchData[1].remove(searchData[1][0])#remove the used data
            if amnt<=0:
                return [True]
            else:
                if ID not in self.unPickupableItems:
                    self.unPickupableItems.append(ID)
                return [False,amnt]
        else:
            if pos[0]=="H":
                if self.hotbar[pos[1]]==None:
                    if unique:
                        self.hotbar[pos[1]]=item
                    else:
                        self.hotbar[pos[1]]=Item(ID,amnt=amnt)
                    return [0]
                elif self.hotbar[pos[1]].ID==ID:
                    if not unique:
                        self.hotbar[pos[1]].amnt+=amnt
                        if self.hotbar[pos[1]].amnt>itemData[ID][4][10]:
                            amnt=self.hotbar[pos[1]].amnt-itemData[ID][4][10]
                            self.hotbar[pos[1]].amnt=itemData[ID][4][10]
                            return [1,amnt]
                    else:
                        item=self.hotbar[pos[1]]
                        return [2,item,"H"]
                elif self.hotbar[pos[1]].ID!=ID:
                    item=self.hotbar[pos[1]]
                    return [2,item,"H"]
            elif pos[0]=="I":
                if self.inventory[pos[1][0]][pos[1][1]]==None:
                    if unique:
                        self.inventory[pos[1][0]][pos[1][1]]=item
                    else:
                        self.inventory[pos[1][0]][pos[1][1]]=Item(ID,amnt=amnt,prefixData=prefixData)
                    return [0]
                elif self.inventory[pos[1][0]][pos[1][1]].ID==ID:
                    if not unique:
                        self.inventory[pos[1][0]][pos[1][1]].amnt+=amnt
                        if self.inventory[pos[1][0]][pos[1][1]].amnt>itemData[ID][4][10]:
                            amnt=self.inventory[pos[1][0]][pos[1][1]].amnt-itemData[ID][4][10]
                            self.inventory[pos[1][0]][pos[1][1]].amnt=itemData[ID][4][10]
                            return [1,amnt]
                    else:
                        item=self.inventory[pos[1][0]][pos[1][1]]
                        return [2,item,"I"]
                elif self.inventory[pos[1][0]][pos[1][1]].ID!=ID:
                    item=self.inventory[pos[1][0]][pos[1][1]]
                    return [2,item,"I"]
##    def sortCoins(self):
##        total=0#idea: get positions of plat gold silver and copper, if copper amnt = 100 +1 to silver if silver=100 +1 to gold,if gold==100 +1 to plat
##        #this should maintain the positions of coins in the inventory or just check if it's a coin in the give item code and work it out there
##        positions=[]
##        for j in range(4):
##            for i in range(10):
##                item=self.inventory[i][j]
##                if item!=None:
##                    if item.ID>=21 and item.ID<=24:
##                        positions.append((i,j))
##                        if item.ID==24:
##                            total+=item.amnt*1000000
##                        elif item.ID==23:
##                            total+=item.amnt*10000
##                        elif item.ID==22:
##                            total+=item.amnt*100
##                        elif item.ID==21:
##                            total+=item.amnt
##                        self.inventory[i][j]=None
##                        pos=["I",(i,j)]
##                        if pos not in self.oldInventoryPositions:
##                            self.oldInventoryPositions.append(pos)
##                else:positions.append((i,j))
##        coins=coinsFromVal(total)
##        positions=sorted(positions,key=lambda x:x[1])
##        for i in range(len(coins)):
##            if coins[i]>0:
##                if len(positions)>0:
##                    self.inventory[positions[0][0]][positions[0][1]]=Item(24-i,amnt=coins[i])
##                    positions.remove(positions[0])
                    
            
                
    def removeItem(self,pos):
        if pos[0]=="H":
            item=self.hotbar[pos[1]]
            self.hotbar[pos[1]]=None
        elif pos[0]=="I":
            item=self.inventory[pos[1][0]][pos[1][1]]
            self.inventory[pos[1][0]][pos[1][1]]=None
        if pos not in self.oldInventoryPositions:
            self.oldInventoryPositions.append(pos)
        return item
        
    def findExistingItemStacks(self,ID,searchHotbar=True,searchInventory=True):#finds existing item stacks and free spaces
        
        #[which array,position in array,amount]
        existingSpaces=[]
        freeSpaces=[]
        
        if searchHotbar:#search hotbar
            for i in range(10):
                if self.hotbar[i]==None:
                    freeSpaces.append(["H",i,int(itemData[ID][4][10])])
                elif self.hotbar[i].ID==ID:
                    available=int(itemData[ID][4][10])-self.hotbar[i].amnt
                    if available>0:
                        existingSpaces.append(["H",i,available])
        
        if searchInventory:#search inventory
            for j in range(4):
                for i in range(10):
                    if self.inventory[i][j]==None:
                        freeSpaces.append(["I",(i,j),int(itemData[ID][4][10])])
                    elif self.inventory[i][j].ID==ID:
                        available=int(itemData[ID][4][10])-self.inventory[i][j].amnt
                        if available>0:
                            existingSpaces.append(["I",(i,j),available])
        return [existingSpaces,freeSpaces]
    def renderHotbar(self,full=False):
        self.hotbarImage.fill((255,0,255))
        for i in range(10):
            self.hotbarImage.blit(miscGuiImages[0],(48*i,0))
            if clientPlayer.hotbar[i]!=None:
                self.hotbarImage.blit(itemImages[self.hotbar[i].ID],(48*i,0))
                if self.hotbar[i].amnt>1:
                    self.hotbarImage.blit(outlineText(str(self.hotbar[i].amnt),(255,255,255),SMALLFONT),(24+48*i,30))
    def updateInventoryOldSlots(self):
        for data in self.oldInventoryPositions:
            if data[0]=="H":
                item=self.hotbar[data[1]]
                self.hotbarImage.blit(miscGuiImages[0],(data[1]*48,0))
                if item!=None:
                    self.hotbarImage.blit(itemImages[item.ID],(48*data[1],0))
                    if item.amnt>1:
                        self.hotbarImage.blit(outlineText(str(item.amnt),(255,255,255),SMALLFONT),(24+48*data[1],30))
            if data[0]=="I":
                item=self.inventory[data[1][0]][data[1][1]]
                self.inventoryImage.blit(miscGuiImages[0],(data[1][0]*48,data[1][1]*48))
                if item!=None:
                    self.inventoryImage.blit(itemImages[item.ID],(data[1][0]*48,data[1][1]*48))
                    if item.amnt>1:
                        self.inventoryImage.blit(outlineText(str(item.amnt),(255,255,255),SMALLFONT),(24+48*data[1][0],30+48*data[1][1]))
        self.oldInventoryPositions=[]
    def renderInventory(self):
        self.inventoryImage.fill((255,0,255))
        pygame.draw.rect(self.inventoryImage,(150,150,150),Rect(5,5,472,184),0)
        for j in range(4):
            for i in range(10):
                self.inventoryImage.blit(miscGuiImages[0],(48*i,48*j))
                if clientPlayer.inventory[i][j]!=None:
                    self.inventoryImage.blit(itemImages[clientPlayer.inventory[i][j].ID],(48*i,48*j))
                    if self.inventory[i][j].amnt>1:
                        self.inventoryImage.blit(outlineText(str(self.inventory[i][j].amnt),(255,255,255),SMALLFONT),(24+48*i,30+48*j))
    def draw(self):#draw player to screen
        if self.alive:
            screen.blit(self.sprites[self.animationFrame],(screenW/2-20,screenH/2-33))
            img=self.currentItemImage.copy()
            if self.armHold:
                item=self.hotbar[self.hotbarIndex]
                img=rot_center(itemImages[item.ID].copy(),self.holdAngle*180/math.pi)
                if self.direction==1:offsetx=10
                else:offsetx=-10;img=pygame.transform.flip(img,True,False)
                screen.blit(img,(screenW/2-img.get_width()/2+offsetx,screenH/2-img.get_height()/2))
            elif self.itemSwing:
                item=self.hotbar[self.hotbarIndex]
                if self.direction==1:  
                    hitRect=Rect(self.pos[0],self.pos[1]-img.get_height()/2,img.get_width(),img.get_height())
                else:
                    hitRect=Rect(self.pos[0]-img.get_width(),self.pos[1]-img.get_height()/2,img.get_width(),img.get_height())
                for enemy in enemies:
                    if enemy.rect.colliderect(hitRect):
                        if enemy.gameID not in self.enemiesHit:
                            if self.direction==0:
                                direction=-1
                            else:direction=1
                            val=int(self.hotbar[self.hotbarIndex].attackDamage)
                            if random.random()<item.critStrikeChance:crit=True
                            else:crit=False
                            enemy.damage(val,item.knockback,direction=direction,crit=crit)
                            self.enemiesHit.append(int(enemy.gameID))
                if self.direction==1:
                    self.swingAngle-=(100-item.attackSpeed)/5
                    if self.swingAngle<-80:
                        self.itemSwing=False
                else:
                    self.swingAngle+=(100-item.attackSpeed)/5
                    if self.swingAngle>155:
                        self.itemSwing=False
                
                angle1=self.swingAngle
                angle2=(self.swingAngle)*math.pi/180
                if self.direction==1:offsetx=img.get_width()/2
                else:offsetx=-img.get_width()/2
                if self.direction==1:offsety=-math.sin(angle2+0.2)*img.get_height()*2/3-img.get_height()/4
                else:offsety=-math.sin(angle2+0.3)*img.get_width()*2/3+img.get_height()/2
                screen.blit(rot_center(img,angle1),(screenW/2-20+offsetx,screenH/2-33+offsety))  
        if HITBOXES:#show hitbox
            pygame.draw.rect(screen,(255,0,0),Rect(screenW/2-playerWidth/2,screenH/2-playerHeight/2,playerWidth,playerHeight),1)
            
class Particle():
    def __init__(self,pos,colour,life=75,magnitude=2,size=5,angle=None,spread=math.pi/4,GRAV=0.2,vel=None,outline=True):
        self.pos=pos 
        self.life=life+random.random()*life/10-life/20#how long it lasts for (randomized slightly)
        self.initLife=self.life
        self.colour=colour
        self.size=size+random.random()*size/10-size/20#how large it will be (randomized slightly)
        self.initSize=self.size
        self.outline=outline
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
        if self.outline:
            pygame.draw.rect(screen,(0,0,0),rect,1)
class Projectile():
    def __init__(self,pos,vel,Type,ID,source,damage,knockback,crit,bounceNum,trail,maxLife=500,GRAVITY=0.1,DRAG=0.99):
        global projectiles
        self.pos=pos
        self.vel=vel
        self.angle=math.atan2(vel[1],vel[0])
        self.type=Type
        self.ID=ID
        self.source=source
        self.damage=damage
        self.knockback=knockback
        self.crit=crit
        self.trail=trail
        self.trailTick=random.randint(0,5)
        self.bounceNum=bounceNum
        self.size=projectileData[ID][6]
        self.rect=Rect(self.pos[0]-self.size/2,self.pos[1]-self.size/2,self.size,self.size)
        self.life=int(maxLife)
        self.GRAVITY=GRAVITY
        self.DRAG=DRAG
        projectiles.append(self)
    def update(self):
        self.life-=1
        if self.life<=0:
            projectiles.remove(self)
            return
        self.vel=(self.vel[0]*self.DRAG,self.vel[1]*self.DRAG+self.GRAVITY)
        self.pos=(self.pos[0]+self.vel[0],self.pos[1]+self.vel[1])
        self.rect.left=self.pos[0]-self.size/2#updating rect
        self.rect.top=self.pos[1]-self.size/2
        self.blockpos=(math.floor(self.pos[1]//BLOCKSIZE),math.floor(self.pos[0]//BLOCKSIZE))
        if self.trail!=None:
            if self.trailTick<=0:
                if self.trail=="arrow":
                    self.trailTick=5
                    if PARTICLES:
                        Particle((self.pos[0]-clientPlayer.pos[0]+screenW/2+self.size/2,self.pos[1]-clientPlayer.pos[1]+screenH/2+self.size/2),(90,90,90),size=7,magnitude=0,GRAV=0)
                #elif self.trail=="bullet":
                    #self.trailTick=1
                    #Particle((self.pos[0]-clientPlayer.pos[0]+screenW/2+self.size/2,self.pos[1]-clientPlayer.pos[1]+screenH/2+self.size/2),(235,20,20),size=6,magnitude=0,GRAV=0,outline=False)
            else:
                self.trailTick-=1
        if self.vel[1]>0:
            if self.pos[1]>WORLDBOARDER_SOUTH:
                self.pos=(self.pos[0],int(WORLDBOARDER_SOUTH))
                self.vel=(self.vel[0],0)
                self.grounded=True
                
        xcollided=False
        ycollided=False
        
        for j in range(-1,2):
            for i in range(-1,2):
                try:
                    val=mapData[self.blockpos[1]+j][self.blockpos[0]+i][0]
                    if val not in uncollidableBlocks:
                        if val not in platformBlocks:
                            blockrect=Rect(BLOCKSIZE*(self.blockpos[1]+j),BLOCKSIZE*(self.blockpos[0]+i),BLOCKSIZE,BLOCKSIZE)    
                            if blockrect.colliderect(self.rect):
                                blockHitVal=int(val)
                                deltaX = self.pos[0]-blockrect.centerx
                                deltaY = self.pos[1]-blockrect.centery
                                if abs(deltaX) > abs(deltaY):
                                    if deltaX > 0:
                                        self.pos=(blockrect.right+playerWidth/2,self.pos[1])#move proj right
                                    else:
                                        self.pos=(blockrect.left-playerWidth/2,self.pos[1])#move proj left
                                    xcollided=True
                                else:
                                    if deltaY > 0:
                                        if self.vel[1]<0:
                                            self.pos=(self.pos[0],blockrect.bottom+self.rect.height/2)#move proj down
                                    else:
                                        if self.vel[1]>0:
                                            self.pos=(self.pos[0],blockrect.top-self.rect.height/2)#move proj up             
                                    ycollided=True
                except:None
        if ycollided or xcollided:
            self.bounceNum-=1
            if ycollided:
                self.vel=(self.vel[0],-self.vel[1])
            else:
                self.vel=(-self.vel[0],-self.vel[1])
            if self.bounceNum<0:
                projectiles.remove(self)
                if PARTICLES:
                    colour=getBlockAverageColour(blockHitVal)
                    for i in range(int(3*PARTICLEDENSITY)):
                        Particle((self.pos[0]-clientPlayer.pos[0]+screenW/2,self.pos[1]-clientPlayer.pos[1]+screenH/2),colour,GRAV=0,size=8)
                if SFX:
                    if self.type=="Bullet":
                        sounds[18].play()
                    else:
                        sounds[random.randint(3,5)].play()
                return
        for enemy in enemies:
            if enemy.rect.colliderect(self.rect):
                if enemy.pos[0]>clientPlayer.pos[0]:direction=1
                else:direction=-1
                enemy.damage(self.damage,crit=self.crit,knockBack=self.knockback,direction=direction)
                projectiles.remove(self)
                return
    def draw(self):
        if self.type=="Arrow":
            angle=math.atan2(self.vel[1],-self.vel[0])*180/math.pi-90
            surf=projectileImages[self.ID].copy()
            surf=rot_center(surf,angle)
            screen.blit(surf,(self.rect.left-clientPlayer.pos[0]+screenW/2,self.rect.top-clientPlayer.pos[1]+screenH/2))
        elif self.type=="Bullet":
            pygame.draw.circle(screen,(60,60,60),(int(self.rect.centerx-clientPlayer.pos[0]+screenW/2),int(self.rect.centery-clientPlayer.pos[1]+screenH/2)),3,0)
        if HITBOXES:
            pygame.draw.rect(screen,(255,0,0),Rect(self.rect.left-clientPlayer.pos[0]+screenW/2,self.rect.top-clientPlayer.pos[1]+screenH/2,self.rect.width,self.rect.height),1)
def updateParticles():
    for particle in particles:
        particle.update()
        
def drawParticles():
    for particle in particles:
        particle.draw()
        
def updatePhysicsItems():
    for physicsItem in physicsItems:
        physicsItem.update()
        
def drawPhysicsItems():
    for physicsItem in physicsItems:
        physicsItem.draw()
        
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
            
def playHitSfx(tile,volume=1):
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
    elif genType=="superflat":
        mapData=[]
        backgroundID=3
        for i in range(MAPSIZEX):
            mapData.append([])
            for j in range(MAPSIZEY):
                if j>100:
                    bval=1
                    wval=1
                else:
                    bval=-1
                    wval=-1
                mapData[i].append([bval,wval])
    makeSpawnPoint()
    
    print("Generation complete!")
def fadeBackground(ID):
    global fadeBackgroundID, fadeBack, fadeFloat
    fadeBackgroundID=ID
    fadeBack=True
    fadeFloat=0
    
def checkMerge(ID1,ID2):#which blocks should merge with each other
    if ID1==ID2:return True
    
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
    elif ID1>=68:return True
    else:return False
    
def drawDeathMessage():#message shown on death
    font=pygame.font.Font(fontFilePath,40)
    text=outlineText("You Were Slain",(255,255,255),font)
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
        
def loadPlayerData():#loads all possible player saves, giving options to load them or create a new save
    global playerData
    possibleLoads=os.listdir("Players")#get filenames
    choice="n"
    if len(possibleLoads)>0:
        print("Which player do you want to load? (player number or 'n' to create a new player)\n")
        for i in range(len(possibleLoads)):
            dat=pickle.load(open("Players/"+possibleLoads[i],"rb"))
            possibleLoads[i]=possibleLoads[i][:-7]
            string="Player "+str(i+1)+": Name: "+dat[0]+", created: "+dat[7]+", playtime: "+str(int((dat[6]/60)//60))+":"+str(int(dat[6]//60%60)).zfill(2)+":"+str(int(dat[6]%60)).zfill(2)
            print(string)
        choice=str(input())
    if choice=="n":
        name=str(input("Enter name of new player: "))
        playerData=[name,defaultModel,None,None,100,100,0,None]
    else:
        playerData=pickle.load(open("Players/"+possibleLoads[int(choice)-1]+".player","rb"))#open selected save player file   
def createPlayer():
    global clientPlayer
    name=playerData[0]
    model=playerData[1]
    hotbar=playerData[2]
    inventory=playerData[3]
    HP=playerData[4]
    maxHP=playerData[5]
    playTime=playerData[6]
    creationDate=playerData[7]
    clientPlayer=Player((0,0),model,name=name,hotbar=hotbar,inventory=inventory,HP=HP,maxHP=maxHP,playTime=playTime,creationDate=creationDate)
    
def loadSaves(forceWorldGen=False):#loads all possible saves, giving options to load them or create a new save
    global mapData, tileMaskData, wallTileMaskData, backgroundID, worldName, MAPSIZEX, MAPSIZEY, clientWorld
    possibleLoads=os.listdir("Saves")#get filenames
    choice="n"
    if len(possibleLoads)>0:
        print("\nWhich slot do you want to load? (slot number or 'n' to create a new save)\n")
        for i in range(len(possibleLoads)):
            if possibleLoads[i][-3:]=="dat":#if it's a dat file
                dat=pickle.load(open("Saves/"+possibleLoads[i],"rb"))
                possibleLoads[i]=possibleLoads[i][:-4]
                string="Slot "+str(math.ceil((i+1)/2))+": Name: "+dat.name+", created: "+dat.creationDate+", playtime: "+str(int((dat.playTime/60)//60))+":"+str(int(dat.playTime//60%60)).zfill(2)+":"+str(int(dat.playTime%60)).zfill(2)
                print(string)
        choice=str(input())
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
        print(worldName+" successfully loaded!\n")
    else:generateTerrain("DEFAULT")
    mapLight=[[None for i in range(MAPSIZEY)]for j in range(MAPSIZEX)]
    
class World():
    def __init__(self,name,creationDate,size):
        self.name=name
        self.creationDate=creationDate
        self.size=size
        self.playTime=0
        self.spawnPoint=(0,0)
        
class Item():
    def __init__(self,ID,amnt=1,prefixData=None):
        self.name=str(itemData[ID][0])
        self.ID=ID
        self.amnt=amnt
        self.tags=list(itemData[ID][2])
        if itemData[ID][4][0]!=None:self.attackDamage=int(itemData[ID][4][0])
        if itemData[ID][4][1]!=None:self.attackSpeed=int(itemData[ID][4][1])
        if itemData[ID][4][2]!=None:self.critStrikeChance=float(itemData[ID][4][2])
        if itemData[ID][4][3]!=None:self.size=float(itemData[ID][4][3])
        if itemData[ID][4][4]!=None:self.velocity=int(itemData[ID][4][4])
        if itemData[ID][4][5]!=None:self.manaCost=int(itemData[ID][4][5])
        if itemData[ID][4][6]!=None:self.knockback=int(itemData[ID][4][6])
        if itemData[ID][4][7]!=None:self.tier=int(itemData[ID][4][7])
        self.description=str(itemData[ID][5])
        if len(itemData[ID][3])>0 and random.random()>0.1:
            self.hasPrefix=True
            if prefixData==None:
                self.prefixData=getItemPrefix(itemData[ID][3][random.randint(0,len(itemData[ID][3])-1)])
            else:self.prefixData=prefixData
            if self.prefixData[0]=="universal":
                self.attackDamage*=(1+self.prefixData[1][1])
                self.critStrikeChance+=self.prefixData[1][2]
                self.knockback*=(1+self.prefixData[1][3])
                self.tier+=self.prefixData[1][4]
            elif self.prefixData[0]=="common":
                self.attackDamage*=(1+self.prefixData[1][1])
                self.attackSpeed*=(1-self.prefixData[1][2])
                self.critStrikeChance+=self.prefixData[1][3]
                self.knockback*=(1+self.prefixData[1][4])
                self.tier+=self.prefixData[1][5]
            elif self.prefixData[0]=="melee":
                self.attackDamage*=(1+self.prefixData[1][1])
                self.attackSpeed*=(1-self.prefixData[1][2])
                self.critStrikeChance+=self.prefixData[1][3]
                self.size*=(1+self.prefixData[1][4])
                self.knockback*=(1+self.prefixData[1][5])
                self.tier+=self.prefixData[1][6]
            elif self.prefixData[0]=="ranged":
                self.attackDamage*=(1+self.prefixData[1][1])
                self.attackSpeed*=(1-self.prefixData[1][2])
                self.critStrikeChance+=self.prefixData[1][3]
                self.velocity*=(1+self.prefixData[1][4])
                self.knockback*=(1+self.prefixData[1][5])
                self.tier+=self.prefixData[1][6]
            elif self.prefixData[0]=="magic":
                self.attackDamage*=(1+self.prefixData[1][1])
                self.attackSpeed*=(1-self.prefixData[1][2])
                self.critStrikeChance+=self.prefixData[1][3]
                self.manaCost*=(1+self.prefixData[1][4])
                self.knockback*=(1+self.prefixData[1][5])
                self.tier+=self.prefixData[1][6]
        else:
            self.prefixData=None
            self.hasPrefix=False
    def getName(self):
        if self.hasPrefix:
            return self.prefixData[1][0]+" "+self.name
        else:
            return self.name
class PhysicsItem():
    def __init__(self,pos,ID,amnt=1,pickupDelay=100):
        global physicsItems
        self.pos=pos
        angle=random.random()*math.pi*2-math.pi
        initSpeed=random.random()*3+1
        self.vel=(math.cos(angle),math.sin(angle))
        self.ID=ID
        self.amnt=amnt
        self.itemScale=1.25
        self.renderImage()
        self.tiltAngle=0
        self.despawnCheckTick=10000
        self.despawnTick=0
        self.pickupDelay=pickupDelay
        self.grounded=False
        self.rect=Rect(pos[0]-BLOCKSIZE/2*self.itemScale,pos[1]-BLOCKSIZE/2*self.itemScale*0.8,BLOCKSIZE*self.itemScale*0.8,BLOCKSIZE*self.itemScale)
        physicsItems.append(self)
    def renderImage(self):
        self.image=pygame.transform.scale(itemImages[self.ID].copy(),(int(BLOCKSIZE*1.414*self.itemScale),int(BLOCKSIZE*1.414*self.itemScale)))
        self.spacing=int((self.image.get_width()-BLOCKSIZE)/2)
    def checkDespawn(self):
        if self.pos[0]<clientPlayer.pos[0]-screenW/2:physicsItems.remove(self)
        elif self.pos[0]>clientPlayer.pos[0]+screenW/2:physicsItems.remove(self)
        elif self.pos[1]<clientPlayer.pos[1]-screenH/2:physicsItems.remove(self)
        elif self.pos[1]>clientPlayer.pos[1]+screenH/2:physicsItems.remove(self)
    def update(self):
        if self.despawnCheckTick<=0:
            if self.despawnTick<=0:
                self.checkDespawn()
            else:self.despawnTick-=1
        else:self.despawnCheckTick-=1
        
        if not self.grounded:
            self.vel=(self.vel[0],self.vel[1]+GRAVITY)
            
        self.vel=(self.vel[0]*0.95,self.vel[1]*0.95)
        self.pos=(self.pos[0]+self.vel[0],self.pos[1]+self.vel[1])
        self.rect.center=tuple(self.pos)
        self.blockpos=(math.floor(self.pos[1]//BLOCKSIZE),math.floor(self.pos[0]//BLOCKSIZE))
        self.grounded=False
        collide=True
        
        if self.ID not in clientPlayer.unPickupableItems:
            if self.pickupDelay<=0:
                if abs(self.pos[0]-clientPlayer.pos[0])<BLOCKSIZE*4:
                    if abs(self.pos[1]-clientPlayer.pos[1])<BLOCKSIZE*4:
                        collide=False
                        angle=math.atan2(clientPlayer.pos[1]-self.pos[1],clientPlayer.pos[0]-self.pos[0])
                        self.vel=(self.vel[0]+math.cos(angle),self.vel[1]+math.sin(angle))
                        if clientPlayer.rect.colliderect(self.rect):
                            physicsItems.remove(self)
                            itemData=clientPlayer.giveItem(self.ID,amnt=self.amnt)
                            
                            if itemData[0]:
                                if SFX:
                                    if self.ID>=21 and self.ID<=24:
                                        sounds[23].play()
                                    else:
                                        sounds[19].play()
                                return
                            else:
                                PhysicsItem(clientPlayer.pos,self.ID,amnt=itemData[1])
                                return
            else:
                self.pickupDelay-=1
        if collide:
            for j in range(-2,3):
                for i in range(-2,3):
                    try:
                        val=mapData[self.blockpos[1]+j][self.blockpos[0]+i][0]
                        if val not in uncollidableBlocks:
                            blockrect=Rect(BLOCKSIZE*(self.blockpos[1]+j),BLOCKSIZE*(self.blockpos[0]+i),BLOCKSIZE,BLOCKSIZE) 
                            if blockrect.colliderect(self.rect):
                                deltaX = self.pos[0]-blockrect.centerx
                                deltaY = self.pos[1]-blockrect.centery
                                if abs(deltaX) > abs(deltaY):
                                    if deltaX > 0:
                                        self.pos=(blockrect.right+self.rect.width/2,self.pos[1])#move item right
                                        self.vel=(0,self.vel[1])#stop item horizontally
                                    else:
                                        self.pos=(blockrect.left-self.rect.width/2,self.pos[1])#move item left
                                        self.vel=(0,self.vel[1])#stop item horizontally
                                else:
                                    if deltaY > 0:
                                        if self.vel[1]<0:
                                            self.pos=(self.pos[0],blockrect.bottom+self.rect.height/2)#move item down
                                            self.vel=(self.vel[0],0)#stop item vertically
                                    else:
                                        if self.vel[1]>0:
                                            self.pos=(self.pos[0],blockrect.top-self.rect.height/2+1)#move item up
                                            self.vel=(self.vel[0],0)#stop item vertically
                                            self.grounded=True
                    except:None
    def draw(self):
        newAngle=-int(self.vel[0]*10)
        if newAngle!=self.tiltAngle:
            self.tiltAngle=newAngle
            img=self.image.copy()
            img=rot_center(img,self.tiltAngle)
            screen.blit(img,(self.rect.left-clientPlayer.pos[0]+screenW/2-self.spacing/2,self.rect.top-clientPlayer.pos[1]+screenH/2-self.spacing/2))
        else:
            screen.blit(self.image,(self.rect.left-clientPlayer.pos[0]+screenW/2-self.spacing/2,self.rect.top-clientPlayer.pos[1]+screenH/2-self.spacing/2))
        if HITBOXES:
            pygame.draw.rect(screen,(255,0,0),Rect(self.rect.left-clientPlayer.pos[0]+screenW/2,self.rect.top-clientPlayer.pos[1]+screenH/2,self.rect.width,self.rect.height),1)
        
            
def Exit():
    Save()
    pygame.quit()
    print("\nRunning slowly? try turning off the particles, \nbackground or lowering the resolution")
    sys.exit()
    
    
def Save():
    pickle.dump(mapData,open("Saves/"+str(worldName)+".wrld","wb"))#save wrld
    pickle.dump(clientWorld,open("Saves/"+str(worldName)+".dat","wb"))#save dat
    playerData=[clientPlayer.name,clientPlayer.model,clientPlayer.hotbar,clientPlayer.inventory,clientPlayer.HP,clientPlayer.maxHP,clientPlayer.playTime,clientPlayer.creationDate]#create player array
    pickle.dump(playerData,open("Players/"+clientPlayer.name+".player","wb"))#save player array
    message("Game saved!",(255,255,255))
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
    global MAPSIZEX, MAPSIZEY, GRAVITY, screenW, screenH, RUNFULLSCREEN, PARTICLES,PARTICLEDENSITY, MUSIC, SFX, CREATIVE, BACKGROUND, PARALLAXAMNT, PASSIVE, MAXENEMYSPAWNS,FANCYTEXT, HITBOXES, SPLASHSCREEN
    
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
    PASSIVE=bool(int(configData[11]))
    MAXENEMYSPAWNS=int(configData[12])
    FANCYTEXT=bool(int(configData[13]))
    HITBOXES=bool(int(configData[14]))
    SPLASHSCREEN=bool(int(configData[15]))

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
    item=clientPlayer.hotbar[clientPlayer.hotbarIndex]
    if item!=None:
        colour=getTierColour(item.tier)
        handText=outlineText(item.getName(),colour,DEFAULTFONT)
    else:
        handText=outlineText("",(255,255,255),DEFAULTFONT)
        
def outlineText(string,colour,font,outlineColour=(0,0,0)):
    text1=font.render(string,False,colour)
    if FANCYTEXT:
        text2=font.render(string,False,outlineColour)
        surf=pygame.Surface((text2.get_width()+2,text2.get_height()+2))
        surf.fill((255,0,255))
        surf.set_colorkey((255,0,255))
        surf.blit(text2,(0,1))
        surf.blit(text2,(2,1))
        surf.blit(text2,(1,0))
        surf.blit(text2,(1,2))
        surf.blit(text1,(1,1))
        return surf
    else:return text1

def runSplashScreen():
    global particles
    done=False
    age=0
    text=outlineText("A Fergus Griggs game...",(255,255,255),LARGEFONT)
    blackSurf=pygame.Surface((screenW,screenH))
    frame=0
    xpos=-30
    tick=0
    while not done:
        screen.blit(backsurfs[1],(0,0))
        if age<50:
            blackSurf.set_alpha(255)
        elif age<150 and age>50:
            alpha=(150-age)/150*255
            blackSurf.set_alpha(alpha)
        elif age>150 and age<450:
            updateParticles()
            if tick<=0:
                tick=10
                if SFX:
                    sounds[random.randint(20,22)].play()
            else:tick-=1
            if frame<18:
                frame+=1
            else:
                frame=6
            if PARTICLES:
                Particle((xpos+playerWidth,screenH*3/4+playerHeight*1.15),(255,255,255),GRAV=-0.1,size=10,angle=math.pi,spread=math.pi,magnitude=1)
            xpos+=screenW/290
        elif age>450 and age<600:
            updateParticles()
            alpha=(age-450)/150*255
            blackSurf.set_alpha(alpha)
        elif age>650:
            done=True
        drawParticles()
        screen.blit(clientPlayer.sprites[frame],(xpos,screenH*3/4))
        screen.blit(text,(screenW/2-text.get_width()/2,screenH/2))
        screen.blit(blackSurf,(0,0))
        age+=1
        for event in pygame.event.get():
            if event.type==QUIT:
                Exit()
            if event.type==KEYDOWN:
                done=True
        pygame.display.flip()
        clock.tick(60)
    particles=[]
def renderStatsText(pos):
    global statsText, lastHoveredItem

    if pos[0]=="H":
        item=clientPlayer.hotbar[pos[1]]
    elif pos[0]=="I":
        item=clientPlayer.inventory[pos[1][0]][pos[1][1]]
    if item!=None:
        if item!=lastHoveredItem: 
            lastHoveredItem=item
            statsText=pygame.Surface((340,200))
            statsText.fill((255,0,255))
            statsText.set_colorkey((255,0,255))
            
            stats=[]
            stats.append(outlineText(item.getName(),getTierColour(item.tier),DEFAULTFONT))
            if "weapon" in item.tags or "tool" in item.tags:
                stats.append(outlineText(str(int(item.attackDamage))+" damage",(255,255,255),DEFAULTFONT))
                stats.append(outlineText(str(int(item.critStrikeChance*100))+"% critical strike chance",(255,255,255),DEFAULTFONT))
                stats.append(outlineText(getSpeedText(item.attackSpeed),(255,255,255),DEFAULTFONT))
                stats.append(outlineText(getKnockbackText(item.knockback),(255,255,255),DEFAULTFONT))
            elif "block" in item.tags:
                stats.append(outlineText("Can be placed.",(255,255,255),DEFAULTFONT))
            if item.description!="None":
                stats.append(outlineText(item.description,(255,255,255),DEFAULTFONT))
            if item.hasPrefix:
                if item.prefixData[1][1]!=0:
                    if item.prefixData[1][1]>0:colour=tuple(goodColour)
                    else:colour=tuple(badColour)
                    stats.append(outlineText(addPlus(str(int(item.prefixData[1][1]*100)))+"% damage",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
                if item.prefixData[0]!="universal":
                    if item.prefixData[1][2]!=0:
                        if item.prefixData[1][2]>0:colour=tuple(goodColour)
                        else:colour=tuple(badColour)
                        stats.append(outlineText(addPlus(str(int(item.prefixData[1][2]*100)))+"% speed",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
                else:
                    if item.prefixData[1][2]!=0:
                        if item.prefixData[1][2]>0:colour=tuple(goodColour)
                        else:colour=tuple(badColour)
                        stats.append(outlineText(addPlus(str(int(item.prefixData[1][2]*100)))+"% critical strike chance",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
                    if item.prefixData[1][3]!=0:
                        if item.prefixData[1][3]>0:colour=tuple(goodColour)
                        else:colour=tuple(badColour)
                        stats.append(outlineText(addPlus(str(int(item.prefixData[1][3]*100)))+"% knockback",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
                if item.prefixData[0]!="universal":
                    if item.prefixData[1][3]!=0:
                        if item.prefixData[1][3]>0:colour=tuple(goodColour)
                        else:colour=tuple(badColour)
                        stats.append(outlineText(addPlus(str(int(item.prefixData[1][3]*100)))+"% critical strike chance",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
                if item.prefixData[0]=="common":
                    if item.prefixData[1][4]!=0:
                        if item.prefixData[1][4]>0:colour=tuple(goodColour)
                        else:colour=tuple(badColour)
                        stats.append(outlineText(addPlus(str(int(item.prefixData[1][4]*100)))+"% knockback",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
                if item.prefixData[0]=="melee":
                    if item.prefixData[1][4]!=0:
                        if item.prefixData[1][4]>0:colour=tuple(goodColour)
                        else:colour=tuple(badColour)
                        stats.append(outlineText(addPlus(str(int(item.prefixData[1][4]*100)))+"% size",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
                elif item.prefixData[0]=="ranged":
                    if item.prefixData[1][4]!=0:
                        if item.prefixData[1][4]>0:colour=tuple(goodColour)
                        else:colour=tuple(badColour)
                        stats.append(outlineText(addPlus(str(int(item.prefixData[1][4]*100)))+"% projectile velocity",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
                elif item.prefixData[0]=="magic":
                    if item.prefixData[1][4]!=0:
                        if item.prefixData[1][4]<0:colour=tuple(goodColour)
                        else:colour=tuple(badColour)
                        stats.append(outlineText(addPlus(str(int(item.prefixData[1][4]*100)))+"% size",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
                if item.prefixData[0]=="melee" or item.prefixData[0]=="ranged" or item.prefixData[0]=="magic":
                    if item.prefixData[1][5]!=0:
                        if item.prefixData[1][5]>0:colour=tuple(goodColour)
                        else:colour=tuple(badColour)
                        stats.append(outlineText(addPlus(str(int(item.prefixData[1][5]*100)))+"% knockback",colour,DEFAULTFONT,outlineColour=darkenCol(colour)))
            for i in range(len(stats)):
                statsText.blit(stats[i],(0,i*15))
        return True
    return False
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
def updateMessages():
    global messages
    for message in messages:
        message[1]-=1
        if message[1]<=0:messages.remove(message)
def drawMessages():
    for i in range(len(messages)):
        if messages[i][1]<100:
             messages[i][0].set_alpha(messages[i][1]/100*255)
        screen.blit(messages[i][0],(10,screenH-25-i*20))
def message(text,col,life=1000):
    global messages
    text1=DEFAULTFONT.render(text,False,col)
    text2=DEFAULTFONT.render(text,False,(0,0,0))
    surf=pygame.Surface((text1.get_width()+2,text1.get_height()+2))
    surf.fill((255,0,255))
    surf.set_colorkey((255,0,255))
    if FANCYTEXT:
        surf.blit(text2,(0,1))
        surf.blit(text2,(2,1))
        surf.blit(text2,(1,0))
        surf.blit(text2,(1,2))
    
    surf.blit(text1,(1,1))
    messages.insert(0,[surf,life])
##def updateLight(xmin,xmax,ymin,ymax):
##    if xmin<0:xmin=0
##    if ymin<0:ymin=0
##    if xmax>MAPSIZEX-1:xmax=MAPSIZEX-1
##    if ymax>MAPSIZEY-1:ymax=MAPSIZEY-1
##    for i in range(xmin,xmax):
##        for j in range(ymin,ymax):
##            if mapData[i][j][0]==-1:
##                if mapData[i][j][1]==-1:
##                    fillLight(i,j,15)
##def fillLight(i,j,lightval):
##   global mapLight
##   if onScreen(i,j):
##      newlightval=lightval-itemData[mapData[i][j][0]][1]
##      if newlightval>mapLight[i][j]:
##         mapLight[i][j]=newlightval
##         fillLight((i-1,j),newlightval)
##         fillLight((i,j+1),newlightval)
##         fillLight((i+1,j),newlightval)
##         fillLight((i,j-1),newlightval)
##      else:return
##   else:return
##   
def onScreen(i,j,width=1):
   if i<-1+width:return False
   if j<-1+width:return False
   if i>MAPSIZEX-width:return False
   if j>MAPSIZEY-width:return False
   return True

def getDeathMessage(name,source):
    string=deathLines[source[0]][random.randint(0,len(deathLines[source[0]])-1)]
    string=string.replace("<p>",name)
    string=string.replace("<w>",clientWorld.name)
    string=string.replace("<e>",source[1])
    return string                   
def checkEnemySpawn():
    global enemySpawnTick
    if not PASSIVE:
        if enemySpawnTick<=0:
            enemySpawnTick=200
            if len(enemies)<MAXENEMYSPAWNS and random.randint(1,5)==1:#reduce enemy spawns
                spawnEnemy()
        else:enemySpawnTick-=1
def spawnEnemy(pos=None,ID=None):
    if ID == None:
        if clientPlayer.pos[1]<200*BLOCKSIZE:
            ID=random.randint(0,1)
        elif clientPlayer.pos[1]<300*BLOCKSIZE:
            ID=random.randint(1,2)
        elif clientPlayer.pos[1]<400*BLOCKSIZE:
            ID=random.randint(3,4)
    if pos == None:
        spawnRect=Rect(clientPlayer.pos[0]-screenW/2,clientPlayer.pos[1]-screenH/2,screenW,screenH)
        for i in range(500):
            randompos=(random.randint(int(clientPlayer.pos[0])-screenW,int(clientPlayer.pos[0])+screenW),random.randint(int(clientPlayer.pos[1])-screenH,int(clientPlayer.pos[1])+screenH))
            if not spawnRect.collidepoint(randompos):
                blockpos=(math.floor(randompos[1]//BLOCKSIZE),math.floor(randompos[0]//BLOCKSIZE))
                if onScreen(blockpos[0],blockpos[1],width=2):
                    if mapData[blockpos[0]][blockpos[1]][0] in uncollidableBlocks:
                        if mapData[blockpos[0]-1][blockpos[1]][0] in uncollidableBlocks:
                            if mapData[blockpos[0]+1][blockpos[1]][0] in uncollidableBlocks:
                                if mapData[blockpos[0]][blockpos[1]-1][0] in uncollidableBlocks:
                                    if mapData[blockpos[0]][blockpos[1]+1][0] in uncollidableBlocks:
                                        if mapData[blockpos[0]-1][blockpos[1]-1][0] in uncollidableBlocks:
                                            if mapData[blockpos[0]-1][blockpos[1]+1][0] in uncollidableBlocks:
                                                if mapData[blockpos[0]+1][blockpos[1]-1][0] in uncollidableBlocks:
                                                    if mapData[blockpos[0]+1][blockpos[1]+1][0] in uncollidableBlocks:
                                                        Enemy(((blockpos[1]+0.5)*BLOCKSIZE,(blockpos[0]+0.5)*BLOCKSIZE),ID)
                                                        return
        return
    else:Enemy(pos,ID)
def getItemPrefix(prefixCategory):
    return [prefixCategory,prefixData[prefixCategory][random.randint(0,len(prefixData[prefixCategory])-1)]]
def getSpeedText(speed):
    if speed<2:
        return "Insanely fast speed"
    elif speed<10:
        return "Extremely fast speed"
    elif speed<25:
        return "Very fast speed"
    elif speed<40:
        return "Fast speed"
    elif speed<60:
        return "Normal speed"
    elif speed<80:
        return "Slow speed"
    else:
        return "Very Slow Speed"
def getKnockbackText(knockback):
    if knockback ==0:
        return "No knockback"
    elif knockback<2:
        return "Very weak knockback"
    elif knockback<5:
        return "Weak knockback"
    elif knockback<7:
        return "Average knockback"
    elif knockback<9:
        return "Strong knockback"
    else:
        return "Very strong knockback"
def getTierColour(tier):
    if tier <0:return(150,150,150)#gray
    elif tier ==1:return(146,146,249)#Blue
    elif tier ==2:return(146,249,146)#Green
    elif tier ==3:return(233,182,137)#Orange
    elif tier ==4:return(253,148,148)#Light Red
    elif tier ==5:return(249,146,249)#Pink
    elif tier ==6:return(191,146,233)#Light Purple
    elif tier ==7:return(139,237,9)#Lime
    elif tier ==8:return(233,233,9)#Yellow
    elif tier ==9:return(3,138,177)#Cyan
    elif tier ==10:return(229,35,89)#Red
    elif tier >10:return(170,37,241)#Purple
    else:return(255,255,255,255)#white
def addPlus(string):
    if string[0]!="-":
        string="+"+string
    return string
def damageNumber(pos,val,crit=False,colour=None):
    global damageNumbers
    if colour==None:
        if crit:
            colour=(246,97,28)
        else:
            colour=(207,127,63)
    
    t1=DEFAULTFONT.render(str(int(val)),False,colour)
    t2=DEFAULTFONT.render(str(int(val)),False,(colour[0]*0.8,colour[1]*0.8,colour[2]*0.8))
    
    width=t1.get_width()+2
    height=t1.get_height()+2
    if width>height:size=width
    else:size=height
    
    surf=pygame.Surface((size,size))
    surf.fill((255,0,255))
    surf.set_colorkey((255,0,255))
    
    midx=size/2-width/2
    midy=size/2-height/2
    if FANCYTEXT:
        surf.blit(t2,(midx,midy))
        surf.blit(t2,(midx+2,midy))
        surf.blit(t2,(midx+1,midy-1))
        surf.blit(t2,(midx+1,midy+1))
    
    surf.blit(t1,(midx,midy))
    
    damageNumbers.append([(pos[0]-clientPlayer.pos[0]+screenW/2,pos[1]-clientPlayer.pos[1]+screenH/2),(random.random()*4-2,-1-random.random()*4),surf,150])
def updateDamageNumbers():
    for damageNumber in damageNumbers:
        damageNumber[1]=(damageNumber[1][0]*0.95,damageNumber[1][1]*0.95)
        damageNumber[0]=(damageNumber[0][0]+damageNumber[1][0]-clientPlayer.posDiff[0],damageNumber[0][1]+damageNumber[1][1]-clientPlayer.posDiff[1])
        damageNumber[3]-=1
        if damageNumber[3]<=0:
            damageNumbers.remove(damageNumber)
def drawDamageNumbers():
    for damageNumber in damageNumbers:
        if damageNumber[3]<25:
            damageNumber[2].set_alpha(damageNumber[3]/25*255)
        surf=damageNumber[2].copy()
        surf=rot_center(surf,-damageNumber[1][0]*35)
        screen.blit(surf,(damageNumber[0][0]-surf.get_width()/2,damageNumber[0][1]-surf.get_height()/2))

def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def updateProjectiles():
    for projectile in projectiles:
        projectile.update()
def drawProjectiles():
    for projectile in projectiles:
        projectile.draw()
def fireProjectile(pos,angle,weaponDamage,weaponKnockback,weaponVel,ID,source,crit):
    
    angle+=(random.random()-0.5)/20
    
    damage=int(weaponDamage)+int(projectileData[ID][2])
    
    speed=int(weaponVel)+int(projectileData[ID][3])
    vel=(math.cos(angle)*speed,math.sin(angle)*speed)
    
    knockback=int(weaponKnockback)+int(projectileData[ID][4])
    if SFX:
        sounds[int(projectileData[ID][10])].play()
    
    Projectile(pos,vel,str(projectileData[ID][1]),ID,source,damage,knockback,crit,int(projectileData[ID][5]),str(projectileData[ID][7]),GRAVITY=float(projectileData[ID][8]),DRAG=float(projectileData[ID][9]))
def checkEnemyHover():
    mpos=(m[0]+clientPlayer.pos[0]-screenW/2,m[1]+clientPlayer.pos[1]-screenH/2)
    found=0
    for enemy in enemies:
        if not found:
            if enemy.rect.collidepoint(mpos):
                found=1
                text1=DEFAULTFONT.render(enemy.name + " " + str(math.ceil(enemy.HP)) + "/" + str(enemy.maxHP),True,(255,255,255))
                text2=DEFAULTFONT.render(enemy.name + " " + str(math.ceil(enemy.HP)) + "/" + str(enemy.maxHP),True,(0,0,0))
                
                screen.blit(text2,(m[0]-text2.get_width()/2,m[1]-39))
                screen.blit(text2,(m[0]-text2.get_width()/2,m[1]-41))
                screen.blit(text2,(m[0]-text2.get_width()/2-1,m[1]-40))
                screen.blit(text2,(m[0]-text2.get_width()/2+1,m[1]-40))
                
                screen.blit(text1,(m[0]-text1.get_width()/2,m[1]-40))
def darkenCol(col,val=0.6):
    return (col[0]*val,col[1]*val,col[2]*val)
def getBlockAverageColour(val):
    if val in platformBlocks:  
        colour=pygame.transform.average_color(tileImages[val],Rect(BLOCKSIZE/8,BLOCKSIZE/8,BLOCKSIZE*3/4,BLOCKSIZE/4))
    else:colour=pygame.transform.average_color(tileImages[val])
    return colour
def drawInventoryHoverText():
    global holdingItemBool, holdingItem, canDropHolding, canPickupItem
    found=False
    if Rect(5,20,480,244).collidepoint(m):
        for i in range(10):
            if Rect(5+48*i,20,48,48).collidepoint(m):
                found=True
                pos=["H",i]
                break
        for j in range(4):
            for i in range(10):
                if Rect(5+48*i,67+48*j,48,48).collidepoint(m):
                    found=True
                    pos=["I",(i,j)]
                    break
    if found:
        if pygame.mouse.get_pressed()[0]:
            if canDropHolding:
                unique=False
                if holdingItem.hasPrefix:
                    unique=True
                itemData=clientPlayer.giveItem(holdingItem.ID,holdingItem.amnt,pos=pos,unique=unique,item=holdingItem)
                if itemData!=None:
                    if itemData[0]==0:
                        if SFX:
                            if holdingItem.ID>=21 and holdingItem.ID<=24:
                                sounds[23].play()
                            else:
                                sounds[19].play()
                        holdingItem=None
                        holdingItemBool=False
                        canDropHolding=False
                    elif itemData[0]==1:
                        canDropHolding=False
                        holdingItem.amnt=itemData[1]
                    elif itemData[0]==2:
                        canDropHolding=False
                        if holdingItem.ID>=21 and holdingItem.ID<=24:
                            sounds[23].play()
                        else:
                            sounds[19].play()
                        if itemData[2]=="I":
                            clientPlayer.inventory[pos[1][0]][pos[1][1]]=holdingItem
                        else:
                            clientPlayer.hotbar[pos[1]]=holdingItem
                        holdingItem=itemData[1]
                    if pos not in clientPlayer.oldInventoryPositions:
                        clientPlayer.oldInventoryPositions.append(pos)
            elif canPickupItem:
                canPickupItem=False
                holdingItem=clientPlayer.removeItem(pos)
                if holdingItem!=None:
                    if SFX:
                        if holdingItem.ID>=21 and holdingItem.ID<=24:
                            sounds[23].play()
                        else:
                            sounds[19].play()
                    holdingItemBool=True
        if renderStatsText(pos) and not holdingItemBool:
            screen.blit(statsText,(m[0]+10,m[1]+10))
def drawHoldingItem():
    if holdingItemBool:
        screen.blit(itemImages[holdingItem.ID],(m[0]+10,m[1]+10))
        if holdingItem.amnt>1:
            screen.blit(outlineText(str(holdingItem.amnt),(255,255,255),SMALLFONT),(m[0]+34,m[1]+40))
def drawExitButton():
    top=screenH-20
    left=screenW-50
    if Rect(left,top,50,20).collidepoint(m):
        colour=(230,230,0)
        if pygame.mouse.get_pressed()[0]:
            Exit()
    else:colour=(255,255,255)
    text=outlineText("Quit",colour,DEFAULTFONT)
    screen.blit(text,(left,top))
noise=perlin.SimplexNoise()#create noise object
OFFSETS=[random.random()*1000,random.random()*1000,random.random()*1000]#randomly generate offsets

biomeTileVals=[[[5,0,1],[0,1]],[[2,2,3],[2,2]],[[8,8,9],[8,9]]]#tiles used in biome generation eg: [[surface tile,base tile, alt tile],[wall tile, alt wall tile]]

uncollidableBlocks=[-1,10,11,12]#blocks voided in collisions
specialBlocks=[13]#blocks drawn without masks
transparentBlocks=[13]#blocks that always have background/walls drawn behind them
platformBlocks=[13]#platforms

#name, light reduction, tags, possible prefix types, [attdamage,attspeed,critchance,size,vel,manaCost,knockback,tier,buyCost,sellPrice,stackCount]
itemData=[["Dirt",0.2,["block"],[],[None,None,None,1,None,None,None,0,None,None,999],"Looks dirty"],
          ["Stone",0.2,["block","material"],[],[None,None,None,1,None,None,None,0,None,None,999],None],
          ["Snow",0.2,["block"],[],[None,None,None,1,None,None,None,0,None,None,999],"It's starting to melt..."],
          ["Ice",0.2,["block"],[],[None,None,None,1,None,None,None,0,None,None,999],"It's icy cold."],
          ["Wood",0.2,["block","material"],[],[None,None,None,1,None,None,None,0,None,None,999],"Looks craftable."],
          ["Grass",0.2,["block"],[],[None,None,None,1,None,None,None,0,None,None,999],None],
          ["Copper",0.2,["block","material"],[],[None,None,None,1,None,None,None,0,None,None,999],"Looks maleable."],
          ["Silver",0.2,["block","material"],[],[None,None,None,1,None,None,None,0,None,None,999],"Looks maleable."],
          ["Sand",0.2,["block","material"],[],[None,None,None,1,None,None,None,0,None,None,999],"It's falling through your fingers."],
          ["Sandstone",0.2,["block"],[],[None,None,None,1,None,None,None,0,None,None,999],"It looks ancient."],
          ["Trunk",0.1,["block"],[],[None,None,None,1,None,None,None,0,None,None,999],None],
          ["Leaves",0.1,["block"],[],[None,None,None,1,None,None,None,0,None,None,999],None],
          ["Snow Leaves",0.2,["block"],[],[None,None,None,1,None,None,None,0,None,None,999],None],
          ["Platform",0,["block"],[],[None,None,None,1,None,None,None,0,None,None,999],"A good alternative to stairs."],
          ["Wooden Sword",0,["melee","weapon"],["melee","common","universal"],[7,30,0.04,40,None,None,4,0,[0,0,0,0],[0,0,0,0],1],"Go get 'em!"],
          ["Copper Sword",0,["melee","weapon"],["melee","common","universal"],[8,26,0.04,45,None,None,5,0,[0,0,0,0],[0,0,0,0],1],"Go get 'em!"],
          ["GOD SLAYER",0,["melee","weapon"],["melee","common","universal"],[10,1,0.1,100,None,None,12,10,[0,0,0,0],[0,0,0,0],1],"Divine."],
          ["Wooden Bow",0,["ranged","weapon","bow"],["ranged","common","universal"],[4,29,0.04,50,6.1,None,0,0,[0,0,0,0],[0,0,0,0],1],"Shoots pointy things."],
          ["Wooden Arrow",0,["material","ammo"],[],[None,None,None,50,None,None,None,0,[0,0,0,0],[0,0,0,0],999],"Pointy."],
          ["Musket",0,["ranged","weapon","gun"],["ranged","common","universal"],[31,65,0.04,50,14,None,3.25,0,[0,0,0,0],[0,0,0,0],1],"You know how to fire that?"],
          ["Musket Ball",0,["material","ammo"],[],[None,None,None,50,None,None,None,0,[0,0,0,0],[0,0,0,0],999],"Blunt."],
          ["Copper Coin",0,["ammo","coin"],[],[None,None,None,1,None,None,None,0,None,None,100],"Keep the change ya filthy animal."],
          ["Silver Coin",0,["ammo","coin"],[],[None,None,None,1,None,None,None,0,None,None,100],"It is cold to the touch."],
          ["Gold Coin",0,["ammo","coin"],[],[None,None,None,1,None,None,None,0,None,None,100],"oooooh, shiny..."],
          ["Platinum Coin",0,["ammo","coin"],[],[None,None,None,1,None,None,None,0,None,None,999],"You're rich!."],
          ["Copper Pickaxe",0,["pickaxe","tool"],["universal","common"],[4,25,0.04,40,None,None,2,0,None,None,1],"The power of destruction is yours."],
          ]#info on tiles

#info on enemies
#name, type, hp, defense, KB resist, Damage, blood col, itemDrops, coinDrops
enemyData=[["Green Slime","Slime",14, 0,-0.2, 6, (10,200,10),[],(5,30)],
          ["Blue Slime","Slime",  25, 2, 0,   7, (10,10,200),[],(15,50)],
          ["Red Slime","Slime",   35, 4, 0,   12,(200,10,10),[],(25,75)],
          ["Purple Slime","Slime",40, 6, 0.1, 12,(200,10,200),[],(35,110)],
          ["Yellow Slime","Slime",45, 7, 0,   15,(200,150,10),[],(45,130)],
        ]
#info on projectiles
#name, type, damage, velocity, knockback, bounces, hitboxsize, trail, gravity, drag co-efficient
projectileData=[["Wooden Arrow","Arrow",5,5,0,0,10,"arrow",0.1,0.99,16],
                ["Musket Ball","Bullet",7,10,2,0,8,"bullet",0,1,17],
                ]
prefixData={"universal":
    [#name, damage, crit chance, knockback, tier
    ["Keen",       0   ,0.03, 0   , 1],
    ["Superior",   0.1 ,0.03, 0.1 , 2],
    ["Forceful",   0   ,0   , 0.15, 1],
    ["Broken",    -0.3 ,0   ,-0.2 ,-2],
    ["Damaged",   -0.15,0   , 0   ,-1],
    ["Shoddy",    -0.1 ,0   ,-0.15,-2],
    ["Hurtful",    0.1 ,0   , 0   , 1],
    ["Strong",     0   ,0   , 0.15, 1],
    ["Unpleasant", 0.05,0   , 0.15, 2],
    ["Weak",       0   ,0   ,-0.2 ,-1],
    ["Ruthless",   0.18,0   ,-0.1 , 1],
    ["Godly",      0.15,0.05, 0.15, 2],
    ["Demonic",    0.15,0.05, 0   , 2],
    ["Zealous",    0   ,0.05, 0   , 1]
    ],
    "common":
    [#name, damage, speed, crit chance, knockback, tier
    ["Quick",     0   , 0.1 ,0   , 0   , 1],
    ["Deadly",    0.1 , 0.1 ,0   , 0   , 2],
    ["Agile",     0   , 0.1 ,0.03, 0   , 1],
    ["Nimble",    0   , 0.05,0   , 0   , 1],
    ["Murderous",-0.07, 0.06,0.03, 0   , 2],
    ["Slow",      0   ,-0.15,0   , 0   ,-1],
    ["Sluggish",  0   ,-0.2 ,0   , 0   ,-2],
    ["Lazy",      0   ,-0.08,0   , 0   ,-1],
    ["Annoying", -0.2 ,-0.15,0   , 0   ,-2],
    ["Nasty",     0.05, 0.1 ,0.02,-0.1 , 1]
    ],
    "melee":
    [#name, damage, speed, crit chance, size, knockback, tier
    ["Large",     0   , 0   ,0   , 0.12, 0   , 1],
    ["Massive",   0   , 0   ,0   , 0.18, 0   , 1],
    ["Dangerous", 0.05, 0   ,0.02, 0.05, 0   , 1],
    ["Savage",    0.1 , 0   ,0   , 0.1 , 0.1 , 2],
    ["Sharp",     0.15, 0   ,0   , 0   , 0   , 1],
    ["Pointy",    0.1 , 0   ,0   , 0   , 0   , 1],
    ["Tiny",      0   , 0   ,0   ,-0.18, 0   ,-1],
    ["Terrible", -0.15, 0   ,0   ,-0.13,-0.15,-2],
    ["Small",     0   , 0   ,0   ,-0.1 , 0   ,-1],
    ["Dull",     -0.15, 0   ,0   , 0   , 0   ,-1],
    ["Unhappy",   0   ,-0.1 ,0   ,-0.1 ,-0.1 ,-2],
    ["Bulky",     0.05,-0.15,0   , 0.1 , 0.1 , 1],
    ["Shameful", -0.1 , 0   ,0   , 0.1 ,-0.2 ,-2],
    ["Heavy",     0   ,-0.1 ,0   , 0   , 0.15, 0],
    ["Light",     0   , 0.15,0   , 0   ,-0.1 , 0],
    ["Legendary", 0.15, 0.1 ,0.05, 0.1 , 0.15, 2]
    ],
    "ranged":
    [#name, damage, speed, crit chance, velocity, knockback, tier
    ["Sighted",      0.1 , 0   ,0.03, 0   , 0   , 1],
    ["Rapid",        0   , 0.15,0   , 0.1 , 0   , 2],
    ["Hasty",        0   , 0.1 ,0   , 0.15, 0   , 2],
    ["Intimidating", 0   , 0   ,0   , 0.05, 0.15, 2],
    ["Deadly",       0.1 , 0.05,0.02, 0.05, 0.05, 2],
    ["Staunch",      0.1 , 0   ,0   , 0   , 0.15, 2],
    ["Awful",       -0.15, 0   ,0   ,-0.1 ,-0.1 ,-2],
    ["Lethargic",    0   , 0.15,0   ,-0.1 , 0   ,-2],
    ["Awkward",      0   ,-0.1 ,0   , 0   ,-0.2 ,-2],
    ["Powerful",     0.15,-0.1 ,0.01, 0   , 0   , 1],
    ["Frenzying",   -0.15, 0.15,0   , 0   , 0   , 0],
    ["Unreal",       0.15, 0.1 ,0.05, 0.1 , 0.15, 2],
    ["ADMIN",        0.5 , 0.5 ,1   , 1   , 1   , 11],
    ["fucked",      -1   , 0   ,0   , -1  , 0   , -10]
    ],
    "magic":
    [#name, damage, speed, crit chance, mana cost, knockback, tier
    ["Mystic",    0.1 , 0   ,0   ,-0.15, 0   , 2],
    ["Adept",     0   , 0   ,0   ,-0.15, 0   , 1],
    ["Masterful", 0.15, 0   ,0   ,-0.2 , 0.05, 2],
    ["Inept",     0   , 0   ,0   , 0.1 , 0   ,-1],
    ["Ignorant", -0.1 , 0   ,0   , 0.2 , 0   ,-2],
    ["Deranged", -0.1 , 0   ,0   , 0   ,-0.1 ,-1],
    ["Intense",   0.1 , 0   ,0   , 0.15, 0   ,-1],
    ["Taboo",     0   , 0.1 ,0   , 0.1 , 0.1 , 1],
    ["Celestial", 0.1 ,-0.1 ,0   ,-0.1 , 0.1 , 1],
    ["Furious",   0.15, 0   ,0   , 0.2 , 0.15, 1],
    ["Manic",    -0.1 , 0.1 ,0   ,-0.1 , 0   , 1],
    ["Mythical",  0.15, 0.1 ,0.05,-0.1 , 0.15, 2]
    ]
            
            }

deathLines={"falling":["<p> fell to their death.",
                       "<p> didn't bounce.",
                       "<p> fell victim of gravity.",
                       "<p> faceplanted the ground.",
                       "<p> left a small crater.",
                       "<p> was crushed into <w>.",
                       ],
            "enemy":["<p> was slain by <e>.",
                    "<p> was eviscerated by <e>.",
                    "<p> was murdered by <e>.",
                    "<p>'s face was torn off by <e>.",
                    "<p>'s entrails were ripped out by <e>.",
                    "<p> was destroyed by <e>.",
                    "<p>'s skull was crushed by <e>.",
                    "<p> got massacred by <e>.",
                    "<p> got impaled by <e>.",
                    "<p> was torn in half by <e>.",
                    "<p> was decapitated by <e>.",
                    "<p> let their arms get torn off by <e>.",
                    "<p> watched their innards become outards by <e>.",
                    "<p> was brutally dissected by <e>.",
                    "<p>'s extremities were detached by <e>.",
                    "<p>'s body was mangled by <e>.",
                    "<p>'s vital organs were ruptured by <e>.",
                    "<p> was turned into a pile of flesh by <e>.",
                    "<p> was removed from <w> by <e>.",
                    "<p> got snapped in half by <e>.",
                    "<p> was cut down the middle by <e>.",
                    "<p> was chopped up by <e>.",
                    "<p>'s plead for death was answered by <e>.",
                    "<p>'s meat was ripped off the bone by <e>.",
                    "<p>'s flailing about was finally stopped by <e>.",
                    "<p> had their head removed by <e>.",
                    "<e> fucked up <p> in <w>.",
                    "<p> got cucked by <e>.",
                    "<p> was sent to another plane by <e>",
                    "The creatures of <w> took <p> to their demise.",
                    "<p>'s particles were distributed across <w>."
                     ]}
helpfulTips=["Watch out for slimes...",
             "Now with over 20 items!",
             "Don't die! I need your business!",
             "Mentally prepare yourself...",
             "So, ya like jazz?",
             "Doesn’t expecting the unexpected make the unexpected expected?",
             "1f you c4n r34d 7h15, you r34lly n33d 2 g37 l41d",
             "What do you call a thieving alligator? A Crookodile",
             "If you were a fruit, you'd be a fine-apple",
             "How do you organize a space party?           You planet.",
             "What do you call a classy fish?             Sofishticated.",
             "Did you hear about the guy whose whole left side was cut off? He's all right now.",
             "I wondered why the baseball was getting bigger. Then it hit me.",
             ]
goodColour=(10,230,10)
badColour=(230,10,10)

particles=[]
enemies=[]
projectiles=[]
physicsItems=[]
messages=[]
damageNumbers=[]
enemySpawnTick=0
#MAX SURF WIDTH IS 16383

loadConfig()#(1920,1080),(1280, 720), (1152, 864), (1024, 768), (800, 600)
BLOCKSIZE=16
BIOMEBOARDER_X1=MAPSIZEX/3
BIOMEBOARDER_X2=MAPSIZEX*2/3

WORLDBOARDER_WEST=int(BLOCKSIZE)
WORLDBOARDER_EAST=int(MAPSIZEX*BLOCKSIZE-BLOCKSIZE)
WORLDBOARDER_NORTH=int(BLOCKSIZE*1.5)
WORLDBOARDER_SOUTH=int(MAPSIZEY*BLOCKSIZE-BLOCKSIZE*1.5)

defaultModel=Model(0,random.randint(0,7),(random.randint(0,128),random.randint(0,128),random.randint(0,128)),(0,0,200),(),(),(),())
playerWidth=26
playerHeight=48

loadPlayerData()

loadSaves()


if RUNFULLSCREEN:screen=pygame.display.set_mode((screenW,screenH),FULLSCREEN)
else:screen=pygame.display.set_mode((screenW,screenH))

pygame.display.set_caption("fegaria remastered "+__version__)
#set to 8000 for creepy mode (48000 norm)
pygame.mixer.pre_init(48000, -16, 2, 1024)
pygame.init()
musicVolume=0.2

SONG_END = pygame.USEREVENT+1
pygame.mixer.music.set_endevent(SONG_END)

if MUSIC:
    pygame.mixer.music.load("Sound/day.mp3")
    pygame.mixer.music.set_volume(musicVolume)
    pygame.mixer.music.play()

if SFX:
    sounds=[]
    sounds.append(pygame.mixer.Sound("Sound/Tink_0.wav"))#0
    sounds.append(pygame.mixer.Sound("Sound/Tink_1.wav"))#1
    sounds.append(pygame.mixer.Sound("Sound/Tink_2.wav"))#2
    sounds.append(pygame.mixer.Sound("Sound/Dig_0.wav"))#3
    sounds.append(pygame.mixer.Sound("Sound/Dig_1.wav"))#4
    sounds.append(pygame.mixer.Sound("Sound/Dig_2.wav"))#5
    sounds.append(pygame.mixer.Sound("Sound/Jump_0.wav"))#6
    sounds.append(pygame.mixer.Sound("Sound/Player_Hit_0.wav"))#7
    sounds.append(pygame.mixer.Sound("Sound/Player_Hit_1.wav"))#8
    sounds.append(pygame.mixer.Sound("Sound/Player_Hit_2.wav"))#9
    sounds.append(pygame.mixer.Sound("Sound/Grass.wav"))#10
    sounds.append(pygame.mixer.Sound("Sound/Player_Killed.wav"))#11
    sounds.append(pygame.mixer.Sound("Sound/Item_6.wav"))#12
    sounds.append(pygame.mixer.Sound("Sound/NPC_Hit_1.wav"))#13
    sounds.append(pygame.mixer.Sound("Sound/NPC_Killed_1.wav"))#14
    sounds.append(pygame.mixer.Sound("Sound/Item_1.wav"))#15
    sounds.append(pygame.mixer.Sound("Sound/Item_5.wav"))#16
    sounds.append(pygame.mixer.Sound("Sound/Item_40.wav"))#17
    sounds.append(pygame.mixer.Sound("Sound/Item_10.wav"))#18
    sounds.append(pygame.mixer.Sound("Sound/Grab.wav"))#19
    sounds.append(pygame.mixer.Sound("Sound/Run_0.wav"))#20
    sounds.append(pygame.mixer.Sound("Sound/Run_1.wav"))#21
    sounds.append(pygame.mixer.Sound("Sound/Run_2.wav"))#22
    sounds.append(pygame.mixer.Sound("Sound/Coins.wav"))#23
    for sound in sounds:
        sound.set_volume(0.5)



loadTorsoFrames()
loadHairStyles() 
loadTileMasks()
loadTiles()
loadBackgroundImages()
loadProjectileImages()
compileBackgroundImages()
loadWallTiles()
loadSlimeFrames()
loadItemTiles()
loadMiscGui()

fontFilePath="Fonts/VCR_OSD_MONO_1.001.ttf"

LARGEFONT=pygame.font.Font(fontFilePath,30)
DEFAULTFONT=pygame.font.Font(fontFilePath,16)
SMALLFONT=pygame.font.Font(fontFilePath,10)

createPlayer()

clock=pygame.time.Clock()

if SPLASHSCREEN:
    runSplashScreen()
    
screen.fill((0,0,0))
text0=outlineText("Greetings "+clientPlayer.name+", bare with us while",(255,255,255),LARGEFONT)
text1=outlineText("we load up '"+clientWorld.name+"'...",(255,255,255),LARGEFONT)
text2=outlineText(helpfulTips[random.randint(0,len(helpfulTips)-1)],(255,255,255),DEFAULTFONT)
screen.blit(text0,(screenW/2-text0.get_width()/2,screenH/2-30))
screen.blit(text1,(screenW/2-text1.get_width()/2,screenH/2))
screen.blit(text2,(screenW/2-text2.get_width()/2,screenH*4/5))
pygame.display.flip()

createSurface()


clientPlayer.pos=tuple(clientWorld.spawnPoint)

fadeBack=False
shift=False
fadeFloat=0
fadeBackgroundID=-1
backgroundTick=0
backgroundScrollVel=0
autoSaveTick=0
autoSaveDelay=3600#every minute
gameAge=0
fps=0
fpsTick=0
lastHoveredItem=None
parallaxPos=(0,0)
holdingItemBool=False
holdingItem=None
canDropHolding=False
canPickupItem=False

clientPlayer.renderCurrentItemImage()
clientPlayer.renderHotbar()
clientPlayer.renderInventory()
fpsText=outlineText(str(int(fps)),(255,255,255),DEFAULTFONT)
renderHandText()

while 1:
    fps=clock.get_fps()
    try:
        clientWorld.playTime+=1/fps
        clientPlayer.playTime+=1/fps
        gameAge+=1/fps
    except:None#fps is zero
    
    m=pygame.mouse.get_pos()
    
    updateEnemies()
    updateProjectiles()
    updateParticles()
    updateMessages()
    updatePhysicsItems()
    checkEnemySpawn()
    clientPlayer.update()
    clientPlayer.animate()
    updateDamageNumbers()
    
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
    drawEnemies()
    drawPhysicsItems()
    drawProjectiles()
    drawDamageNumbers()
    drawMessages()
    checkEnemyHover()
    
##    if not clientPlayer.inventoryOpen:
##        screen.blit(handText,(0,60))
##        screen.blit(hpText,(0,80))
##        if statsVisible:
##            screen.blit(statsText,(0,100))
        
    
    screen.blit(fpsText,(screenW-fpsText.get_width(),0))

    screen.blit(clientPlayer.hotbarImage,(5,20))
    if clientPlayer.inventoryOpen:
        screen.blit(clientPlayer.inventoryImage,(5,70))
    pygame.draw.rect(screen,(230,230,10),Rect(5+clientPlayer.hotbarIndex*48,20,48,48),3)
    if clientPlayer.inventoryOpen:
        drawInventoryHoverText()
        drawExitButton()
    screen.blit(handText,(242-handText.get_width()/2,0))
    drawHoldingItem()
    
    if BACKGROUND:
        changeBackground()
        moveParallax((backgroundScrollVel,0))
        
    if autoSaveTick<=0:
        autoSaveTick=autoSaveDelay
        Save()
    else:autoSaveTick-=1

    if fpsTick<=0:
        fpsTick=100
        fpsText=outlineText(str(int(fps)),(255,255,255),DEFAULTFONT)
    else:fpsTick-=1

    if not pygame.mouse.get_pressed()[0]:
        if holdingItemBool:
            canDropHolding=True
        elif not holdingItemBool:
            canPickupItem=True
        
    for event in pygame.event.get():
        if event.type==QUIT:
            Exit()
        if event.type==SONG_END:
            pygame.mixer.music.load("Sound/day.mp3")
            pygame.mixer.music.set_volume(musicVolume)
            pygame.mixer.music.play()
        if event.type==KEYDOWN:
            if event.key==K_LSHIFT:
                shift=True
            if event.key==K_ESCAPE:
                if clientPlayer.inventoryOpen:
                    clientPlayer.inventoryOpen=False
                else:
                    clientPlayer.inventoryOpen=True
            if event.key==K_a:
                clientPlayer.movingLeft=True
                clientPlayer.animationFrame=random.randint(25,36)
                if clientPlayer.direction==1:
                    clientPlayer.itemSwing=False
                clientPlayer.direction=0
            if event.key==K_d:
                clientPlayer.movingRight=True
                clientPlayer.animationFrame=random.randint(5,17)
                if clientPlayer.direction==0:
                    clientPlayer.itemSwing=False
                clientPlayer.direction=1
            if pygame.key.get_mods() & KMOD_LSHIFT:
                if event.key==K_s:
                    clientWorld.spawnPoint=tuple(clientPlayer.pos)
                    print("Spawn point moved to "+str(clientWorld.spawnPoint))
            if event.key==K_s:
                clientPlayer.movingDown=True
                clientPlayer.animationSpeed=4
            if event.key==K_k:
                while len(enemies)>0:
                    enemies[0].kill()
            if event.key==K_SPACE:
                if clientPlayer.alive:
                    if clientPlayer.grounded:
                        if SFX:
                            sounds[6].play()
                        if PARTICLES:
                            colour=getBlockAverageColour(clientPlayer.lastBlockOn)
                            for i in range(int(random.randint(4,6)*PARTICLEDENSITY)):
                                Particle((screenW/2,screenH/2+BLOCKSIZE*1.5),colour,size=10,life=100,angle=-math.pi/2,spread=math.pi/4,GRAV=0,magnitude=1+random.random()*3)
                        clientPlayer.vel=(clientPlayer.vel[0],-8.5)
                        clientPlayer.grounded=False
            if event.key==K_r:
                clientPlayer.model.hairCol=(random.randint(0,128),random.randint(0,128),random.randint(0,128))
                clientPlayer.model.hairID=random.randint(0,7)
                clientPlayer.renderSprites()
                message("Hair randomized!",(random.randint(0,255),random.randint(0,255),random.randint(0,255)),life=500)
            if event.key==K_j:
                if PARTICLES:
                    for i in range(int(40*PARTICLEDENSITY)):
                        Particle((screenW/2,screenH/2),(230,230,255),magnitude=1+random.random()*1,size=15,GRAV=0)
                if SFX:
                    sounds[12].play()
                clientPlayer.respawn()
            if event.key==K_g:
                GRAVITY=-GRAVITY;print("Gravity Reversed")
            if event.key==K_p:
                clientPlayer.hotbar[clientPlayer.hotbarIndex]=Item(clientPlayer.hotbar[clientPlayer.hotbarIndex].ID)
                message("Item prefix randomized!",(random.randint(0,255),random.randint(0,255),random.randint(0,255)),life=500)
                clientPlayer.renderCurrentItemImage()
                renderHandText()
                statsVisible=True
                statDisappearTick=500
                
            if event.key==K_1:clientPlayer.hotbarIndex=0;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
            if event.key==K_2:clientPlayer.hotbarIndex=1;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
            if event.key==K_3:clientPlayer.hotbarIndex=2;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
            if event.key==K_4:clientPlayer.hotbarIndex=3;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
            if event.key==K_5:clientPlayer.hotbarIndex=4;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
            if event.key==K_6:clientPlayer.hotbarIndex=5;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
            if event.key==K_7:clientPlayer.hotbarIndex=6;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
            if event.key==K_8:clientPlayer.hotbarIndex=7;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
            if event.key==K_9:clientPlayer.hotbarIndex=8;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
            if event.key==K_0:clientPlayer.hotbarIndex=9;clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()

            if event.key==K_UP and shift:
                musicVolume+=0.05
                if musicVolume>1:musicVolume=1
                pygame.mixer.music.set_volume(musicVolume)
            if event.key==K_DOWN and shift:
                musicVolume-=0.05
                if musicVolume<0:musicVolume=0
                pygame.mixer.music.set_volume(musicVolume)

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
                
        if event.type==MOUSEBUTTONDOWN:
            if event.button==4:
                if clientPlayer.hotbarIndex>0:
                    clientPlayer.hotbarIndex-=1
                    clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
                else:
                    clientPlayer.hotbarIndex=9
            if event.button==5:
                if clientPlayer.hotbarIndex<9:
                    clientPlayer.hotbarIndex+=1
                    clientPlayer.renderCurrentItemImage();clientPlayer.itemSwing=False;renderHandText()
                else:
                    clientPlayer.hotbarIndex=0
    pygame.display.flip()
    clock.tick(80)
