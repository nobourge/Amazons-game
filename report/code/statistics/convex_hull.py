from pos2d import Pos2D
from const import INF

class ConvexHull(set):  # hérite de set
    """
    Classe représentant l'enveloppe convexe d'un ensemble. Se manipule comme un set.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.min_x = +INF
        self.max_x = -INF
        self.min_y = +INF
        self.max_y = -INF

    def add(self, item):
        """
        Ajoute un élément à l'enveloppe convexe (c.f. set.add)
        """
        if not isinstance(item, Pos2D):
            raise TypeError(f'ConvexHull ne peut contenir que des objets de type Pos2D. Reçu :{type(item)}')
        super().add(item)  # on ajoute à l'ensemble
        self.min_x = min(self.min_x, item.x)
        self.max_x = max(self.max_x, item.x)
        self.min_y = min(self.min_y, item.y)
        self.max_y = max(self.max_y, item.y)

    @property
    def width(self):
        """
        int (ou float): la largeur de l'ensemble
        """
        return self.max_x - self.min_x + 1

    @property
    def height(self):
        """
        int (ou float): la hauteur de l'ensemble
        """
        return self.max_y - self.min_y + 1

class QuickHull:
    """
    Classe implémentant l'algorithme quickhull.

    Attributes:
        points (list (ou set)): l'ensemble E dont on veut déterminer Conv E
        convex_hull (ConvexHull): la composante connexe
    """
    def __init__(self, points):
        self.points = points
        self.convex_hull = ConvexHull()

    @staticmethod
    def find_minmax(S):
        """
        Détermine les points d'abscisse minimale et maximale.
        S'il y a plusieurs points ayant la même abscisse minimale (resp. maximale),
        alors on prend celui d'ordonnée minimale (resp. maximale).

        Args:
            S (set (ou list)): ensemble d'instances de Pos2D

        Returns:
            tuple: (min_point, max_point) représentant les instances de Pos2D contenues dans S
                   d'abscisse respectivement minimale et maximale.
        """
        min_point = Pos2D(x=+float('inf'), y=0)
        max_point = Pos2D(x=-float('inf'), y=0)
        for point in S:
            if point.x < min_point.x or (point.x == min_point.x and point.y < min_point.y):
                min_point = point
            if point.x > max_point.x or (point.x == max_point.x and point.y > max_point.y):
                max_point = point
        return min_point, max_point

    def compute(self):
        """
        Calcule l'enveloppe convexe de self.points

        Returns:
            ConvexHull: les coins du polygone Conv E
        """
        min_point, max_point = QuickHull.find_minmax(self.points)
        self.convex_hull.add(min_point)
        self.convex_hull.add(max_point)
        lefts = set()
        rights = set()
        for point, signed_area in QuickHull.signed_areas(min_point, max_point, self.points):
            if signed_area < 0:
                lefts.add(point)
            else:
                rights.add(point)
        self.find_hull(lefts, min_point, max_point)
        self.find_hull(rights, max_point, min_point)
        return self.convex_hull

    @staticmethod
    def signed_areas(a, b, cs):
        """
        Énumère l'aire signée des triangles abc pour chaque c dans cs

        Args:
            a (Pos2D): point d'origine du vecteur ab
            b (Pos2D): point d'arrivée du vecteur ab
            cs (iterable): conteneur de Pos2D

        Returns:
            generator: de float qui sont < 0 si c est à gauche de ab et > 0 si c est à droite de ab
        """
        ab = b-a
        delta_x = ab.x
        delta_y = ab.y
        for c in cs:
            if c is not a and c is not b:
                signed_area = (c.x-a.x)*delta_y - delta_x*(c.y-a.y)
                if signed_area == 0:
                    continue
                yield (c, signed_area)

    @staticmethod
    def signed_area(a, b, c):
        """
        Détermine l'aire signée du triangle abc.

        Args:
            a (Pos2D): premier coin du triangle
            b (Pos2D): deuxième coin du triangle
            c (Pos2D): troisième coin du triangle

        Returns:
            float: l'aire signée de abc
        """
        ab = b-a
        delta_x = ab.x
        delta_y = ab.y
        signed_area = (c.x-a.x)*delta_y - delta_x*(c.y-a.y)
        return signed_area

    def find_hull(self, S, a, b):
        """
        Détermine récursivement l'enveloppe convexe de l'ensemble S (c.f. énoncé)
        """
        if not S:
            return
        c = QuickHull.find_furthest(S, a, b)
        if c is None:
            print(S, a, b)
        self.convex_hull.add(c)
        pc = c-a
        S1 = set()
        S2 = set()
        sign = QuickHull.signed_area(a, c, b)
        for p, signed_area in QuickHull.signed_areas(a, c, S):
            if p is c:
                continue
            if sign*signed_area < 0:
                S1.add(p)
        sign = QuickHull.signed_area(b, c, a)
        for p, signed_area in QuickHull.signed_areas(b, c, S):
            if p is c:
                continue
            if sign*signed_area < 0:
                S2.add(p)
        self.find_hull(S1, a, c)
        self.find_hull(S2, c, b)

    @staticmethod
    def find_furthest(S, a, b):
        """
        Trouve le point de S le plus éloigné du segment [a, b].

        Args:
            S (iterable): conteneur de Pos2D
            a (Pos2D): point d'origine du vecteur ab
            b (Pos2D): point d'arrivée du vecteur ab

        Returns:
            Pos2D: le point de S le plus éloigné de [a, b]
        """
        max_dist = -float('inf')
        furthest = None
        for point in S:
            c = QuickHull.project(a, b, point)
            vec = point-c
            dist = vec @ vec
            if dist > max_dist:
                max_dist = dist
                furthest = point
        return furthest

    @staticmethod
    def project(a, b, c):
        """
        Calcule la projection du point c sur le vecteur ab

        Args:
            a (Pos2D): point d'origine du vecteur ab
            b (Pos2D): point d'arrivée du vecteur ab
            c (Pos2D): point à projeter

        Returns:
            Pos2D: la projection de c sur ab
        """
        ab = b-a
        ac = c-a
        return a + (ab @ ac) / (ab @ ab) * ab
