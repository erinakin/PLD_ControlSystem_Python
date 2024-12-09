import serial
from serial.tools import list_ports
from PLD_ControlSystem_Python.src.pld_controlsystem_python.pfeiffer_vacuum_protocol import PfeifferVacuumProtocol as pvp

class VacuumControls:
    def __init__(self, port=None, baudrate=9600, address=1):
        """
        Initializes the VacuumControls class with the specified serial port and baudrate.
        """
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.address = address
        self.port = port
        self.pressure_hpa = None
        self.pressure_torr = None
        self.current_setpoint = None
    
    def read_pressure(self):
        """
        Reads the actual pressure value from the device.

        Returns:
        tuple: A tuple containing the pressure in hPa (equivalent to mbar) and Torr (hPa, Torr).
               Returns (None, None) if no response is received.
        """
        try:
            self.pressure_hpa = pvp.read_pressure(self.ser, self.address)
            self.pressure_torr = self.pressure_hpa / 1.33322  # Convert hPa to Torr
            return self.pressure_hpa, 'hPa', self.pressure_torr, 'Torr' # Return the pressure in hPa and Torr
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
    
    def pressure_setpoint(self, option):
        """
        Sets the pressure value on the device based on the provided option.

        Parameters:
        option (str): '0' to set the pressure to 0e-4 hPa for low pressure
                      '1' to set the pressure to 1000 hPa  for atmospheric pressure.(high pressure)

        Returns:
        str: The response string from the device.

        Raises:
        ValueError: If an invalid option is provided.
        """
        if option == '0':
            val = 000
            self.current_setpoint = "Low Pressure"
            
        elif option == '1':
            val = 1
            self.current_setpoint = "Atmospheric Pressure"
            
        else:
            raise ValueError("Invalid option. Use '0' or '1'.")
        
        try:
            pvp.write_pressure_setpoint(self.ser, self.address, val)
            return "Pressure setpoint updated successfully.", self.current_setpoint
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

    @staticmethod
    def find_vacuum_controller_port(baudrate=9600, address=1):
        """
        Checks each available serial port to find the correct one for the Pfeiffer vacuum controller.

        Parameters:
        baudrate (int): The baud rate for the serial communication (default is 9600).
        address (int): The address of the device (default is 1).

        Returns:
        str: The port name if found, else None.
        """
        for port_info in list_ports.comports():
            try:
                with serial.Serial(port_info.device, baudrate, timeout=1) as _ser:
                    vacuum_control = VacuumControls(port=port_info.device, baudrate=baudrate, address=address)
                    pressure = vacuum_control.read_pressure()[0]  # Get the pressure in hPa
                    if pressure is not None: #and isinstance(pressure, (int, float)):
                        return port_info.device
            except (serial.SerialException, ValueError):
                continue
        return None

    def close(self):
        """
        Closes the serial connection.
        """
        if self.ser is not None:
            self.ser.close()
            print(f"Serial connection on {self.port} closed.")


