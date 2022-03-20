from board import Board
from exceptions import InvalidFormatError
from players import *
from tournoi import TournoiAIPlayer
from const import *


def extract_positions(line):
    """
    Récupère la liste de positions dans line

    Args:
        line (str): string sous la forme '<pos1>,<pos2>,<pos3>,...,<posn>'

    Returns:
        list: liste d'instances de Pos2D

    Raises:
        InvalidFormatError: si la ligne est vide
    """
    if line == '' or line == '\n':
        raise InvalidFormatError('Liste de positions vide')
    else:
        return line.strip().split(',')


def read_file(path, history=False):
    """
    Récupère les informations stockées dans le fichier donné

    Args:
        path (str): chemin vers un fichier de format de plateau

    Returns:
        tuple: (size, pos_black, pos_white, pos_arrows)

    Raises:
        InvalidFormatError: si le format du fichier est invalide
    """
    with open(path, 'r') as f:
        try:
            size = int(f.readline().strip())
        except ValueError:  # Si la première ligne n'est pas un entier
            raise InvalidFormatError(
                'La taille du plateau n\'est pas donnée')
        pos_black = extract_positions(f.readline())
        pos_white = extract_positions(f.readline())
        history_line = []
        # line = 2

        # on récupère la liste des positions des flèches
        try:
            pos_arrows = extract_positions(f.readline())
            # line = 3
        except InvalidFormatError:
            pos_arrows = []

        line = f.readline()
        if line != '':  # S'il reste du texte dans le fichier
            if history:
                while line != '':
                    history_action = line.strip()
                    action = []

                    i = 3
                    for move in range(3):
                        x = ''
                        while history_action[i].isdigit():
                            x += history_action[i]
                            i += 1
                        x = int(x)
                        i += 4
                        y = ''
                        while history_action[i].isdigit():
                            y += history_action[i]
                            i += 1
                        y = int(y)
                        i += 5
                        action.append([x, y])

                    history_line.append(action)
                    line = f.readline()

                return size, pos_black, pos_white, pos_arrows, history_line

            else:
                raise InvalidFormatError(
                    'Format invalide: informations après les flèches')

    return size, pos_black, pos_white, pos_arrows


class Amazons:
    """
    La classe Amazons représente une instance du jeu des amazones au complet.

    Attributes:
        board (Board): le plateau de jeu
        players (tuple): tuple des joueurs (instances de Player)
        current_player_idx (int): indice du joueur dont c'est le tour
        status (EndOfGameStatus): état de la fin de partie
    """

    def __init__(self, N, pos_black, pos_white, pos_arrows):
        """
        Args:
            path (str): chemin vers le fichier représentant le plateau
        """
        self.board = Board(N, pos_black, pos_white, pos_arrows)
        # self.players = (HumanPlayer(self.board, PLAYER_1),
        #               AIPlayer(self.board, PLAYER_2))
        self.current_player_idx = 1
        self.status = None

    def play(self):
        """
        Joue une partie du jeu des amazones
        """
        while not self.is_over():
            print(self.board)  # on affiche l'état actuel du plateau
            # Le joueur actuel joue son coup
            self.players[self.current_player_idx].play()
            # On passe au joueur suivant
            self.current_player_idx = self.current_player_idx % 2
        print(self.board)  # On affiche le plateau après le dernier coup
        self.show_winner()  # On montre qui a gagné

    def is_over(self):
        """
        Détermine si la partie est terminée

        Returns:
            bool: True si la partie est finie et False sinon
        """
        self.status = self.board.status
        return self.status.over

    def get_winner_id(self):
        return '1' if self.status.winner == PLAYER_1 else '2'

    def show_winner(self):
        winner = '1' if self.status.winner == PLAYER_1 else '2'
        print(
            f'Player {winner} won: {self.status.winner_score} vs {self.status.loser_score}!')
