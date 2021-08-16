"""
Main file. Handles user input and displays the current game state.
"""
import pygame as pg
from engine import GameState, Move
from chess_ai import ChessAi

WIDTH = HEIGHT = 512
DIMENSION = 8  # Dimensions of a chess board - 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
HOOVERED_SQ_COLOR = (100, 100, 100)
POSSIBLE_MOVE_SQ_COLOR = (120, 255, 50)
SELECTED_SQ_COLOR = (255, 255, 0)


class Game:
    def __init__(self):
        self.game_state = GameState()
        self.images = {}
        self.load_images()

        pg.init()
        pg.display.set_caption('Chess Game')
        pg.display.set_icon(pg.transform.scale(pg.image.load('resources/logo.png'), (32, 32)))
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.colors = [pg.Color('white'), pg.Color('gray')]

        self.selected_piece = ()
        self.location = ()
        self.col = 0
        self.row = 0
        self.hoovered_square = pg.Surface((SQ_SIZE, SQ_SIZE))
        self.hoovered_square.fill(HOOVERED_SQ_COLOR)

    def load_images(self):
        """
        Loads images of chess pieces based on starting state of a chess board.
        """
        pieces = set()
        for row in self.game_state.board:
            for square in row:
                if square != '--':
                    pieces.add(square)

        for piece in pieces:
            self.images[piece] = pg.transform.scale(pg.image.load(f'resources/figures_images/{piece}.png'), (SQ_SIZE, SQ_SIZE))

    def draw_game_state(self, valid_moves, square_selected, display_hoovering=True):
        self.draw_board()
        if display_hoovering:
            self.draw_hoovered_square()
        self.highlight_squares(valid_moves, square_selected)
        self.draw_pieces()

    def draw_board(self):
        # Top left square is always light
        for row in range(DIMENSION):
            for column in range(DIMENSION):
                color = self.colors[(row + column) % 2]
                pg.draw.rect(self.screen, color, pg.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def highlight_squares(self, valid_moves, square_selected):
        """
        Highlights square selected and moves for piece selected
        """
        if square_selected != ():
            row, col = square_selected
            if self.game_state.board[row][col][0] == ('w' if self.game_state.white_to_move else 'b'):  # Square selected is a piece that can be moved

                # Highlights selected square
                surface = pg.Surface((SQ_SIZE, SQ_SIZE))
                surface.set_alpha(150)  # Transparency -> 0 = transparent, 255 = opaque
                surface.fill(SELECTED_SQ_COLOR)
                self.screen.blit(surface, (col*SQ_SIZE, row*SQ_SIZE))

                # Highlights moves from that square
                surface.set_alpha(100)
                surface.fill(POSSIBLE_MOVE_SQ_COLOR)
                for move in valid_moves:
                    if move.start_row == row and move.start_col == col:
                        self.screen.blit(surface, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))

    def draw_hoovered_square(self):
        self.screen.blit(self.hoovered_square, (self.col*SQ_SIZE, self.row*SQ_SIZE))

    def draw_pieces(self):
        for row in range(DIMENSION):
            for column in range(DIMENSION):
                piece = self.game_state.board[row][column]
                if piece != '--':
                    self.screen.blit(self.images[piece], pg.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def animate_move(self, move, clock):
        d_row = move.end_row - move.start_row
        d_col = move.end_col - move.start_col
        frames_per_square = 10  # Frames to move one square
        frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
        for frame in range(frame_count+1):
            row, col = (move.start_row + d_row*frame/frame_count, move.start_col + d_col*frame/frame_count)
            self.draw_board()
            self.draw_pieces()

            # Erase the piece moved from its ending square
            color = self.colors[(move.end_row + move.end_col) % 2]
            end_square = pg.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pg.draw.rect(self.screen, color, end_square)

            # Draw captured piece onto rectangle
            if move.piece_captured != '--' and not move.enpassant:
                self.screen.blit(self.images[move.piece_captured], end_square)

            # Draw moving piece
            self.screen.blit(self.images[move.piece_moved], pg.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

            pg.display.flip()
            clock.tick(60)

    def start(self):
        """
        e.button:
            1 - left click
            2 - middle click
            3 - right click
            4 - scroll up
            5 - scroll down
        """
        clock = pg.time.Clock()
        self.screen.fill(pg.Color('white'))
        running = True

        # Moving by clicking
        sq_selected = ()    # (row, column)
        player_clicks = []

        # # Moving by dragging  TODO: dragging
        # dragging = False
        # dragging_sq_selected = ()   # (row, column)

        # Move validation
        valid_moves = self.game_state.get_valid_moves()
        move_made = False

        animate = False

        game_over = False
        player_one = True  # If human is playing white - True, if ai is playing - False
        player_two = True  # Same as above but for black

        while running:

            is_human_turn = (self.game_state.white_to_move and player_one) or (not self.game_state.white_to_move and player_two)

            self.location = pg.mouse.get_pos()  # (x, y)
            self.col = self.location[0] // SQ_SIZE
            self.row = self.location[1] // SQ_SIZE

            for e in pg.event.get():

                # QUIT
                if e.type == pg.QUIT:
                    running = False

                # MOUSE CLICKS
                elif e.type == pg.MOUSEBUTTONUP:
                    if not game_over and is_human_turn:
                        # MOVE - left mouse button
                        if e.button == 1:
                            if sq_selected == (self.row, self.col):
                                sq_selected = ()
                                player_clicks = []
                                self.selected_piece = ()
                            else:
                                sq_selected = (self.row, self.col)
                                player_clicks.append(sq_selected)

                            if len(player_clicks) == 1:  # After 1st click
                                if not self.game_state.board[sq_selected[0]][sq_selected[1]] == '--':
                                    self.selected_piece = sq_selected
                                else:
                                    sq_selected = ()
                                    player_clicks = []

                            if len(player_clicks) == 2:  # After 2nd click
                                move = Move(player_clicks[0], player_clicks[1], self.game_state.board)
                                for i in range(len(valid_moves)):
                                    if move == valid_moves[i]:
                                        print(move.get_chess_notation())
                                        self.game_state.make_move(valid_moves[i])
                                        move_made = True
                                        animate = True
                                sq_selected = ()
                                player_clicks = []
                                self.selected_piece = ()

                # # DRAGGING  # TODO: dragging
                # elif e.type == pg.MOUSEBUTTONDOWN:
                #     if e.button == 1:
                #         pass

                # KEY HANDLERS
                elif e.type == pg.KEYDOWN:

                    # Undo move
                    if e.key == pg.K_z:
                        self.game_state.undo_move()
                        move_made = True
                        animate = False
                        game_over = False

                    # Reset the board
                    if e.key == pg.K_r:
                        self.game_state = GameState()
                        valid_moves = self.game_state.get_valid_moves()
                        sq_selected = ()
                        player_clicks = []
                        game_over = False
                        move_made = False
                        animate = False

            # Ai move finder logic
            if not game_over and not is_human_turn:
                ai_move = ChessAi.find_best_move_negamax_alpha_beta(self.game_state, valid_moves)
                if ai_move is None:
                    ai_move = ChessAi.find_random_move(valid_moves)
                self.game_state.make_move(ai_move)
                move_made = True
                animate = True

            if move_made:
                if animate:
                    self.animate_move(self.game_state.move_log[-1], clock)
                valid_moves = self.game_state.get_valid_moves()
                move_made = False
                animate = False

            if is_human_turn:
                self.draw_game_state(valid_moves, sq_selected, display_hoovering=True)
            else:
                self.draw_game_state(valid_moves, sq_selected, display_hoovering=False)

            if self.game_state.check_mate:
                game_over = True
                if self.game_state.white_to_move:
                    self.draw_text('Black wins by checkmate')
                else:
                    self.draw_text('White wins by checkmate')
            elif self.game_state.stale_mate:
                game_over = True
                self.draw_text('Stalemate')

            clock.tick(MAX_FPS)
            pg.display.flip()

    def draw_text(self, text):
        font = pg.font.SysFont('Helvitca', 32, True, False)
        text_object = font.render(text, False, pg.Color('Dark Red'))
        text_location = pg.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH//2-text_object.get_width()//2, HEIGHT//2-text_object.get_height()//2)
        self.screen.blit(text_object, text_location)
        text_object = font.render(text, False, pg.Color('Red'))
        self.screen.blit(text_object, text_location.move(2, 2))  # Shadow effect


def main():
    game = Game()
    game.start()


if __name__ == '__main__':
    main()
