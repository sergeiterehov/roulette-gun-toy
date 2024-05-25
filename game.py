import random
from time import sleep
from player import Player
from health import Health
from cards import Cards
from gun import Gun
import scenario

class Game:
  gun = Gun()

  master = Player()
  slave = Player()

  first = master
  shutter = master

  health = Health([master, slave], maximum=5)

  cards = Cards([master, slave], maximum=8)

  def reset(self):
    self.gun.reset()
    self.health.reset()
    self.cards.reset()
    self.first = self.master
    self.shutter = self.master

  def begin(self):
    self.tell(scenario.call_master)
    self.wait_for_reload()

    self.tell(scenario.master_called)
    self.wait_for_click_ok()

    self.tell(scenario.select_first_player)
    self.wait_for_shut()
    self.first = random.choice([self.master, self.slave])
    master_first = self.first == self.master
    self.health.reset(4)
    self.tell(scenario.before_first_player_is_master if master_first else scenario.before_first_player_is_slave)
    self.tell(scenario.first_player_is)
    self.tell(scenario.first_player_is_master if master_first else scenario.first_player_is_slave)
    self.tell(scenario.after_first_player_is)
    self.wait_for_click_ok()

    self.tell(scenario.main_rules)
    self.tell(scenario.prepare_cards)
    self.load()
    self.shutter = self.first
    self.tell(scenario.order_is_unknown)
    self.tell(scenario.shut_rules)
    self.tell(scenario.first_master if master_first else scenario.first_slave)
    self.tell(scenario.first_is_permanent)

    winner: Player

    winner_1 = self.begin_shutting()
    self.tell(scenario.round_of_master if winner_1 == self.master else scenario.round_of_slave)

    self.tell(scenario.info_screen_is_helpful) # TODO: это было бы прикольно после первого выстрела
    self.tell(scenario.before_explain_cards)

    self.shuffle_cards()
    self.give_cards()

    self.tell(scenario.explain_cards)

    self.load()
    self.shutter = self.first
    self.tell(scenario.first_master if master_first else scenario.first_slave)

    winner_2 = self.begin_shutting()

    if winner_1 == winner_2:
      winner = winner_1
    else:
      self.tell(scenario.round_of_master if winner_2 == self.master else scenario.round_of_slave)
      self.tell(scenario.final)

      self.shuffle_cards()
      self.tell(scenario.reorder_cards)
      self.wait_for_click_ok()

      self.give_cards()
      self.load()
      self.shutter = self.first
      self.tell(scenario.first_master if master_first else scenario.first_slave)

      winner_3 = self.begin_shutting()

      winner = winner_1 if winner_1 == winner_3 else winner_2

    self.tell(scenario.win_master if winner == self.master else scenario.win_slave)
    self.tell(scenario.goodby)

  def begin_shutting(self):
    winner: Player
  
    while True:
      if self.gun.empty():
        self.load()

      is_forward = self.wait_for_shut(with_direction=True)
      is_live = self.gun.shut()

      if not is_live:
        self.tell(scenario.change if is_forward else scenario.not_change)
      else:
        target: Player

        if self.shutter == self.master: target = self.slave if is_forward else self.master
        if self.shutter == self.slave: target = self.master if is_forward else self.slave

        winner = self.master if target == self.slave else self.slave

        self.health.reduce(player=target)

        self.tell(random.choice([
          scenario.after_shut_1,
          scenario.after_shut_2,
          scenario.after_shut_3,
        ]))

      self.monit()
      
      if is_live: break

    self.gun.reset()

    return winner

  def load(self, amount: int = None, amount_live: int = None):
    if amount == None: amount = random.randint(2, 8)
    if amount_live == None: amount_live = round(random.randint(1, amount - 1))

    amount_live = min(amount - 1, amount_live)
    amount_dummy = amount - amount_live
    cartridges = self.gun.make(amount_live, amount_dummy)
    random.shuffle(cartridges)

    self.gun.load(cartridges)

    self.monit()

    self.tell([
      None,
      None,
      scenario.loaded_2,
      scenario.loaded_3,
      scenario.loaded_4,
      scenario.loaded_5,
      scenario.loaded_6,
      scenario.loaded_7,
      scenario.loaded_8,
    ][amount])
    self.tell([
      None,
      scenario.dummy_1,
      scenario.dummy_2,
      scenario.dummy_3,
      scenario.dummy_4,
      scenario.dummy_5,
      scenario.dummy_6,
      scenario.dummy_7,
    ][amount_dummy])
    self.tell([
      None,
      scenario.live_1,
      scenario.live_2,
      scenario.live_3,
      scenario.live_4,
      scenario.live_5,
      scenario.live_6,
      scenario.live_7,
    ][amount_live])

  def shuffle_cards(self):
    self.cards.reset()

    stack = self.cards.make_stack()
    random.shuffle(stack)

  def give_cards(self, amount: int = None):
    if amount == None: amount = random.randint(1, self.cards.maximum - 3)

    self.cards.add(amount)
    self.monit()

    self.tell([
      None,
      scenario.take_1_cards,
      scenario.take_2_cards,
      scenario.take_3_cards,
      scenario.take_4_cards,
      scenario.take_5_cards,
    ][amount])

  def wait_for_reload(self):
    input("RELOAD")

  def wait_for_shut(self, with_direction=False):
    while True:
      value = input("SHUT")

      if not with_direction: return None

      if value == 'forward': return True
      if value == 'back': return False

  def wait_for_click_ok(self):
    input("OK")
  
  def tell(self, chunk: scenario.Chunk):
    for char in chunk.text:
      print(char, end='',flush=True)
      sleep(chunk.duration / len(chunk.text))

    print('')

  def monit(self):
    print('[MONIT]: [!%s/%s]cases->(%s) health(%s:%s)' % (
      self.gun.cartridges.count(True), len(self.gun.cartridges), ''.join(['X' if e else '0' for e in self.gun.history]),
      self.health.get(self.master), self.health.get(self.slave),
    ))
    print('Master cards: %s' % ' | '.join(map(lambda c: c.type.name, self.cards.get_credit(self.master))))
    print('Slave cards: %s' % ' | '.join(map(lambda c: c.type.name, self.cards.get_credit(self.slave))))