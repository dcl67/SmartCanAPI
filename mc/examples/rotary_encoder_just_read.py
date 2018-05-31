"""Run from the mc directory"""
import time

import RPi.GPIO as GPIO

from mc.scpi.rotary_encoder import RotaryEncoderPair


BTM_GEAR_RATIO = 5.928 #5.8
TOP_GEAR_RATIO = 5.934 #6

def main():
    while True:
        print(f'Current gear ratio is top {TOP_GEAR_RATIO} btm {BTM_GEAR_RATIO}')

        encoders = RotaryEncoderPair(top_gear_ratio=TOP_GEAR_RATIO, btm_gear_ratio=BTM_GEAR_RATIO)
        top_encoder = encoders.encoder_top
        btm_encoder = encoders.encoder_btm
        encoders.calibrate()

        print(f'top rollover is {top_encoder._rollover_steps}')
        print(f'btm rollover is {btm_encoder._rollover_steps}')

        while True:
            top_raw = top_encoder.get_raw_pos()
            top_deg = top_encoder.get_degrees()
            print(f'Top: Raw is {top_raw:6.02f} Degrees is {top_deg:6.02f}')

            btm_raw = btm_encoder.get_raw_pos()
            btm_deg = btm_encoder.get_degrees()
            print(f'Btm: Raw is {btm_raw:6.02f} Degrees is {btm_deg:6.02f}')
            time.sleep(0.5)

        GPIO.cleanup()


if __name__ == '__main__':
    main()
