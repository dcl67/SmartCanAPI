import asyncio
import time

import RPi.GPIO as io


class MotorController():
    """A class for controlling a motor attached the raspberry pi"""
    def __init__(self, encoder, fwd_pin, rev_pin, num_bins=3):
        self.encoder = encoder
        self.f_pin = fwd_pin
        self.r_pin = rev_pin
        self.num_bins = num_bins
        self._curr_bin = 0
        self._setup_motor()

    @staticmethod
    def _getting_closer(start_loc, final_loc, curr_loc, last_loc, fwd):
        return abs(curr_loc - final_loc) < abs(last_loc - final_loc) or \
               final_loc < start_loc and curr_loc > start_loc and fwd or \
               final_loc > start_loc and curr_loc < start_loc and not fwd

    def _degrees_per_bin(self):
        """Returns the degrees per bin"""
        return 360 / self.num_bins

    def _setup_motor(self):
        """Initial signals to send to motor"""
        io.setmode(io.BOARD)
        io.setup(self.f_pin, io.OUT)
        io.setup(self.r_pin, io.OUT)
        # Set initial values for pins
        self.off()

    def fwd(self) -> None:
        """Sets the motor to forward (counter-clockwise)"""
        io.output(self.f_pin, io.HIGH)
        io.output(self.r_pin, io.LOW)

    def off(self) -> None:
        """Turns off the motor"""
        io.output(self.f_pin, io.HIGH)
        io.output(self.r_pin, io.HIGH)

    def rev(self) -> None:
        """Sets the motor to reverse (clockwise)"""
        io.output(self.f_pin, io.LOW)
        io.output(self.r_pin, io.HIGH)

    def get_bin_location(self, bin_num) -> int:
        """Takes a bin number and returns the degrees of the open position"""
        return self._degrees_per_bin() * bin_num

    def get_curr_bin(self) -> int:
        """Returns the current bin"""
        return self._curr_bin

    async def move_degrees(self, deg, fwd=True) -> None:
        """
        Moves the lid deg degrees in the fwd or reverse direction up to 179 degrees.
        Returns nothing.
        """
        curr_loc = self.encoder.get_degrees()
        start_loc = curr_loc
        last_loc = curr_loc
        final_loc_unbounded = (curr_loc + deg) if fwd else (curr_loc - deg)
        final_loc = final_loc_unbounded % 360

        # Continue until we stop getting closer
        await self.move_seconds(fwd=fwd, seconds=0.5) # Move before first check
        print(f'last:{last_loc} current:{curr_loc} final:{final_loc}')
        last_loc, curr_loc = curr_loc, self.encoder.get_degrees()

        while self._getting_closer(start_loc, final_loc, curr_loc, last_loc, fwd):
            await self.move_seconds(fwd=fwd, seconds=0.1)
            last_loc, curr_loc = curr_loc, self.encoder.get_degrees()

    async def move_seconds(self, seconds=1, fwd=True) -> None:
        """
        Takes a boolean indicating fwd or rev an amount of time to go in the
        specified direction. Tenth of a second resolution.

        Returns nothing.
        """
        if fwd:
            self.fwd()
        else:
            self.rev()

        start_time = time.monotonic()

        while (time.monotonic() - start_time) < seconds:
            await asyncio.sleep(0.1)

        self.off()

    async def move_to_bin(self, bin_num) -> None:
        """
        Takes a bin number and moves the opening of the lid to that bin's
        position. Optimizes movement direction.
        Returns nothing.
        """
        if bin_num < 0 or bin_num >= self.num_bins:
            raise ValueError("Specified bin is out of range")

        bin_deg = self.get_bin_location(bin_num)
        curr_deg = self.encoder.get_degrees()
        # fwd is ccw (decreasing angle)
        fwd_faster = True
        distance = abs(bin_deg - curr_deg)
        if self._curr_bin == bin_num or distance == 0:
            return
        if (distance <= 180 and bin_deg < curr_deg) or (distance > 180 and bin_deg > curr_deg):
            fwd_faster = False

        if distance > 180:
            distance = 360 - distance

        await self.move_degrees(distance, fwd_faster)
        self._curr_bin = bin_num
