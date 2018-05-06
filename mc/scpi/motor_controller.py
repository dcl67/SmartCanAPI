import asyncio
import time

import RPi.GPIO as io

# TODO: Make sure we use the BOARD pin numbering
class MotorController():
    """A class for controlling a motor attached the raspberry pi"""
    def __init__(self, resistor_reader, fwd_pin=3, rev_pin=5, num_bins=3):
        self.res_reader = resistor_reader
        self.f_pin = fwd_pin
        self.r_pin = rev_pin
        self.num_bins = num_bins
        self._curr_bin = None
        self._setup_motor()

    def _degrees_per_bin(self):
        """Returns the degrees per bin"""
        # TODO: Check that this lines up and there isn't some gap beween bins
        return 360 / self.num_bins

    def _setup_motor(self):
        """Initial signals to send to motor"""
        io.setup(self.f_pin, io.OUT)
        io.setup(self.r_pin, io.OUT)
        # Set initial values for pins
        self.off()

    def fwd(self):
        """Sets the motor to forward"""
        io.output(self.f_pin, io.LOW)
        io.output(self.r_pin, io.HIGH)

    def off(self):
        """Turns off the motor"""
        io.output(self.f_pin, io.LOW)
        io.output(self.r_pin, io.LOW)

    def rev(self):
        """Sets the motor to reverse"""
        io.output(self.f_pin, io.HIGH)
        io.output(self.r_pin, io.LOW)

    def get_bin_location(self, bin_num):
        """Takes a bin number and returns the degrees of the open position"""
        # TODO: Again, check that this lines up
        return self._degrees_per_bin() * bin_num   

    def get_curr_bin(self):
        return self._curr_bin

    async def move_degrees(self, deg, fwd=True):
        """
        Moves the lid deg degrees in the fwd or reverse direction.
        Returns nothing.
        """
        curr_loc = self.res_reader.get_degrees()
        last_loc = curr_loc
        final_loc_unbounded = (curr_loc + deg) if fwd else (curr_loc - deg)
        if final_loc_unbounded < 0:
            final_loc_unbounded = final_loc_unbounded + 360 
        final_loc = final_loc_unbounded % 360

        # Continue until we stop getting closer
        await self.move_seconds(fwd=fwd, seconds=0.2) # Move before first check
        while (abs(curr_loc - final_loc) < abs(last_loc - final_loc)):
            await self.move_seconds(fwd=fwd, seconds=0.2)
            curr_loc = self.res_reader.get_degrees()

    async def move_seconds(self, seconds=1, fwd=True):
        """
        Takes a boolean indicating fwd or rev an amount of time to go in the
        specified direction. Tenth of a second resolution. Returns nothing.
        """
        if fwd:
            self.fwd()
        else:
            self.rev()

        start_time = time.monotonic()

        while (time.monotonic() - start_time) < seconds:
            await asyncio.sleep(0.1)

        self.off()     

    async def move_to_bin(self, bin_num):
        """
        Takes a bin number and moves the opening of the lid to that bin's 
        position. Optimizes movement direction. Returns nothing.
        """
        if bin_num < 0 or bin_num >= self.num_bins:
            raise ValueError("Specified bin is out of range")

        bin_loc = self.get_bin_location(bin_num)
        curr_loc = self.res_reader.get_degrees()
        fwd_faster = True
        distance = abs(bin_loc - curr_loc)
        if self._curr_bin == bin_num or distance == 0:
            return
        if ((distance <= 180 and bin_loc < curr_loc) 
          or (distance > 180 and bin_loc > curr_loc)):
            fwd_faster = False

        await self.move_degrees(distance, fwd_faster)
        self._curr_bin = bin_num