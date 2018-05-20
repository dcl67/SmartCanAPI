from math import floor
import statistics as stats
from time import sleep

from mc.scpi.resistor_reader import ResistorReader


TOTAL_MS = 200
SAMPLES = 10

def main():
    r_r = ResistorReader(0)
    sample_rate = floor(TOTAL_MS / SAMPLES)
    while True:
        val_list = []
        for _ in range(SAMPLES):
            val_list.append(r_r.get_degrees())
            sleep(sample_rate)

        print('\n-----------NEW RUN----------')
        print(f'Sampling every {sample_rate}ms over {TOTAL_MS}ms')
        print(f'Max:            {max(val_list):06.2f} deg')
        print(f'Avg:            {stats.mean(val_list):06.2f} deg')
        print(f'Median_grouped: {stats.median_grouped(val_list):06.2f} deg')
        print(f'Mode:           {stats.mode(val_list):06.2f} deg')

        sleep(5)

if __name__ == '__main__':
    main()
