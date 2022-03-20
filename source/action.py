from const import *
from exceptions import *
from pos2d import Pos2D


class Action:
    """
    Une instance de la classe Action représente une action faite par un
    joueur sur le plateau.

    Attributs:
        old_pos (Pos2D): case de départ de la reine
        new_pos (Pos2D): case d'arrivée de la reine
        arrow_pos (Pos2D): case d'arrivée de la flèche
        player (int): identifiant du joueur
    """

    def __init__(self, old_pos, new_pos, arrow_pos, player_id):
        self.old_pos = Action.as_Pos2D(old_pos)
        self.new_pos = Action.as_Pos2D(new_pos)
        self.arrow_pos = Action.as_Pos2D(arrow_pos)
        self.player = player_id
        if self.player not in (PLAYER_1, PLAYER_2):
            raise InvalidActionError(
                'Une action doit être associée à un joueur valide')

    @property
    def player_id(self):
        return self.player

    @staticmethod
    def as_Pos2D(pos):
        if isinstance(pos, str):
            return Pos2D.from_string(pos)
        elif isinstance(pos, Pos2D):
            return pos
        else:
            raise InvalidActionError(
                'Type inconnu pour un Pos2D: {type(pos)}')

    def __str__(self):
        return f'{self.old_pos}>{self.new_pos}>{self.arrow_pos}'

    def __repr__(self):
        return f'<Action {self}>'
