import micropython

micropython.alloc_emergency_exception_buf(100)

from machine import SPI, I2C, Pin, Timer
import time

from dfplayer import DFPlayer

from mpu6050 import MPU6050

from ST7735 import TFT
from sysfont import sysfont

from game import Game


def play():
    df = DFPlayer(uart_id=1, tx_pin_id=10, rx_pin_id=9)

    time.sleep(0.2)

    df.volume(30)
    df.play(1, 1)


def draw_layout():
    tft.fill(TFT.BLACK)
    tft.line((0, 64), (128, 64), TFT.WHITE)
    tft.line((0, 54), (128, 54), TFT.WHITE)


def draw_stat():
    tft.text((2, 56), "1:0", TFT.WHITE, sysfont, 1)
    tft.text((2 + 30, 56), "2:4", TFT.RED, sysfont, 1)

    tft.fillrect((64 + 5 * 0, 56), (4, 8), TFT.BLUE)
    tft.fillrect((64 + 5 * 1, 56), (4, 8), TFT.RED)
    tft.fillrect((64 + 5 * 2, 56), (4, 8), TFT.RED)

    tft.rect((64 + 6 + 5 * 3, 57), (4, 6), TFT.BLUE)
    tft.rect((64 + 6 + 5 * 4, 57), (4, 6), TFT.BLUE)
    tft.rect((64 + 6 + 5 * 5, 57), (4, 6), TFT.RED)
    tft.rect((64 + 6 + 5 * 6, 57), (4, 6), TFT.RED)
    tft.rect((64 + 6 + 5 * 7, 57), (4, 6), TFT.RED)

    mpu.read()

    rate = mpu.acc_y / 16384
    self_shot = rate > 0.65

    tft.text(
        (2, 2), "R:%.2f   " % (rate), TFT.RED if self_shot else TFT.GREEN, sysfont, 1
    )


def draw_interface(_):
    draw_stat()


def handle_press_button(key):
    print("KEY", key)

    if key == Button_reload:
        game.reload()
    elif key == Button_trigger:
        game.shut()
    elif key == Button_ok:
        game.ok()


# interfaces

i2c = I2C(scl=Pin(5), sda=Pin(4))
spi = SPI(
    2, baudrate=20000000, polarity=0, phase=0, sck=Pin(7), mosi=Pin(11), miso=Pin(9)
)

# components

# Buttons
Button_reload = 1
Button_trigger = 2
Button_ok = 3

# MPU6050
mpu = MPU6050(i2c)

# TFT
tft = TFT(spi, 16, 17, 18)
tft.initr()
tft.rgb(False)

# GAME
game = Game()

game.reset()
game.begin()

# render loop

draw_layout()

tim0 = Timer(0)
tim0.init(
    period=500,
    mode=Timer.PERIODIC,
    callback=lambda t: micropython.schedule(draw_interface, 0),
)

# button irqs

Pin(Button_reload, Pin.IN, Pin.PULL_UP).irq(
    handler=lambda t: micropython.schedule(handle_press_button, Button_reload),
    trigger=Pin.IRQ_FALLING,
)
Pin(Button_trigger, Pin.IN, Pin.PULL_UP).irq(
    handler=lambda t: micropython.schedule(handle_press_button, Button_trigger),
    trigger=Pin.IRQ_FALLING,
)
Pin(Button_ok, Pin.IN, Pin.PULL_UP).irq(
    handler=lambda t: micropython.schedule(handle_press_button, Button_ok),
    trigger=Pin.IRQ_FALLING,
)
