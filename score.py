from player import Player


class Score:
    history: list[Player] = []

    rounds_limit = 0

    def __init__(self, limit: int = 3) -> None:
        self.rounds_limit = limit

    def reset(self):
        self.history.clear()

    def put_winner(self, winner: Player):
        self.history.append(winner)

    def is_final(self):
        return len(self.history) >= self.rounds_limit

    def get_by_player(self, player: Player):
        return self.history.count(player)

    def get_leader(self):
        counter = 0
        leader = self.history[0]

        for player in self.history:
            curr_frequency = self.history.count(player)

            if curr_frequency > counter:
                counter = curr_frequency
                leader = player

        return leader
