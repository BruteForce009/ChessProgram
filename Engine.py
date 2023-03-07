class GameState:
    def __init__(self):
        # Alphabetic representation of chess board
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves, 'B': self.getBishopMoves}
        self.whiteToMove = True
        self.movelog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # coordinates for the square where an en passant capture is possible.
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [
            CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs,
                         self.currentCastlingRight.bqs)]


    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movelog.append(move)
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        self.whiteToMove = not self.whiteToMove  # swap turn
        # Pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

            # en passant
            if move.isEnpassantMove:
                self.board[move.startRow][move.endCol] = '--'
            # update enpassantPossible variable
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # only on 2-square pawn advances
                self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
            else:
                self.enpassantPossible = ()

            # castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside castle move
                    self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                        move.endCol + 1]  # copies the rook into its new square
                    self.board[move.endRow][move.endCol + 1] = '--'  # erase old rook.
                else:  # queenside castle move
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                    self.board[move.endRow][move.endCol - 2] = '--'

            # update castling rights - whenever a rook or king moves.
            self.updateCastleRights(move)
            self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    '''
        Update castle rights given a move.
        '''

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.bks = False
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False


    def undoMove(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            self.whiteToMove = not self.whiteToMove  # swap turn

            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

                # undo castling rights
                self.castleRightsLog.pop()  # get rid of the most recent entry
                self.currentCastlingRight = CastleRights(self.castleRightsLog[-1].wks, self.castleRightsLog[-1].bks,
                                                         self.castleRightsLog[-1].wqs, self.castleRightsLog[
                                                             -1].bqs)  # set current castle rights to what is now the last in the list.
                # undo castle move
                if move.isCastleMove:
                    if move.endCol - move.startCol == 2:  # kingside
                        self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                        self.board[move.endRow][move.endCol - 1] = '--'
                    else:
                        self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                        self.board[move.endRow][move.endCol + 1] = '--'

                checkmate = False
                stalemate = False

    def getValidMoves(self):
        tempEPpossible = self.enpassantPossible
        tempCurrentCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                               self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # 1 generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # 1. generate all moves
        moves = self.getAllPossibleMoves()
        # 2. for each, make the move
        for i in range((len(moves)-1), -1, -1):  #iterating backwards to remove
            self.makeMove(moves[i])
            # 3. generate all opponent's move
            # oppMoves = self.getAllPossibleMoves()
            # 4. for each of (3) check if they attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  # if attackking king not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEPpossible
        self.currentCastlingRight = tempCurrentCastleRights
        return moves


    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False


    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--":  # one forward move
                moves.append(Move((r, c), (r-1, c), self.board))
                if r==6 and self.board[r-2][c] == "--":  # one forward move
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:  # left-side capture
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7:  # right-side capture
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
        else:
            if self.board[r + 1][c] == "--":  # one forward move
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # one forward move
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # left-side capture
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # right-side capture
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))


    def getRookMoves(self, r, c, moves):
        directions = {(-1, 0), (0, -1), (1, 0), (0, 1)}
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly-piece
                        break
                else:
                    break  # off-board

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)


    def getKingMoves(self, r, c, moves):
        knightMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + knightMoves[i][0]
            endCol = c + knightMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = {(-1, -1), (-1, 1), (1, -1), (1, 1)}
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly-piece
                        break
                else:
                    break  # off-board

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  # can't castle in check.
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # value mapping
    ranks2Rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows2Ranks = {v: k for k, v in ranks2Rows.items()}
    files2Cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols2Files = {v: k for k, v in files2Cols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # if self.pieceMoved[1] == 'p' and (self.endRow, self.endCol) == isEnpassantMove:
        #     self.isPawnPromotion = True
        # pawn promotion
        self.isPawnPromotion = False
        self.promotionChoice = 'Q'
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True
        # castle move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

    def __eq__(self, other):  # Overriding equals method
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return '[' + self.pieceMoved + ']' + self.getRankFile(self.startRow, self.startCol) + '-' + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.cols2Files[c] + self.rows2Ranks[r]