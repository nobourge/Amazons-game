from pos2d import Vec2D

WHITE = '\u25CB'  # caractère du joueur blanc
BLACK = '\u25CF'  # caractère du joueur noir

INF = float('inf')

PLAYER_1 = 0
PLAYER_2 = 1
EMPTY = 2
ARROW = 3

WIN = 10
DRAW = 0
# LOSS = -WIN

NORTH =      (1, 0)
NORTH_EAST = (1, 1)
EAST =       (0, 1)
SOUTH_EAST = (-1, 1)
SOUTH =      (-1, 0)
SOUTH_WEST = (-1, -1)
WEST =       (0, -1)
NORTH_WEST = (1, -1)
DIRECTIONS = (NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST)
DIRECTIONS = tuple(Vec2D(*direction) for direction in DIRECTIONS)  # tuple des 8 directions (inter)cardinales

#       PLAYER_1  PLAYER_2  EMPTY  ARROW
CHARS = [WHITE,   BLACK,    '.',   'X']

ERREUR_COUP = "Format du coup non valide"
ERREUR_REINE = "Pas de reine à la position de départ"
ERREUR_CHEMIN = "Le coup n'est pas valide, soit parce qu'il ne respecte pas les règles du jeu d'échec, soit parce que " \
                "le chemin est occupé"
MESSAGE_COUP = "Joueur {}, donnez un coup de format 'position reine avant > position reine après > position flèche' " \
               "(ex : a7>b7>a8) >> "
