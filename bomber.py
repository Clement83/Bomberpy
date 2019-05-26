from gamebuino_meta import waitForUpdate, display, color, buttons
from micropython import const
from random import *

SCREEN_WIDTH  = const(80)
SCREEN_HEIGHT = const(64)

COLOR_BG      = color.BROWN
COLOR_WALL    = color.BLACK
COLOR_WALL_2  = color.DARKGRAY
COLOR_PLAYER1 = color.PURPLE
COLOR_BOMBE = color.PINK
COLOR_BOMBE_ALT = color.RED
COLOR_FLAME = color.YELLOW

ELEMENT_COTE = const(8)

TIME_TO_BOOM = const(48)
FLAME_TIME_TO_LIVE = const(5)
FLAME_MAX_ITERATION = const(2)

IDLE = const(0)
MOVE_UP = const(1)
MOVE_RIGHT = const(2)
MOVE_DOWN = const(3)
MOVE_LEFT = const(4)
MOVE_SPEED = const(2) 

MAP_WALL_BREAKABLE = const(100)
MAP_WALL_UNBREAKABLE = const(200)
MAP_BOMBE = const(150)

MAP_FLAME = const(90)
MAP_DANGER = const(10)
MAP_VOID = const(0)

map =[
[MAP_VOID,MAP_WALL_BREAKABLE,MAP_VOID,MAP_WALL_BREAKABLE,MAP_VOID,MAP_VOID,MAP_VOID,MAP_VOID,MAP_WALL_BREAKABLE,MAP_VOID],
[MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_VOID],
[MAP_VOID,MAP_VOID,MAP_VOID,MAP_WALL_BREAKABLE,MAP_VOID,MAP_VOID,MAP_VOID,MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_VOID],
[MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_WALL_BREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_VOID],
[MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_BREAKABLE,MAP_WALL_UNBREAKABLE,MAP_VOID],
[MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_VOID,MAP_VOID,MAP_VOID,MAP_VOID,MAP_WALL_BREAKABLE,MAP_VOID,MAP_VOID,MAP_VOID],
[MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_VOID,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_WALL_UNBREAKABLE,MAP_VOID],
[MAP_VOID,MAP_WALL_BREAKABLE,MAP_VOID,MAP_VOID,MAP_VOID,MAP_VOID,MAP_WALL_BREAKABLE,MAP_VOID,MAP_WALL_BREAKABLE,MAP_VOID],
]

bombes = []
flames = []
players = []

class Entity:
    def __init__(self, x, y):
        self.posX = x
        self.posY = y
        
        # bombe
        self.timeActive = 0

        # user 
        self.nexDir = IDLE
        self.currentDir = IDLE
        self.ia = False
        
        # flame
        self.timeFlame = FLAME_TIME_TO_LIVE
        self.direction = IDLE
        self.iteration = 0
        self.maxIteration = 0
    
def isInMap(x, y):
    if x < 0:
        return False
    if x + ELEMENT_COTE > SCREEN_WIDTH:
        return False
    if y < 0:
        return False
    if y + ELEMENT_COTE > SCREEN_HEIGHT:
        return False
    return True

def setValueToMap(x, y, value):
    map[y//8][x//8] = value

def getValueToMap(x, y):
    return map[y//8][x//8]

###################################################################################
# ### Player
# #################################################################################
def initPlayer(x, y, ia):
    player = Entity(x, y)
    player.nexDir = IDLE
    player.currentDir = IDLE
    players.append(player)
    player.ia = ia

def updatePlayer(player):
    if player.ia == False:
        handleButtons(player)
        
    if player.ia == True:
        moveIa(player)
    movePlayer(player)

def drawPlayer(player):
    display.setColor(COLOR_PLAYER1)
    display.fillRect(player.posX, player.posY, ELEMENT_COTE, ELEMENT_COTE)

def movePlayer(player):
    nextX = player.posX
    nextY = player.posY
    nextCaseX = player.posX
    nextCaseY = player.posY

    if player.currentDir == IDLE:
        player.currentDir = player.nexDir
        player.nexDir = IDLE

    if player.currentDir == MOVE_RIGHT:
        nextX += MOVE_SPEED
        nextCaseX += 8

    if player.currentDir == MOVE_LEFT:
        nextX -= MOVE_SPEED
        nextCaseX = nextX
        
    if player.currentDir == MOVE_UP:
        nextY -= MOVE_SPEED
        nextCaseY = nextY
        
    if player.currentDir == MOVE_DOWN:
        nextY += MOVE_SPEED
        nextCaseY += 8
    
    if canMovePlayer(player, nextX, nextY, nextCaseX, nextCaseY):
        player.posX = nextX
        player.posY = nextY
        if (player.currentDir == MOVE_LEFT or player.currentDir == MOVE_RIGHT) and nextX % ELEMENT_COTE == 0:
            player.currentDir = IDLE
        if (player.currentDir == MOVE_UP or player.currentDir == MOVE_DOWN) and nextY % ELEMENT_COTE == 0:
            player.currentDir = IDLE
    else:
        player.currentDir = IDLE
        player.nexDir = IDLE

def canMovePlayer(player, x, y, xNextCase, yNextCase):
    
    if isInMap(x, y) == False:
        return False

    if getValueToMap(xNextCase, yNextCase) >= MAP_WALL_BREAKABLE:
        return False

    return True

def moveIa(player):
    player.nexDir = randint(1,4)
    if randint(0,100) == 0:
        initBombe(player.posX, player.posY)

def handleButtons(player):
    if buttons.repeat(buttons.LEFT, 0):
        player.nexDir = MOVE_LEFT
    elif buttons.repeat(buttons.RIGHT, 0):
        player.nexDir = MOVE_RIGHT
    elif buttons.repeat(buttons.UP, 0):
        player.nexDir = MOVE_UP
    elif buttons.repeat(buttons.DOWN, 0):
        player.nexDir = MOVE_DOWN
    
    if buttons.repeat(buttons.A, 5):
        initBombe(player.posX, player.posY)

###################################################################################
# ### Flame
# #################################################################################
def initFlame(x, y, direction, maxIteration, iteration):
    flame = Entity(x, y)
    flame.timeFlame = FLAME_TIME_TO_LIVE
    flame.direction = direction
    flame.iteration = iteration
    flame.maxIteration = maxIteration
    flames.append(flame)

def isAliveFlame(flame):
    return flame.timeFlame > 0

def drawFlame(flame):
    display.setColor(COLOR_FLAME)
    display.fillRect(flame.posX, flame.posY, ELEMENT_COTE, ELEMENT_COTE)

def updateFlame(flame):
    destroyWall(flame)
    if getValueToMap(flame.posX, flame.posY) == MAP_WALL_BREAKABLE:
        flame.iteration = flame.maxIteration
    setValueToMap(flame.posX, flame.posY, MAP_FLAME)
    if flame.timeFlame == FLAME_TIME_TO_LIVE and flame.maxIteration > flame.iteration:
        nextIteration = flame.iteration + 1
        if flame.direction == MOVE_DOWN or flame.direction == IDLE and canBurn(flame, flame.posX + 8, flame.posY):
            initFlame(flame.posX + 8, flame.posY, MOVE_DOWN, flame.maxIteration, nextIteration)
        
        if flame.direction == MOVE_UP or flame.direction == IDLE and canBurn(flame, flame.posX - 8, flame.posY):
            initFlame(flame.posX - 8, flame.posY, MOVE_UP, flame.maxIteration, nextIteration)
        
        if flame.direction == MOVE_RIGHT or flame.direction == IDLE and canBurn(flame, flame.posX, flame.posY + 8):
            initFlame(flame.posX , flame.posY + 8, MOVE_RIGHT, flame.maxIteration, nextIteration)
        
        if flame.direction == MOVE_LEFT or flame.direction == IDLE and canBurn(flame, flame.posX, flame.posY - 8):
            initFlame(flame.posX, flame.posY - 8, MOVE_LEFT, flame.maxIteration, nextIteration)

    if flame.timeFlame>0:
        flame.timeFlame -= 1

def canBurn(flame, x, y):
    if isInMap(x, y) == False:
        return False
    return getValueToMap(x,y) < MAP_WALL_UNBREAKABLE

def destroyWall(flame):
    if isInMap(flame.posX, flame.posY) and getValueToMap(flame.posX, flame.posY) == MAP_WALL_BREAKABLE:
        setValueToMap(flame.posX, flame.posY, MAP_VOID)
        flame.iteration = flame.maxIteration

###################################################################################
# ### Bombe
# #################################################################################
def initBombe(x, y):
    bombe = Entity(0, 0)
    bombe.timeActive = 0
    acivateBombe(bombe, x // 8 * 8, y // 8 * 8)
    bombes.append(bombe)
    setValueToMap(x, y, MAP_BOMBE)

def isAliveBombe(bombe):
    return bombe.timeActive>0

def drawBombe(bombe):
    if bombe.timeActive > 0 :
        if bombe.timeActive % 5 == 0:
            display.setColor(COLOR_BOMBE)
        else : 
            display.setColor(COLOR_BOMBE_ALT)
        halfElement = (ELEMENT_COTE//2)
        display.fillCircle(bombe.posX+halfElement, bombe.posY+halfElement, halfElement)

def updateBombe(bombe) :
    if getValueToMap(bombe.posX, bombe.posY) == MAP_FLAME:
       bombe.timeActive = 0 
    if bombe.timeActive > 0 :
        bombe.timeActive -= 1
    if bombe.timeActive == 0:
        initFlame(bombe.posX, bombe.posY, IDLE, FLAME_MAX_ITERATION, 0)

def acivateBombe(bombe, x, y):
    bombe.posX = x
    bombe.posY = y
    bombe.timeActive = TIME_TO_BOOM


###################################################################################
# ### Gmae engine
# #################################################################################


def draw():
    display.clear(COLOR_BG)
    for player in players:
        drawPlayer(player)

    for lineIndex in range(len(map)):
        for colIndex in range(len(map[lineIndex])):
            if map[lineIndex][colIndex] == MAP_WALL_BREAKABLE:
                display.setColor(COLOR_WALL)
                display.fillRect(colIndex * ELEMENT_COTE, lineIndex * ELEMENT_COTE, ELEMENT_COTE, ELEMENT_COTE)
            elif map[lineIndex][colIndex] == MAP_WALL_UNBREAKABLE:
                display.setColor(COLOR_WALL_2)
                display.fillRect(colIndex * ELEMENT_COTE, lineIndex * ELEMENT_COTE, ELEMENT_COTE, ELEMENT_COTE)
    
    for bombe in bombes:
        drawBombe(bombe)
    for flame in flames:
        drawFlame(flame)

def update():
    for player in players:
        updatePlayer(player)

    for bombe in bombes:
        if isAliveBombe(bombe) == False:
            bombes.remove(bombe)
    for bombe in bombes:
        updateBombe(bombe)
    
    for flame in flames:
        if isAliveFlame(flame) == False:
            flames.remove(flame)
    for flame in flames:
        updateFlame(flame)

def run():
    initPlayer(0, 0, False)
    initPlayer(72, 56, True)
    while True:
        waitForUpdate()
        update()
        draw()