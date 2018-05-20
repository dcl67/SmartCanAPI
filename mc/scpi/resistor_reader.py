import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

NUM_RESISTORS = 64
RESOLUTION = 1024

class ResistorReader():
    """
    A class for reading resistor values
    """

    def __init__(self, adc_chan, spi_port=0, spi_device=0):
        self.adc_chan = adc_chan # We're using channels 0 and 1
        self.adc = self._make_adc(spi_port, spi_device)

    def _make_adc(self, spi_port, spi_device):
        """Takes an SPI port and an SPI device, returns a configured ADC"""
        spi = SPI.SpiDev(spi_port, spi_device)
        return Adafruit_MCP3008.MCP3008(spi=spi)

    def convert_res_to_deg(self, resistance: int):
        """Returns the degrees corresponding to the provided resistance"""
        # group into NUM_RESISTOR bins
        bin_size = RESOLUTION / NUM_RESISTORS
        return round(value / bin_size) / NUM_RESISTORS * 360

    def get_adc_raw_output(self):
        """Returns the 0-1023 value of resistance read by the ADC"""
        # 0-1023 value representing resistance
        return self.adc.read_adc(self.adc_chan)

    def get_degrees(self):
        """Returns the current angular position represented in degrees"""
        value = self.get_adc_raw_output()
        return self.convert_res_to_deg(value)
