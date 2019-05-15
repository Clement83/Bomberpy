# Ecrit ton programme ici ;-)
from gamebuino_meta import waitForUpdate, display, color, buttons

SCREEN_WIDTH  = 80
SCREEN_HEIGHT = 64
COLOR_BG      = color.BROWN
COLOR_WALL    = color.BLACK
COLOR_WALL_2  = color.DARKGRAY
COLOR_PLAYER1 = color.PURPLE
COLOR_BOMBE = color.PINK
ELEMENT_COTE = 8

map =[
[0,1,0,1,0,1,0,0,1,0],
[0,2,0,2,0,2,0,0,2,0],
[0,2,2,2,1,2,2,0,2,0],
[0,1,0,0,0,0,1,0,2,0],
[0,2,2,1,2,2,2,0,2,0],
[0,0,0,1,0,0,0,0,1,0],
[1,2,2,1,2,2,2,2,2,0],
[0,0,0,0,0,0,0,2,0,0],
]

class Entity:
    def __init__(self, x, y):
        self.posX = x
        self.posY = y

class Player(Entity):

    def __init__(self, x, y):
        Entity.__init__(self, x, y)
        self.bombe = Bombe()

    def update(self):
        self.handleButtons()

    def draw(self):
        display.setColor(COLOR_PLAYER1)
        display.drawRect(self.posX, self.posY, ELEMENT_COTE, ELEMENT_COTE)
        self.bombe.draw()

    def handleButtons(self):
        if buttons.repeat(buttons.LEFT, 0):
            self.posX = self.posX - 1
        elif buttons.repeat(buttons.RIGHT, 0):
            self.posX = self.posX + 1
        elif buttons.repeat(buttons.UP, 0):
            self.posY = self.posY - 1
        elif buttons.repeat(buttons.DOWN, 0):
            self.posY = self.posY + 1
        elif buttons.repeat(buttons.A, 0):
            self.bombe.acivate(self.posX, self.posY)


class Bombe(Entity):

    def __init__(self):
        Entity.__init__(self, 0, 0)
        self.isActive = 0

    def draw(self):
        if self.isActive == 1:
            display.setColor(COLOR_BOMBE)
            display.drawRect(self.posX, self.posY, ELEMENT_COTE, ELEMENT_COTE)

    def acivate(self, x, y):
        self.posX = x
        self.posY = y
        self.isActive = 1


class GameEngine:

    def __init__(self):
        self.player1 = Player(0, 0)

    def draw(self):
        display.clear(COLOR_BG)
        self.player1.draw()
        for lineIndex in range(len(map)):
            for colIndex in range(len(map[lineIndex])):
                if map[lineIndex][colIndex] == 1:
                    display.setColor(COLOR_WALL)
                    display.drawRect(colIndex * ELEMENT_COTE, lineIndex * ELEMENT_COTE, ELEMENT_COTE, ELEMENT_COTE)
                if map[lineIndex][colIndex] == 2:
                    display.setColor(COLOR_WALL_2)
                    display.drawRect(colIndex * ELEMENT_COTE, lineIndex * ELEMENT_COTE, ELEMENT_COTE, ELEMENT_COTE)
        
    def update(self):
        self.player1.update()

    def run(self):
        while True:
            waitForUpdate()
            self.update()
            self.draw()