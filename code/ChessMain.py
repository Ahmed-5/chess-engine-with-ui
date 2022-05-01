import pygame as p
from pygame.surface import Surface
from sqlalchemy import true
from ChessEngine import GameState, Move
from ChessAI import findMinMaxDepth2Move

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH//DIMENSION
MAX_FPS = 15
IMAGES = {}
colors = [p.Color("#EBCD7D"), p.Color("#B88B4A")]  # light, dark


def load_images():
    pieces = ['wb', 'wn', 'wk', "wq", 'wr',
              'wp', 'bb', 'bn', 'bk', "bq", 'br', 'bp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(
            "../img/"+piece+".png"), (SQ_SIZE, SQ_SIZE))


def draw_board(screen: p.Surface):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen: p.Surface, board: list):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlight_squares(screen: p.Surface, gs: GameState, valid_moves, selected_sq):
    if selected_sq != ():
        r, c = selected_sq
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('yellow'))
            latest_drawn = ""
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    current = "{}{}".format(move.end_row, move.end_col)
                    if current != latest_drawn:
                        screen.blit(
                            s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))
                        latest_drawn = "{}{}".format(
                            move.end_row, move.end_col)


def animate_move(move: Move, screen: p.Surface, board, clock):
    dr = move.end_row - move.start_row
    dc = move.end_col - move.start_col
    fpsq = 5
    frame_count = 6

    for f in range(frame_count + 1):
        r, c = move.start_row + dr*f/frame_count, move.start_col + dc*f/frame_count
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_sq = p.Rect(move.end_col*SQ_SIZE, move.end_row *
                        SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_sq)

        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_sq)

        screen.blit(IMAGES[move.piece_moved], p.Rect(
            c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def draw_game_state(screen, gs: GameState, valid_moves, selected_sq):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, selected_sq)
    draw_pieces(screen, gs.board)


def draw_text(screen: p.Surface, text):
    font = p.font.SysFont("Helvitca", 34, True, False)
    text_obj = font.render(text, 0, p.Color("white"))
    text_loc = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2 - text_obj.get_width()/2, HEIGHT/2 - text_obj.get_height()/2)
    screen.blit(text_obj, text_loc)
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_obj = font.render(text, 0, p.Color("black"))
    text_loc = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2 - text_obj.get_width()/2, HEIGHT/2 - text_obj.get_height()/2)
    screen.blit(text_obj, text_loc)


if __name__ == '__main__':
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    load_images()
    undone = False

    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False
    playerOne = False  # if human is the player true, if AI is the player false
    playerTwo = False  # if human is the player true, if AI is the player false

    while(running):
        humanTurn = (gs.white_to_move and playerOne) or (
            not gs.white_to_move and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and humanTurn:
                    x, y = p.mouse.get_pos()
                    row = x//SQ_SIZE
                    col = y//SQ_SIZE
                    if sq_selected == (col, row):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (col, row)
                        player_clicks.append(sq_selected)
                        if len(player_clicks) == 2:
                            # move = Move(player_clicks[0],
                            # player_clicks[1], gs.board)
                            m = "{}{}{}{}".format(
                                player_clicks[0][0], player_clicks[0][1], player_clicks[1][0], player_clicks[1][1])
                            filtered = list(filter(lambda move: move.move_id[:4] == m, valid_moves))

                            if len(filtered) > 0:
                                if len(filtered) > 1:
                                    choice = ''
                                    valid_choices = ['q', 'r', 'n', 'b']
                                    while choice not in valid_choices:
                                        choice = input("Enter the piece\n").strip()
                                    m = m+choice
                                    filtered = list(filter(lambda move: move.move_id == m, filtered))
                                
                                move = filtered[0]
                                print(move.get_chess_notation())
                                gs.make_move(move)
                                move_made = True
                                sq_selected = ()
                                player_clicks = []

                            if not move_made:
                                player_clicks = [sq_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_BACKSPACE:
                    gs.undo_move()
                    move_made = True
                    undone = True
                    game_over = False
                elif e.key == p.K_r:
                    gs = GameState()
                    valid_moves = gs.get_valid_moves()
                    move_made = False
                    undone = False
                    sq_selected = ()
                    player_clicks = []
                    game_over = False

        # AI move logic
        if not game_over and not humanTurn:
            ai_move = findMinMaxDepth2Move(gs, valid_moves)
            gs.make_move(ai_move)
            move_made = true
            animate = true

        if move_made:
            if not undone:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            undone = False

        draw_game_state(screen, gs, valid_moves, sq_selected)

        game_over = gs.stalemate or gs.checkmate
        if gs.checkmate:
            if gs.white_to_move:
                draw_text(screen, "Black wins!!!")
            if not gs.white_to_move:
                draw_text(screen, "White wins!!!")
        elif gs.stalemate:
            draw_text(screen, "Stalemate!!!")

        clock.tick(MAX_FPS)
        p.display.flip()
