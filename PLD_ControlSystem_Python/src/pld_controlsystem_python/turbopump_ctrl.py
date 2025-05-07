import serial


# from serial.tools import list_ports
#from PLD_ControlSystem_Python.src.pld_controlsystem_python.pfeiffer_turbopump_protocol import PfeifferTurbopumpProtocol as ptp
from pfeiffer_turbopump_protocol import PfeifferTurbopumpProtocol as ptp

class TurbopumpControls:
    def __init__(self, port, baudrate=9600, timeout=1, address=1):
        """
        Initialize the serial connection to the TC-400 driver.
        
        Parameters:
        - port (str): COM port to which the TC-400 is connected (e.g., 'COM3').
        - baudrate (int): Communication baud rate, typically 9600.
        - timeout (int/float): Read timeout value in seconds.
        """
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.address = address

    def read_error(self):
        """
        Reads the actual error code from the device.

        Returns:
        str: The error code string.
             Returns None if no response is received.
        """
        try:
            error_code = ptp.read_error_code(self.ser, self.address)
            return error_code.name  # Return the name of the ErrorCode enum
        except ValueError:
            return None

    def get_hardware_version(self):
        """
        Reads the hardware version from the device.

        Returns:
        str: The hardware version string.
             Returns None if no response is received.
        """
        try:
            hardware_version = ptp.get_hardware_version(self.ser, self.address)
            return hardware_version
        except ValueError:
            return None

    def get_drive_current(self):
        """
        Reads the actual drive current from the device.

        Returns:
        float: The drive current in mA.
               Returns None if no response is received.
        """
        try:
            drive_current = ptp.get_drive_current(self.ser, self.address)
            return drive_current
        except ValueError:
            return None

    def get_firmware_version(self):
        """
        Reads the firmware version from the device and drive unit type from the device.

        Returns:
        str: The firmware version string and the string representing the name of the electronic drive unit.
             Returns None if no response is received.
        """
        try:
            firmware_version = ptp.get_firmware_version(self.ser, self.address)
            # electronics_name = ptp.get_electronics_name(self.ser, self.address)
            return print(firmware_version) #electronics_name
        except ValueError:
            return None


    

    def close_connection(self):
        """
        Close the serial connection.
        """
        if self.ser.is_open:
            self.ser.close()

# Example usage
if __name__ == "__main__":
    # Replace 'COM3' with the actual COM port where the TC-400 is connected
    controller = TurbopumpControls(port='COM6')
    try:
        status = controller.query_status()
        print("Pump status:", status)
    finally:
        controller.close_connection()
