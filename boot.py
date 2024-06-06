import micropython

micropython.alloc_emergency_exception_buf(100)

from machine import SoftI2C, Pin, Timer, UART
import asyncio
import time

from dfplayer import DFPlayer
from mpu6050 import MPU6050
from sh1107 import SH1107_I2C
from game import Game
from interface import Interface


# components
i2c = SoftI2C(scl=Pin(5), sda=Pin(4))
uart = UART(1, 9600, bits=8, parity=None, stop=1, tx=10, rx=9)

# Buttons
Button_reload = 1
Button_trigger = 2
Button_ok = 3
Button_up = 6
Button_down = 8

# MPU6050
mpu = MPU6050(i2c)

# Player
df = DFPlayer(uart)
time.sleep(0.2)
df.volume(20)

# GAME
game = Game()

# Интерфейс
display = SH1107_I2C(128, 64, i2c, address=60, rotate=0)
interface = Interface(display)

# Функции

playing_task = None


async def play_audio(file=1, duration=0.0):
    print("PLAY %s" % file)

    df.play(1, file)
    await asyncio.sleep(duration + 0.2)

    while df.is_playing() != 0:
        await asyncio.sleep(0.1)

    print("PLAYED!! %s" % file)


async def play_messages():
    global playing_task

    try:
        for msg in game.message:
            await play_audio(msg.audio, msg.duration)
    except asyncio.CancelledError:
        raise
    finally:
        playing_task = None


def handle_press_button(key):
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


def handle_tell():
    global playing_task

    if not playing_task is None:
        # FIXME: нужно прерывать таску, даже если она исполняется. Не делать через event loop?
        playing_task.cancel()

    # TODO: перестало работать :-(
    # playing_task = asyncio.create_task(play_messages())

    message = " ".join([msg.text for msg in game.message])

    interface.set_message(message)


def handle_monit():
    interface.set_cartridges(game.gun.cartridges)
    interface.set_hp(game.health.get(game.master), game.health.get(game.slave))
    interface.set_shouter(game.shutter == game.master)


def physics_loop(_):
    mpu.read()

    rate = mpu.acc_y / 16384
    self_shot = rate > 0.65

    game.set_direction(not self_shot)
    interface.set_direction_forward(not self_shot)


# Подписки

game.on_tell = handle_tell
game.on_monit = handle_monit

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


async def main():
    while True:
        # Это чтобы ampy не отваливался по таймауту
        print("\0", end="")
        await asyncio.sleep(3)


asyncio.run(main())
