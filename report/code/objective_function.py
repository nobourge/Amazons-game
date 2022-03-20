def objective_function(self, player_id):
    if self.board_copy.scores[0]:
        return self.board_copy.scores[player_id] - \
               self.board_copy.scores[abs(player_id - 1)]
    else:
        return 0
