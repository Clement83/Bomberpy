from gamebuino_meta import waitForUpdate, display, color, buttons
from micropython import const

SCREEN_WIDTH  = const(80)
SCREEN_HEIGHT = const(64)

COLOR_BG      = const(color.BROWN)
COLOR_WALL    = const(color.BLACK)
COLOR_WALL_2  = const(color.DARKGRAY)
COLOR_PLAYER1 = const(color.PURPLE)
COLOR_BOMBE = const(color.PINK)
COLOR_BOMBE_ALT = const(color.RED)
COLOR_FLAME = const(color.YELLOW)

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
    
    def isInMap(self, x, y):
        if x < 0:
            return False
        if x + ELEMENT_COTE > SCREEN_WIDTH:
            return False
        if y < 0:
            return False
        if y + ELEMENT_COTE > SCREEN_HEIGHT:
            return False

class Player(Entity):

    def __init__(self, x, y):
        Entity.__init__(self, x, y)
        self.nexDir = IDLE
        self.currentDir = IDLE

    def update(self):
        self.handleButtons()
        self.move()

    def draw(self):
        display.setColor(COLOR_PLAYER1)
        display.fillRect(self.posX, self.posY, ELEMENT_COTE, ELEMENT_COTE)
    
    def move(self):
        nextX = self.posX
        nextY = self.posY
        nextCaseX = self.posX
        nextCaseY = self.posY

        if self.currentDir == IDLE:
            self.currentDir = self.nexDir
            self.nexDir = IDLE

        if self.currentDir == MOVE_RIGHT:
            nextX += MOVE_SPEED
            nextCaseX += 8

        if self.currentDir == MOVE_LEFT:
            nextX -= MOVE_SPEED
            nextCaseX = nextX
            
        if self.currentDir == MOVE_UP:
            nextY -= MOVE_SPEED
            nextCaseY = nextY
            
        if self.currentDir == MOVE_DOWN:
            nextY += MOVE_SPEED
            nextCaseY += 8
        
        if self.canMove(nextX, nextY, nextCaseX, nextCaseY):
            self.posX = nextX
            self.posY = nextY
            if (self.currentDir == MOVE_LEFT or self.currentDir == MOVE_RIGHT) and nextX % ELEMENT_COTE == 0:
                self.currentDir = IDLE
            if (self.currentDir == MOVE_UP or self.currentDir == MOVE_DOWN) and nextY % ELEMENT_COTE == 0:
                self.currentDir = IDLE
        else:
            self.currentDir = IDLE
            self.nexDir = IDLE

    def canMove(self, x, y, xNextCase, yNextCase):
        
        if self.isInMap(x, y) == False:
            return False

        if map[(yNextCase//8)][(xNextCase//8)] != MAP_VOID:
            return False

        return True

    def handleButtons(self):
        if buttons.repeat(buttons.LEFT, 0):
            self.nexDir = MOVE_LEFT
        elif buttons.repeat(buttons.RIGHT, 0):
            self.nexDir = MOVE_RIGHT
        elif buttons.repeat(buttons.UP, 0):
            self.nexDir = MOVE_UP
        elif buttons.repeat(buttons.DOWN, 0):
            self.nexDir = MOVE_DOWN
        
        if buttons.repeat(buttons.A, 5):
            bombe = Bombe()
            bombe.acivate(self.posX // 8 * 8, self.posY // 8 * 8)
            bombes.append(bombe)

class Flame(Entity):
    def __init__(self, x, y, direction, maxIteration, iteration):
        Entity.__init__(self, x, y)
        self.timeFlame = FLAME_TIME_TO_LIVE
        self.direction = direction
        self.iteration = iteration
        self.maxIteration = maxIteration
    
    def isAlive(self):
        return self.timeFlame>0

    def draw(self):
        display.setColor(COLOR_FLAME)
        display.fillRect(self.posX, self.posY, ELEMENT_COTE, ELEMENT_COTE)
    
    def update(self):
        self.destroyWall()
        if self.timeFlame == FLAME_TIME_TO_LIVE and self.maxIteration > self.iteration:
            nextIteration = self.iteration + 1
            if self.direction == MOVE_DOWN or self.direction == IDLE and \
                 self.canBurn(self.posX + 8, self.posY):
                    flames.append(Flame(self.posX + 8, self.posY, MOVE_DOWN, self.maxIteration, nextIteration))
            
            if self.direction == MOVE_UP or self.direction == IDLE and \
                self.canBurn(self.posX + 8, self.posY):
                    flames.append(Flame(self.posX - 8, self.posY, MOVE_UP, self.maxIteration, nextIteration))
            
            if self.direction == MOVE_RIGHT or self.direction == IDLE and \
                self.canBurn(self.posX, self.posY + 8):
                    flames.append(Flame(self.posX, self.posY + 8, MOVE_RIGHT, self.maxIteration, nextIteration))
            
            if self.direction == MOVE_LEFT or self.direction == IDLE and \
                self.canBurn(self.posX, self.posY - 8):
                    flames.append(Flame(self.posX, self.posY - 8, MOVE_LEFT, self.maxIteration, nextIteration))

        if self.timeFlame>0:
            self.timeFlame -= 1

    def canBurn(self, x, y):
        if self.isInMap(x, y) == False:
            return False
        return map[y//8][x//8] < MAP_WALL_UNBREAKABLE

    def destroyWall(self):
        indexX = self.posX // 8
        indexY = self.posY // 8
        if self.isInMap(indexX, indexY) and \
             map[indexY][indexX] == MAP_WALL_BREAKABLE:
                map[indexY][indexX] = MAP_VOID

class Bombe(Entity):
    def __init__(self):
        Entity.__init__(self, 0, 0)
        self.timeActive = 0

    def isAlive(self):
        return self.timeActive>0

    def draw(self):
        if self.timeActive > 0 :
            if self.timeActive % 5 == 0:
                display.setColor(COLOR_BOMBE)
            else : 
                display.setColor(COLOR_BOMBE_ALT)
            halfElement = (ELEMENT_COTE//2)
            display.fillCircle(self.posX+halfElement, self.posY+halfElement, halfElement)
    
    def update(self) :
        if self.timeActive > 0 :
            self.timeActive -= 1
        if self.timeActive == 0:
            flames.append(Flame(self.posX, self.posY, IDLE, FLAME_MAX_ITERATION, 0))

    def acivate(self, x, y):
        self.posX = x
        self.posY = y
        self.timeActive = TIME_TO_BOOM

class GameEngine:

    def __init__(self):
        players.append(Player(0, 0))

    def draw(self):
        display.clear(COLOR_BG)
        for player in players:
 	        player.draw()

        for lineIndex in range(len(map)):
            for colIndex in range(len(map[lineIndex])):
                if map[lineIndex][colIndex] == MAP_WALL_BREAKABLE:
                    display.setColor(COLOR_WALL)
                    display.fillRect(colIndex * ELEMENT_COTE, lineIndex * ELEMENT_COTE, ELEMENT_COTE, ELEMENT_COTE)
                elif map[lineIndex][colIndex] == MAP_WALL_UNBREAKABLE:
                    display.setColor(COLOR_WALL_2)
                    display.fillRect(colIndex * ELEMENT_COTE, lineIndex * ELEMENT_COTE, ELEMENT_COTE, ELEMENT_COTE)
        
        for bombe in bombes:
 	        bombe.draw()
        for flame in flames:
 	        flame.draw()

    def update(self):
        for player in players:
 	        player.update()

        for bombe in bombes:
            if bombe.isAlive() == False:
                bombes.remove(bombe)
        for bombe in bombes:
            bombe.update()
        
        for flame in flames:
            if flame.isAlive() == False:
                flames.remove(flame)
        for flame in flames:
            flame.update()

    def run(self):
        while True:
            waitForUpdate()
            self.update()
            self.draw()