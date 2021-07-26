"""
Main file. Handles user input and displays the current game state.
"""
import pygame as pg
from engine import GameState, Move

WIDTH = HEIGHT = 512
DIMENSION = 8  # Dimensions of a chess board - 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
HOOVERED_SQ_COLOR = (100, 100, 100)


class Player:
    def __init__(self, color):
        self.color = color
        self.player_clicks = []  # Keep track of player clicks


class Game:
    def __init__(self):
        self.game_state = GameState()
        self.images = {}
        self.load_images()

        # self.white_player = Player('white')
        # self.black_player = Player('black')

        pg.init()
        pg.display.set_caption('Chess Game')
        pg.display.set_icon(pg.transform.scale(pg.image.load('resources/logo.png'), (32, 32)))
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))

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

    def draw_game_state(self):
        self.draw_board()
        self.draw_hoovered_square()
        if self.selected_piece != ():
            self.draw_piece_selection()
        self.draw_pieces()

    def draw_board(self):
        # Top left square is always light
        colors = [pg.Color('white'), pg.Color('gray')]
        for row in range(DIMENSION):
            for column in range(DIMENSION):
                color = colors[(row + column) % 2]
                pg.draw.rect(self.screen, color, pg.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def draw_piece_selection(self):
        color = pg.Color('gold')
        pg.draw.rect(self.screen, color, pg.Rect(self.selected_piece[1] * SQ_SIZE,
                                                 self.selected_piece[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def draw_hoovered_square(self):
        self.screen.blit(self.hoovered_square, (self.col*SQ_SIZE, self.row*SQ_SIZE))

    def draw_pieces(self):
        for row in range(DIMENSION):
            for column in range(DIMENSION):
                piece = self.game_state.board[row][column]
                if piece != '--':
                    self.screen.blit(self.images[piece], pg.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

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

        # Moving by dragging
        dragging = False
        dragging_sq_selected = ()   # (row, column)

        # Move validation
        valid_moves = self.game_state.get_valid_moves()
        move_made = False

        while running:

            self.location = pg.mouse.get_pos()  # (x, y)
            self.col = self.location[0] // SQ_SIZE
            self.row = self.location[1] // SQ_SIZE

            for e in pg.event.get():

                # QUIT
                if e.type == pg.QUIT:
                    running = False

                # MOUSE CLICKS
                elif e.type == pg.MOUSEBUTTONUP:

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
                            # if not self.game_state.is_square_empty(sq_selected):
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
                            sq_selected = ()
                            player_clicks = []
                            self.selected_piece = ()

                # DRAGGING
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        pass

                # KEY HANDLERS
                elif e.type == pg.KEYDOWN:
                    if e.key == pg.K_z:
                        self.game_state.undo_move()
                        move_made = True

            if move_made:
                valid_moves = self.game_state.get_valid_moves()
                move_made = False

            self.draw_game_state()

            clock.tick(MAX_FPS)
            pg.display.flip()


def main():
    game = Game()
    game.start()


if __name__ == '__main__':
    main()
