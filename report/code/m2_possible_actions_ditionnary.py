try:
    possible_actions = self.board_state_dico[
        self.board_copy.grid,
        player_id]
except:
    possible_actions = self.gen_possible_actions(player_id)
    self.board_state_dico[deepcopy(self.board_copy.grid),
                          player_id] = possible_actions
