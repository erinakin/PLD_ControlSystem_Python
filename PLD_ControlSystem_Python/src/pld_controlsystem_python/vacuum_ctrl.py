# This code utilizes the `example_function` from `example-library` by `electronsandstuff`.
# Source: https://github.com/electronsandstuff/py-pfeiffer-vacuum-protocol/blob/master/src/pfeiffer_vacuum_protocol/pfeiffer_vacuum_protocol.py

import serial

class VacuumControls:
    def __init__(self, port='COM6', baudrate=9600):
        """
        Initializes the VacuumControls class with the specified serial port and baudrate.

        Parameters:
        port (str): The serial port to which the device is connected (e.g., 'COM3' or '/dev/ttyUSB0').
        baudrate (int): The baud rate for the serial communication (default is 9600).
        """
        self.ser = serial.Serial(port, baudrate, timeout=1)
    
    def _send_command(self, command):
        """
        Sends a command to the device and reads the response.

        Parameters:
        command (str): The command string to be sent.

        Returns:
        str: The response string from the device.
        """
        self.ser.write(f"{command}\r".encode())
        response = self.ser.readline().decode().strip()
        return response
    
    def read_pressure(self):
        """
        Reads the actual pressure value from the device.

        Returns:
        tuple: A tuple containing the pressure in mbar and Torr (mbar, Torr).
               Returns (None, None) if no response is received.
        """
        response = self._send_command("P740")
        if response:
            pressure_mbar = float(response)
            pressure_torr = pressure_mbar / 1.33322  # Convert mbar to Torr
            return pressure_mbar, pressure_torr
        else:
            return None, None

    def read_error(self):
        """
        Reads the actual error code from the device.

        Returns:
        str: The error code string.
             Returns None if no response is received.
        """
        response = self._send_command("P303")
        if response:
            return response
        else:
            return None
    
    def set_pressure(self, option):
        """
        Sets the pressure value on the device based on the provided option.

        Parameters:
        option (str): '0' to set the pressure to 0e-4 mbar, '1' to set the pressure to 2050 mbar.

        Returns:
        str: The response string from the device.

        Raises:
        ValueError: If an invalid option is provided.
        """
        if option == '0':
            # Set pressure to 0e-4 mbar
            command = "S001 0e-4"
        elif option == '1':
            # Set pressure to 2050 mbar
            command = "S001 2050"
        else:
            raise ValueError("Invalid option. Use '0' or '1'.")
        
        response = self._send_command(command)
        return response
    
    def correction_factor(self, new_factor=None):
        """
        Reads or sets the Pirani gas correction factor.

        Parameters:
        new_factor (float, optional): The new correction factor to be set. If None, the current correction factor is read.

        Returns:
        float: The current correction factor if new_factor is None.
        str: The response string from the device if new_factor is provided.

        Raises:
        ValueError: If the new_factor is out of the acceptable range (0.2 to 8.0).
        """
        if new_factor is None:
            # Read the correction factor
            response = self._send_command("P742")
            if response:
                return float(response)
            else:
                return None
        else:
            # Set the new correction factor
            if 0.2 <= new_factor <= 8.0:
                command = f"S742 {new_factor:.1f}"
                response = self._send_command(command)
                return response
            else:
                raise ValueError("Correction factor out of range. Must be between 0.2 and 8.0.")

    def close(self):
        """
        Closes the serial connection.
        """
        self.ser.close()

# Example usage:
# vacuum = VacuumControls(port='COM3')
# print(vacuum.read_pressure())
# print(vacuum.read_error())
# vacuum.set_pressure('0')
# print(vacuum.correction_factor())
# vacuum.correction_factor(1.5)
# vacuum.close()
