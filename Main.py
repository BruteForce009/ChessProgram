import pygame as p
import pygame_menu as pm
import Engine
import os


WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
FPS = 15
IMAGES = {}
p.init()
screen = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption('Game on !')
pygame_icon = p.image.load("images/wN.png")
p.display.set_icon(pygame_icon)
colors = [p.Color(232, 235, 239), p.Color(100, 100, 100)]


def theme(value, n):
    # if value == "Classic":
    if n == 1:
        if colors:
            del colors[:]
        colors.append(p.Color(232, 235, 239))
        colors.append(p.Color(100, 100, 100))
    # elif value == "Wood":
    elif n == 2:
        if colors:
            del colors[:]
        colors.append(p.Color(240, 217, 181))
        colors.append(p.Color(181, 136, 99))
    # elif value == "Blue":
    elif n == 3:
        if colors:
            del colors[:]
        colors.append(p.Color(240, 240, 240))
        colors.append(p.Color(59, 153, 217))
    # elif value == "Green":
    elif n == 4:
        if colors:
            del colors[:]
        colors.append(p.Color(255, 255, 255))
        colors.append(p.Color(118,151,86))


def start_the_game():
    clock = p.time.Clock()
    screen.fill(p.Color("gray"))
    gs = Engine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    loadImages()  # loads once
    running = True
    sqSelected = ()
    playerClicks = []
    sl_num = 1
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # mouse coordinates
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):  # same square re-clicked
                    playerClicks = []   # empty clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)  # append 1st and 2nd clicks
                if len(playerClicks) == 2:  # after 2nd click
                    move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(sl_num.__str__() + ". " + move.getChessNotation())
                    gs.makeMove(move)
                    moveMade = True
                    sqSelected = ()  # reset clicks
                    playerClicks = []
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:  # undo when u is pressed
                    gs.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs)
        clock.tick(FPS)
        p.display.flip()


mytheme = pm.themes.THEME_SOLARIZED.copy()
mytheme.title_font = pm.font.FONT_8BIT  # FONT_DIGITAL # FONT_FIRACODE
myimage = pm.baseimage.BaseImage(image_path="images/KeqTo3B.jpg", drawing_mode=pm.baseimage.IMAGE_MODE_FILL, drawing_offset=(0,0))
mytheme.background_color = myimage
menu = pm.Menu('Welcome', 512, 512, theme=mytheme)
# menu.add.text_input('Username: ', default='Bot')
# menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
menu.add.button('Play', start_the_game)
menu.add.selector('Theme: ', [('Classic', 1), ('Wood', 2), ('Blue', 3), ('Green', 4)], onchange=theme)
menu.add.button('Quit', pm.events.EXIT)


def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR', 'bp', 'wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # IMAGES['wp'] = p.image.load("images/wp.png")


def main():
    menu.mainloop(screen)


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # color = colors[(r + c) & 1]
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, c*SQ_SIZE, c*SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, c*SQ_SIZE, c*SQ_SIZE))


if __name__ == "__main__":
    main()
