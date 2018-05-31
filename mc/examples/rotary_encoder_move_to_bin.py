"""Run from the mc directory"""
import asyncio
import datetime
import signal

import RPi.GPIO as GPIO

from mc.scpi.motor_controller import MotorController
from mc.scpi.rotary_encoder import RotaryEncoderPair


async def main():
    top_gear_ratio = 5.934
    btm_gear_ratio = 5.928

    print(f'Current gear ratio is top {top_gear_ratio} btm {btm_gear_ratio}')

    encoder_pair = RotaryEncoderPair(top_gear_ratio=top_gear_ratio, btm_gear_ratio=btm_gear_ratio)
    top_encoder = encoder_pair.encoder_top
    btm_encoder = encoder_pair.encoder_btm
    encoder_pair.calibrate()
    print(f'rollover is top {top_encoder._rollover_steps} btm {btm_encoder._rollover_steps}')

    motor_ctrl_top = MotorController(top_encoder, 5, 7)
    motor_ctrl_btm = MotorController(btm_encoder, 13, 15)

    bin_num = 1

    while True:
        start_time = datetime.datetime.now()

        # TODO: Try move_degrees then wrap in LidController
        await motor_ctrl_top.move_to_bin(bin_num)
        await motor_ctrl_btm.move_to_bin(bin_num)

        time_delta = datetime.datetime.now() - start_time
        print(f"Rotated {bin_num} in {time_delta.total_seconds()} seconds")

        response = input("Press enter to continue, or enter a bin num")
        try:
            new_bin = float(response)
        except (TypeError, ValueError):
            print('Did not recognize new value, reusing old bin')
        else:
            bin_num = new_bin

    GPIO.cleanup()


if __name__ == '__main__':
    # This restores the Ctrl+C signal handler, normally the loop ignores it
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
