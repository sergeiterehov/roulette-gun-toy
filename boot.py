import micropython

micropython.alloc_emergency_exception_buf(100)

from machine import I2C, Pin, Timer
import time

from dfplayer import DFPlayer
from mpu6050 import MPU6050
from game import Game
from interface import Interface


# components

# Buttons
Button_reload = 1
Button_trigger = 2
Button_ok = 3

# MPU6050
i2c = I2C(scl=Pin(5), sda=Pin(4))
mpu = MPU6050(i2c)

# GAME
game = Game()

game.reset()
game.begin()

# Интерфейс
interface = Interface(game)

# Функции


def play():
    df = DFPlayer(uart_id=1, tx_pin_id=10, rx_pin_id=9)

    time.sleep(0.2)

    df.volume(30)
    df.play(1, 1)


def handle_press_button(key):
    print("KEY", key)

    if key == Button_reload:
        game.reload()
    elif key == Button_trigger:
        game.shut()
    elif key == Button_ok:
        game.ok()


def physics_loop(_):
    mpu.read()

    rate = mpu.acc_y / 16384
    self_shot = rate > 0.65

    game.set_direction(not self_shot)


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

Timer(0).init(
    period=500,
    mode=Timer.PERIODIC,
    callback=lambda t: micropython.schedule(interface.render, 0),
)

Timer(1).init(
    period=100,
    mode=Timer.PERIODIC,
    callback=lambda t: micropython.schedule(physics_loop, 0),
)
