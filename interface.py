import math
from sh1107 import SH1107
from font import font

WIDTH = 128
HEIGHT = 64


class Interface:
    display: SH1107

    _message: str = ""
    _message_scroll = 0
    _message_flag = False

    def __init__(self, display: SH1107) -> None:
        self.display = display

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
        self.display.fill(0)

        self.display.hline(0, 54, WIDTH, 1)
        self.display.show()

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
            self.display.fill_rect(
                x,
                y + c_height * full_rows,
                128 - x,
                c_height * (limit_lines - full_rows),
                0,
            )

        self.display.text_area(
            message,
            x,
            y,
            font,
        )

        self.display.show()

    def draw_stat(self):
        self.display.text_area(
            "%i:%s"
            % (
                0,
                0,
            ),
            2,
            56,
            font,
        )
        self.display.text_area(
            "%i:%s"
            % (
                0,
                0,
            ),
            2 + 30,
            56,
            font,
        )

        self.display.show()

    def render(self, _):
        self.draw_stat()

        self.draw_message()
