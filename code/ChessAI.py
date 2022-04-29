import random
from ChessEngine import GameState

pieceValues = {"k": 0, "p": 1, "q": 9, "r": 5, "b": 3, "n": 3}
CHECKMATE = 1000
STALEMATE = 0

def findRandomMove(validMoves: list):
    return validMoves[random.randint(0, len(validMoves)-1)]


def findGreedyBestMove(gs: GameState, validMoves):
    turn = 1 if gs.white_to_move else -1
    maxScore = -CHECKMATE
    best_move = None
    for m in validMoves:
        gs.make_move(m)
        gs.get_valid_moves()
        if gs.checkmate:
            score = CHECKMATE
        elif gs.stalemate:
            score = STALEMATE
        else:
            score = turn*scoreBoard(gs.board)
        if score > maxScore:
            maxScore = score
            best_move = m
        gs.undo_move()
    return best_move


'''
Score board based on materail
'''

def scoreBoard(board):
    score = 0
    for r in board:
        for c in r:
            if c[0] == 'w':
                score += pieceValues[c[1]]
            elif c[0] == 'b': 
                score -= pieceValues[c[1]]

    return score