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
