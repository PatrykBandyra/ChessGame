"""
Stores information about the current state of a chess game. Responsible for determining valid moves and keeping a move log.
"""
import numpy as np


class GameState:
    def __init__(self):
        self.board = np.array(  # 2D array [y, x]
            [
                ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
                ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
                ['--', '--', '--', '--', '--', '--', '--', '--'],
                ['--', '--', '--', '--', '--', '--', '--', '--'],
                ['--', '--', '--', '--', '--', '--', '--', '--'],
                ['--', '--', '--', '--', '--', '--', '--', '--'],
                ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
                ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
            ]
        )

        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.white_to_move = True
        self.move_log = []

        self.white_king_location = self.get_king_location('w')
        self.black_king_location = self.get_king_location('b')

        self.in_check = False
        self.pins = []
        self.checks = []

    def get_king_location(self, color):
        if color == 'b' or color == 'w':
            for i, row in enumerate(self.board):
                for j, col in enumerate(row):
                    if col == f'{color}K':
                        return i, j

    def make_move(self, move):
        """
        TODO: castling, pawn promotion
        """
        if self.board[move.start_row][move.start_col] != '--':
            self.board[move.start_row][move.start_col] = '--'
            self.board[move.end_row][move.end_col] = move.piece_moved
            self.move_log.append(move)
            self.white_to_move = not self.white_to_move

            # Update the king's location
            if move.piece_moved == 'wK':
                self.white_king_location = (move.end_row, move.end_col)
            if move.piece_moved == 'bK':
                self.black_king_location = (move.end_row, move.end_col)

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

            # Update the king's location
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            if move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

    def get_valid_moves(self):
        """
        All moves considering checks.
        """
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:  # Only 1 check - block check or move king
                moves = self.get_all_possible_moves()
                # To block a square - move a piece into one of the squares between the enemy piece and king
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # Squares that piece can move to
                # If knight - capture the knight or move the king (other pieces can be blocked)
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, len(self.board)):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)  # check[2] and check[3] - check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:  # When you get to piece - end checks
                            break
                # Get rid of any moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':  # Move doesn't move the king so it must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:  # Move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:  # Double check - king has to move
                self.get_king_moves(king_row, king_col, moves)
        else:  # Not in check - all moves allowed
            moves = self.get_all_possible_moves()

        return moves

    def check_for_pins_and_checks(self):
        pins = []  # Squares where the allied pinned piece is and direction pinned from
        checks = []  # Squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]

        # Check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # Reset possible pins
            for i in range(1, len(self.board)):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color:
                        if possible_pin == ():  # 1st allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        # 5 possibilities:
                        # 1. Orthogonally away from king and piece is a rook
                        # 2. Diagonally away from king and piece is a bishop
                        # 3. 1 square away from king and piece is a pawn
                        # 4. Any direction and piece is a queen
                        # 5. Any direction 1 square away and piece is a king

                        if (0 <= j <= 3 and piece_type == 'R') or (4 <= j <= 7 and piece_type == 'B') or \
                                (i == 1 and piece_type == 'P' and ((enemy_color == 'w' and 6 <= j <= 7) or
                                                                   (enemy_color == 'b' and 4 <= j <= 5))) or \
                                (piece_type == 'Q') or (i == 1 and piece_type == 'K'):

                            if possible_pin == ():  # No piece blocking - no check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # Piece blocking - pin
                                pins.append(possible_pin)
                                break
                        else:  # Enemy piece not applying check
                            break
                else:  # Off board
                    break
        # Check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':  # Enemy knight attacking the king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    def in_check(self):
        """
        Determines if the current player is under attack.
        """
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, row, col):
        """
        Determines if the enemy can attack the square (row, col)
        """
        self.white_to_move = not self.white_to_move
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponent_moves:
            if move.end_row == row and move.end_col == col:  # Square under attack
                return True
        return False

    def get_all_possible_moves(self):
        """
        All moves without considering checks.
        """
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn = self.board[row][column][0]  # 'b' or 'w'
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][column][1]
                    self.move_functions[piece](row, column, moves)  # Call appropriate function
        return moves

    def get_pawn_moves(self, row, column, moves):
        """
        Gets all the pawn moves for the pawn at given location and adds these moves to the list.
        """
        if self.white_to_move:
            if row - 1 >= 0:
                if self.board[row - 1][column] == '--':  # 1 square advance
                    moves.append(Move((row, column), (row - 1, column), self.board))
                    if row == len(self.board) - 2 and self.board[row - 2][column]:  # 2 squares advance
                        moves.append(Move((row, column), (row - 2, column), self.board))
                if column - 1 >= 0:  # Captures to the left
                    if self.board[row - 1][column - 1][0] == 'b':  # Enemy piece to capture
                        moves.append(Move((row, column), (row - 1, column - 1), self.board))
                if column + 1 <= len(self.board[row]) - 1:  # Captures to the right
                    if self.board[row - 1][column + 1][0] == 'b':  # Enemy piece to capture
                        moves.append(Move((row, column), (row - 1, column + 1), self.board))
        else:
            if row + 1 <= len(self.board) - 1:
                if self.board[row + 1][column] == '--':  # 1 square advance
                    moves.append(Move((row, column), (row + 1, column), self.board))
                    if row == 1 and self.board[row + 2][column]:  # 2 squares advance
                        moves.append(Move((row, column), (row + 2, column), self.board))
                if column - 1 >= 0:  # Captures to left
                    if self.board[row + 1][column - 1][0] == 'w':  # Enemy piece to capture
                        moves.append(Move((row, column), (row + 1, column - 1), self.board))
                if column + 1 <= len(self.board[row]) - 1:  # Captures to right
                    if self.board[row + 1][column + 1][0] == 'w':  # Enemy piece to capture
                        moves.append(Move((row, column), (row + 1, column + 1), self.board))

    def get_rook_moves(self, row, column, moves):
        """
        Gets all the rook moves for the rook at given location and adds these moves to the list.
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Up, left, down, right
        self.get_long_distance_move(row, column, directions, moves, len(self.board) - 1)

    def get_bishop_moves(self, row, column, moves):
        """
        Gets all the bishop moves for the bishop at given location and adds these moves to the list.
        """
        directions = ((-1, -1), (1, 1), (1, -1), (-1, 1))
        self.get_long_distance_move(row, column, directions, moves, len(self.board) - 1)

    def get_long_distance_move(self, row, column, directions, moves, longest_move):
        """
        Gets all the moves for a specific figure in a given location. Figure can move in different directions for a
        given maximum number of tiles.
        """
        enemy_color = 'b' if self.white_to_move else 'w'
        for direction in directions:
            for i in range(1, longest_move + 1):
                end_row = row + direction[0] * i
                end_col = column + direction[1] * i
                if 0 <= end_row <= len(self.board) - 1 and 0 <= end_col <= len(self.board[row]) - 1:  # On board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':  # Empty space - valid
                        moves.append(Move((row, column), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # Enemy piece - valid
                        moves.append(Move((row, column), (end_row, end_col), self.board))
                        break  # Cannot jump over the enemy piece - no need to check further
                    else:  # Friendly piece - invalid
                        break
                else:  # Off board
                    break

    def get_queen_moves(self, row, column, moves):
        """
         Gets all the queen moves for the queen at given location and adds these moves to the list.
         Queen's moves are combination of moves of rook and bishop.
        """
        self.get_rook_moves(row, column, moves)
        self.get_bishop_moves(row, column, moves)

    def get_king_moves(self, row, column, moves):
        """
        Gets all the king moves for the king at given location and adds these moves to the list.
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1))
        self.get_long_distance_move(row, column, directions, moves, 1)

    def get_knight_moves(self, row, column, moves):
        """
        Gets all the knight moves for the knight at given location and adds these moves to the list.
        """
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.white_to_move else 'b'
        for move in knight_moves:
            end_row = row + move[0]
            end_col = column + move[1]
            if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board[row]):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # empty or enemy piece
                    moves.append(Move((row, column), (end_row, end_col), self.board))


class Move:
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
