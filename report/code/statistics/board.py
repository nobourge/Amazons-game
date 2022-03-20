from exceptions import InvalidActionError
from action import Action, Pos2D
from const import *
from matrix import Matrix
from convex_hull import QuickHull


def as_char(cell):
    return CHARS[cell]


def argmax(a, b):
    return 0 if a > b else 1


class EndOfGameStatus:
    """
    Une instance de EndOfGameStatus représente l'état de fin de partie,
    i.e. la partie est-elle finie ? Si oui quels sont les scores des joueurs ?
    Et qui a gagné ?
    """

    def __init__(self, score_player_1=None, score_player_2=None):
        self.scores = (score_player_1, score_player_2)

    @property
    def score_player_1(self):
        return self.scores[0]

    @property
    def score_player_2(self):
        return self.scores[1]

    @property
    def winner_score(self):
        return max(self.scores)

    @property
    def loser_score(self):
        return min(self.scores)

    @property
    def winner(self):
        if None in self.scores:
            return None
        else:
            return (PLAYER_1, PLAYER_2)[argmax(*self.scores)]

    @property
    def over(self):
        return self.winner is not None


class Board:
    """
    Classe représentant le plateau de jeu.
    Attributes:
        N (int): dimension du plateau
        grid (Matrix): la grill du plateau de jeu en lui-même
        history (list): historique des coups joués sur le plateau
        queens (list): conteneur des positions des reines de chacun des joueurs
        nb_arrows (int): nombre de flèches présentes sur le plateau
        scores (list): score de chaque joueur
    """
    #                     PLAYER_2   PLAYER_1

    def __init__(self, N, pos_black, pos_white, pos_arrows):
        self.N = N
        self.letters = ' '.join(map(chr, range(ord('a'), ord('a')+self.N)))
        self.grid = Matrix(self.N, EMPTY)
        self.history = []
        for positions, value in zip([pos_white, pos_black, pos_arrows], [PLAYER_1, PLAYER_2, ARROW]):
            for pos in positions:
                self.grid[pos] = value
        self.queens = [list(map(Pos2D.from_string, positions))
                       for positions in (pos_white, pos_black)]
        self.nb_arrows = len(pos_arrows)
        self.scores = [None, None]  # score of player 1 and player 2

    @property
    def size(self):
        """
        int: Dimension du plateau de jeu
        """
        return self.N

    @property
    def all_queens(self):
        """
        generator: Positions des reines
        """
        for array in self.queens:
            for pos in array:
                yield pos

    @property
    def nb_queens(self):
        """
        int: Nombre de reines sur le plateau
        """
        return sum(map(len, self.queens))

    def label_components(self):
        """
        Identifie les composantes connexes du plateau de jeu
        Returns:
            tuple: (components, component_ids) où components est une liste dont chaque
            élément est une liste contenant une composante connexe et où component_ids
            est une matrice pour laquelle l'entrée (i, j) contient un identifiant
            permettant de déterminer de manière unique chaque composante
        """
        component_ids = Matrix(self.size, -1)
        components = []  # Par défaut : aucune composante connexe
        component_id = 0  # On commence à identifier les composantes par l'id 0
        for row in range(self.size):
            for col in range(self.size):
                pos = Pos2D(row, col)  # Pour chaque position pos
                if component_ids[pos] != -1:  # si la case est déjà dans une composante connexe
                    continue  # on passe à la case suivante
                # si la case est une flèche, on l'ignore
                if self.at(pos) != ARROW:
                    # sinon on détermine la composante connexe qui contient cette case
                    components.append([])
                    self.label_component(component_ids, components[-1], component_id, pos)
                    component_id += 1  # une fois la composante déterminée, on passe à l'id suivant
        return components, component_ids

    def label_component(self, component_ids, component, component_id, pos):
        """
        Détermine récursivement la composante connexe qui contient la case pos.
        Args:
            component_ids (Matrix): matrice d'ids des composantes connexes pour chaque case
            component (list): liste contenant toutes les positions dans la composante connexe
            component_id (int): id de la composante connexe contenant la case pos
            pos (Pos2D): position sur le plateau
        """
        # Si la case a déjà été visitée, on s'arrête
        if component_ids[pos] != -1:
            return
        # Sinon on ajoute la case à la composante connexe
        component_ids[pos] = component_id
        component.append(pos)
        for direction in DIRECTIONS:
            new_pos = pos+direction
            # Et on recommence sur chaque case adjacente
            if self.is_valid_pos(new_pos) and self.at(new_pos) != ARROW:
                self.label_component(component_ids, component, component_id, new_pos)

    def check_regions(self):
        """
        Vérifie que toutes les composantes connexes du plateau sont de forme
        simple et ne contiennent qu'une unique reine.
        Returns:
            bool: True si la condition est remplie et False sinon
        """
        components, component_ids = self.label_components()
        if len(components) < self.nb_queens:
            return False
        return self.identify_components(components)

    def count_queens(self, component):
        """
        Compte le nombre de reines dans la composante connexe actuelle.
        Args:
            component (list): liste de positions de la composante connexe
        Returns:
            tuple: (player, count) où player est l'identifiant du joueur qui possède
                   les reines et où count est le nombre de reines. S'il y a des reines
                   des deux joueurs dans la composante, alors player vaut None.
        """
        component = set(component)
        n1 = len(component & set(self.queens[PLAYER_1]))
        n2 = len(component & set(self.queens[PLAYER_2]))
        player = None if n1*n2 != 0 else PLAYER_1 if n2 == 0 else PLAYER_2
        return player, n1+n2

    def is_simple(self, component):
        """
        Détermine si une composante connexe est simple.
        On peut déterminer la forme d'une composante connexe sur base du nombre de points de
        son enveloppe convexe comme calculée par quickhull. Notons C la composante connexe
        et E = Conv C son enveloppe convexe. Notons également W et H la longueur (donc xmax - xmin)
        et la hauteur (donc ymax - ymin) de C (et donc de E). Nous savons que :
        * C est un rectangle ssi |E| = 4 et |C| = W x H ;
        * C est une ligne horizontale ssi (|E| = 2 ou H = 1) et |C| = W ;
        * C est une ligne verticale ssi (|E| = 2 ou W = 1) et |C| = H ;
        * C est une ligne diagonale ssi |E| = 2 et |C| = W = H ;
        * C est un triangle de type 1 ssi |E| = 3 et H = W et |C| = W(W+1)/2 ;
        * C est un triangle de type 2 ssi |E| = 3 et n = m^2 et M = 2m-1 pour m = min{H, W} et M = max{H, W}.
        Ces critères se démontrent facilement sur base de la forme des composantes et ne nécessitent que des
        informations sur le nombre d'éléments dans l'enveloppe convexe pour déterminer la forme de la composante
        et sur le nombre d'éléments dans la composante connexe pour s'assurer que l'ensemble n'a pas de "trou" et
        qu'il ne "dépasse" pas.
        Args:
            component (list): liste des positions de la composante connexe
        Returns:
            tuple: (player, count, is_simple) où is_simple est un bool et où
                   (player, count) est l'output de count_queens(component)
        """
        player, nb_queens = self.count_queens(component)
        if player is None or nb_queens != 1:
            return player, nb_queens, False
        convex_hull = QuickHull(component).compute()
        w = convex_hull.width
        h = convex_hull.height
        n = len(component)
        is_simple = False
        if w == 1 and n == h or h == 1 and n == w:  # H/V line
            is_simple = True
        elif w == h == n:  # diagonal line
            is_simple = True
        elif n == w*h:  # rectangle
            is_simple = True
        elif n == 3:  # triangle
            if h == w and 2*n == h*(h+1):  # type 1
                is_simple = True
            else:
                m, M = min(h, w), max(h, w)
                if M == 2*m-1 and n == m*m:  # type 2
                    is_simple = True
        return player, nb_queens, is_simple

    def identify_components(self, components):
        """
        Détermine si toutes les composantes connexes sont simples et à une seule reine.
        Args:
            component (list): liste des positions dans la composante
        Returns:
            bool: True si la condition est vérifiée et False sinon
        """
        self.scores = [0, 0]
        for component in components:
            player, nb_queens, is_simple = self.is_simple(component)
            if nb_queens == 0:
                continue
            if player is None or nb_queens != 1 or not is_simple:
                return False
            self.scores[player] += len(component)-1
        return True

    @property
    def status(self):
        """
        EndOfGameStatus: le statu de fin de partie
        """
        # il ne faut chercher à identifier les différentes composantes connexes que s'il
        # y a au moins autant de flèches sur le plateau que de lignes/colonnes.
        # En effet, si ce n'est pas le cas, alors il n'y a obligatoirement qu'une
        # unique composante connexe contenant toutes les reines.
        if self.nb_arrows >= self.size:
            if self.check_regions():
                return EndOfGameStatus(*self.scores)
        player1_has_moves = self.has_moves(PLAYER_1)
        player2_has_moves = self.has_moves(PLAYER_2)
        if player1_has_moves and player2_has_moves:
            return EndOfGameStatus()  # Partie pas encore finie
        return EndOfGameStatus(*map(int, (player1_has_moves, player2_has_moves)))

    def has_moves(self, player_id):
        """
        Détermine si un certain joueur a encore des coups possibles
        Args:
            player_id (int): l'id du joueur
        Returns:
            bool: True si le joueur a encore des coups possibles et False sinon
        """
        possible_actions = self.possible_actions(player_id)
        # Puisque possible_actions est un générateur, on regarde s'il est vide ou non.
        # Il n'est donc pas nécessaire de lister tous les mouvements potentiels si
        # on cherche uniquement à s'assurer qu'il y en a au moins un
        return next(possible_actions, None) is not None

    def act(self, action, log_action=True):
        """
        Effectue une action sur le plateau.
        Args:
            action (Action): l'action à effectuer
            log_action (bool): True pour ajouter l'action à l'historique et False sinon
        Raises:
            TypeError: si action n'a pas le bon type
            InvalidActionError: si l'action demandée n'est pas valide
        """
        if not isinstance(action, Action):
            raise TypeError('Une instance de Action est attendue')
        if not self.is_valid_action(action):
            raise InvalidActionError(
                f'{action} n\'est pas une action valide pour le joueur {action.player_id}')
        self._move(action.old_pos, action.new_pos)  # on déplace la reine
        self._shoot_arrow(action.arrow_pos)  # et on tire la flèche
        if log_action:
            self.history.append(action)

    def _move(self, old_pos, new_pos):
        """
        Déplace une reine sur le plateau.
        Args:
            old_pos (Pos2D): la position actuelle de la reine
            new_pos (Pos2D): la position de la reine après déplacement
        """
        player_id = self.grid[old_pos]  # on regarde quel joueur veut faire le déplacement
        self.grid[new_pos] = player_id  # on ajoute une reine à la nouvelle position
        self.grid[old_pos] = EMPTY  # et on retire la reine à l'ancienne position
        # On modifie la position de la reine dans la liste queens
        idx = self.queens[player_id].index(old_pos)
        self.queens[player_id][idx] = new_pos

    def _shoot_arrow(self, pos):
        """
        Tire une flèche sur le plateau
        Args:
            pos (Pos2D): la position où tirer la flèche
        """
        self.grid[pos] = ARROW
        self.nb_arrows += 1

    def at(self, pos):
        """
        Récupère la valeur contenue par une certaine case du plateau de jeu
        Args:
            pos (Pos2D): la position regardée
        Returns:
            int: la valeur à la case du tableau. Est parmi les valeurs suivantes :
                 * PLAYER_1 ;
                 * PLAYER_2 ;
                 * EMPTY ;
                 * ARROW.
        """
        return self.grid[pos]

    def undo(self):
        """
        Revient en arrière d'une action (utile pour le minimax).
        """
        action = self.history.pop()
        self._move(action.new_pos, action.old_pos)  # on déplace dans le sens inverse
        if action.arrow_pos != action.old_pos:
            self.grid[action.arrow_pos] = EMPTY  # et on retire la flèche (si nécessaire)
        self.nb_arrows -= 1

    def is_valid_action(self, action):
        """
        Détermine si une action est valide.
        Args:
            action (Action): l'action qui veut être effectuée
        Returns:
            bool: True si l'action est valide et False sinon
        """
        return self.is_valid_pos(action.old_pos) \
            and self.is_valid_pos(action.new_pos) \
            and self.is_valid_pos(action.arrow_pos) \
            and self.at(action.old_pos) == action.player_id \
            and self.at(action.new_pos) == EMPTY \
            and (self.at(action.arrow_pos) == EMPTY or action.arrow_pos == action.old_pos) \
            and action.arrow_pos != action.new_pos \
            and self.is_accessible(action.old_pos, action.new_pos) \
            and self.is_accessible(action.new_pos, action.arrow_pos, ignore=action.old_pos)

    def is_valid_pos(self, pos):
        """
        Détermine si une position est valide sur le plateau
        Args:
            pos (Pos2D): la position désirée
        Returns:
            bool: True si la position est valide et False sinon
        """
        return 0 <= pos.row < self.size and 0 <= pos.col < self.size

    def is_accessible(self, pos1, pos2, ignore=None):
        """
        Détermine si une case est accessible depuis une reine en une autre position.
        Args:
            pos1 (Pos2D): la position de départ de la reine
            pos2 (Pos2D): la position d'arrivée de la reine
            ignore (Pos2D): Une unique case qui peut potentiellement bloquer la
                            route que l'on doit ignorer (None si aucune telle case)
        Returns:
            bool: True si pos2 ests accessible depuis pos1
        """
        if pos1.row == pos2.row:  # si sur la même colonne
            return self._is_accessible_col(pos1, pos2, ignore)
        elif pos1.col == pos2.col:  # si sur la même ligne
            return self._is_accessible_row(pos1, pos2, ignore)
        elif pos1.row-pos2.row == pos1.col-pos2.col:  # si sur la même diagonale
            return self._is_accessible_diag(pos1, pos2, ignore)
        elif pos1.row-pos2.row == pos2.col-pos1.col:  # si sur la même anti-diagonale
            return self._is_accessible_reverse_diag(pos1, pos2, ignore)
        else:  # sinon
            return False

    def _is_accessible_col(self, pos1, pos2, ignore):
        """
        Détermine si une case est accessible depuis une reine en une autre position sur la même colonne
        Args:
            pos1 (Pos2D): la position de départ de la reine
            pos2 (Pos2D): la position d'arrivée de la reine
            ignore (Pos2D): Une unique case qui peut potentiellement bloquer la
                            route que l'on doit ignorer (None si aucune telle case)
        Returns:
            bool: True si pos2 ests accessible depuis pos1
        """
        return self._is_accessible_direction(pos1, pos2, EAST if pos1.col < pos2.col else WEST, ignore)

    def _is_accessible_row(self, pos1, pos2, ignore):
        """
        Détermine si une case est accessible depuis une reine en une autre position sur la même ligne
        Args:
            pos1 (Pos2D): la position de départ de la reine
            pos2 (Pos2D): la position d'arrivée de la reine
            ignore (Pos2D): Une unique case qui peut potentiellement bloquer la
                            route que l'on doit ignorer (None si aucune telle case)
        Returns:
            bool: True si pos2 ests accessible depuis pos1
        """
        return self._is_accessible_direction(pos1, pos2, SOUTH if pos1.row > pos2.row else NORTH, ignore)

    def _is_accessible_diag(self, pos1, pos2, ignore):
        """
        Détermine si une case est accessible depuis une reine en une autre position sur la même diagonale
        Args:
            pos1 (Pos2D): la position de départ de la reine
            pos2 (Pos2D): la position d'arrivée de la reine
            ignore (Pos2D): Une unique case qui peut potentiellement bloquer la
                            route que l'on doit ignorer (None si aucune telle case)
        Returns:
            bool: True si pos2 ests accessible depuis pos1
        """
        return self._is_accessible_direction(pos1, pos2, NORTH_EAST if pos1.row < pos2.row else SOUTH_WEST, ignore)

    def _is_accessible_reverse_diag(self, pos1, pos2, ignore):
        """
        Détermine si une case est accessible depuis une reine en une autre position sur la même anti-diagonale
        Args:
            pos1 (Pos2D): la position de départ de la reine
            pos2 (Pos2D): la position d'arrivée de la reine
            ignore (Pos2D): Une unique case qui peut potentiellement bloquer la
                            route que l'on doit ignorer (None si aucune telle case)
        Returns:
            bool: True si pos2 ests accessible depuis pos1
        """
        return self._is_accessible_direction(pos1, pos2, NORTH_WEST if pos1.row < pos2.row else SOUTH_EAST, ignore)

    def _is_accessible_direction(self, pos1, pos2, direction, ignore=None):
        """
        Détermine si une case est accessible depuis une reine en une autre position en suivant une certaine direction
        Args:
            pos1 (Pos2D): la position de départ de la reine
            pos2 (Pos2D): la position d'arrivée de la reine
            direction (Vec2D): le vecteur de direction
            ignore (Pos2D): Une unique case qui peut potentiellement bloquer la
                            route que l'on doit ignorer (None si aucune telle case)
        Returns:
            bool: True si pos2 ests accessible depuis pos1
        """
        pos = pos1 + direction
        if pos == pos2:
            return True
        while pos != pos2:
            if self.at(pos) != EMPTY and (ignore is None or pos != ignore):
                return False
            pos += direction
        return True

    def possible_actions(self, player_id):
        """
        Énumère les actions possibles pour un certain joueur
        Args:
            player_id (int): l'id du joueur
        Returns:
            generator: un générateur listant toutes les actions possibles pour
                       chacune des reines du joueur
        """
        for queen in self.queens[player_id]:
            for new_pos in self._possible_moves_from(queen):
                for arrow_pos in self._possible_moves_from(new_pos, ignore=queen):
                    yield Action(queen, new_pos, arrow_pos, player_id)

    def _possible_moves_from(self, origin, ignore=None):
        """
        Énumère les déplacements possibles depuis une certaine position sur le
         plateau
        Args:
            origin (Pos2D): la position de départ d'une reine
            ignore (Pos2D): une potentielle position à ignorer et None sinon
        """
        for direction in DIRECTIONS:
            new_pos = origin+direction
            while self.is_valid_pos(new_pos) and (self.at(new_pos) == EMPTY
                                                  or (ignore is not None and new_pos == ignore)):
                yield new_pos.copy()
                new_pos += direction

    def __str__(self):
        fill = ' '
        align = '<'
        width = 3
        ret = ''
        for i in range(self.size, 0, -1):
            ret += f"{i:{fill}{align}{width}}{' '.join(map(as_char, self.grid.row(i-1)))}\n"
        ret += f"{' ':{fill}{align}{width}}{self.letters}"
        return ret
