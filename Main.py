import pygame as p
import pygame_menu as pm
import Engine, chessAI

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
playWhite = True
p.mixer.init()
moveSound = p.mixer.Sound('sounds/move.wav')
gameOverSound = p.mixer.Sound('sounds/spooky-game-over-1948.wav')
staleSound = p.mixer.Sound('sounds/sad-game-over-trombone-471.wav')



def pieceColor(value, n):
    global playWhite
    # if value == "White":
    if n == 1:
        playWhite = True
    # if value == "Black":
    else:
        playWhite = False

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
    animate = False  # flag variable for when we should animate a move
    loadImages()  # loads once
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = playWhite  # True if Human is white
    playerTwo = not playWhite # True if Human is black
    sl_num = [1, 1]
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # x y coordinates of the mouse.
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append both first and second clicks.
                    if len(playerClicks) == 2:
                        move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                if sl_num[1] == 1:
                                    print(sl_num[0].__str__() + ". " + move.getChessNotation() + ',', end=" ")
                                    sl_num[1] = sl_num[1] + 1
                                else:
                                    print( move.getChessNotation())
                                    sl_num[1] = sl_num[1] - 1
                                    sl_num[0] = sl_num[0] + 1
                                moveSound.play()
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:  # undo when u is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    sqSelected = ()
                    playerClicks = []
                    gameOver = False
                if e.key == p.K_r:  # reset board if 'r' is pressed
                    gs = Engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = chessAI.findBestMoveMinMax(gs, validMoves)
            if AIMove is None:
                AIMove = chessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveSound.play()
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            gameOverSound.play(fade_ms=30000)
            # gameOverSound.fadeout(5000)
            if gs.whiteToMove:
                drawText(screen, 'Checkmate! Black wins')
            else:
                drawText(screen, 'Checkmate! White wins')
            # time.sleep(5)
            # break
        elif gs.stalemate:
            gameOver = True
            staleSound.play(fade_ms=15000)
            drawText(screen, 'Stalemate!')

        # if playerTwo:
        #     screen.blit(p.transform.rotate(screen, 180), (0, 0))
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
menu.add.selector('Color: ', [('White', 1), ('Black', 2)], onchange=pieceColor)
menu.add.selector('Theme: ', [('Classic', 1), ('Wood', 2), ('Blue', 3), ('Green', 4)], onchange=theme)
menu.add.button('Quit', pm.events.EXIT)


def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR', 'bp', 'wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # IMAGES['wp'] = p.image.load("images/wp.png")


def main():
    menu.mainloop(screen)


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # square selected contains a piece that can be moved on this turn.
            # highlight the selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency value 0-255
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r*SQ_SIZE))
            # highlight moves available from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE * move.endCol, SQ_SIZE*move.endRow))



def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # draw squares on board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on squares


def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # color = colors[(r + c) & 1]
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 3
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw any captured piece onto the rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c* SQ_SIZE, r* SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, False, p.Color('Black'))
    textLocation = p.Rect(0,0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("Cyan"))
    screen.blit(textObject, textLocation.move(2,2))


if __name__ == "__main__":
    main()
