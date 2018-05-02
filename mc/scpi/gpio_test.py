import asyncio
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Probably need to sudo this.")
import signal

BTN_CHAN = 40

def setup_asyncio():
    # This restores the Ctrl+C signal handler, normally the loop ignores it
    signal.signal(signal.SIGINT, signal.SIG_DFL)

def setup_gpio(loop):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BTN_CHAN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Don't worry about other things going on on the board
    GPIO.setwarnings(False)

    # Setup event callback
    GPIO.add_event_detect(BTN_CHAN, GPIO.RISING, callback=lambda chan: loop.call_soon_threadsafe(intermediate_on_event_loop(chan)), bouncetime=20)


async def async_func(channel: int):
    print(f'Btn was pressed on channel #{channel}!')


def intermediate_on_event_loop(channel: int):
    asyncio.ensure_future(async_func(channel))


def main():
    loop = asyncio.get_event_loop()

    setup_asyncio()
    setup_gpio(loop)

    loop.run_forever()

    # Be nice and cleanup
    GPIO.cleanup()

if __name__ == '__main__':
    main()
