class Move():
    def __init__(self, start_sq, end_sq, board, is_enpassant=False, is_castle=False, promotion_choice=None) -> None:
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.is_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (
            self.piece_moved == 'bp' and self.end_row == 7)

        self.is_enpassant = is_enpassant
        if self.is_enpassant:
            self.piece_captured = board[self.start_row][self.end_col]

        self.is_castle = is_castle
        self.promotion_choice = promotion_choice

        self.move_id = "{}{}{}{}".format(
            self.start_row, self.start_col, self.end_row, self.end_col)
        if (self.is_promotion):
            self.move_id = "{}{}{}{}{}".format(
                self.start_row, self.start_col, self.end_row, self.end_col, self.promotion_choice)

    def rank_to_row(self, rank):
        if rank > 0 and rank < 9:
            return rank-8
        else:
            return -1

    def row_to_rank(self, row):
        if row > -1 and row < 8:
            return 8-row
        else:
            return -1

    def file_to_col(self, file):
        if file in 'abcdefgh':
            return ord(file)-ord("a")
        else:
            return -1

    def col_to_file(self, col):
        if col > -1 and col < 8:
            return chr(ord("a") + col)
        else:
            return -1

    def get_rank_file(self, r, c):
        rank = self.row_to_rank(r)
        file = self.col_to_file(c)
        return "{}{}".format(file, rank)

    def get_chess_notation(self):
        if self.is_promotion:
            return self.get_rank_file(self.start_row, self.start_col)+self.get_rank_file(self.end_row, self.end_col)+self.promotion_choice
        return self.get_rank_file(self.start_row, self.start_col)+self.get_rank_file(self.end_row, self.end_col)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Move):
            return __o.move_id == self.move_id
        return False


class CastleRights():
    def __init__(self, wks, wqs, bks, bqs) -> None:
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class GameState():
    def __init__(self) -> None:
        self.board = [
            ['br', 'bn', 'bb', "bq", 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', "wq", 'wk', 'wb', 'wn', 'wr'],
        ]

        self.move_function = {
            'p': self.get_pawn_moves,
            'k': self.get_king_moves,
            'r': self.get_rook_moves,
            'n': self.get_knight_moves,
            'b': self.get_bishop_moves,
            'q': self.get_queen_moves,
        }

        self.king_moves = [[1, 1], [1, 0], [1, -1],
                           [0, 1], [0, -1], [-1, 1], [-1, 0], [-1, -1]]

        self.knight_moves = [[2, 1], [2, -1], [-2, 1],
                             [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]

        self.white_to_move = True
        self.move_log: list[Move] = []
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.is_in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassant_square = ()
        self.current_castle_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [
            self.copy_castle_rights(self.current_castle_rights)]

    def copy_castle_rights(self, cr: CastleRights) -> CastleRights:
        return CastleRights(cr.wks, cr.wqs, cr.bks, cr.bqs)

    def make_move(self, move: Move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if (move.piece_moved == 'wk'):
            self.white_king_loc = (move.end_row, move.end_col)
        elif (move.piece_moved == 'bk'):
            self.black_king_loc = (move.end_row, move.end_col)

        if move.is_enpassant:
            self.board[move.start_row][move.end_col] = "--"

        if move.piece_moved[1] == 'p' and abs(move.end_row - move.start_row) == 2:
            self.enpassant_square = (
                (move.start_row + move.end_row)//2, move.end_col)
        else:
            self.enpassant_square = ()

        if move.is_promotion:
            choice = move.promotion_choice
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + choice

        if move.is_castle:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col -
                                         1] = move.piece_moved[0]+'r'
                self.board[move.end_row][7] = '--'
            else:
                self.board[move.end_row][move.end_col +
                                         1] = move.piece_moved[0]+'r'
                self.board[move.end_row][0] = '--'

        self.update_castle_rights(move)

    def undo_move(self):
        if len(self.move_log) > 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # print("undone move "+move.get_chess_notation())
            if (move.piece_moved == 'wk'):
                self.white_king_loc = (move.start_row, move.start_col)
            elif (move.piece_moved == 'bk'):
                self.black_king_loc = (move.start_row, move.start_col)

            if move.is_enpassant:
                self.board[move.end_row][move.end_col] = '--'
                # has to be fixed
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_square = (move.end_row, move.end_col)

            if move.piece_moved[1] == 'p' and abs(move.end_row - move.start_row) == 2:
                self.enpassant_square = ()

            if move.is_castle:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col-1] = '--'
                    self.board[move.end_row][7] = move.piece_moved[0]+'r'
                else:
                    self.board[move.end_row][move.end_col+1] = '--'
                    self.board[move.end_row][0] = move.piece_moved[0]+'r'

            self.castle_rights_log.pop()
            self.current_castle_rights = self.copy_castle_rights(
                self.castle_rights_log[-1])
            
            self.checkmate = False
            self.stalemate = False

    def update_castle_rights(self, move: Move):
        if move.piece_moved == 'wk':
            self.current_castle_rights.wks = False
            self.current_castle_rights.wqs = False
        elif move.piece_moved == 'bk':
            self.current_castle_rights.bks = False
            self.current_castle_rights.bqs = False
        elif move.piece_moved == 'wr':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castle_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castle_rights.wks = False
        elif move.piece_moved == 'br':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castle_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castle_rights.bks = False

        self.castle_rights_log.append(
            self.copy_castle_rights(self.current_castle_rights))

    def is_piece_pinned(self, r, c):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        return piece_pinned, pin_direction

    def get_pawn_moves(self, r, c, moves):
        piece_pinned, pin_direction = self.is_piece_pinned(r, c)

        if self.white_to_move:
            if self.board[r-1][c] == "--":
                if not piece_pinned or pin_direction == (-1, 0):
                    if r == 1:
                        moves.append(
                            Move((r, c), (r-1, c), self.board, promotion_choice="q"))
                        moves.append(
                            Move((r, c), (r-1, c), self.board, promotion_choice="r"))
                        moves.append(
                            Move((r, c), (r-1, c), self.board, promotion_choice="b"))
                        moves.append(
                            Move((r, c), (r-1, c), self.board, promotion_choice="n"))
                    else:
                        moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r, c), (r-2, c), self.board))

            if not piece_pinned or pin_direction == (-1, -1):
                if c > 0 and self.board[r-1][c-1].startswith('b'):
                    if r == 1:
                        moves.append(
                            Move((r, c), (r-1, c-1), self.board, promotion_choice="q"))
                        moves.append(
                            Move((r, c), (r-1, c-1), self.board, promotion_choice="r"))
                        moves.append(
                            Move((r, c), (r-1, c-1), self.board, promotion_choice="b"))
                        moves.append(
                            Move((r, c), (r-1, c-1), self.board, promotion_choice="n"))
                    else:
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                if (r-1, c-1) == self.enpassant_square:
                    moves.append(Move((r, c), (r-1, c-1), self.board, True))

            if not piece_pinned or pin_direction == (-1, 1):
                if c+1 < len(self.board[r-1]) and self.board[r-1][c+1].startswith('b'):
                    if r == 1:
                        moves.append(
                            Move((r, c), (r-1, c+1), self.board, promotion_choice="q"))
                        moves.append(
                            Move((r, c), (r-1, c+1), self.board, promotion_choice="r"))
                        moves.append(
                            Move((r, c), (r-1, c+1), self.board, promotion_choice="b"))
                        moves.append(
                            Move((r, c), (r-1, c+1), self.board, promotion_choice="n"))
                    else:
                        moves.append(Move((r, c), (r-1, c+1), self.board))
                if (r-1, c+1) == self.enpassant_square:
                    moves.append(Move((r, c), (r-1, c+1), self.board, True))

        else:
            if self.board[r+1][c] == "--":
                if not piece_pinned or pin_direction == (1, 0):
                    if r == 6:
                        moves.append(
                            Move((r, c), (r+1, c), self.board, promotion_choice="q"))
                        moves.append(
                            Move((r, c), (r+1, c), self.board, promotion_choice="r"))
                        moves.append(
                            Move((r, c), (r+1, c), self.board, promotion_choice="b"))
                        moves.append(
                            Move((r, c), (r+1, c), self.board, promotion_choice="n"))
                    else:
                        moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r, c), (r+2, c), self.board))

            if not piece_pinned or pin_direction == (1, -1):
                if c > 0 and self.board[r+1][c-1].startswith('w'):
                    if r == 6:
                        moves.append(
                            Move((r, c), (r+1, c-1), self.board, promotion_choice="q"))
                        moves.append(
                            Move((r, c), (r+1, c-1), self.board, promotion_choice="r"))
                        moves.append(
                            Move((r, c), (r+1, c-1), self.board, promotion_choice="b"))
                        moves.append(
                            Move((r, c), (r+1, c-1), self.board, promotion_choice="n"))
                    else:
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                if (r+1, c-1) == self.enpassant_square:
                    moves.append(Move((r, c), (r+1, c-1), self.board, True))

            if not piece_pinned or pin_direction == (1, 1):
                if c+1 < len(self.board[r+1]) and self.board[r+1][c+1].startswith('w'):
                    if r == 6:
                        moves.append(
                            Move((r, c), (r+1, c+1), self.board, promotion_choice="q"))
                        moves.append(
                            Move((r, c), (r+1, c+1), self.board, promotion_choice="r"))
                        moves.append(
                            Move((r, c), (r+1, c+1), self.board, promotion_choice="b"))
                        moves.append(
                            Move((r, c), (r+1, c+1), self.board, promotion_choice="n"))
                    else:
                        moves.append(Move((r, c), (r+1, c+1), self.board))
                if (r+1, c+1) == self.enpassant_square:
                    moves.append(Move((r, c), (r+1, c+1), self.board, True))

    def get_rook_moves(self, r, c, moves):
        piece_pinned, pin_direction = self.is_piece_pinned(r, c)
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

        for d in directions:
            if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                for i in range(1, 8):
                    end_row = r + i*d[0]
                    end_col = c + i*d[1]
                    if 0 <= end_row < 8 and 0 <= end_col < 8:
                        if self.board[end_row][end_col] == '--':
                            moves.append(
                                Move((r, c), (end_row, end_col), self.board))
                        else:
                            if self.board[r][c][0] != self.board[end_row][end_col][0]:
                                moves.append(
                                    Move((r, c), (end_row, end_col), self.board))
                            break
                    else:
                        break

    def get_bishop_moves(self, r, c, moves):
        piece_pinned, pin_direction = self.is_piece_pinned(r, c)
        directions = ((1, 1), (-1, 1), (1, -1), (-1, -1))

        for d in directions:
            if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                for i in range(1, 8):
                    end_row = r + i*d[0]
                    end_col = c + i*d[1]
                    if 0 <= end_row < 8 and 0 <= end_col < 8:
                        if self.board[end_row][end_col] == '--':
                            moves.append(
                                Move((r, c), (end_row, end_col), self.board))
                        else:
                            if self.board[r][c][0] != self.board[end_row][end_col][0]:
                                moves.append(
                                    Move((r, c), (end_row, end_col), self.board))
                            break
                    else:
                        break

    def get_queen_moves(self, r, c, moves):
        piece_pinned, pin_direction = self.is_piece_pinned(r, c)
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (-1, 1), (1, -1), (-1, -1))

        for d in directions:
            if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                for i in range(1, 8):
                    end_row = r + i*d[0]
                    end_col = c + i*d[1]
                    if 0 <= end_row < 8 and 0 <= end_col < 8:
                        if self.board[end_row][end_col] == '--':
                            moves.append(
                                Move((r, c), (end_row, end_col), self.board))
                        else:
                            if self.board[r][c][0] != self.board[end_row][end_col][0]:
                                moves.append(
                                    Move((r, c), (end_row, end_col), self.board))
                            break
                    else:
                        break

    def get_knight_moves(self, r, c, moves):
        piece_pinned, pin_direction = self.is_piece_pinned(r, c)
        if not piece_pinned:
            for i, j in self.knight_moves:
                if r+i < len(self.board) and r+i > -1:
                    if c+j < len(self.board[r+i]) and c+j > -1:
                        if self.board[r+i][c+j][0] != self.board[r][c][0]:
                            moves.append(Move((r, c), (r+i, c+j), self.board))

    def get_king_moves(self, r, c, moves):
        ally_color = self.board[r][c][0]
        for i, j in self.king_moves:
            if -1 < r+i < len(self.board):
                if c+j < len(self.board[r+i]) and c+j > -1:
                    if self.board[r+i][c+j][0] != self.board[r][c][0]:
                        if ally_color == 'w':
                            self.white_king_loc = (r+i, c+j)
                        elif ally_color == 'b':
                            self.black_king_loc = (r+i, c+j)

                        is_in_check, pins, checks = self.check_pins_checks()
                        if not is_in_check:
                            moves.append(Move((r, c), (r+i, c+j), self.board))

                        if ally_color == 'w':
                            self.white_king_loc = (r, c)
                        elif ally_color == 'b':
                            self.black_king_loc = (r, c)

        self.get_castle_moves(r, c, moves, ally_color)

    def get_castle_moves(self, r, c, moves, ally_color):
        # is_in_check, pins, checks = self.check_pins_checks()
        # if is_in_check:
        if self.is_in_check:
            return

        if (self.white_to_move and self.current_castle_rights.wks) or ((not self.white_to_move) and self.current_castle_rights.bks):
            self.get_kingside_castle(r, c, moves, ally_color)
        if (self.white_to_move and self.current_castle_rights.wqs) or ((not self.white_to_move) and self.current_castle_rights.bqs):
            self.get_queenside_castle(r, c, moves, ally_color)

    def get_kingside_castle(self, r, c, moves, ally_color):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(
                    Move((r, c), (r, c+2), self.board, is_castle=True))

    def get_queenside_castle(self, r, c, moves, ally_color):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(
                    Move((r, c), (r, c-2), self.board, is_castle=True))

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and (not self.white_to_move)):
                    piece = self.board[r][c][1]
                    self.move_function[piece](r, c, moves)
        return moves

    def check_pins_checks(self):
        pins = []
        checks = []
        is_in_check = False
        if self.white_to_move:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_loc[0]
            start_col = self.white_king_loc[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + i*d[0]
                end_col = start_col + i*d[1]
                if -1 < end_row < 8 and -1 < end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'k':
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    if end_piece[0] == enemy_color:
                        type = end_piece[1]
                        if type == 'q' or (0 <= j <= 3 and type == 'r') or (4 <= j <= 7 and type == 'b') or (i == 1 and type == 'k') or (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))):
                            if possible_pin == ():
                                is_in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break

        for m in self.knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if -1 < end_row < len(self.board) and -1 < end_col < len(self.board[end_row]):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'n':
                    is_in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return is_in_check, pins, checks

    def get_valid_moves(self):
        moves = []
        self.is_in_check, self.pins, self.checks = self.check_pins_checks()
        if self.white_to_move:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]

        if self.is_in_check:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()

                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_check = self.board[check_row][check_col]
                valid_squares = []

                if piece_check[1] == 'n':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_sq = (
                            king_row + i*check[2], king_col + i*check[3])
                        valid_squares.append(valid_sq)
                        if valid_sq[0] == check_row and valid_sq[1] == check_col:
                            break
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].piece_moved[1] != 'k':
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])

            else:
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_all_possible_moves()

        if len(moves) == 0:
            if self.is_in_check:
                # print("CHECKMATE")
                self.checkmate = True
            else:
                # print("STALEMATE")
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def square_under_attack(self, start_row, start_col):
        is_in_check = False
        ally_color = 'w' if self.white_to_move else 'b'
        enemy_color = 'b' if self.white_to_move else 'w'

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                end_row = start_row + i*d[0]
                end_col = start_col + i*d[1]
                if -1 < end_row < 8 and -1 < end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color:
                        break
                    if end_piece[0] == enemy_color:
                        type = end_piece[1]
                        if type == 'q' or (0 <= j <= 3 and type == 'r') or (4 <= j <= 7 and type == 'b') or (i == 1 and type == 'k') or (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))):
                            is_in_check = True
                        break

        for m in self.knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if -1 < end_row < len(self.board) and -1 < end_col < len(self.board[end_row]):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'n':
                    is_in_check = True

        return is_in_check
