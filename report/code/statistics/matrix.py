from pos2d import Pos2D

class Matrix:
    """
    Classe représentant une matrice carrée. Les indices de la matrice sont donnés
    par des instances de Pos2D.

    Attributes:
        n (int): dimension de la matrice
        grid (list): la matrice en tant que telle (représentée par une liste de listes)
    """
    def __init__(self, n, init_value):
        """
        Args:
            n (int): la dimension de la matrice
            init_value (int): la valeur par défaut des entrées de la matrice
        """
        self.n = n
        self.grid = [[init_value]*n for _ in range(n)]

    @property
    def size(self):
        return self.n

    def set(self, pos, value):
        self.grid[pos.row][pos.col] = value

    def __setitem__(self, pos, value):
        """
        Opérateur [] en écriture
        """
        if isinstance(pos, str):
            self.set(Pos2D.from_string(pos), value)
        elif isinstance(pos, Pos2D):
            self.set(pos, value)
        else:
            raise TypeError(f'{type(pos)} n\'est pas un indice valide pour une matrice')

    def at(self, pos):
        return self.grid[pos.row][pos.col]

    def __getitem__(self, pos):
        """
        Opérateur [] en lecture
        """
        if isinstance(pos, str):
            return self.at(Pos2D.from_string(pos))
        elif isinstance(pos, Pos2D):
            return self.at(pos)
        else:
            raise TypeError(f'{type(pos)} n\'est pas un indice valide pour une matrice')

    def row(self, i):
        """
        Récupère la ième ligne de la matrice

        Args:
            i (int): l'indice de la ligne

        Returns:
            list: la ième ligne de la matrice
        """
        return self.grid[i]
