import random

from player import Player
from health import Health
from score import Score
from cards import Cards, CardType
from gun import Gun
import scenario
import utils


class State:
    _ = 0
    IDLE = 1
    MASTER_SELECTION = 2
    SHUTTING = 3
    EXTRACTING = 4
    EMPTY_MAGAZINE = 5
    DONE = 6


class Game:
    state = State._

    gun = Gun()
    pointed_forward = False

    master = Player()
    slave = Player()

    first = master
    shutter = master

    score = Score(3)
    health = Health([master, slave], maximum=6)

    cards = Cards([master, slave], maximum=8)

    total_shots = 0
    total_cards = 0

    message: list[scenario.Chunk] = []

    handle_ok = None
    handle_shut = None
    handle_reload = None

    on_tell = None
    on_monit = None

    def reset(self):
        self.state = State._

        self.gun.reset()
        self.pointed_forward = False
        self.score.reset()
        self.health.reset()
        self.cards.reset()
        self.first = self.master
        self.shutter = self.master

        self.total_shots = 0
        self.total_cards = 0

    def init_card(self, card: CardType):
        # TODO: использование карт
        self._clear_message()

        if card == CardType.EJECT:
            self._tell(scenario.card_eject)
        elif card == CardType.HEAL:
            self._tell(scenario.card_heal)

    def set_direction(self, forward: bool):
        self.pointed_forward = forward

    def begin(self):
        self._tell(scenario.call_master)

        self.state = State.IDLE

        self._set_handlers(reload=self._start)

    def reload(self):
        if not self.handle_reload is None:
            self.handle_reload()

    def shut(self):
        if not self.handle_shut is None:
            self.handle_shut()

    def ok(self):
        if not self.handle_ok is None:
            self.handle_ok()

    def _start(self):
        self._clear_message()
        self._tell(scenario.master_called)

        self.state = State.MASTER_SELECTION

        self._set_handlers(ok=self._explain_master_selection)

    def _explain_master_selection(self):
        self._clear_message()
        self._tell(scenario.select_first_player)

        self._set_handlers(shut=self._select_master)

    def _select_master(self):
        self.health.reset(random.choice([2, 3, 4]))

        self.first = random.choice([self.master, self.slave])
        master_first = self.first == self.master

        self._clear_message()
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

        self._tell(scenario.main_rules)
        self._tell(scenario.prepare_cards)

        self.state = State.SHUTTING

        self._set_handlers(reload=self._load_and_continue_shutting)

    def _shut(self):
        if self.gun.empty():
            # TODO: добавить звук?
            return

        self.total_shots += 1

        is_forward = self.pointed_forward
        is_lethal = self.gun.shut()

        self._clear_message()

        # TODO: добавить звук!

        victim: Player

        if self.shutter == self.master:
            victim = self.slave if is_forward else self.master
        else:
            victim = self.master if is_forward else self.slave

        if is_lethal:
            self.health.reduce(victim)

        if self.health.get(victim) <= 0:
            # Здоровье жертвы закончилось
            self._tell(
                scenario.round_of_master
                if victim == self.slave
                else scenario.round_of_slave
            )

            self.score.put_winner(self.shutter)

            if self.score.is_final():
                # Это был финальный выстрел, нужно определить победителя
                self._game_over()
            else:
                # Выстрел оканчивает раунд
                self._set_handlers(reload=self._start_new_round)
        else:
            self.state = State.EXTRACTING

            if is_lethal:
                # Говорим, что жертва еще поживет
                self._tell(
                    random.choice(
                        [
                            scenario.after_shut_1,
                            scenario.after_shut_2,
                            scenario.after_shut_3,
                        ]
                    )
                )

            if not self.gun.empty():
                # Если магазин пуст, то будет смена
                # TODO: можно перенести это после перезарядки, так будет интересней
                if not is_forward and not is_lethal:
                    # Продолжаем ход, если стреляли в себя и был холостой
                    self._tell(scenario.not_change)
                else:
                    # Переход хода
                    self.shutter = (
                        self.slave if self.shutter == self.master else self.master
                    )

                    self._tell(scenario.change)
                    self._tell(
                        scenario.shut_master
                        if self.shutter == self.master
                        else scenario.shut_slave
                    )

            if self.total_shots == 1:
                # После первого выстрела рассказываем про полезность экрана
                self._tell(scenario.info_screen_is_helpful)

            self._set_handlers(reload=self._eject_and_continue_shutting)

        self._monit()

    def _eject_and_continue_shutting(self):
        self._clear_message()

        # TODO: Звук извлечения?

        if self.gun.empty():
            # Нужна перезарядка
            self._tell(scenario.magazine_is_empty)

            self.state = State.EMPTY_MAGAZINE

            self._set_handlers(reload=self._give_cards_and_load)
        else:
            self._set_handlers(shut=self._shut)

    def _start_new_round(self):
        self._clear_message()

        current_round = len(self.score.history)

        if current_round == 1:
            self.health.reset(random.choice([3, 4, 5]))
        elif current_round == 2:
            self.health.reset(random.choice([4, 5, 6]))

        self.cards.reset()
        self._tell(scenario.reorder_cards)

        self._set_handlers(reload=self._give_cards_and_load)

    def _give_cards_and_load(self):
        self._clear_message()

        if self.total_cards == 0:
            # Если это первая раздача, то нужно объяснить смысл карт
            self._tell(scenario.before_explain_cards)
            self.cards.reset()

        # TODO: перемешивать, если не осталось

        self._give_cards()

        self._set_handlers(ok=self._load_and_continue_shutting)

    def _load_and_continue_shutting(self):
        self._clear_message()

        self._load()
        self.shutter = self.first

        self._tell(
            scenario.first_master if self.first == self.master else scenario.first_slave
        )

        self.state = State.SHUTTING

        self._set_handlers(shut=self._shut)

    def _game_over(self):
        winner = self.score.get_leader()

        self._clear_message()
        self._tell(scenario.win_master if winner == self.master else scenario.win_slave)
        self._tell(scenario.goodby)

        self.state = State.DONE

        self._set_handlers()

    def _load(self, amount: int = None, amount_live: int = None):
        # TODO: звук перезарядки?

        if amount == None:
            amount = random.randint(2, 8)
        if amount_live == None:
            amount_live = round(random.randint(1, amount - 1))

        amount_live = min(amount - 1, amount_live)
        amount_dummy = amount - amount_live
        cartridges = self.gun.make(amount_live, amount_dummy)
        utils.shuffle(cartridges)

        self.gun.load(cartridges)

        self._monit()

        self._clear_message()
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

        if self.total_shots == 0:
            self._tell(scenario.order_is_unknown)
            self._tell(scenario.shut_rules)
            self._tell(scenario.first_is_permanent)

    def _give_cards(self):
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

    def _set_handlers(self, ok=None, shut=None, reload=None):
        self.handle_ok = ok
        self.handle_shut = shut
        self.handle_reload = reload

    def _clear_message(self):
        self.message.clear()

        if not self.on_tell is None:
            self.on_tell()

    def _tell(self, chunk: scenario.Chunk):
        self.message.append(chunk)

        if not self.on_tell is None:
            self.on_tell()

    def _monit(self):
        if not self.on_monit is None:
            self.on_monit()

    def print_state(self):
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
        print("Shutter: %s" % "MASTER" if self.shutter == self.master else "SLAVE")
        print("Master cards: %s" % self.cards.get_by_player(self.master))
        print("Slave cards: %s" % self.cards.get_by_player(self.slave))
