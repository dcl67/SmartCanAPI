"""Contains a LidController for use in Smart Can

Classes:
    LidController -- wraps the MotorControllers providing open and close methods
"""

import asyncio
from motor_controller import MotorController


class LidController():
    """A class that wraps the top and bottom lid MotorControllers"""
    def __init__(self, top_mc: MotorController, btm_mc: MotorController):
        self.top_mc = top_mc
        self.btm_mc = btm_mc
        self.num_bins = top_mc.num_bins
        self._validate()

    async def close(self):
        """
        Move the bottom lid to match the position of the top lid, closing the
        opening. Returns nothing.
        """
        open_bin = self.top_mc.get_curr_bin()
        num_bins = self.num_bins
        left = (open_bin - 1) % num_bins
        await self.btm_mc.move_to_bin(left)


    async def open(self, bin_num):
        """Moves the lids in an efficient manner to open the correct hole"""
        top_move = self.top_mc.move_to_bin(bin_num)
        btm_move = self.btm_mc.move_to_bin(bin_num)
        await asyncio.gather(*[top_move, btm_move])


    def _validate(self):
        if self.top_mc.num_bins != self.btm_mc.num_bins:
            raise ValueError(
                "Number of bins does not match:" +
                f"top_mc {self.top_mc.num_bins} != btm_mc {self.btm_mc.num_bins}"
            )
