import serial
from pld_controlsystem_python.pfeiffer_vacuum_protocol import PfeifferVacuumProtocol as pvp

class VacuumControls:
    def __init__(self, port='COM6', baudrate=9600, address=1):
        """
        Initializes the VacuumControls class with the specified serial port and baudrate.

        Parameters:
        port (str): The serial port to which the device is connected (e.g., 'COM3' or '/dev/ttyUSB0').
        baudrate (int): The baud rate for the serial communication (default is 9600).
        """
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.address = address
    
    def read_pressure(self):
        """
        Reads the actual pressure value from the device.

        Returns:
        tuple: A tuple containing the pressure in hPa (equivalent to mbar) and Torr (hPa, Torr).
               Returns (None, None) if no response is received.
        """
        try:
            pressure_hpa = pvp.read_pressure(self.ser, self.address)
            pressure_torr = pressure_hpa / 1.33322  # Convert hPa to Torr
            return pressure_hpa, pressure_torr
        except ValueError:
            return None, None


    def read_error(self):
        """
        Reads the actual error code from the device.

        Returns:
        str: The error code string.
             Returns None if no response is received.
        """
        try:
            error_code = pvp.read_error_code(self.ser, self.address)
            return error_code.name  # Return the name of the ErrorCode enum
        except ValueError:
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
            val = 0.00001
        elif option == '1':
            val = 2050
        else:
            raise ValueError("Invalid option. Use '0' or '1'.")
        
        try:
            pvp.write_pressure_setpoint(self.ser, self.address, val)
            return "Pressure setpoint updated successfully."
        except ValueError as e:
            return str(e)
    
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
            try:
                return pvp.read_correction_value(self.ser, self.address)
            except ValueError:
                return None
        else:
            if 0.2 <= new_factor <= 8.0:
                try:
                    pvp.write_correction_value(self.ser, self.address, new_factor)
                    return "Correction factor updated successfully."
                except ValueError as e:
                    return str(e)
            else:
                raise ValueError("Correction factor out of range. Must be between 0.2 and 8.0.")

    def close(self):
        """
        Closes the serial connection.
        """
        self.ser.close()


