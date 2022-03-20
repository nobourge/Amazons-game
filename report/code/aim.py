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
