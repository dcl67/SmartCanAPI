"""
Script for testing different ways of analyzing the resistor rings output.
To make use of this script, power the motor for the resistor wheel and
connect the resistor_reader.
"""
from math import floor
import statistics as stats
from time import sleep
from typing import Callable, List

from mc.scpi.resistor_reader import ResistorReader


TOTAL_MS = 200
SAMPLES = 10

def print_stats(val_list: List[int],
                val_name: str,
                func: Callable[[int], int] = lambda x: x) -> None:
    """Print the analysis for the given list of values

    Arguments:
        val_list {List[int]} -- List of values to operate on
        val_name {str} -- Description of what generated the val_list

    Keyword Arguments:
        func {Callable[[int], int]} -- Function that takes an int and returns an
            int, applied to the statistical result (default: {None})

    Returns:
        None
    """
    print(f'#### Using the values of {val_name}')
    print(f'Max:            {func(max(val_list)):06.2f} deg')
    print(f'Avg:            {func(stats.mean(val_list)):06.2f} deg')
    print(f'Median_grouped: {func(stats.median_grouped(val_list)):06.2f} deg')
    print(f'Mode:           {func(stats.mode(val_list)):06.2f} deg')

def main():
    """Run the script"""
    r_r = ResistorReader(0)
    sample_rate = floor(TOTAL_MS / SAMPLES)
    while True:
        deg_list, res_list = [], []

        _ = input('Press enter to begin...')

        for _ in range(SAMPLES):
            deg_list.append(r_r.get_degrees())
            res_list.append(r_r.get_adc_raw_output())
            sleep(sample_rate)

        print('\n\n-----------NEW RUN----------')
        print(f'Sampled every {int(sample_rate)}ms over {TOTAL_MS}ms')
        print_stats(deg_list, "reader's get_degrees()")
        print_stats(res_list, "reader's get_adc_raw_output()")
        print_stats(
            [res_list for res in res_list],
            "reader's get_adc_raw_output() converted to deg "
        )


if __name__ == '__main__':
    main()
