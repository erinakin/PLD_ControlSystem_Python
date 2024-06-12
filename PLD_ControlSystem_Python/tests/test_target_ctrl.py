import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pld_controlsystem_python.target_ctrl import TargetControls  # adjust the import to match your file structure

class TestTargetControls(unittest.TestCase):

    @patch('pld_controlsystem_python.target_ctrl.serial.Serial')  # Mocking the serial.Serial class in the module
    def setUp(self, mock_serial):
        """
        Set up the TargetControls instance and mock the serial connection.
        """
        self.mock_serial_instance = mock_serial.return_value  # This is the mock instance of serial.Serial
        self.target_controls = TargetControls()


    def test_send_command(self):
        """
        Test the send_command method to ensure it sends the correct command.
        """
        command = 'test_command\n'
        self.target_controls.send_command(command)
        self.mock_serial_instance.write.assert_called_with(command.encode())

    def test_rotate_to_angle(self):
        """
        Test the rotate_to_angle method to ensure it sends the correct command.
        """
        angle = 45.5
        self.target_controls.rotate_to_angle(angle)
        expected_command = ',46\n'  # angle is rounded to the nearest integer
        self.mock_serial_instance.write.assert_called_with(expected_command.encode())

    def test_step_raster_cw(self):
        """
        Test the step_raster_cw method to ensure it sends the correct command.
        """
        self.target_controls.step_raster_cw()
        self.mock_serial_instance.write.assert_called_with('>\n'.encode())

    def test_step_raster_ccw(self):
        """
        Test the step_raster_ccw method to ensure it sends the correct command.
        """
        self.target_controls.step_raster_ccw()
        self.mock_serial_instance.write.assert_called_with('<\n'.encode())

    def test_home_raster(self):
        """
        Test the home_raster method to ensure it sends the correct command.
        """
        self.target_controls.home_raster()
        self.mock_serial_instance.write.assert_called_with('o\n'.encode())

    def test_set_raster_speed(self):
        """
        Test the set_raster_speed method to ensure it sends the correct command.
        """
        speed = 5.3
        self.target_controls.set_raster_speed(speed)
        expected_command = "'5\n"  # speed is rounded to the nearest integer
        self.mock_serial_instance.write.assert_called_with(expected_command.encode())

    def test_start_raster(self):
        """
        Test the start_raster method to ensure it sends the correct command.
        """
        raster_angle = 44.6
        self.target_controls.start_raster(raster_angle)
        expected_command = 's45\n'  # angle is rounded to the nearest integer
        self.mock_serial_instance.write.assert_called_with(expected_command.encode())

    def test_stop_raster(self):
        """
        Test the stop_raster method to ensure it sends the correct command.
        """
        self.target_controls.stop_raster()
        self.mock_serial_instance.write.assert_called_with('h\n'.encode())

    def test_start_rotate(self):
        """
        Test the start_rotate method to ensure it sends the correct command.
        """
        self.target_controls.start_rotate()
        self.mock_serial_instance.write.assert_called_with('g\n'.encode())

    def test_stop_rotation(self):
        """
        Test the stop_rotation method to ensure it sends the correct command.
        """
        self.target_controls.stop_rotation()
        self.mock_serial_instance.write.assert_called_with('r\n'.encode())

    def test_set_rotation_speed(self):
        """
        Test the set_rotation_speed method to ensure it sends the correct command.
        """
        speed = 5.3
        self.target_controls.set_rotation_speed(speed)
        expected_command = '#5\n'  # speed is rounded to the nearest integer
        self.mock_serial_instance.write.assert_called_with(expected_command.encode())

    def test_move_to_target(self):
        """
        Test the move_to_target method to ensure it sends the correct command.
        """
        self.target_controls.move_to_target(1)
        expected_command = 't14\n'
        self.mock_serial_instance.write.assert_called_with(expected_command.encode())

    def test_close(self):
        """
        Test the close method to ensure it closes the serial connection.
        """
        self.target_controls.close()
        self.mock_serial_instance.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
