import unittest
from unittest.mock import patch, MagicMock
import serial
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pld_controlsystem_python.vacuum_ctrl import VacuumControls

class TestVacuumControls(unittest.TestCase):

    @patch('pld_controlsystem_python.vacuum_ctrl.serial.Serial')
    def setUp(self, mock_serial):
        self.mock_serial_instance = MagicMock()
        mock_serial.return_value = self.mock_serial_instance
        self.vacuum = VacuumControls(port='COM6', baudrate=9600, address=1)

    @patch('pld_controlsystem_python.vacuum_ctrl.pvp.read_pressure')
    def test_read_pressure(self, mock_read_pressure):
        # Mocking the return value of read_pressure function
        mock_read_pressure.return_value = 1000.0

        pressure_hpa, pressure_torr = self.vacuum.read_pressure()

        self.assertEqual(pressure_hpa, 1000.0)
        self.assertEqual(pressure_torr, 1000.0 / 1.33322)
        mock_read_pressure.assert_called_once_with(self.mock_serial_instance, 1)

    @patch('pld_controlsystem_python.vacuum_ctrl.pvp.read_error_code')
    def test_read_error(self, mock_read_error_code):
        # Mocking the return value of read_error_code function
        mock_read_error_code.return_value.name = 'NO_ERROR'

        error = self.vacuum.read_error()

        self.assertEqual(error, 'NO_ERROR')
        mock_read_error_code.assert_called_once_with(self.mock_serial_instance, 1)

    @patch('pld_controlsystem_python.vacuum_ctrl.pvp.write_pressure_setpoint')
    def test_set_pressure(self, mock_write_pressure_setpoint):
        response = self.vacuum.set_pressure('0')
        self.assertEqual(response, "Pressure setpoint updated successfully.")
        mock_write_pressure_setpoint.assert_called_once_with(self.mock_serial_instance, 1, 1e-5)

        response = self.vacuum.set_pressure('1')
        self.assertEqual(response, "Pressure setpoint updated successfully.")
        mock_write_pressure_setpoint.assert_called_with(self.mock_serial_instance, 1, 2050)

        with self.assertRaises(ValueError):
            self.vacuum.set_pressure('2')

    @patch('pld_controlsystem_python.vacuum_ctrl.pvp.read_correction_value')
    def test_correction_factor_read(self, mock_read_correction_value):
        # Mocking the return value of read_correction_value function
        mock_read_correction_value.return_value = 1.0

        correction_factor = self.vacuum.correction_factor()

        self.assertEqual(correction_factor, 1.0)
        mock_read_correction_value.assert_called_once_with(self.mock_serial_instance, 1)

    @patch('pld_controlsystem_python.vacuum_ctrl.pvp.write_correction_value')
    def test_correction_factor_write(self, mock_write_correction_value):
        response = self.vacuum.correction_factor(2.0)
        self.assertEqual(response, "Correction factor updated successfully.")
        mock_write_correction_value.assert_called_once_with(self.mock_serial_instance, 1, 2.0)

        with self.assertRaises(ValueError):
            self.vacuum.correction_factor(0.1)
        with self.assertRaises(ValueError):
            self.vacuum.correction_factor(8.1)

    def test_close(self):
        self.vacuum.close()
        self.mock_serial_instance.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
