def minimax(self, depth=2, maximizing=True):
    """
    Determines the optimal action to play jouer following minimax
    algorithm

    Args:
        depth (int): depth to explore in the possibles actions tree
        maximizing (bool): True if we want to maximise the score,
        False if we want to minimise it

    Returns:
        Action: best action found in explored depth
    """
    if depth == 0:
        return (None, DRAW)
    if maximizing:
        best_score = -INF
        player = self.player_id
    else:
        best_score = +INF
        player = self.other_player_id
    best_actions = []
    assert self.board.has_moves(player)
    for action in self.board.possible_actions(player):
        self.board.act(action)
        winner = self.board.status.winner
        if winner is not None:
            # better win early or lose late
            score = WIN + depth
            if winner == self.other_player_id:
                score *= -1
        else:
            score = self.minimax(depth - 1, not maximizing)[1]
        self.board.undo()
        # Si on trouve un meilleur score
        if (score > best_score and maximizing) or (
                score < best_score and not maximizing):
            best_score = score
            best_actions = [action]
        elif score == best_score:
            best_actions.append(action)
    return random.choice(best_actions), best_score
