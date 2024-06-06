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

    _direction_forward = False
    _cartridges: list[bool] = []
    _master_hp = 0
    _slave_hp = 0
    _shouter_master = True

    _status_flag = False

    def __init__(self, display: SH1107) -> None:
        self.display = display

        self.draw_layout()

    def up(self):
        self._message_scroll -= 1
        self._message_flag = True

    def down(self):
        self._message_scroll += 1
        self._message_flag = True

    def set_cartridges(self, new_cartridges: list[bool]):
        self._cartridges.clear()
        for c in new_cartridges:
            self._cartridges.append(c)
        self._cartridges.sort()
        self._status_flag = True

    def set_hp(self, master: int, slave: int):
        self._master_hp = master
        self._slave_hp = slave
        self._status_flag = True

    def set_shouter(self, is_master: bool):
        self._shouter_master = is_master
        self._status_flag = True

    def set_direction_forward(self, is_forward: bool):
        if self._direction_forward == is_forward:
            return

        self._direction_forward = is_forward
        self._status_flag = True

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

    def draw_cartridges(self):
        if not self._status_flag:
            return

        self._status_flag = False

        amount = len(self._cartridges)

        item_width = 3
        item_height = 6

        x_offset = WIDTH - amount * (item_width + 1)
        y_offset = 56

        self.display.fill_rect(
            WIDTH - 8 * (item_width + 1), y_offset, WIDTH, item_height, 0
        )

        for i in range(amount):
            is_lethal = self._cartridges[i]

            x = x_offset + (item_width + 1) * i

            if is_lethal:
                self.display.fill_rect(x, y_offset, item_width, item_height, 1)
            else:
                self.display.rect(x, y_offset, item_width, item_height, 1)

        self.display.show()

    def draw_stat(self):
        self.display.fill_rect(0, 56, 75, font.height, 0)
        self.display.text_area(
            "%i:%s"
            % (
                self._master_hp,
                self._slave_hp,
            ),
            2,
            56,
            font,
        )
        self.display.text_area(
            "ГЛАВНЫЙ" if self._shouter_master else "второй",
            30,
            56,
            font,
        )

        self.display.fill_rect(0, 0, WIDTH, font.height, 0)
        self.display.text_area(
            "В ДРУГОГО ИГРОКА" if self._direction_forward else "В СЕБЯ!",
            0,
            0,
            font,
        )

        self.display.show()

    def render(self, _):
        self.draw_stat()
        self.draw_cartridges()

        self.draw_message()
