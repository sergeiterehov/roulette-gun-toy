class Gun:
  history: list[bool] = []
  cartridges: list[bool] = []

  def reset(self):
    self.history = []
    self.cartridges = []

  def empty(self):
    return len(self.cartridges) == 0

  def make(self, live: int, dummy: int) -> list[bool]:
    return [True for _ in range(live)] + [False for _ in range(dummy)]

  def load(self, cartridges: list[bool]):
    self.history = []
    self.cartridges = cartridges

  def shut(self):
    cartridge = self.cartridges.pop()
    self.history.append(cartridge)

    return cartridge