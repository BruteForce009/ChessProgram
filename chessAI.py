import random

pieceScore = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'p': 1}

knightScores = [[2, 3, 4, 4, 4, 4, 3, 2],
                [3, 4, 6, 6, 6, 6, 4, 3],
                [4, 6, 8, 8, 8, 8, 6, 4],
                [4, 6, 8, 8, 8, 8, 6, 4],
                [4, 6, 8, 8, 8, 8, 6, 4],
                [4, 6, 8, 8, 8, 8, 6, 4],
                [4, 4, 6, 6, 6, 6, 4, 3],
                [2, 3, 4, 4, 4, 4, 3, 2]]

'''
bishopScores
rookScores
queenScores
kingScores
'''

WPScores = [[8, 9, 10, 11, 11, 10, 9, 8],
            [6, 7, 8, 9, 9, 8, 7, 6],
            [5, 6, 7, 8, 8, 7, 6, 5],
            [4, 5, 6, 7, 7, 6, 5, 4],
            [2, 4, 6, 6, 6, 3, 3, 2],
            [3, 3, 4, 2, 2, 1, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0]]

BPScores = [[0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [3, 3, 4, 2, 2, 1, 2, 2],
            [2, 4, 6, 6, 6, 3, 3, 2],
            [4, 5, 6, 7, 7, 6, 5, 4],
            [5, 6, 7, 8, 8, 7, 6, 5],
            [5, 6, 7, 8, 8, 7, 6, 5],
            [8, 9, 10, 11, 11, 10, 9, 8]]

piecePositionScores = {'N': knightScores, 'bp': BPScores, 'wp': WPScores}
# 'B': bishopScores, 'R': rookScores, 'Q': queenScores, 'K': kingScores

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


def findSmartMove(gs, validMoves):  # greedy two move ahead
    turnMultiplier = 1 if gs.whiteToMove else -1
    oppMinMaxScore = CHECKMATE
    bestMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        oppMoves = gs.getValidMoves()
        if gs.stalemate:
            oppMaxScore = STALEMATE
        elif gs.checkmate:
            oppMaxScore = -CHECKMATE
        else:
            oppMaxScore = -CHECKMATE
            for oppMove in oppMoves:
                gs.makeMove(oppMove)
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > oppMaxScore:
                    oppMaxScore = score
                gs.undoMove()
        if oppMaxScore < oppMinMaxScore:
            oppMinMaxScore = oppMaxScore
            bestMove = playerMove
        gs.undoMove()
    return bestMove


# helper function
def findBestMove(gs, validMoves):
# def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    # findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    return nextMove
    # returnQueue.put(nextMove)


def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    # move ordering
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:  # pruning
            aplha = maxScore
        if alpha >= beta:
            break
    return maxScore


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != '--':
                # positional scoring
                piecePositionScore = 0
                if square[1] == 'p':
                    piecePositionScore = piecePositionScores[square][row][col]
                elif square[1] == 'N':
                    piecePositionScore = piecePositionScores[square[1]][row][col]

                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore // 8
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore // 8

    return score


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score
