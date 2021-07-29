import random


class ChessAi:

    PIECE_SCORES = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'P': 1}
    CHECKMATE = 1000
    STALEMATE = 0

    next_move = None
    DEPTH = 4

    @staticmethod
    def find_random_move(valid_moves):
        return random.choice(valid_moves)

    @staticmethod
    def find_best_move(game_state, valid_moves):
        turn_multiplier = 1 if game_state.white_to_move else -1
        opponent_minmax_score = ChessAi.CHECKMATE
        best_player_move = None
        random.shuffle(valid_moves)

        for player_move in valid_moves:
            game_state.make_move(player_move)
            opponent_moves = game_state.get_valid_moves()

            if game_state.stale_mate:
                opponent_max_score = ChessAi.STALEMATE
            elif game_state.check_mate:
                opponent_max_score = -ChessAi.CHECKMATE
            else:
                opponent_max_score = -ChessAi.CHECKMATE

                for opponent_move in opponent_moves:
                    game_state.make_move(opponent_move)
                    game_state.get_valid_moves()
                    if game_state.check_mate:
                        score = ChessAi.CHECKMATE
                    elif game_state.stale_mate:
                        score = ChessAi.STALEMATE
                    else:
                        score = -turn_multiplier * ChessAi.score_material(game_state.board)
                    if score > opponent_max_score:
                        opponent_max_score = score
                    game_state.undo_move()

            if opponent_max_score < opponent_minmax_score:
                opponent_minmax_score = opponent_max_score
                best_player_move = player_move

            game_state.undo_move()

        return best_player_move

    @staticmethod
    def find_best_move_minmax(game_state, valid_moves):
        """
        Helper method to make first recursive call.
        """
        ChessAi.find_move_minmax(game_state, valid_moves, ChessAi.DEPTH, game_state.white_to_move)
        return ChessAi.next_move

    @staticmethod
    def find_move_minmax(game_state, valid_moves, depth, white_to_move):
        pass

    @staticmethod
    def score_material(board):
        """
        Score the board based on material.
        """
        score = 0
        for row in board:
            for square in row:
                if square[0] == 'w':
                    score += ChessAi.PIECE_SCORES[square[1]]
                elif square[0] == 'b':
                    score -= ChessAi.PIECE_SCORES[square[1]]

        return score
