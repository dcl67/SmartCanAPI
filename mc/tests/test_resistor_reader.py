"""Tests for the ResistorReader module"""
import sys
sys.path.append("..") # Adds higher directory to python modules path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from mc.scpi.resistor_reader import ResistorReader


class ResistorReaderTest(TestCase):
    def setUp(self):
        self.patcher_1 = patch('mc.scpi.resistor_reader.SPI')
        self.mock_spi = self.patcher_1.start()
        self.patcher_2 = patch('mc.scpi.resistor_reader.Adafruit_MCP3008')
        self.mock_3008 = self.patcher_2.start()
        self.addCleanup(self.patcher_1.stop)
        self.addCleanup(self.patcher_2.stop)

    # autoSpec makes sure the mock still enforces the methods' signatures
    @patch('mc.scpi.resistor_reader.ResistorReader._make_adc', autoSpec=True)
    def test_instantiate(self, mock_make_adc: MagicMock):
        """ResistorReader creates an adc and sets the adc_chan"""
        adc_chan = 0
        mock_make_adc.return_value = 'adc'
        r_r = ResistorReader(adc_chan, spi_device=0, spi_port=0)
        self.assertEqual(r_r.adc, 'adc')
