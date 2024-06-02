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
  HOPE = 9

class Card:
  type: CardType = CardType.LOOK

  def __init__(self, type: CardType) -> None:
    self.type = type

class Cards:
  lib: list[Card] = []
  stack: list[Card] = []

  owned: dict[Player, list[Card]] = {}

  maximum = 1

  def __init__(self, players: list[Player], maximum: int = 8) -> None:
    self.maximum = maximum

    for type in range(1,9):
      for _ in range(maximum):
        self.lib.append(Card(type))

    for player in players:
      self.owned[player] = []

  def reset(self):
    self.stack = []

    for player in self.owned.keys():
      self.owned[player] = []

  def get_credit(self, player: Player):
    return self.owned[player]
  
  def make_stack(self):
    for player in self.owned.keys():
      self.owned[player] = []

    self.stack = [e for e in self.lib]

    return self.stack

  def add(self, amount: int = None):
    if amount == None: amount = self.maximum

    amount = min(self.maximum, max(0, amount))

    for player in self.owned.keys():
      current = len(self.owned[player])
      diff = min(self.maximum, current + amount) - current

      for _ in range(diff):
        card = self.stack.pop()
        self.owned[player].append(card)

  def validate(self, player: Player, card: Card):
    return card in self.owned[player]

  def use(self, player: Player, card: Card):
    self.owned[player].remove(card)