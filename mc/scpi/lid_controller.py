from motor_controller import MotorController


class LidController():
    """A class that wraps the top and bottom lid MotorControllers"""
    def __init__(self, top_mc: MotorController, btm_mc: MotorController):
        self.top_mc = top_mc
        self.btm_mc = btm_mc
        self._validate()

    async def close(self):
        """
        Move the bottom lid to match the position of the top lid, closing the
        opening. Returns nothing.
        """
        await self.btm_mc.move_to_bin(self.top_mc.get_curr_bin())

    async def open(self, bin_num):
        """Moves the lids in an efficient manner to open the correct hole"""
        await self.top_mc.move_to_bin(bin_num)

        num_bins = self.btm_mc.num_bins
        left = (bin_num - 1) % num_bins
        right = (bin_num + 1) % num_bins
        right_pos = [x % num_bins for x in range(right, num_bins // 2 + right)]
        if self.btm_mc.get_curr_bin() == left or \
           self.btm_mc.get_curr_bin() == right:
            return
        elif bin_num in right_pos:
            await self.btm_mc.move_to_bin(right)
        else:
            await self.btm_mc.move_to_bin(left)


    def _validate(self):
        if self.top_mc.num_bins != self.btm_mc.num_bins:
            raise ValueError(
                "Number of bins does not match:" +
                f"top_mc {self.top_mc.num_bins} != btm_mc {self.btm_mc.num_bins}"
            )
