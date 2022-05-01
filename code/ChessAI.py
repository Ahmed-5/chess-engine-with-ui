import random
from ChessEngine import GameState

pieceValues = {"k": 0, "p": 1, "q": 9, "r": 5, "b": 3, "n": 3}
CHECKMATE = 1000
STALEMATE = -10
DEPTH = 2

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
            score = -STALEMATE
        else:
            score = turn*scoreMaterial(gs.board)
        if score > maxScore:
            maxScore = score
            best_move = m
        gs.undo_move()
    return best_move


def findMinMaxDepth2Move(gs: GameState, valid_moves):
    turn = 1 if gs.white_to_move else -1
    opponenet_minmax_score = CHECKMATE+1
    best_move = None
    random.shuffle(valid_moves)
    for m in valid_moves:
        gs.make_move(m)
        oppponent_moves = gs.get_valid_moves()
        opponent_max_score = -CHECKMATE-1
        if gs.checkmate:
            opponent_max_score = -CHECKMATE
        elif gs.stalemate:
            opponent_max_score = STALEMATE
        for oppo_move in oppponent_moves:
            gs.make_move(oppo_move)
            gs.get_valid_moves()
            if gs.checkmate:
                score = CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turn*scoreMaterial(gs.board)
            if score > opponent_max_score:
                opponent_max_score = score
            gs.undo_move()
        if opponent_max_score < opponenet_minmax_score:
            opponenet_minmax_score = opponent_max_score
            best_move = m
        gs.undo_move()
    return best_move

def findBestMoveMinMax(gs:GameState, validMoves):
    global nextMove
    nextMove = None
    findMinMaxMove(gs, validMoves, DEPTH, gs.white_to_move)
    return nextMove

def findMinMaxMove(gs:GameState, validMoves, depth, whiteToMove):
    global nextMove
    random.shuffle(validMoves)
    if depth == 0:
        return scoreBoard(gs)
    

    if whiteToMove:
        maxScore = -CHECKMATE-1
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = findMinMaxMove(gs, nextMoves, depth-1, not whiteToMove)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo_move()
        return maxScore

    else:
        minScore = CHECKMATE+1
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = findMinMaxMove(gs, nextMoves, depth-1, not whiteToMove)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo_move()
        return minScore
    


'''
Score board based on materail
'''

def scoreMaterial(board):
    score = 0
    for r in board:
        for c in r:
            if c[0] == 'w':
                score += pieceValues[c[1]]
            elif c[0] == 'b': 
                score -= pieceValues[c[1]]

    return score

def scoreBoard(gs:GameState):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    
    if gs.stalemate:
        if gs.white_to_move:
            return -STALEMATE
        else:
            return STALEMATE
    
    score = 0
    for r in gs.board:
        for c in r:
            if c[0] == 'w':
                score += pieceValues[c[1]]
            elif c[0] == 'b': 
                score -= pieceValues[c[1]]

    return score