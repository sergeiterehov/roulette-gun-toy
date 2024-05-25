from player import Player

class Health:
  values: dict[Player, int] = {}
  maximum = 1

  def __init__(self, players: list[Player], maximum: int = 5) -> None:
    self.maximum = maximum

    for player in players:
      self.values[player] = maximum

  def reset(self, amount: int = None):
    if amount == None: amount = self.maximum

    amount = min(amount, self.maximum)

    for player in self.values.keys():
      self.values[player] = amount

  def get(self, player: Player):
    return self.values[player]
  
  def add(self, player: Player, amount = 1):
    amount = abs(amount)

    self.values[player] = min(self.values[player] + amount, self.maximum)
  
  def reduce(self, player: Player, amount = 1):
    amount = abs(amount)

    self.values[player] = max(0, self.values[player] - amount)