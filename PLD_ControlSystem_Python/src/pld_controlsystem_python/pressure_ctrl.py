import serial
import time

class PressureControls:
    """
    A class to manage and control a pressure controller via RS-232 commands.

    This class provides methods to set levels of set points A, B, C, D, and E, set the F.S. level of the analog set point,
    and select set points A and B. Each command sent to the pressure controller ends with a carriage return-line feed (CRLF).
    """

    def __init__(self, port='COM1', baudrate=9600, timeout=1):
        """
        Initialize the serial connection to the pressure controller.

        Args:
            port (str): The port to which the pressure controller is connected.
            baudrate (int, optional): The baud rate for the serial communication. Default is 9600.
            timeout (int, optional): The read timeout value for the serial communication. Default is 1 second.
        """
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.ser.write(b'\r\n') # Send CRLF to the pressure controller to start communication

        # Clear residual data from input and output buffers
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        # 1s Delay to allow the pressure controller to process the command
        time.sleep(1)

    def send_request(self, request, response_prefix, wait_time=0.25):
        """
        Send a request to the device and process the response.

        Parameters:
        request (str): The request command to send to the device.
        response_prefix (str): The expected prefix of the response.
        wait_time (float): The time to wait after sending the request, in seconds. Default is 0.25 (250ms).

        Returns:
        str: The response from the device if the response prefix matches.
        str: "Wrong response" if the response prefix does not match.
        """
        # Send the request with CRLF termination
        self.ser.write((request + '\r\n').encode())

        # Wait for the device to respond
        time.sleep(wait_time)

        # Check how many bytes are available to read
        bytes_available = self.ser.in_waiting

        if bytes_available > 0:
            # Read the available bytes from the device
            response = self.ser.read(bytes_available).decode().strip()

            # Check if the response starts with the expected prefix
            if response.startswith(response_prefix):
                return response
            else:
                return "Wrong response"
        else:
            return "No response"
    
    def send_command(self, command, delay=0.25):
        """
        Send a command to the device and read the response.

        Parameters:
        command (str): The command to send to the device.
        delay (float): The time to wait after sending the command, in seconds. Default is 0.25 (250ms).

        Returns:
        str: The response from the device. 
        """
        # Send the command with CRLF termination
        self.ser.write((command + '\r\n').encode())

        # Wait for the specified delay
        time.sleep(delay)

        # Check how many bytes are available to read
        bytes_available = self.ser.in_waiting

        # Read the available bytes from the device
        if bytes_available > 0:
            response = self.ser.read(bytes_available).decode().strip()
            return response
        else:
            return "No response"
        
# First write all info request methods to confirm connection to device and corrent response

    def software_version_request(self):
        """
        Request the software version of the pressure controller.

        Returns:
        str: The software version of the pressure controller.
        """
        return self.send_request('R38', 'H')
    
    def status_request(self):
        """
        Request the status of the pressure controller.

        Returns:
        str: The status of the pressure controller.
        """
        response = self.send_request('R37', 'M')

        if response != "No response" and response.startswith("M"):
            status_code = response[1:]
            if len(status_code) == 3:
                control_mode = int(status_code[0])
                learning_mode = int(status_code[1])
                selection_mode = int(status_code[2])

                control_mode_map = {0: "Local", 1: "Remote"}
                learning_mode_map = {0: "not learning", 1: "learning system", 2: "learning valve"}
                selection_mode_map = {
                    0: "open",
                    1: "close",
                    2: "stop",
                    3: "set point A",
                    4: "set point B",
                    5: "set point C",
                    6: "set point D",
                    7: "set point E",
                    8: "Analog set point"
                }

                return {
                    "control_mode": control_mode_map.get(control_mode, "Unknown"),
                    "learning_mode": learning_mode_map.get(learning_mode, "Unknown"),
                    "selection_mode": selection_mode_map.get(selection_mode, "Unknown")
                }
            else:
                raise ValueError("Invalid status code length")
        else:
            raise ValueError("Invalid response or no response from device")

    
        
    def close(self):
        """
        Close the serial connection.
        """
        self.ser.close()