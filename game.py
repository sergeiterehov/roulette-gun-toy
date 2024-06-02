import random

from player import Player
from health import Health
from score import Score
from cards import Cards
from gun import Gun
import scenario

State_idle = 0
State_reload_to_start = 1
State_ok_to_before_select_master = 2
State_shut_to_select_master = 3
State_ok_to_read_main_rules = 4
State_shut_to_play = 5
State_ok_to_continue_shutting = 6
State_reload_to_continue_shutting = 7
State_ok_to_exit = 8


class Game:
    state = State_idle

    gun = Gun()
    pointed_forward = False

    master = Player()
    slave = Player()

    first = master
    shutter = master

    score = Score(3)
    health = Health([master, slave], maximum=5)

    cards = Cards([master, slave], maximum=8)

    total_shots = 0
    total_cards = 0

    def reset(self):
        self.state = State_idle

        self.gun.reset()
        self.pointed_forward = False
        self.score.reset()
        self.health.reset()
        self.cards.reset()
        self.first = self.master
        self.shutter = self.master

        self.total_shots = 0
        self.total_cards = 0

    def set_direction(self, forward: bool):
        self.pointed_forward = forward

    def begin(self):
        self._tell(scenario.call_master)

        self.state = State_reload_to_start

    def reload(self):
        if self.state == State_reload_to_start:
            self._start()
        elif self.state == State_reload_to_continue_shutting:
            self._reload_and_continue_shutting()

    def shut(self):
        if self.state == State_shut_to_select_master:
            self._select_master()
        elif self.state == State_shut_to_play:
            self._shut()

    def ok(self):
        if self.state == State_ok_to_before_select_master:
            self._before_select_master()
        elif self.state == State_ok_to_read_main_rules:
            self._read_main_rules()
        elif self.state == State_ok_to_continue_shutting:
            self._continue_shutting()
        elif self.state == State_ok_to_exit:
            self._exit()

    def _start(self):
        self._tell(scenario.master_called)

        self.state = State_ok_to_before_select_master

    def _before_select_master(self):
        self._tell(scenario.select_first_player)

        self.state = State_shut_to_select_master

    def _select_master(self):
        self.first = random.choice([self.master, self.slave])
        master_first = self.first == self.master
        self.health.reset(4)
        self._tell(
            scenario.before_first_player_is_master
            if master_first
            else scenario.before_first_player_is_slave
        )
        self._tell(scenario.first_player_is)
        self._tell(
            scenario.first_player_is_master
            if master_first
            else scenario.first_player_is_slave
        )
        self._tell(scenario.after_first_player_is)

        self.state = State_ok_to_read_main_rules

    def _read_main_rules(self):
        master_first = self.first == self.master

        self._tell(scenario.main_rules)
        self._tell(scenario.prepare_cards)
        self._load()
        self.shutter = self.first
        self._tell(scenario.order_is_unknown)
        self._tell(scenario.shut_rules)
        self._tell(scenario.first_master if master_first else scenario.first_slave)
        self._tell(scenario.first_is_permanent)

        self.state = State_shut_to_play

    def _shut(self):
        if self.gun.empty():
            # Но такого быть не должно!
            return

        self.total_shots += 1

        is_forward = self.pointed_forward
        is_lethal = self.gun.shut()

        if not is_lethal:
            self._tell(scenario.change if is_forward else scenario.not_change)

            self.shutter = self.slave if self.shutter == self.master else self.master
            self._monit()

            self.state = State_ok_to_continue_shutting
            return

        victim: Player

        if self.shutter == self.master:
            victim = self.slave if is_forward else self.master
        else:
            victim = self.master if is_forward else self.slave

        self.health.reduce(victim)
        self._monit()

        self._tell(
            random.choice(
                [
                    scenario.after_shut_1,
                    scenario.after_shut_2,
                    scenario.after_shut_3,
                ]
            )
        )

        if self.total_shots == 1:
            self._tell(scenario.info_screen_is_helpful)

        if self.health.get(victim) <= 0:
            self._tell(
                scenario.round_of_master
                if self.shutter == self.master
                else scenario.round_of_slave
            )

            self.score.put_winner(self.shutter)

            if self.score.is_final():
                winner = self.score.get_leader()

                self._tell(scenario.win_master if winner == self.master else scenario.win_slave)
                self._tell(scenario.goodby)

                self.state = State_ok_to_exit
            else:
                pass

            return

        if self.total_cards == 0:
            self._tell(scenario.before_explain_cards)

            self._shuffle_cards()
            self._give_cards()

        if self.gun.empty():
            self.state = State_reload_to_continue_shutting
        else:
            self.state = State_ok_to_continue_shutting

    def _reload_and_continue_shutting(self):
        self._load()

        self.state = State_shut_to_play

    def _continue_shutting(self):
        self.state = State_shut_to_play

    def _exit(self):
        self.reset()

        self.state = State_idle

    def _load(self, amount: int = None, amount_live: int = None):
        if amount == None:
            amount = random.randint(2, 8)
        if amount_live == None:
            amount_live = round(random.randint(1, amount - 1))

        amount_live = min(amount - 1, amount_live)
        amount_dummy = amount - amount_live
        cartridges = self.gun.make(amount_live, amount_dummy)
        # random.shuffle(cartridges)

        self.gun.load(cartridges)

        self._monit()

        self._tell(
            [
                None,
                None,
                scenario.loaded_2,
                scenario.loaded_3,
                scenario.loaded_4,
                scenario.loaded_5,
                scenario.loaded_6,
                scenario.loaded_7,
                scenario.loaded_8,
            ][amount]
        )
        self._tell(
            [
                None,
                scenario.dummy_1,
                scenario.dummy_2,
                scenario.dummy_3,
                scenario.dummy_4,
                scenario.dummy_5,
                scenario.dummy_6,
                scenario.dummy_7,
            ][amount_dummy]
        )
        self._tell(
            [
                None,
                scenario.live_1,
                scenario.live_2,
                scenario.live_3,
                scenario.live_4,
                scenario.live_5,
                scenario.live_6,
                scenario.live_7,
            ][amount_live]
        )

    def _shuffle_cards(self):
        self.cards.reset()

        stack = self.cards.make_stack()
        # random.shuffle(stack)

    def _give_cards(self, amount: int = None):
        if amount == None:
            amount = random.randint(1, self.cards.maximum - 3)

        self.cards.add(amount)
        self.total_cards += amount
        self._monit()

        self._tell(
            [
                None,
                scenario.take_1_cards,
                scenario.take_2_cards,
                scenario.take_3_cards,
                scenario.take_4_cards,
                scenario.take_5_cards,
            ][amount]
        )

    def _tell(self, chunk: scenario.Chunk):
        print(chunk)

    def _monit(self):
        print(
            "[MONIT]: [!%s/%s]cases->(%s) health(%s:%s)"
            % (
                self.gun.cartridges.count(True),
                len(self.gun.cartridges),
                "".join(["X" if e else "0" for e in self.gun.history]),
                self.health.get(self.master),
                self.health.get(self.slave),
            )
        )
        print(
            "Master cards: %s"
            % " | ".join([str(c.type) for c in self.cards.get_credit(self.master)])
        )
        print(
            "Slave cards:  %s"
            % " | ".join([str(c.type) for c in self.cards.get_credit(self.slave)])
        )
