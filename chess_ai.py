import random


class ChessAi:

    PIECE_SCORES = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'P': 1}
    CHECKMATE = 1000
    STALEMATE = 0

    next_move = None
    DEPTH = 3

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
        random.shuffle(valid_moves)
        ChessAi.find_move_minmax(game_state, valid_moves, ChessAi.DEPTH, game_state.white_to_move)
        return ChessAi.next_move

    @staticmethod
    def find_move_minmax(game_state, valid_moves, depth, white_to_move):
        if depth == 0:
            return ChessAi.score_board(game_state)

        if white_to_move:
            max_score = -ChessAi.CHECKMATE
            for move in valid_moves:
                game_state.make_move(move)
                next_moves = game_state.get_valid_moves()
                score = ChessAi.find_move_minmax(game_state, next_moves, depth-1, False)
                if score > max_score:
                    max_score = score
                    if depth == ChessAi.DEPTH:
                        ChessAi.next_move = move
                game_state.undo_move()
            return max_score

        else:
            min_score = ChessAi.CHECKMATE
            for move in valid_moves:
                game_state.make_move(move)
                next_moves = game_state.get_valid_moves()
                score = ChessAi.find_move_minmax(game_state, next_moves, depth-1, True)
                if score < min_score:
                    min_score = score
                    if depth == ChessAi.DEPTH:
                        ChessAi.next_move = move
                game_state.undo_move()
            return min_score

    @staticmethod
    def find_best_move_negamax(game_state, valid_moves):
        random.shuffle(valid_moves)
        ChessAi.find_move_negamax(game_state, valid_moves, ChessAi.DEPTH, 1 if game_state.white_to_move else -1)
        return ChessAi.next_move

    @staticmethod
    def find_move_negamax(game_state, valid_moves, depth, turn_multiplier):
        if depth == 0:
            return turn_multiplier * ChessAi.score_board(game_state)

        max_score = -ChessAi.CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.get_valid_moves()
            score = -ChessAi.find_move_negamax(game_state, next_moves, depth-1, -turn_multiplier)
            if score > max_score:
                max_score = score
                if depth == ChessAi.DEPTH:
                    ChessAi.next_move = move
            game_state.undo_move()

        return max_score

    @staticmethod
    def find_best_move_negamax_alpha_beta(game_state, valid_moves):
        random.shuffle(valid_moves)
        ChessAi.find_move_negamax_alpha_beta(game_state, valid_moves, ChessAi.DEPTH, -ChessAi.CHECKMATE, ChessAi.CHECKMATE, 1 if game_state.white_to_move else -1)
        return ChessAi.next_move

    @staticmethod
    def find_move_negamax_alpha_beta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
        if depth == 0:
            return turn_multiplier * ChessAi.score_board(game_state)

        # TODO: Move ordering - implement later

        max_score = -ChessAi.CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.get_valid_moves()
            score = -ChessAi.find_move_negamax_alpha_beta(game_state, next_moves, depth-1, -beta, -alpha, -turn_multiplier)
            if score > max_score:
                max_score = score
                if depth == ChessAi.DEPTH:
                    ChessAi.next_move = move
            game_state.undo_move()

            if max_score > alpha:  # Pruning
                alpha = max_score
            if alpha >= beta:
                break

        return max_score

    @staticmethod
    def score_board(game_state):
        """
        A positive score is good for white, a negative score is good for black.
        """
        if game_state.check_mate:
            if game_state.white_to_move:
                return -ChessAi.CHECKMATE  # Black wins
            else:
                return ChessAi.CHECKMATE  # White wins
        elif game_state.stale_mate:
            return ChessAi.STALEMATE

        score = 0
        for row in game_state.board:
            for square in row:
                if square[0] == 'w':
                    score += ChessAi.PIECE_SCORES[square[1]]
                elif square[0] == 'b':
                    score -= ChessAi.PIECE_SCORES[square[1]]

        return score

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
