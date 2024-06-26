import micropython

micropython.alloc_emergency_exception_buf(100)

from machine import SoftI2C, Pin, Timer, UART, SoftSPI
import asyncio
import time

from dfplayer import DFPlayer
from mpu6050 import MPU6050
from sh1107 import SH1107_I2C
from game import Game
from known_cards import known_cards
from interface import Interface
from mfrc522 import MFRC522


ENABLE_AUDIO = True


# components
i2c = SoftI2C(scl=Pin(5), sda=Pin(4))
uart = UART(1, 9600, bits=8, parity=None, stop=1, tx=10, rx=9)
spi = SoftSPI(
    baudrate=500000,
    polarity=0,
    phase=0,
    sck=35,
    mosi=37,
    miso=38,
)
rfid_rst = Pin(39, Pin.OUT)
rfid_cs = Pin(36, Pin.OUT)

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
time.sleep(0.1)
df.reset()
time.sleep(0.1)
df.volume(15)  # TODO: не хватает питания для большей громкости. плохой контакт??
time.sleep(0.1)
df.play(1, 1)


# RFID
rfid = MFRC522(spi, rfid_rst, rfid_cs)

# GAME
game = Game()

# Интерфейс
display = SH1107_I2C(128, 64, i2c, address=60, rotate=0)
interface = Interface(display)

# Функции

playing_task = None
last_press_ms = 0


async def play_messages():
    global playing_task

    try:
        for msg in game.message:
            print("PLAY %s/%s" % (msg.folder, msg.audio))

            if msg.audio:
                df.play(msg.folder, msg.audio)

                await asyncio.sleep(msg.duration + 0.2)
                while df.is_playing() != 0:
                    await asyncio.sleep(0.1)

            print("PLAYED!!")
    except asyncio.CancelledError:
        df.stop()
        raise
    finally:
        playing_task = None


def handle_press_button(key):
    # Сперва реализуем debounce
    global last_press_ms

    now_ms = time.ticks_ms()

    if now_ms - last_press_ms < 200:
        return

    last_press_ms = now_ms

    # Затем, определяем обработчик события
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

    if ENABLE_AUDIO:
        playing_task = asyncio.create_task(play_messages())

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


def rfid_read():
    (stat, tag_type) = rfid.request(rfid.REQIDL)

    if stat != rfid.OK:
        return

    (stat, raw_uid) = rfid.anticoll()

    if stat != rfid.OK:
        print("Failed to select tag")
        return

    uid = int.from_bytes(
        bytearray([raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]]), "big"
    )

    print("New card detected: %s (type %s)" % (hex(uid), tag_type))

    card_type = known_cards.get(uid)

    if card_type is None:
        return

    game.init_card(card_type)


async def rfid_loop():
    while True:
        rfid_read()
        await asyncio.sleep(1)


async def main():
    asyncio.create_task(rfid_loop())

    while True:
        # Это чтобы ampy не отваливался по таймауту
        print("\0", end="")
        await asyncio.sleep(3)


# Запуск игры

game.reset()
game.begin()

asyncio.run(main())
