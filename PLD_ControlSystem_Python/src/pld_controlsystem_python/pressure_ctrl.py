import serial
import time

class PressureControls:
    """
    A class to manage and control a pressure controller via RS-232 commands.

    This class provides methods to set levels of set points A, B, C, D, and E, set the F.S. level of the analog set point,
    and select set points A and B. Each command sent to the pressure controller ends with a carriage return-line feed (CRLF).
    """

    def __init__(self, port='COM1', baudrate=9600):
        """
        Initialize the serial connection to the pressure controller.

        Args:
            port (str): The port to which the pressure controller is connected.
            baudrate (int, optional): The baud rate for the serial communication. Default is 9600.
            timeout (int, optional): The read timeout value for the serial communication. Default is 1 second.
        """
        self.ser = serial.Serial(port, baudrate)
        self.ser.write(b'\r\n') # Send CRLF to the pressure controller to start communication

        # Clear residual data from input and output buffers
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.sensor_range = self.sensor_range_request()
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

    def setpoint_request(self, setpoint, full_scale=None):

        """
        Request the setpoint value from the pressure controller and convert it to the actual value based on F.S.

        Args:
            setpoint (str): The setpoint identifier (A, B, C, D or E).
            full_scale (float): The full scale value (F.S.) of the pressure unit.

        Returns:
            float: The actual setpoint value based on F.S.
        """
        # Request Pressure Sensor Full Scale Range value 
        self.sensor_range = self.sensor_range_request()

        # If full_scale is not provided, use the sensor range value just requested
        if full_scale is None:
            full_scale = self.sensor_range        

        # Mapping setpoint to corresponding request command
        setpoint_map = {
            'A': 'R1',
            'B': 'R2',
            'C': 'R3',
            'D': 'R4',
            'E': 'R10'
        }

        if setpoint not in setpoint_map:
            raise ValueError("Invalid setpoint. Choose between 'A', 'B', 'C', 'D', or 'E'.")

        # Get the corresponding request command
        request_command = setpoint_map[setpoint]

        # Send the request and get the response
        response = self.send_request(request_command, 'S')

        # Strip any CRLF and handle no spaces in the response
        response = response.strip()

        if response.startswith('S'):
            # Extract the value after the 'S1' part
            percentage_value = float(response[2:])

            # Calculate the actual setpoint value based on the full scale
            actual_value = (percentage_value / 100.0) * full_scale
            return actual_value
        else:
            return "Invalid response or no response"
        

    def setpoint_controltype_request(self, setpoint):
        """
        Request the control type for a specified setpoint from the pressure controller.

        Args:
            setpoint (str): The setpoint identifier ('analog', 'A', 'B', 'C', 'D', or 'E').

        Returns:
            dict: A dictionary containing the setpoint and control type.
        """
        # Mapping setpoint to corresponding request code (Rxx)
        setpoint_map = {
            'analog': '25',
            'A': '26',
            'B': '27',
            'C': '28',
            'D': '29',
            'E': '30'
        }

        if setpoint not in setpoint_map:
            raise ValueError("Invalid setpoint. Choose between 'analog', 'A', 'B', 'C', 'D', or 'E'.")

        # Get the corresponding request code
        request_code = setpoint_map[setpoint]

        # Send the request to check the control type for the specified setpoint
        response = self.send_request(f'R{request_code}', 'T')

        # Strip any CRLF characters
        response = response.strip()

        if response.startswith('T') and len(response) == 3:
            # Extract the setpoint code (x) and control type value
            setpoint_code = int(response[1])
            control_type_value = int(response[2])

            # Map the setpoint code back to setpoint name
            setpoint_name_map = {
                0: 'Analog set point',
                1: 'Set point A',
                2: 'Set point B',
                3: 'Set point C',
                4: 'Set point D',
                5: 'Set point E'
            }

            # Map the control type value
            control_type_map = {
                0: 'Position',
                1: 'Pressure'
            }

            # Get the setpoint name and control type
            setpoint_name = setpoint_name_map.get(setpoint_code, "Unknown setpoint")
            control_type = control_type_map.get(control_type_value, "Unknown control type")

            # Return the result as a dictionary
            return {
                "setpoint": setpoint_name,
                "control_type": control_type
            }
        else:
            return "Invalid response or no response"


    def pressure_request(self):
        """
        Request the current pressure value from the pressure controller.

        Returns:
        float: The current pressure value in the pressure units.
        """
        # Send the R30 command to request the pressure value
        response = self.send_request('R5', 'P')
        pressure_units = self.pressure_units_request()


        # Strip any CRLF characters
        response = response.strip()

        if response.startswith('P'):
            # Extract the value after the 'A' part
            percentage_value = float(response[1:])

            # Calculate the actual pressure value based on the sensor range
            actual_value = (percentage_value / 100.0) * self.sensor_range
            return "{:.2f} {}".format(actual_value, pressure_units)
        else:
            return "Invalid response or no response"        

    def sensor_range_request(self):

        """
        Request the Pressure sensor range from the pressure controller.

        Returns:
            float: The sensor range in terms of pressure units (based on the table).
        """
        # Send the R33 command to request the sensor range
        response = self.send_request('R33', 'E')

        # Strip any CRLF characters
        response = response.strip()

        if response.startswith('E'):
            # Extract the value code after the 'E'
            value_code = response[1:3]

            # Map the value code to the corresponding sensor range
            sensor_range_map = {
                '00': 0.1,
                '01': 0.2,
                '02': 0.5,
                '03': 1,
                '04': 2,
                '05': 5,
                '06': 10,
                '07': 50,
                '08': 100,
                '09': 500,
                '10': 1000,
                '11': 5000,
                '12': 10000,
                '13': 1.33,
                '14': 2.66,
                '15': 13.33,
                '16': 133.3,
                '17': 1333,
                '18': 6666,
                '19': 13332
            }

            # Get the sensor range based on the value code
            sensor_range = sensor_range_map.get(value_code, None)

            if sensor_range is not None:
                return sensor_range
            else:
                return "Invalid sensor range value"
        else:
            return "Invalid response or no response"

    def pressure_units_request(self):
        """
        Request the pressure units of the pressure controller.

        Returns:
        str: The pressure units of the pressure controller.
        """
        # Send the R34 command to request the pressure units
        response = self.send_request('R34', 'F')

        # Strip any CRLF characters
        response = response.strip()

        if response.startswith('F'):
            # Extract the value code after the 'F'
            value_code = response[1:3]

            # Map the value code to the corresponding pressure unit
            pressure_unit_map = {
                '00': 'Torr',
                '01': 'mTorr',
                '02': 'mbar',
                '03': 'µbar',
                '04': 'kPa',
                '05': 'Pa',
                '06': 'cmH₂O',
                '07': 'inH₂O'
            }

            # Get the pressure unit based on the value code
            pressure_unit = pressure_unit_map.get(value_code, None)

            if pressure_unit is not None:
                return pressure_unit
            else:
                return "Invalid pressure unit value"
        else:
            return "Invalid response or no response"
        
    def active_setpoint_request(self):
        """
        Request the currently active set point from the pressure controller and interpret the response.

        Returns:
            dict: A dictionary containing the active setpoint, valve status, and pressure status.
        """
        # Send the R7 command to request the active setpoint
        response = self.send_request('R7', 'M')

        # Strip any CRLF characters
        response = response.strip()

        if len(response) != 4:
            return "Invalid response format or no response"

        # Extract the components of the response: MXYZ
        active_setpoint_code = int(response[1])
        valve_status_code = int(response[2])
        pressure_status_code = int(response[3])

        # Map for active setpoint (X)
        active_setpoint_map = {
            0: "Analog set point",
            1: "Set point A",
            2: "Set point B",
            3: "Set point C",
            4: "Set point D",
            5: "Set point E"
        }

        # Map for valve status (Y)
        valve_status_map = {
            0: "Controlling",
            1: "Valve open (direct direction)",
            2: "Valve close (direct direction)",
            3: "Valve close (reverse direction)",
            4: "Valve open (reverse direction)"
        }

        # Map for pressure status (Z)
        pressure_status_map = {
            0: "Pressure < 10% F.S.",
            1: "Pressure ≥ 10% F.S."
        }

        # Interpret the response
        active_setpoint = active_setpoint_map.get(active_setpoint_code, "Unknown set point")
        valve_status = valve_status_map.get(valve_status_code, "Unknown valve status")
        pressure_status = pressure_status_map.get(pressure_status_code, "Unknown pressure status")

        # Return the interpreted values in a dictionary
        return {
            "active_setpoint": active_setpoint,
            "valve_status": valve_status,
            "pressure_status": pressure_status
        }
    # CONTROL COMMANDS

    # Learn the system charcteristics using self-tuning function
    def self_tune(self):
        """
        Initiates the learn function for Self-Tuning control and checks the status of the learn process.

        Use case:
        - The learn function enables the 651 controller to identify important system characteristics 
        for Self-Tuning control. Use this function whenever a new vacuum system is installed, 
        or any processing conditions (e.g., flow rate, pump changes) are modified.

        Note:
        - The system pressure will vary during the learn cycle. Ensure the system is set up properly 
        before initiating the learn function.

        Steps:
        1. The function first sends the 'L' command to initiate the learn process.
        2. It then uses the 'R37' command to check the status of the learn process, interpreting the response
        (0 = no learn process, 1 = performing the learn process, 2 = learning the valve).

        Returns:
            str: Status of the learn process.
        """
        # Step 1: Send the command 'L' to initiate the learn process
        self.send_command('L')
        
        # Step 2: Check the status of the learn process by sending the R37 request
        response = self.status_request('R37')

        # Process the response based on the MXYZ format (M = X, Y, Z represent control, system status, and valve status)
        response = response.strip()
        
        if len(response) == 4 and response[1] in ['0', '1', '2']:
            system_status = int(response[1])

            status_map = {
                0: "System is not performing the learn process.",
                1: "System is performing the learn process.",
                2: "System is learning the valve."
            }

            return status_map.get(system_status, "Unknown learn status")
        else:
            return "Invalid response or no response"


    #Stop the self-tune process 
    def stop_self_tune(self):
        """
        Stops the learn function for Self-Tuning control.

        Use case:
        - It is recommended to allow the learn function to complete. However, if the process is slow to reach 
        its highest pressures and your process will not be operating at those pressures, you can stop the learn function early.

        Note:
        - Do not stop the learn function until it is well above the highest pressure at which the process will be operating.
        - Once the learn function is stopped, the system returns to its prior operation state.

        Steps:
        1. The function sends the 'Q' command to stop the learn process and returns the system to its previous state.

        Returns:
            str: Confirmation message that the learn function has been stopped.
        """
        # Step 1: Send the command 'Q' to stop the learn function
        self.send_command('Q')
        
        return "Learn function stopped and system returned to prior operation."


    # Control Mode: Request and Set Control Mode
    def control_mode(self, action, mode=None):
        """
        Check or set the control mode of the pressure controller.

        Args:
            action (str): 'check' to check the current control mode, 'set' to change the control mode.
            mode (str, optional): 'self-tuning' or 'pid' (used only when action is 'set').

        Returns:
            str: The current control mode (if action is 'check').
            str: Confirmation message after setting the control mode (if action is 'set').
        """
        if action == 'check':
            # Send the R51 command to check the control mode
            response = self.send_request('R51', 'V')

            # Strip any CRLF characters and check the response format
            response = response.strip()

            if response.startswith('V'):
                # Extract the control mode value
                control_value = int(response[1])

                # Map the control value to the corresponding mode
                control_map = {
                    0: "Self-Tuning control",
                    1: "PID control"
                }

                return f"Current control mode: {control_map.get(control_value, 'Unknown mode')}"
            else:
                return "Invalid response or no response"

        elif action == 'set':
            if mode not in ['self-tuning', 'pid']:
                raise ValueError("Invalid mode. Choose 'self-tuning' or 'pid'.")

            # Set the control mode based on the provided mode
            if mode == 'self-tuning':
                self.send_command('V0')  # Set to Self-Tuning control
                return "Control mode set to Self-Tuning control"
            elif mode == 'pid':
                self.send_command('V1')  # Set to PID control
                return "Control mode set to PID control"

        else:
            raise ValueError("Invalid action. Use 'check' or 'set'.")



    #Setting the Full Scale Level of the Analog Set Point
    def analog_fullscale(self, action, value=None):
        """
        Set or check the full scale level of the analog set point.

        Args:
            action (str): 'set' to set the full scale level, 'check' to check the current full scale level.
            value (int, optional): 0 for 100% of the transducer's range, 1 for 10% of the range (used only when action is 'set').

        Returns:
            str: Current full scale level as a percentage (if action is 'check').
            str: Confirmation message after setting the full scale level (if action is 'set').
        """
        if action == 'set':
            if value not in [0, 1]:
                raise ValueError("Invalid value. Choose 0 for 100% or 1 for 10% of the transducer's range.")
            # Send the command to set the full scale level
            command = f'S6{value}'
            self.send_command(command)
            return f"Analog set point full scale level set to {'100%' if value == 0 else '10%'} of the transducer's range."

        elif action == 'check':
            # Send the R0 command to check the current full scale level
            response = self.send_request('R0', 'S')

            # Strip any CRLF characters
            response = response.strip()

            if response.startswith('S'):
                # Extract the percentage from the response
                full_scale_percentage = int(response[1:])
                return f"Current full scale level of the analog set point: {full_scale_percentage}%"
            else:
                return "Invalid response or no response"
        else:
            raise ValueError("Invalid action. Use 'set' or 'check'.")


    # Leadand Gain Parameters for PID Control
    def lead_gain_parameters(self, action, parameter_type=None, setpoint=None, value=None):
        """
        Manage lead and gain parameters for PID control.

        Args:
            action (str): 'check' to check the current parameters, 'set' to change the parameters.
            parameter_type (str, optional): 'lead' or 'gain' (used for both checking and setting parameters).
            setpoint (str, optional): 'A', 'B', 'C', 'D', or 'E' (specifies the setpoint for the lead or gain parameter).
            value (float, optional): The new lead (in seconds) or gain (in percent) value (used for setting parameters).

        Returns:
            str: The current lead or gain parameter value (if action is 'check').
            str: Confirmation message after setting the lead or gain parameter (if action is 'set').
        """
        # Step 1: Check the current control mode using R51
        response = self.send_request('R51', 'V')

        # Strip any CRLF characters and check the response format
        response = response.strip()

        if response.startswith('V'):
            control_mode = int(response[1])

            # If the control mode is not PID (i.e., if V0), switch to PID control (V1)
            if control_mode == 0:
                self.send_command('V1')
                return "Controller switched to PID control."

        # Step 2: Define setpoint and parameter mappings
        setpoint_map = {
            'A': 1,
            'B': 2,
            'C': 3,
            'D': 4,
            'E': 5
        }

        if setpoint not in setpoint_map:
            raise ValueError("Invalid setpoint. Choose between 'A', 'B', 'C', 'D', or 'E'.")

        setpoint_code = setpoint_map[setpoint]

        # Step 3: Check or set the lead or gain parameter
        if action == 'check':
            if parameter_type == 'lead':
                # Request the lead parameter using Rxx where xx is 41-45
                request_code = f'R4{setpoint_code}'
                response = self.send_request(request_code, 'X')
            elif parameter_type == 'gain':
                # Request the gain parameter using Rxx where xx is 46-50
                request_code = f'R4{5 + setpoint_code}'
                response = self.send_request(request_code, 'M')
            else:
                raise ValueError("Invalid parameter type. Use 'lead' or 'gain'.")

            # Process and return the response
            response = response.strip()
            if parameter_type == 'lead' and response.startswith('X'):
                return f"Lead parameter for setpoint {setpoint}: {response[2:]} seconds"
            elif parameter_type == 'gain' and response.startswith('M'):
                return f"Gain parameter for setpoint {setpoint}: {response[2:]} percent"
            else:
                return "Invalid response or no response"

        elif action == 'set':
            if value is None:
                raise ValueError("You must specify a value to set the parameter.")

            if parameter_type == 'lead':
                # Set the lead parameter using Xx value
                command_code = f'X{setpoint_code}{value}'
            elif parameter_type == 'gain':
                # Set the gain parameter using Mx value
                command_code = f'M{setpoint_code}{value}'
            else:
                raise ValueError("Invalid parameter type. Use 'lead' or 'gain'.")

            # Send the command to set the parameter
            self.send_command(command_code)

            return f"{parameter_type.capitalize()} parameter for setpoint {setpoint} set to {value}"
        else:
            raise ValueError("Invalid action. Use 'check' or 'set'.")

    # Valve Position Control
    def valve_position_output(self, action, output_range=None):
        """
        Check or change the valve position output range.

        Args:
            action (str): 'check' to check the current output range, 'set' to change the output range.
            output_range (str, optional): '5V' for 5 Volt range, '10V' for 10 Volt range (only used if action is 'set').

        Returns:
            str: The current valve position output range (if action is 'check').
            str: Confirmation message after setting the valve position output range (if action is 'set').
        """
        # Check the current valve position output range
        if action == 'check':
            # Send the R31 command to check the valve position output
            response = self.send_request('R31', 'B')

            # Strip any CRLF characters
            response = response.strip()

            if response.startswith('B') and len(response) == 2:
                # Extract the value (0 for 5V, 1 for 10V)
                output_value = int(response[1])

                # Map the value to the corresponding output range
                output_map = {
                    0: "5 Volt",
                    1: "10 Volt"
                }

                return f"Current valve position output range: {output_map.get(output_value, 'Unknown range')}"
            else:
                return "Invalid response or no response"

        # Change the valve position output range
        elif action == 'set':
            if output_range not in ['5V', '10V']:
                raise ValueError("Invalid output range. Choose between '5V' or '10V'.")

            # Map output range to the corresponding value
            output_value_map = {
                '5V': '0',
                '10V': '1'
            }

            # Get the corresponding value for the output range
            output_value = output_value_map[output_range]

            # Send the command to change the valve position output range
            command = f'B{output_value}'
            response = self.send_command(command)

            return f"Valve position output range set to {output_range}"

        else:
            raise ValueError("Invalid action. Use 'check' or 'set'.")


    # Valve Control Direction
    def valve_control_direction(self, action, direction=None):
        """
        Check or change the valve control direction.

        Args:
            action (str): 'check' to check the current direction, 'set' to change the direction.
            direction (str, optional): 'direct' for direct direction, 'reverse' for reverse direction (only used if action is 'set').

        Returns:
            str: The current valve control direction (if action is 'check').
            str: Confirmation message after setting the valve control direction (if action is 'set').
        """
        # Check the current valve control direction
        if action == 'check':
            # Send the R32 command to check the valve control selection
            response = self.send_request('R32', 'N')

            # Strip any CRLF characters
            response = response.strip()

            if response.startswith('N') and len(response) == 2:
                # Extract the value (0 for direct, 1 for reverse)
                control_value = int(response[1])

                # Map the control value to the corresponding direction
                control_map = {
                    0: "Direct",
                    1: "Reverse"
                }

                return f"Current valve control direction: {control_map.get(control_value, 'Unknown direction')}"
            else:
                return "Invalid response or no response"

        # Change the valve control direction
        elif action == 'set':
            if direction not in ['direct', 'reverse']:
                raise ValueError("Invalid direction. Choose between 'direct' or 'reverse'.")

            # Map direction to the corresponding value
            direction_value_map = {
                'direct': '0',
                'reverse': '1'
            }

            # Get the corresponding value for the direction
            direction_value = direction_value_map[direction]

            # Send the command to change the valve control direction
            command = f'N{direction_value}'
            response = self.send_command(command)

            return f"Valve control direction set to {direction.capitalize()}"

        else:
            raise ValueError("Invalid action. Use 'check' or 'set'.")


    # Process Limits

    def process_limit(self, action, limit_type, threshold=None):
        """
        Check or change a process limit relay.

        Args:
            action (str): 'check' to check the limit, 'set' to change the limit.
            limit_type (str): Specifies the limit type ('low1', 'high1', 'low2', 'high2').
            threshold (float, optional): The value to set for the process limit relay (only used if action is 'set').

        Returns:
            str: The process limit threshold (if action is 'check').
            str: Confirmation message after setting the process limit (if action is 'set').
        """
        # Mapping limit types to the corresponding Rxx and Px codes
        limit_type_map = {
            'low1': {'Rxx': 'R10', 'Px': 'P1'},
            'high1': {'Rxx': 'R11', 'Px': 'P2'},
            'low2': {'Rxx': 'R13', 'Px': 'P3'},
            'high2': {'Rxx': 'R14', 'Px': 'P4'}
        }

        if limit_type not in limit_type_map:
            raise ValueError("Invalid limit type. Choose between 'low1', 'high1', 'low2', 'high2'.")

        # Check process limit threshold
        if action == 'check':
            # Get the corresponding Rxx code for the specified limit type
            request_code = limit_type_map[limit_type]['Rxx']

            # Send the request to check the process limit threshold
            response = self.send_request(request_code, 'P')

            # Strip any CRLF characters and check the response format
            response = response.strip()

            if response.startswith('P') and len(response) > 2:
                # Extract the value from the response (e.g., "Px value")
                limit_code = int(response[1])
                limit_value = response[2:]

                # Map the limit code to its corresponding meaning
                limit_code_map = {
                    1: "Low threshold for process limit 1",
                    2: "High threshold for process limit 1",
                    3: "Low threshold for process limit 2",
                    4: "High threshold for process limit 2"
                }

                limit_type_str = limit_code_map.get(limit_code, "Unknown limit type")
                return f"{limit_type_str}: {limit_value}"
            else:
                return "Invalid response or no response"

        # Change process limit relay
        elif action == 'set':
            if threshold is None:
                raise ValueError("You must specify a threshold value when setting the process limit.")

            # Get the corresponding Px code for the specified limit type
            command_code = limit_type_map[limit_type]['Px']

            # Format the threshold value and send the command
            command = f"{command_code}{threshold}"
            response = self.send_command(command)

            return f"Process limit {limit_type} set to {threshold}"
        
        else:
            raise ValueError("Invalid action. Use 'check' or 'set'.")

        
    def close(self):
        """
        Close the serial connection.
        """
        self.ser.close()