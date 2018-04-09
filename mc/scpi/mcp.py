import asyncio

from lid_controller import LidController
from motor_controller import MotorController
from resistor_reader import ResistorReader

async def add_to_queue(bin_q, bin_num, delay_s=0):
    """
    Add a bin number to the queue. Can specify a delay in seconds before adding
    the bin number to the queue.
    """
    await asyncio.sleep(delay_s)
    await bin_q.put(bin_num)

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

def main():
    # Initialize devices
    top_rr = ResistorReader(0)
    top_mc = MotorController(top_rr, fwd_pin=2, rev_pin=3)
    btm_rr = ResistorReader(1)
    btm_mc = MotorController(btm_rr, fwd_pin=4, rev_pin=5)
    lc = LidController(top_mc, btm_mc)

    # TODO: Registration

    # TODO: Setup pedal events with GPIO

    # TODO: add websockets loop and pedal listener
    bin_q = asyncio.Queue()
    tasks = [asyncio.ensure_future(move_consumer(bin_q, lc)),]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()