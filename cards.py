from player import Player


class CardType:
    LOOK = 1
    HEAL = 2
    EJECT = 3
    MAGNUM = 4
    HOLDER = 5
    TAROT = 6
    INVERT = 7
    STEAL = 8
    CHANCE = 9


class Cards:
    library: int = 0
    maximum = 1

    stack: int = 0
    over: int = 0
    owned: dict[Player, int] = {}

    def __init__(
        self, players: list[Player], maximum: int = 8, library: int = 25
    ) -> None:
        self.maximum = maximum
        self.library = library

        self.over = 0
        self.stack = self.library

        for player in players:
            self.owned[player] = 0

    def reset(self):
        self.over = 0
        self.stack = self.library

        for player in self.owned.keys():
            self.owned[player] = 0

    def get_by_player(self, player: Player):
        return self.owned[player]

    def add(self, amount: int = None):
        if amount == None:
            amount = self.maximum

        amount = min(self.maximum, max(0, amount))

        for player in self.owned.keys():
            current = self.owned[player]
            diff = min(self.maximum, current + amount) - current

            self.stack -= diff
            self.owned[player] += diff

    def use(self, player: Player):
        self.owned[player] -= 1
        self.over += 1
