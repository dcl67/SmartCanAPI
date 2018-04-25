import asyncio
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Probably need to sudo this.")

BTN_CHAN = 13

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BTN_CHAN, GPIO.IN, pull_up_down=GPIO_UP)

    # Don't worry about other things going on on the board
    GPIO.setwarnings(False)

def callback():
    print('Btn was pressed!')

def main():
    # Setup event callback
    GPIO.add_event_detected(BTN_CHAN, GPIO.RISING, callback=callback,
                            bouncetime=200)

    # Be nice and cleanup
    GPIO.cleanup()

if __name__ == '__main__':
    main()
