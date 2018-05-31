"""Classes for working with rotary encoding on an rpi

Classes:
    Encoder - A single rotary encoder to be aggregated as necessary
    RotaryEncoderPair - For reading rotations of a pair of rotary encoders on rPi
"""
from typing import Tuple
import warnings
import tkinter as tk

try:
    import RPi.GPIO as GPIO
except ImportError:
    warnings.warn('GPIO library not avaiable. Are you not running on a raspberry pi?')
    warnings.warn("For testing purposes you need to Mock 'GPIO'")


class Encoder():
    """A single rotary encoder

    Arguments:
        ccw_pin {int} -- The counter-clockwise pin number
        cw_pin {int} -- The clockwise pin number
        rollover_steps {int} -- The amount of steps to mod the position by
        name {str} -- A human readable name of the encoder for messages
    """

    def __init__(self, ccw_pin: int, cw_pin: int, rollover_steps: int = 360,
                 name: str = 'encoder'):
        self._ccw_pin = ccw_pin
        self._cw_pin = cw_pin
        self._rollover_steps = rollover_steps
        self._pos = 0
        self.calibrated = True
        self.name = name

        self._setup()

    def _decrement(self) -> None:
        self._pos = (self._pos - 1) % self._rollover_steps

    def _increment(self) -> None:
        self._pos = (self._pos + 1) % self._rollover_steps

    def _setup(self) -> None:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup([self._ccw_pin, self._cw_pin], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # NOTE: might need to pass in loop to get this working async
        # GPIO events
        GPIO.add_event_detect(self._ccw_pin, GPIO.RISING, lambda _: self._increment())
        GPIO.add_event_detect(self._cw_pin, GPIO.FALLING, lambda _: self._decrement())

    # TODO: Maybe make this a decorator
    def _warn_if_uncalibrated(self):
        if not self.calibrated:
            warnings.warn(f"Encoder titled '{self.name}' has not been calibrated.")

    def calibrate(self) -> None:
        """Asks user to perform initial calibration"""
        # tkinter popup for calibration
        self.generate_tkinter_popup()

        self._pos = 0
        self.calibrated = True

    def get_degrees(self) -> float:
        """Get the position in degrees [0-359]

        Returns:
            float -- The angle in degrees
        """
        self._warn_if_uncalibrated()
        return (self._pos / self._rollover_steps * 360) % 360

    def get_raw_pos(self) -> int:
        """
        Get the position of the encoder centered at the rollover and within
        the range of 0 - rollover_steps.

        Returns:
            int -- The position of the encoder. Needs to be converted to degrees.
        """
        self._warn_if_uncalibrated()
        return self._pos

    def generate_tkinter_popup(self):
        """ Generates calibration pop up message for the user """
        root = tk.Tk()

        # Gets the requested values of the height and widht.
        window_width = root.winfo_reqwidth()
        window_height = root.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        position_right = int(root.winfo_screenwidth()/2 - window_width/2)
        position_down = int(root.winfo_screenheight()/2 - window_height/2)

        # Positions the window in the center of the page.
        root.geometry(f"+{position_right}+{position_down}")

        # Push window to the front
        root.lift()
        root.attributes("-topmost", True)

        # Window contents
        msg = tk.Label(root, text=f"Please align '{self.name}' and then press OK...")
        msg.pack()
        button = tk.Button(root, text="OK", command=root.destroy)
        button.pack()

        root.mainloop()


class RotaryEncoderPair():
    """A pair of encoders for use with the LidController"""

    def __init__(self, top_ccw=37, top_cw=35, btm_ccw=33, btm_cw=31,
                 steps_per_revolution: int = 360, top_gear_ratio: float = 6,
                 btm_gear_ratio: float = 5.8):
        top_rollover_steps = int(steps_per_revolution * top_gear_ratio)
        btm_rollover_steps = int(steps_per_revolution * btm_gear_ratio)
        self.encoder_top = Encoder(top_ccw, top_cw, top_rollover_steps, 'top encoder')
        self.encoder_btm = Encoder(btm_ccw, btm_cw, btm_rollover_steps, 'bottom encoder')

    def calibrate(self) -> None:
        """Calibrates each encoder"""
        self.encoder_top.calibrate()
        self.encoder_btm.calibrate()

    def get_raw_pos(self) -> Tuple[int, int]:
        """Get the raw positions of the top and bottom encoders

        Returns:
            Tuple[int, int] -- (top_encoder_pos, btm_encoder_pos)
        """
        return (encoder.get_raw_pos() for encoder in [self.encoder_top, self.encoder_btm])

    def get_degrees(self) -> Tuple[int, int]:
        """Get the degrees of the top and bottom encoders

        Returns:
            Tuple[int, int] -- (top_encoder_degrees, btm_encoder_degrees)
        """
        return (encoder.get_degrees() for encoder in [self.encoder_top, self.encoder_btm])
