from const import *
from convex_hull import QuickHull
from exceptions import *
from action import Action
from players import Player, AIPlayer
from board import EndOfGameStatus
from time import time
from pos2d import Pos2D
from copy import deepcopy
from collections import deque


class TournoiAIPlayer(AIPlayer):
    """
    [queen in a region isolated from enemy] action decreases its
    region's points -> play only [exposed to enemy queen] action

    new_pos and arrow_pos next enemy > not
    """

    def __init__(self, board, player_id):
        super().__init__(board, player_id)

        self.player_id = player_id
        self.board_copy = board
        self.action_number = 0
        self.board_queens = self.board_copy.queens
        self.player_queens = self.board_queens[player_id]
        self.isolated_queens = []
        self.exposed_queens = self.board_queens
        self.player_exposed_queens = self.exposed_queens[player_id]
        self.player_exposed_queens_nb = len(self.player_exposed_queens)

        self.other_player_exposed_queens = self.board.queens[
            self.other_player_id]
        self.other_player_exposed_queens_nb = len(
            self.other_player_exposed_queens)
        self.win = board.N ** 2
        self.board_state_dico = {}
        self.depth_range = self.board.N ** 2

    def play(self):
        """
        """
        start = time()
        self.board_copy = self.board
        self.timeout = False
        self.t = start + 1.9
        best_action = None
        best_score = -INF
        for depth in range(1, self.depth_range):  # iterative deepening
            action, score = self.m(self.player_id,
                                   1,
                                   -INF,
                                   +INF,
                                   depth
                                   )
            if self.timeout:
                if not best_action or (best_score < score):
                    best_action = action
                break
            else:
                best_action = action
        self.board.act(best_action)
        self.action_number += 1

    def m(self,
          player_id,
          color,
          best_score,
          worst_score,
          depth):
        """
        Détermine le coup optimal à jouer selon l'algorithme negascout.

        Args:
            depth (int): la profondeur à explorer dans l'arbre des coups
             possibles

        Returns:
            Action: le meilleur coup trouvé dans la profondeur explorée
        """
        action = None
        best_action = None

        if depth == 0:
            return (None, color * self.objective_function(
                player_id))
        child = -1
        try:
            possible_actions = self.board_state_dico[
                self.board_copy.grid,
                player_id]
        except:
            possible_actions = self.gen_possible_actions(player_id)
            self.board_state_dico[deepcopy(self.board_copy.grid),
                                  player_id] = \
                possible_actions
        for action in possible_actions:
            now = time()
            if self.t < now:
                self.timeout = True
                break
            child += 1
            self.board_copy.act(action)
            winner = self.status().winner
            if winner is not None:
                score = self.win + depth
                if winner == abs(player_id - 1):
                    score *= -1

            elif not child:
                score = -self.m(abs(player_id - 1),
                                -color,
                                -worst_score,
                                -best_score,
                                depth - 1)[1]
            else:
                score = -self.m(abs(player_id - 1),
                                -color,
                                -best_score - 1,
                                -best_score,
                                depth - 1)[1]
                if best_score < score and score < worst_score:
                    score = -self.m(abs(player_id - 1),
                                    -color,
                                    -worst_score,
                                    -best_score,
                                    depth - 1)[1]

            self.board_copy.undo()
            if score > best_score:
                best_score = score
                best_action = action

            if worst_score <= best_score:
                break  # worst score cut-off
        if self.timeout:
            best_action = action
        return best_action, best_score

    def objective_function(self, player_id):
        if self.board_copy.scores[0]:
            return self.board_copy.scores[player_id] - \
                   self.board_copy.scores[abs(player_id - 1)]
        else:
            return 0

    def aim(self, player_id):
        average_pos = Pos2D(0, 0)

        for pos in self.board_copy.queens[player_id]:
            average_pos += pos
        for coord in [average_pos.y_, average_pos.x_]:
            coord *= 1 / len(self.board_copy.queens[player_id])

        other_player_average_pos = Pos2D(0, 0)
        for pos in self.board_copy.queens[abs(player_id - 1)]:
            other_player_average_pos += pos
        for coord in [other_player_average_pos.y_,
                      other_player_average_pos.x_]:
            coord *= 1 / len(self.board_copy.queens[player_id - 1])

        compare_average_pos = average_pos - other_player_average_pos
        if 0 < compare_average_pos.y_:
            # player_queens
            # other_player_queens
            if 0 < compare_average_pos.x_:
                #                     player_queens
                # other_player_queens

                directions = (SOUTH_WEST, WEST, SOUTH,
                              SOUTH_EAST, EAST, NORTH,
                              NORTH_EAST, NORTH_WEST)
            elif compare_average_pos.x_ < 0:
                # player_queens
                #               other_player_queens
                directions = (SOUTH_EAST, EAST, SOUTH,
                              SOUTH_WEST, WEST, NORTH,
                              NORTH_EAST, NORTH_WEST)
            else:
                directions = (SOUTH, SOUTH_EAST, SOUTH_WEST,
                              WEST, EAST, NORTH, NORTH_EAST,
                              NORTH_WEST)
        elif compare_average_pos.y_ < 0:
            # other_player_queens
            # player_queens
            if 0 < compare_average_pos.x_:
                # other_player_queens
                #                       player_queens
                directions = (NORTH_WEST, WEST, NORTH, NORTH_EAST,
                              SOUTH_EAST, SOUTH_WEST, EAST, SOUTH)
            elif compare_average_pos.x_ < 0:
                #                   other_player_queens
                # player_queens
                directions = (NORTH_EAST, EAST, NORTH,
                              NORTH_WEST, SOUTH_EAST,
                              SOUTH_WEST, WEST, SOUTH)
            else:
                directions = (NORTH, NORTH_EAST, NORTH_WEST, EAST,
                              WEST, SOUTH_EAST, SOUTH_WEST, SOUTH)
        else:
            # player_queens y = other_player_queens y
            if 0 < compare_average_pos.x_:
                # other_player_queens player_queens
                directions = (WEST, NORTH_WEST, SOUTH_WEST,
                              NORTH, SOUTH, NORTH_EAST,
                              SOUTH_EAST, EAST)

            elif compare_average_pos.x_ < 0:
                # player_queens other_player_queens
                directions = (EAST, NORTH_EAST, SOUTH_EAST,
                              NORTH, SOUTH,
                              NORTH_WEST,
                              SOUTH_WEST, WEST)
            else:
                # player_queens x = other_player_queens x
                directions = DIRECTIONS
        # directions = directions[:(self.action_number + 2)]
        directions = tuple(Vec2D(*direction) for direction in
                           directions)
        # tuple des 8 directions (inter)cardinales
        return directions

    def gen_possible_actions(self, player_id,
                             aim=True):
        """
        Énumère les actions possibles pour un certain joueur
        Args:
            player_id (int): l'id du joueur
        Returns:
            generator: un générateur listant toutes les actions
            possibles pour chaque reine du joueur
        """
        if aim:
            directions = self.aim(player_id)
        else:
            directions = DIRECTIONS
        actions = []
        for queen in self.board_copy.queens[player_id]:
            possible_new_pos = self.possible_moves_from(player_id,
                                                        queen,
                                                        aim,
                                                        directions)
            for new_pos in possible_new_pos:
                possible_arrow_pos = self.possible_moves_from(player_id,
                                                              new_pos,
                                                              aim,
                                                              directions,
                                                              ignore=queen)
                for arrow_pos in possible_arrow_pos:
                    actions.append(Action(queen, new_pos, arrow_pos,
                                          player_id))
        return actions

    def possible_moves_from(self,
                            player_id,
                            origin,
                            aim,
                            directions,
                            ignore=None):
        """
        Énumère les déplacements possibles depuis une certaine
        position sur le plateau
        Args: origin (Pos2D): la position de
        départ d'une reine ignore (Pos2D): une potentielle position à
        ignorer et None sinon
        """
        moves = deque()
        if aim and self.action_number < len(self.board.queens[
                                                abs(player_id) - 1]):
            # queens aim and not all other player queens moved
            # assume most of them are stacked to other board edge
            for direction in directions:
                new_pos = origin + direction
                while self.board_copy.is_valid_pos(new_pos) and \
                        (self.board_copy.at(new_pos) == EMPTY or
                         (ignore is not None and new_pos == ignore)):
                    placed = False
                    for front_direction in directions[:3]:
                        neighbor_pos = new_pos + front_direction
                        if self.board_copy.is_valid_pos(
                                neighbor_pos) and \
                                self.board_copy.at(neighbor_pos) == abs(
                            player_id - 1):
                            moves.appendleft(new_pos.copy())
                            placed = True
                            break
                    if not placed:
                        moves.append(new_pos.copy())
                    new_pos += direction
        else:
            for direction in directions:
                new_pos = origin + direction
                while self.board_copy.is_valid_pos(new_pos) and \
                        (self.board_copy.at(new_pos) == EMPTY or
                         (ignore is not None and new_pos == ignore)):
                    moves.append(new_pos.copy())
                    new_pos += direction
        return moves

    def act(self, action, log_action=True):
        """
        Effectue une action sur le plateau.
        Args:
            action (Action): l'action à effectuer
            log_action (bool): True pour ajouter l'action à l'historique
             et False sinon
        Raises:
            TypeError: si action n'a pas le bon type
            InvalidActionError: si l'action demandée n'est pas valide
        """
        self.move(action.old_pos, action.new_pos,
                  action.player_id)
        self.shoot_arrow(action.arrow_pos)
        if log_action:
            self.board_copy.history.append(action)

    def move(self, old_pos, new_pos, player_id):
        """
        Déplace une reine sur le plateau.
        Args:
            old_pos (Pos2D): la position actuelle de la reine
            new_pos (Pos2D): la position de la reine après déplacement
        """
        self.board_copy.grid[
            new_pos] = player_id  # on ajoute une reine à la nouvelle position
        self.board_copy.grid[
            old_pos] = EMPTY  # et on retire la reine à l'ancienne position
        # On modifie la position de la reine dans la liste queens
        idx = self.board_copy.queens[player_id].index(old_pos)
        self.board_copy.queens[player_id][idx] = new_pos

    def shoot_arrow(self, pos):
        """
        Tire une flèche sur le plateau
        Args:
            pos (Pos2D): la position où tirer la flèche
        """
        self.board_copy.grid[pos] = ARROW
        self.board_copy.nb_arrows += 1

    def undo(self):
        """
        Revient en arrière d'une action (utile pour le minimax).
        """
        action = self.board_copy.history.pop()
        self.move(action.new_pos, action.old_pos,
                  action.player_id)  # on
        # déplace dans
        # le sens inverse
        if action.arrow_pos != action.old_pos:
            self.board_copy.grid[action.arrow_pos] = EMPTY  # et on
            # retire la
            # flèche (si nécessaire)
        self.board_copy.nb_arrows -= 1

    def status(self):
        """
        EndOfGameStatus: le statu de fin de partie
        """
        # il ne faut chercher à identifier les différentes composantes connexes que s'il
        # y a au moins 4 flèches sur le plateau.
        # En effet, si ce n'est pas le cas, alors il n'y a obligatoirement qu'une
        # unique composante connexe contenant toutes les reines.
        if 3 < self.board_copy.nb_arrows:
            if self.check_regions():
                # return EndOfGameStatus(*self.board_copy.scores)
                return EndOfGameStatus(*self.board_copy.scores)
        player1_has_moves = self.board_copy.has_moves(PLAYER_1)
        player2_has_moves = self.board_copy.has_moves(PLAYER_2)
        if player1_has_moves and player2_has_moves:
            return EndOfGameStatus()  # Partie pas encore finie
        return EndOfGameStatus(
            *map(int, (player1_has_moves, player2_has_moves)))

    def check_regions(self):
        """
        Vérifie que toutes les composantes connexes du plateau sont de forme
        simple et ne contiennent qu'une unique reine.
        Returns:
            bool: True si la condition est remplie et False sinon
        """
        components, component_ids = self.board_copy.label_components()
        # if len(components) < self.board_copy.nb_queens:
        #   return False
        return self.identify_components(components)

    def identify_components(self, components):
        """
        Détermine si toutes les composantes connexes sont simples et à
        une seule reine.
        Args:
            component (list): liste des positions dans la composante
        Returns:
            bool: True si la condition est vérifiée et False sinon
        """
        self.board_copy.scores = [0, 0]
        for component in components:
            player_id, nb_queens, is_simple = self.board_copy.is_simple(
                component)
            if nb_queens == 0:
                continue
            if player_id is None or nb_queens != 1:
                return False

            if not is_simple:

                return False
            self.board_copy.scores[player_id] += len(component) - 1
        return True

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
        component_queen  = None
        res = self.count_queens(component)
        if res[2] is not None:
            player, nb_queens, component_queen = res
        else:
            player, nb_queens = res[: 2]
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
        elif not self.in_snake_canyon(component, component_queen):
            is_simple = True

        return player, nb_queens, is_simple

    def in_snake_canyon(self, component, component_queen):
        for tile in component:
            pass
            # if neighbors form a snake canyon:
                # return True

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
        component_queen = None # todo

        component = set(component)
        component_queens = [[], []]
        component_queens[0] = list(component & set(
            self.board_copy.queens[PLAYER_1]))
        component_queens[1] = list(component & set(
            self.board_copy.queens[PLAYER_2]))
        if (component_queens[0] and component_queens[1]) or not (
                component_queens[0] or component_queens[1]):
            # il y a des reines des deux joueurs dans la composante
            # ou il n'y en a pas
            player = None
        else:
            if component_queens[0]:
                player = PLAYER_1
            else:
                player = PLAYER_2
            for q in component_queens[player]:
                self.board_copy.queens[player].sort(key=q.__eq__)
            if len(component_queens[player]) == 1:
                component_queen = component_queens[player][0]

        return [player, len(component_queens[0]) + len(
            component_queens[1]), component_queen]

    def get_smallest_subregions_tiles_number(self,
                                             component,
                                             queen_position):
        queen_adjacent_free_tiles = self.get_free_adjacent_tiles(
            component,
            queen_position)
        if len(queen_adjacent_free_tiles) == 2:
            # if vertical NW-queen-SW or NE-queen-SE or... snake:
            if self.tile_in_mid_of_snake_canyon(
                    queen_adjacent_free_tiles,
                    queen_position):
                print('queen_in_mid_of_snake_canyon')
                smallest_subregion_tile_number = \
                    self.get_smallest_subregion_tile_number(
                        component,
                        queen_position)
                if smallest_subregion_tile_number == 0:
                    # no subregion, no baggend
                    pass
                elif smallest_subregion_tile_number == 1:
                    # 1 subregion is 1 tile baggend
                    region_map = self.region_map(component,
                                            queen_adjacent_free_tiles,
                                            queen_position)
                    if region_map == 'size3snake':
                        # the 2 subregions are 1 tile baggend
                        return 1
                    elif region_map == 'other':
                        pass

    def get_smallest_subregion_tile_number(self, component,
                                           queen_position):
        arrowqueen_subregion = deepcopy(component)
        arrowqueen_subregion[queen_position[0]][queen_position[
            1]] = 'X'
        label_region = self.board_copy.label_components()(
            label_region=component,
            game_region=arrowqueen_subregion)
        subregion0tile_number = 0
        subregion1tile_number = 0
        for y in range(len(label_region)):
            for x in range(len(label_region)):
                if label_region[y][x] == 1:
                    subregion0tile_number += 1
                elif label_region[y][x] == 2:
                    subregion1tile_number += 1
        smallest_subregion_tile_number = min(
            subregion0tile_number, subregion1tile_number)
        return smallest_subregion_tile_number


    @staticmethod
    def to_Pos2D(history_action):
        x = history_action[3]
        y = history_action[8]
        action = [[x, y]]
        x = history_action[14]
        y = history_action[19]
        action.append([x, y])
        x = history_action[25]
        y = history_action[30]
        action.append([x, y])
        return action
