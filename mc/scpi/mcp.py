#!/usr/bin/python3
import asyncio
import json

import signal
import websockets

from can_ws_client import CanWsClient
#from lid_controller import LidController
#from motor_controller import MotorController
from registration import Registration
#from resistor_reader import ResistorReader


##### Bin methods

async def add_to_queue(bin_q, bin_num, delay_s=0):
    """
    Add a bin number to the queue. Can specify a delay in seconds before adding
    the bin number to the queue.
    """
    await asyncio.sleep(delay_s)
    await bin_q.put(bin_num)
    print(f'Added a request to move to bin #{bin_num}')


async def move_consumer(bin_q):#, lid_controller: LidController):
    """
    Run the next move in the queue.
    Will yield and wait if the Queue is empty.
    """
    while True:
        bin_num = await bin_q.get()
        print(f"Consuming 'move to bin #{bin_num}' from queue'")
        #await lid_controller.open(bin_num)
        await asyncio.sleep(10)
        #await lid_controller.close()


##### Other funcs

# def setup_lid_controller():
#     """Sets up the devices for the lid controller"""
#     top_rr = ResistorReader(0)
#     top_mc = MotorController(top_rr, fwd_pin=2, rev_pin=3)
#     btm_rr = ResistorReader(1)
#     btm_mc = MotorController(btm_rr, fwd_pin=4, rev_pin=5)
#     return LidController(top_mc, btm_mc)


async def handler_persistance_warpper(bin_q, config):
    client = CanWsClient(bin_q, config, add_to_queue, 'localhost:8000/ws/')
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


def main():
    # This restores the Ctrl+C signal handler, normally the loop ignores it
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # TODO: uncomment
    # # Initialize devices
    # l_c = setup_lid_controller()

    # Initialize queue
    bin_q = asyncio.Queue()

    # Registration
    registration = Registration(config_file_name='test_config.json')
    if not registration.is_registered():
        registration.register()
    config = registration.config

    # TODO: Setup pedal events with GPIO

    # TODO: add pedal listener
    tasks = [move_consumer(bin_q),#, l_c), #TODO: uncomment
             handler_persistance_warpper(bin_q, config),]
    # schedule the tasks
    for task in tasks:
        asyncio.ensure_future(task)
    loop = asyncio.get_event_loop()
    # Debug mode to catch anything weird
    loop.set_debug(True)
    # Run event loop forever
    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    main()
