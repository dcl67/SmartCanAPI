#!/usr/bin/python3
import asyncio
import json
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


def main():
    # Initialize devices
    l_c = None #setup_lid_controller()

    # Initialize queue
    bin_q = asyncio.Queue()

    # TODO: remove this test
    tasks = [add_to_queue(bin_q, 1, 3), add_to_queue(bin_q, 2, 5), move_consumer(bin_q)]#, l_c)]
    futures = [asyncio.ensure_future(task) for task in tasks]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*futures))
    

    # # Registration
    # registration = Registration(config_file_name='test_config.json')
    # if not registration.is_registered():
    #     registration.register()
    # config = registration.config

    # # Client websocket for can
    # client = CanWsClient(bin_q, config, add_to_queue, 'localhost:8000')

    # # TODO: Setup pedal events with GPIO

    # # TODO: add pedal listener
    # tasks = [move_consumer(bin_q, l_c),
    #          client.handler(),]
    # futures = [asyncio.ensure_future(task) for task in tasks]
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.gather(*futures))


if __name__ == '__main__':
    main()
