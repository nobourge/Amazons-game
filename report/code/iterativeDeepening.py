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
