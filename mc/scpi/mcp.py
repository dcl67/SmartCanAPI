#!/usr/bin/python3
import asyncio
import json
import websockets

from lid_controller import LidController
from motor_controller import MotorController
from registration import Registration
from resistor_reader import ResistorReader


##### Websocket funcs

async def can_client(bin_q, hostname, config: dict):
    async with websockets.connect(f'ws://{hostname}') as ws:
        async for msg in ws:
            try:
                json_data = json.loads(msg)
            except json.JSONDecodeError:
                print(f"Failed to parse json content in msg: '{msg}'")
            else:
                print(json_data)
                command = json_data.get('command')
                if command == 'identify':
                    await identify_handler(ws, config)
                elif command == 'echo':
                    await echo_handler(ws, msg)
                elif command == 'rotate':
                    await rotate_handler(msg, bin_q)
        print('Connection closed.')


async def echo_handler(ws, msg):
    message = msg.get('message')
    await ws.send(message)


async def identify_handler(ws, config):
    await send_identity(ws, config['uuid'], config['password'])


async def rotate_handler(msg, bin_q):
    pos = msg.get('position')
    await add_to_queue(bin_q, pos)


async def send_echo(ws, message):
    data = {'command':'echo', 'message': message}
    json_data = json.dumps(data)
    await ws.send(json_data)


async def send_identity(ws, username, password):
    data = {'command': 'identify', 'username': username, 'password': password}
    json_data = json.dumps(data)
    await ws.send(json_data)


##### Bin methods

async def add_to_queue(bin_q, bin_num, delay_s=0):
    """
    Add a bin number to the queue. Can specify a delay in seconds before adding
    the bin number to the queue.
    """
    await asyncio.sleep(delay_s)
    await bin_q.put(bin_num)
    print(f'Added a request to move to bin #{bin_num}')


async def move_consumer(bin_q, lid_controller: LidController):
    """
    Run the next move in the queue.
    Will yield and wait if the Queue is empty.
    """
    while True:
        bin_num = await bin_q.get()
        print(f"Consuming the move to bin #{bin_num}")
        await lid_controller.open(bin_num)
        await asyncio.sleep(10)
        await lid_controller.close()


##### Other funcs

def setup_lid_controller():
    """Sets up the devices for the lid controller"""
    top_rr = ResistorReader(0)
    top_mc = MotorController(top_rr, fwd_pin=2, rev_pin=3)
    btm_rr = ResistorReader(1)
    btm_mc = MotorController(btm_rr, fwd_pin=4, rev_pin=5)
    return LidController(top_mc, btm_mc)


def main():
    # Initialize devices
    l_c = setup_lid_controller()

    # Registration
    registration = Registration(config_file_name='test_config.json')
    if not registration.is_registered():
        registration.register()
    config = registration.config

    # TODO: Setup pedal events with GPIO

    # TODO: add pedal listener
    bin_q = asyncio.Queue()
    tasks = [move_consumer(bin_q, l_c),
             can_client(bin_q, 'localhost:8000', config),]
    futures = [asyncio.ensure_future(task) for task in tasks]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*futures))

if __name__ == '__main__':
    main()
