import micropython

micropython.alloc_emergency_exception_buf(100)

from machine import I2C, Pin, Timer
import asyncio
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
Button_up = 6
Button_down = 8

# MPU6050
i2c = I2C(scl=Pin(5), sda=Pin(4))
mpu = MPU6050(i2c)

# Player
df = DFPlayer(uart_id=1, tx_pin_id=10, rx_pin_id=9)
time.sleep(0.2)
df.volume(15)

# GAME
game = Game()

# Интерфейс
interface = Interface(game)

# Функции

playing_task = None


async def play_audio(file=1, duration=0.0):
    df.play(1, file)
    await asyncio.sleep(duration + 0.2)

    while df.is_playing() != 0:
        await asyncio.sleep(0.1)


def handle_press_button(key):
    print("KEY", key)

    if key == Button_reload:
        game.reload()
    elif key == Button_trigger:
        game.shut()
    elif key == Button_ok:
        game.ok()
    elif key == Button_up:
        interface.up()
    elif key == Button_down:
        interface.down()


async def play_messages():
    global playing_task

    for msg in game.message:
        await play_audio(msg.audio, msg.duration)

    playing_task = None


def handle_tell():
    global playing_task

    if not playing_task is None:
        # FIXME: нужно прерывать таску, даже если она исполняется. Не делать через event loop?
        playing_task.cancel()

    loop = asyncio.get_event_loop()
    playing_task = loop.create_task(play_messages())

    message = ""

    for msg in game.message:
        message = message + msg.text

    interface.set_message(message)


def physics_loop(_):
    mpu.read()

    rate = mpu.acc_y / 16384
    self_shot = rate > 0.65

    game.set_direction(not self_shot)


# Подписки

game.on_tell = handle_tell

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
Pin(Button_up, Pin.IN, Pin.PULL_UP).irq(
    handler=lambda t: micropython.schedule(handle_press_button, Button_up),
    trigger=Pin.IRQ_FALLING,
)
Pin(Button_down, Pin.IN, Pin.PULL_UP).irq(
    handler=lambda t: micropython.schedule(handle_press_button, Button_down),
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

# Запуск игры

game.reset()
game.begin()

while True:
    asyncio.get_event_loop().run_forever()
