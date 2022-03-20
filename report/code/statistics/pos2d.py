from exceptions import *


def cell_tuple_to_str(tup):
    return str(chr(tup[1] + 97) + str(tup[0] + 1))

def rowcol_to_str(row, col):
    return str(chr(col + 97) + str(row + 1))


class Pos2D:
    """
    Classe représentant une coordonnée (x, y) dans le plan (ou un vecteur dans le plan). Sert également de coordonnées sur le plateau.
    """

    def __init__(self, y, x):
        self.y_ = y
        self.x_ = x

    @property
    def y(self):
        """
        int (ou float): l'ordonnée du point
        """
        return self.y_

    @property
    def row(self):
        """
        int: la ligne de la position dans le plateau
        """
        return self.y

    @property
    def x(self):
        """
        int (ou float): l'abscisse du point
        """
        return self.x_

    @property
    def col(self):
        """
        int: la colonne de la position dans le plateau
        """
        return self.x

    @staticmethod
    def from_string(pos):
        """
        Crée une instance de Pos2D sur base d'un str sous la forme <l><n> où <l> est
        une lettre désignant la colonne et <n> est un nombre désignant la ligne.

        Args:
            pos (str): la position sur le plateau

        Returns:
            Pos2D: la représentation de pos en Pos2D

        Raises:
            InvalidPositionError: si pos ne suit pas le format attendu
        """
        if len(pos) < 2:
            raise InvalidPositionError(
                f'Une position doit être de la forme <l><n> et non: {pos}')
        col = pos[0]
        if not (col.isalpha() and 'a' <= col <= 'z'):
            raise InvalidPositionError(
                'Colonne inconnue: {col}. Doit être entre \'a\' et \'z\'')
        row = pos[1:]
        if not row.isnumeric():
            raise InvalidPositionError(
                'Ligne inconnue: {row}. Doit être un nombre entier')
        return Pos2D(int(row) - 1, ord(col) - ord('a'))

    def __str__(self):
        return f"(x={self.x}, y={self.y})"

    def __repr__(self):
        return f'<Pos2D: {self}>'

    def __eq__(self, other):
        return self.row == other.row \
               and self.col == other.col

    def __iadd__(self, offset):
        """
        Calcule self += offset
        """
        if isinstance(offset, tuple):
            self.y_ += offset[0]
            self.x_ += offset[1]
        elif isinstance(offset, Pos2D):
            self.y_ += offset.y
            self.x_ += offset.x
        else:
            raise TypeError()  # TODO
        return self

    def __add__(self, offset):
        """
        Calcule self + offset
        """
        ret = self.copy()
        ret += offset
        return ret

    def __neg__(self):
        """
        Calcule -self
        """
        return Pos2D(x=-self.x, y=-self.y)

    def __isub__(self, other):
        """
        Calcule self -= other
        """
        self += -other
        return self

    def __sub__(self, other):
        """
        Calcule self - other
        """
        return self + (-other)

    def __matmul__(self, other):
        """
        Calcule le produit scalaire self @ other
        """
        return self.x * other.x + self.y * other.y

    def __imul__(self, scalar):
        """
        Calcule le produit par un scalaire self *= scalar
        """
        if not isinstance(scalar, (int, float)):
            raise TypeError()
        self.x_ *= scalar
        self.y_ *= scalar
        return self

    def __mul__(self, scalar):
        """
        Calcule le produit par un scalaire self * scalar
        """
        ret = self.copy()
        ret *= scalar
        return ret

    def __rmul__(self, scalar):
        """
        compute the scalar product ``scalar * self``
        """
        return self * scalar

    def __lt__(self, other):
        return self.col < other.col or (
                    self.col == other.col and self.row < other.row)

    # Pour stocker un Pos2D dans un set
    def __hash__(self):
        return hash((self.x, self.y))

    def copy(self):
        """
        Crée une copie de l'instance self
        """
        return Pos2D(x=self.x, y=self.y)


Vec2D = Pos2D  # alias pour la classe Pos2D
