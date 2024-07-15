import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pld_controlsystem_python.eurotherm_source import eurotherm2408  # adjust the import to match your file structure

class TestEurotherm2408(unittest.TestCase):

    @patch('pld_controlsystem_python.eurotherm_source.minimalmodbus.Instrument')  # Mocking the Instrument class in minimalmodbus
    def setUp(self, mock_instrument):
        """
        Set up the eurotherm2408 instance and mock the minimalmodbus instrument connection.
        """
        self.mock_instrument_instance = mock_instrument.return_value  # This is the mock instance of minimalmodbus.Instrument
        self.tempctrl = eurotherm2408()
        self.tempctrl.instrument = MagicMock()
        self.tempctrl._registers = {
            'Process_Variable': 1,
            'Target_setpoint': 2,
            'Setpoint_Max___High_range_limit': 3,
            'Setpoint_1_high_limit': 4,
            'AA_Comms_Resolution': 5,
            'Input_type': 6,
            'Setpoint_rate_limit': 7,
            'Setpoint_rate_limit_units': 8,
            'Integral_and_Derivative_time_units': 9,
            '_1A_Minimum_electrical_output': 10,
            '_1A_Maximum_electrical_output': 11,
            'Decimal_places_in_displayed_value': 12,
        }

    def test_temperature_get(self):
        self.tempctrl.Process_Variable = 100.0
        self.assertEqual(self.tempctrl.temperature, 100.0)

    def test_setpoint_get(self):
        self.tempctrl.Target_setpoint = 150.0
        self.assertEqual(self.tempctrl.setpoint, 150.0)

    def test_setpoint_set(self):
        self.tempctrl.Setpoint_Max___High_range_limit = 200.0
        self.tempctrl.Setpoint_1_high_limit = 180.0
        self.tempctrl.setpoint = 170.0
        self.assertEqual(self.tempctrl.Target_setpoint, 170.0)

    def test_pid_get(self):
        self.tempctrl.Proportional_band_PID1 = 1.0
        self.tempctrl.Integral_time_PID1 = 2.0
        self.tempctrl.Derivative_time_PID1 = 3.0
        self.assertEqual(self.tempctrl.pid, (1.0, 2.0, 3.0))

    def test_pid_set(self):
        self.tempctrl.pid = (1.5, 2.5, 3.5)
        self.assertEqual(self.tempctrl.Proportional_band_PID1, 1.5)
        self.assertEqual(self.tempctrl.Integral_time_PID1, 2.5)
        self.assertEqual(self.tempctrl.Derivative_time_PID1, 3.5)

    def test_temperatureSensor_get(self):
        self.tempctrl.Input_type = 1
        self.assertEqual(self.tempctrl.temperatureSensor, "K")

    @patch('time.sleep', return_value=None)
    def test_temperatureSensor_set(self, _):
        self.tempctrl.Instrument_Mode = 0
        self.tempctrl.temperatureSensor = "K"
        self.assertEqual(self.tempctrl.Input_type, 1)

    def test_resolution_get(self):
        self.tempctrl.AA_Comms_Resolution = 0
        self.assertEqual(self.tempctrl.resolution, "Full")

    def test_tensionRange_get(self):
        self.tempctrl._1A_Minimum_electrical_output = 0
        self.tempctrl._1A_Maximum_electrical_output = 10
        self.assertEqual(self.tempctrl.tensionRange, (0, 10))

    @patch('time.sleep', return_value=None)
    def test_tensionRange_set(self, _):
        self.tempctrl.Instrument_Mode = 0
        self.tempctrl.tensionRange = (1, 9)
        self.assertEqual(self.tempctrl._1A_Minimum_electrical_output, 1)
        self.assertEqual(self.tempctrl._1A_Maximum_electrical_output, 9)

    def test_rampRate_get(self):
        self.tempctrl.Setpoint_rate_limit = 5
        self.assertEqual(self.tempctrl.rampRate, 5)

    @patch('time.sleep', return_value=None)
    def test_rampRate_set(self, _):
        self.tempctrl.Ramp_Rate_Disable = 0
        self.tempctrl.rampRate = 10
        self.assertEqual(self.tempctrl.Setpoint_rate_limit, 10)

    def test_timeUnits_get(self):
        self.tempctrl.Integral_and_Derivative_time_units = 1
        self.assertEqual(self.tempctrl.timeUnits, "Minutes")

    @patch('time.sleep', return_value=None)
    def test_timeUnits_set(self, _):
        self.tempctrl.timeUnits = "Hours"
        self.assertEqual(self.tempctrl.Integral_and_Derivative_time_units, 2)

    def test_decimalsDisp_get(self):
        self.tempctrl.Decimal_places_in_displayed_value = 2
        self.assertEqual(self.tempctrl.decimalsDisp, 2)

    @patch('time.sleep', return_value=None)
    def test_decimalsDisp_set(self, _):
        self.tempctrl.decimalsDisp = 1
        self.assertEqual(self.tempctrl.Decimal_places_in_displayed_value, 1)

    def test_cutbackHigh_get(self):
        self.tempctrl.Cutback_high_PID1 = 5.0
        self.assertEqual(self.tempctrl.cutbackHigh, 5.0)

    def test_cutbackHigh_set(self):
        self.tempctrl.cutbackHigh = 6.0
        self.assertEqual(self.tempctrl.Cutback_high_PID1, 6.0)

    def test_cutbackLow_get(self):
        self.tempctrl.Cutback_low_PID1 = 3.0
        self.assertEqual(self.tempctrl.cutbackLow, 3.0)

    def test_cutbackLow_set(self):
        self.tempctrl.cutbackLow = 2.5
        self.assertEqual(self.tempctrl.Cutback_low_PID1, 2.5)

    def test_power_get(self):
        self.tempctrl.pc_Output_power = 50.0
        self.assertEqual(self.tempctrl.power, 50.0)

    def test_power_set(self):
        self.tempctrl.power = 55.0
        self.assertEqual(self.tempctrl.pc_Output_power, 55.0)

    def test_manual_get(self):
        self.tempctrl.Auto_man_select = 1
        self.assertTrue(self.tempctrl.manual)

    def test_manual_set(self):
        self.tempctrl.manual = True
        self.assertEqual(self.tempctrl.Auto_man_select, 1)

    def test_automatic_get(self):
        self.tempctrl.Auto_man_select = 0
        self.assertTrue(self.tempctrl.automatic)

    def test_automatic_set(self):
        self.tempctrl.automatic = True
        self.assertFalse(self.tempctrl.manual)

    def test_dumpAll(self):
        self.tempctrl._readRegister = MagicMock(return_value=123)
        expected = {key: 123 for key in self.tempctrl._registers.keys()}
        self.assertEqual(self.tempctrl.dumpAll(), expected)

if __name__ == '__main__':
    unittest.main()