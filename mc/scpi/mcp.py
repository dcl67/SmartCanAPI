#!/usr/bin/python3
"""
The mcp is the main script to be run on the RPi.
Handles registration, pedal events, motor control, and the websocket connection.
"""
import argparse
import asyncio
from functools import partial
import signal

import websockets

import RPi.GPIO as GPIO

from can_ws_client import CanWsClient
from lid_controller import LidController
from motor_controller import MotorController
from registration import Registration, HOSTNAME
from rotary_encoder import RotaryEncoderPair


BTN_CHAN_0 = 40
BTN_CHAN_1 = 38
BTN_CHAN_2 = 36

MTR_1_FWD = 5
MTR_1_REV = 7
MTR_2_FWD = 13
MTR_2_REV = 15

ROT_TOP_CCW = 37
ROT_TOP_CW = 35
ROT_BTM_CCW = 33
ROT_BTM_CW = 31

TOP_GEAR_RATIO = 5.934
BTM_GEAR_RATIO = 5.928

CHAN_TO_BINS = {
    40: 0,
    38: 1,
    36: 2
}


##### Bin methods

async def add_to_queue(bin_q, bin_num, delay_s=0):
    """
    Add a bin number to the queue. Can specify a delay in seconds before adding
    the bin number to the queue.
    """
    try:
        await asyncio.sleep(delay_s)
        await bin_q.put(bin_num)
    except Exception as ex:
        print(f"Failed to add 'move to bin #{bin_num}'. Error: {ex}")
    else:
        print(f"Added 'move to bin #{bin_num}' to queue")


async def move_consumer(bin_q, lid_controller: LidController):
    """
    Run the next move in the queue.
    Will yield and wait if the Queue is empty.
    """
    while True:
        try:
            bin_num = await bin_q.get()
            print(f"Consuming 'move to bin #{bin_num}'")
            await lid_controller.open(bin_num)
            await asyncio.sleep(10)
        except Exception as ex:
            print(f"Failed to 'move to bin #{bin_num}'. Error: {ex}")
        else:
            print(f"Succesful 'move to bin #{bin_num}'")
        finally:
            try:
                await lid_controller.close()
            except Exception as ex:
                print(f"Failed to close after 'move to bin #{bin_num}'. Error: {ex}")


##### Setup funcs

def setup_gpio(loop, bin_q):
    """
    Setup the GPIO event detection to run in the background but call back to a
    function on the main event loop
    """
    # Don't worry about other things going on on the board
    GPIO.setwarnings(False)
    # Set pin mode
    GPIO.setmode(GPIO.BOARD)
    # Configure button event callbacks
    for chan in CHAN_TO_BINS:
        GPIO.setup(chan, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Setup event callback
        GPIO.add_event_detect(
            chan,
            GPIO.RISING,
            callback=lambda chan: loop.call_soon_threadsafe(
                partial(on_event_loop, bin_q=bin_q, channel=chan)
            ),
            bouncetime=1000
        )


def setup_lid_controller(loop):
    """Sets up the devices for the lid controller"""
    encoder_pair = RotaryEncoderPair(
        top_ccw=ROT_TOP_CCW,
        top_cw=ROT_TOP_CW,
        btm_ccw=ROT_BTM_CCW,
        btm_cw=ROT_BTM_CW,
        top_gear_ratio=TOP_GEAR_RATIO,
        btm_gear_ratio=BTM_GEAR_RATIO
    )
    encoder_pair.calibrate()

    top_mc = MotorController(encoder_pair.encoder_top, fwd_pin=MTR_1_FWD, rev_pin=MTR_1_REV)
    btm_mc = MotorController(encoder_pair.encoder_btm, fwd_pin=MTR_2_FWD, rev_pin=MTR_2_REV)

    lid = LidController(top_mc, btm_mc)

    lid_fut = asyncio.ensure_future(lid.close())
    loop.run_until_complete(lid_fut)

    return lid


##### Other funcs

def get_args() -> object:
    """Sets up and parses the arguments"""
    parser = argparse.ArgumentParser(description='The main Smart Can process.')
    parser.add_argument('--offline', action='store_true',
                        help='Run in offline mode, only using pedals as input.')
    return parser.parse_args()


async def handler_persistance_warpper(bin_q, config):
    """
    Wraps the ws client in a wrapper that retries on disconnects and prints
    error messages rather than crashing
    """
    client = CanWsClient(bin_q, config, add_to_queue, f'{HOSTNAME}:8000/ws/')
    while True:
        print(f'Connecting to {client.hostname}')
        try:
            await client.handler()
        except (websockets.exceptions.ConnectionClosed, ConnectionError) as ex:
            print(f'Connection closed \'{ex}\'. Attempting to reconnect...')
        except Exception as ex:
            print(f'An exception occured: {ex}')
        finally:
            # Cooldown between retries, up to 10 minutes
            client.cooldown = min(client.cooldown * 2, 600)
            print(f'Cooling down for {client.cooldown} seconds')
            await asyncio.sleep(client.cooldown)


def on_event_loop(bin_q, channel):
    """
    An function that runs on the main event loop.
    This is called by the GPIO callback.
    """
    bin_num = CHAN_TO_BINS[channel]
    print(f'Button press detected on channel {channel} for bin {bin_num}')
    asyncio.ensure_future(add_to_queue(bin_q, bin_num))


#### Main

def main():
    """The main function sets up and kicks off all of the listeners"""
    # This restores the Ctrl+C signal handler, normally the loop ignores it
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Initialize devices
    loop = asyncio.get_event_loop()
    lid = setup_lid_controller(loop)

    # Initialize queue
    bin_q = asyncio.Queue()

    # Argument setup and parsing
    args = get_args()
    offline = args.offline

    # Registration
    if not offline:
        registration = Registration(config_file_name='test_config.json')
        print('Checking registration...')
        if not registration.is_registered():
            print('No registration found. Creating registration')
            registration.register()
        else:
            print('Registration found')
        config = registration.config

    # Setup pedal events with GPIO
    setup_gpio(loop, bin_q)

    # Schedule the tasks
    tasks = [move_consumer(bin_q, lid)]
    if not offline:
        tasks.append(handler_persistance_warpper(bin_q, config))
    for task in tasks:
        asyncio.ensure_future(task)

    # Setup loop in debug mode to catch anything weird
    loop.set_debug(True)

    # Run event loop forever
    print('Beginning event loop')
    loop.run_forever()
    loop.close()

    # Be nice and cleanup
    GPIO.cleanup()


if __name__ == '__main__':
    main()
