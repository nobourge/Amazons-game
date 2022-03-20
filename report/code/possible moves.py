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
