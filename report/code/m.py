def m(self, player_id, color, best_score, worst_score, depth):
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
                              player_id] = possible_actions
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
            score = -self.m(abs(player_id - 1), -color, -worst_score,
                            -best_score, depth - 1)[1]
        else:
            score = -self.m(abs(player_id - 1), -color, -best_score - 1,
                            -best_score, depth - 1)[1]
            if best_score < score and score < worst_score:
                score = -self.m(abs(player_id - 1), -color,
                                -worst_score, -best_score, depth - 1)[1]
        self.board_copy.undo()
        if score > best_score:
            best_score = score
            best_action = action
        if worst_score <= best_score:
            break  # worst score cut-off
    if self.timeout:
        best_action = action
    return best_action, best_score
