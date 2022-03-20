import random
from abc import ABCMeta, abstractmethod
from const import *
from exceptions import *
from action import Action
from PyQt5.QtGui import QMouseEvent


class Player(metaclass=ABCMeta):
    """
    Classe abstraite représentant un joueur quelconque.

    Attributes:
        board (Board): le plateau de jeu sur lequel le joueur va effectuer ses actions
        player_id (int): l'id du joueur
    """

    def __init__(self, board, player_id):
        self.board = board
        self.player_id = player_id
        self.not_your_turn()

    def your_turn(self):
        """
        Tell the player it is their turn
        """
        self.is_playing = True

    def not_your_turn(self):
        """
        Tell the player it is not their turn anymore
        """
        self.is_playing = False

    def is_currently_playing(self):
        """
        Tell whether it is the player's turn
        :return: True if it is player's turn and False otherwise
        """
        return self.is_playing

    @property
    def other_player_id(self):
        """
        int: l'id du joueur adverse
        """
        return PLAYER_2 if self.player_id == PLAYER_1 else PLAYER_1


class HumanPlayer(Player):
    """
    Spécialisation de Player représentant un joueur humain
    """

    def __init__(self, board, player_id):
        super().__init__(board, player_id)

    def play(self, action):
        """
        Callback for Clicked event on board canvas.
        Play the demanded action on the board.
        :param event:  QMouseEvent generated when clicked on Canvas
        :raise: `InvalidActionException` if player cannot play or if action is invalid
        """
        if not self.is_currently_playing():
            raise InvalidActionError()
        self.board.act(action)


class AIPlayer(Player):
    """
    Spécialisation de la classe Player
    représentant un joueur utilisant un minimax
    """

    def __init__(self, board, player_id):
        super().__init__(board, player_id)

    def your_turn(self):
        self.is_playing = True

    def play(self):
        """
        Détermine le meilleur coup à jouer

        Returns:
            Action: le meilleur coup déterminé via minimax
        """
        action = self.minimax()[0]
        # self.board.act(action, self.player_id)
        self.board.act(action)

    def minimax(self, depth=2, maximizing=True):
        """
        Determines the optimal action to play jouer following minimax
        algorithm

        Args:
            depth (int): depth to explore in the possibles actions tree
            maximizing (bool): True if we want to maximise the score,
            False if we want to minimise it

        Returns:
            Action: best action found in explored depth
        """
        if depth == 0:
            return (None, DRAW)
        if maximizing:
            best_score = -INF
            player = self.player_id
        else:
            best_score = +INF
            player = self.other_player_id
        best_actions = []
        assert self.board.has_moves(player)
        for action in self.board.possible_actions(player):
            self.board.act(action)
            winner = self.board.status.winner
            if winner is not None:
                # Il vaut mieux gagner tôt (ou perdre tard) que de gagner tard (ou perdre tôt)
                score = WIN+depth
                if winner == self.other_player_id:
                    score *= -1
            else:
                score = self.minimax(depth-1, not maximizing)[1]
            self.board.undo()
            # Si on trouve un meilleur score
            if (score > best_score and maximizing) or (score < best_score and not maximizing):
                best_score = score
                best_actions = [action]
            elif score == best_score:
                best_actions.append(action)
        return random.choice(best_actions), best_score
