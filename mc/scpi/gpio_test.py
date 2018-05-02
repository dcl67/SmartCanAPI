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
    GPIO.add_event_detect(BTN_CHAN, GPIO.RISING, callback=lambda _: callback2(loop), bouncetime=50)
    #GPIO.add_event_detect(BTN_CHAN, GPIO.RISING, callback=callback1,bouncetime=50)


def callback1(channel: int):
    print(f'Btn was pressed on channel #{channel}!')


def callback2(loop):
    if loop is None:
        print(":(")
        return       # should not come to this
    asyncio.ensure_future(async_func)


async def async_func():
    print('Some async stuff')


def main():
    loop = asyncio.get_event_loop()

    setup_asyncio()
    setup_gpio(loop)

    loop.run_forever()

    # Be nice and cleanup
    GPIO.cleanup()

if __name__ == '__main__':
    main()
