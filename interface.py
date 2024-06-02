from machine import SPI, Pin

from ST7735 import TFT
from font import font

from game import Game


class Interface:
    spi = SPI(
        2, baudrate=20000000, polarity=0, phase=0, sck=Pin(7), mosi=Pin(11), miso=Pin(9)
    )
    tft = TFT(spi, 16, 17, 18)

    game: Game

    msg: str = ""

    def __init__(self, game: Game) -> None:
        self.game = game

        self.tft.initr()
        self.tft.rgb(False)

        self.draw_layout()

    def draw_layout(self):
        self.tft.fill(TFT.BLACK)
        self.tft.line((0, 64), (128, 64), TFT.WHITE)
        self.tft.line((0, 54), (128, 54), TFT.WHITE)

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

        newMsg = ""

        for msg in self.game.message:
            newMsg = newMsg + msg.text

        if newMsg != self.msg:
            self.msg = newMsg

            self.tft.text(
                (2, 20),
                self.msg,
                TFT.WHITE,
                font,
            )
