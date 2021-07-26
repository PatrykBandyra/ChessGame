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

        self.checkmate = False
        self.stalemate = False  # No valid moves and king not in check

        self.enpassant_possible = ()  # Coordinates for the square where en passant capture is possible

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
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.end_row, move.end_col)

            # Pawn promotion
            if move.is_pawn_promotion:
                self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'  # TODO: different figures in pawn promotion

            # En passant move
            if move.is_enpassant_move:
                self.board[move.start_row][move.end_col] = '--'  # Capture the pawn

            if move.piece_moved[1] == 'P' and abs(move.start_row-move.end_row) == 2:  # Only on 2 square pawn advances
                self.enpassant_possible = ((move.start_row+move.end_row)//2, move.start_col)
            else:
                self.enpassant_possible = ()

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

            # Undoing un passant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--'  # Leave landing location empty
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)

            # Undoing 2 square pawn advance
            if move.piece_moved[1] == 'P' and abs(move.start_row-move.end_row) == 2:
                self.enpassant_possible = ()

    def get_valid_moves(self):
        """
        All moves considering checks.
        """
        temp_enpassant_possible = self.enpassant_possible
        # 1. Generate all possible moves
        moves = self.get_all_possible_moves()
        # 2. For each move, make the move
        for i in range(len(moves)-1, -1, -1):   # When removing from a list go backwards through that list
            self.make_move(moves[i])
            # 3. Generate all opponent's moves
            # 4. For each of opponent's moves, see if they attack the king
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])  # 5. If they opponent attacks the king - not a valid move
            self.white_to_move = not self.white_to_move
            self.undo_move()

        if len(moves) == 0:  # Either checkmate or stalemate
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        # else:
        #     self.checkmate = False
        #     self.stalemate = False

        self.enpassant_possible = temp_enpassant_possible
        return moves

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
                turn = self.board[row][column][0]   # 'b' or 'w'
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
                if self.board[row-1][column] == '--':   # 1 square advance
                    moves.append(Move((row, column), (row - 1, column), self.board))
                    if row == len(self.board) - 2 and self.board[row-2][column]:  # 2 squares advance
                        moves.append(Move((row, column), (row - 2, column), self.board))
                if column - 1 >= 0:  # Captures to the left
                    if self.board[row-1][column-1][0] == 'b':   # Enemy piece to capture
                        moves.append(Move((row, column), (row - 1, column - 1), self.board))
                    elif (row-1, column-1) == self.enpassant_possible:
                        moves.append(Move((row, column), (row - 1, column - 1), self.board, is_enpassant_move=True))
                if column + 1 <= len(self.board[row])-1:  # Captures to the right
                    if self.board[row-1][column+1][0] == 'b':   # Enemy piece to capture
                        moves.append(Move((row, column), (row - 1, column + 1), self.board))
                    elif (row-1, column+1) == self.enpassant_possible:
                        moves.append(Move((row, column), (row - 1, column + 1), self.board, is_enpassant_move=True))
        else:
            if row + 1 <= len(self.board) - 1:
                if self.board[row+1][column] == '--':   # 1 square advance
                    moves.append(Move((row, column), (row + 1, column), self.board))
                    if row == 1 and self.board[row+2][column]:  # 2 squares advance
                        moves.append(Move((row, column), (row + 2, column), self.board))
                if column - 1 >= 0:  # Captures to left
                    if self.board[row+1][column-1][0] == 'w':   # Enemy piece to capture
                        moves.append(Move((row, column), (row + 1, column - 1), self.board))
                    elif (row+1, column-1) == self.enpassant_possible:
                        moves.append(Move((row, column), (row + 1, column - 1), self.board, is_enpassant_move=True))
                if column + 1 <= len(self.board[row])-1:  # Captures to right
                    if self.board[row+1][column+1][0] == 'w':   # Enemy piece to capture
                        moves.append(Move((row, column), (row + 1, column + 1), self.board))
                    elif (row+1, column+1) == self.enpassant_possible:
                        moves.append(Move((row, column), (row + 1, column + 1), self.board, is_enpassant_move=True))

    def get_rook_moves(self, row, column, moves):
        """
        Gets all the rook moves for the rook at given location and adds these moves to the list.
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Up, left, down, right
        self.get_long_distance_move(row, column, directions, moves, len(self.board)-1)

    def get_bishop_moves(self, row, column, moves):
        """
        Gets all the bishop moves for the bishop at given location and adds these moves to the list.
        """
        directions = ((-1, -1), (1, 1), (1, -1), (-1, 1))
        self.get_long_distance_move(row, column, directions, moves, len(self.board)-1)

    def get_long_distance_move(self, row, column, directions, moves, longest_move):
        """
        Gets all the moves for a specific figure in a given location. Figure can move in different directions for a
        given maximum number of tiles.
        """
        enemy_color = 'b' if self.white_to_move else 'w'
        for direction in directions:
            for i in range(1, longest_move+1):
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

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # Pawn promotion
        self.is_pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == len(board)-1)

        # En passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

