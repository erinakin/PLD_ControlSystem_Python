import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the src directory to the system path 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pld_controlsystem_python.attenuator_ctrl import AttenuatorControls

class TestAttenuatorControls(unittest.TestCase):

    @patch('pld_controlsystem_python.attenuator_ctrl.serial.Serial')  # Mocking the serial.Serial class in the attenuator_controls module
    def setUp(self, mock_serial):
        """
        Set up the AttenuatorControls instance and mock the serial connection.
        """
        self.mock_serial_instance = mock_serial.return_value  # This is the mock instance of serial.Serial
        self.attenuator = AttenuatorControls()

    # Need to resolve this unittest for initializing the serial connection or reframe the test
    # def test_initialization(self):
    #     """
    #     Test that the AttenuatorControls initializes the serial connection correctly.
    #     """
    #     self.attenuator = AttenuatorControls(port='COM3', baudrate=9600, timeout=1)
    #     self.mock_serial_instance.assert_called_with(port='COM3', baudrate=9600, timeout=1)

    def test_send_command(self):
        """
        Test the send_command method to ensure it sends the correct command.
        """
        command = 'test_command\n'
        self.attenuator.send_command(command)
        self.mock_serial_instance.write.assert_called_with(command.encode())

    def test_rotate_to_angle(self):
        """
        Test the rotate_to_angle method to ensure it sends the correct command.
        """
        angle = 45.5
        self.attenuator.rotate_to_angle(angle)
        expected_command = ',46\n'  # angle is rounded to the nearest integer
        self.mock_serial_instance.write.assert_called_with(expected_command.encode())

    def test_clear_laser(self):
        """
        Test the clear_laser method to ensure it sends the correct command.
        """
        self.attenuator.clear_laser()
        self.mock_serial_instance.write.assert_called_with('f\n'.encode())

    def test_block_laser(self):
        """
        Test the block_laser method to ensure it sends the correct command.
        """
        self.attenuator.block_laser()
        self.mock_serial_instance.write.assert_called_with('g\n'.encode())

    def test_home_attenuator(self):
        """
        Test the home_attenuator method to ensure it sends the correct command.
        """
        self.attenuator.home_attenuator()
        self.mock_serial_instance.write.assert_called_with('o\n'.encode())

    def test_set_rotation_speed(self):
        """
        Test the set_rotation_speed method to ensure it sends the correct command.
        """
        speed = 5.3
        self.attenuator.set_rotation_speed(speed)
        expected_command = '#5\n'  # speed is rounded to the nearest integer
        self.mock_serial_instance.write.assert_called_with(expected_command.encode())

    def test_close(self):
        """
        Test the close method to ensure it closes the serial connection.
        """
        self.attenuator.close()
        self.mock_serial_instance.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
