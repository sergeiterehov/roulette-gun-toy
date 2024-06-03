from machine import SPI, Pin
import math

from ST7735 import TFT
from font import font

from game import Game


class Interface:
    spi = SPI(
        2, baudrate=20000000, polarity=0, phase=0, sck=Pin(7), mosi=Pin(11), miso=Pin(9)
    )
    tft = TFT(spi, 16, 17, 18)

    game: Game

    _message: str = ""
    _message_scroll = 0
    _message_flag = False

    def __init__(self, game: Game) -> None:
        self.game = game

        self.tft.initr()
        self.tft.rgb(False)

        self.draw_layout()

    def up(self):
        self._message_scroll -= 1
        self._message_flag = True
        pass

    def down(self):
        self._message_scroll += 1
        self._message_flag = True
        pass

    def set_message(self, new_message: str):
        self._message = new_message
        self._message_scroll = 0
        self._message_flag = True

    def draw_layout(self):
        self.tft.fill(TFT.BLACK)
        self.tft.line((0, 64), (128, 64), TFT.WHITE)
        self.tft.line((0, 54), (128, 54), TFT.WHITE)

    def draw_message(self):
        if not self._message_flag:
            return

        self._message_flag = False

        c_width = 5 + 1
        c_height = 8 + 1
        limit_per_line = 21
        limit_lines = 4
        limit_total = limit_per_line * limit_lines

        message = self._message
        length = len(message)

        self._message_scroll = max(
            0,
            min(
                math.ceil(length / limit_per_line) - limit_lines,
                self._message_scroll,
            ),
        )

        scroll_offset = limit_per_line * self._message_scroll

        message = message[scroll_offset : scroll_offset + limit_total]
        length = len(message)

        x, y = 2, 16

        full_rows = math.floor(length / limit_per_line)

        if full_rows < limit_lines:
            self.tft.fillrect(
                (x, y + c_height * full_rows),
                (128 - x, c_height * (limit_lines - full_rows)),
                TFT.BLACK,
            )

        self.tft.text(
            (x, y),
            message,
            TFT.WHITE,
            font,
        )

    def draw_stat(self):
        self.tft.text(
            (2, 56),
            "%i:%s"
            % (
                self.game.score.get_by_player(self.game.master),
                self.game.score.get_by_player(self.game.slave),
            ),
            TFT.WHITE,
            font,
        )
        self.tft.text(
            (2 + 30, 56),
            "%i:%s"
            % (
                self.game.health.get(self.game.master),
                self.game.health.get(self.game.slave),
            ),
            TFT.RED,
            font,
        )

        offset = 64

        self.tft.fillrect((offset, 56), (64, 8), TFT.BLACK)

        dummy_count = self.game.gun.cartridges.count(False)
        lethal_count = self.game.gun.cartridges.count(True)

        for i in range(dummy_count):
            self.tft.fillrect((offset, 56), (4, 8), TFT.BLUE)
            offset += 5

        for i in range(lethal_count):
            self.tft.fillrect((offset, 56), (4, 8), TFT.RED)
            offset += 5

        history_dummy_count = self.game.gun.history.count(False)
        history_lethal_count = self.game.gun.history.count(True)

        offset += 10

        for i in range(history_dummy_count):
            self.tft.rect((offset, 57), (4, 6), TFT.BLUE)
            offset += 5

        for i in range(history_lethal_count):
            self.tft.rect((offset, 57), (4, 6), TFT.BLUE)
            offset += 5

        self.tft.text(
            (2, 2),
            "%s     " % ("В ПРОТИВНИКА" if self.game.pointed_forward else "В СЕБЯ"),
            TFT.GREEN if self.game.pointed_forward else TFT.RED,
            font,
        )

    def render(self, _):
        self.draw_stat()

        self.draw_message()
