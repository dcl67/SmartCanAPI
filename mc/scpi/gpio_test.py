import asyncio
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Probably need to sudo this.")

BTN_CHAN = 40

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BTN_CHAN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Don't worry about other things going on on the board
    GPIO.setwarnings(False)

    # Setup event callback
    GPIO.add_event_detect(BTN_CHAN, GPIO.RISING, callback=callback,
                            bouncetime=50)


def callback(channel: int):
    print(f'Btn was pressed on channel #{channel}!')


def main():
    setup()

    # Be nice and cleanup
    GPIO.cleanup()

if __name__ == '__main__':
    main()
