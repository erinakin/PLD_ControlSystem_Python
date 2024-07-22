import serial

class PressureControls:
    """
    A class to manage and control a pressure controller via RS-232 commands.

    This class provides methods to set levels of set points A, B, C, D, and E, set the F.S. level of the analog set point,
    and select set points A and B. Each command sent to the pressure controller ends with a carriage return-line feed (CRLF).
    """

    def __init__(self, port, baudrate=9600, timeout=1):
        """
        Initialize the serial connection to the pressure controller.

        Args:
            port (str): The port to which the pressure controller is connected.
            baudrate (int, optional): The baud rate for the serial communication. Default is 9600.
            timeout (int, optional): The read timeout value for the serial communication. Default is 1 second.
        """
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

    def send_command(self, command):
        """
        Send a command to the pressure controller with CRLF appended.

        Args:
            command (str): The command to send to the pressure controller.

        Returns:
            str: The response from the pressure controller.
        """
        # Append CRLF to the command
        command_with_crlf = command + '\r\n'
        self.ser.write(command_with_crlf.encode())
        response = self.ser.readline().decode().strip()
        return response

    def set_setpoint_A(self, value):
        """
        Set the level of set point A.

        Args:
            value (float): The value to set for set point A. This is a percentage of F.S. (Full Scale) pressure,
                           position for position set points, % of open for direct direction control,
                           or % of closed for reverse direction control.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"S1{value}"
        return self.send_command(command)

    def set_setpoint_B(self, value):
        """
        Set the level of set point B.

        Args:
            value (float): The value to set for set point B. This is a percentage of F.S. pressure,
                           position for position set points, % of open for direct direction control,
                           or % of closed for reverse direction control.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"S2{value}"
        return self.send_command(command)

    def set_setpoint_C(self, value):
        """
        Set the level of set point C.

        Args:
            value (float): The value to set for set point C. This is a percentage of F.S. pressure,
                           position for position set points, % of open for direct direction control,
                           or % of closed for reverse direction control.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"S3{value}"
        return self.send_command(command)

    def set_setpoint_D(self, value):
        """
        Set the level of set point D.

        Args:
            value (float): The value to set for set point D. This is a percentage of F.S. pressure,
                           position for position set points, % of open for direct direction control,
                           or % of closed for reverse direction control.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"S4{value}"
        return self.send_command(command)

    def set_setpoint_E(self, value):
        """
        Set the level of set point E.

        Args:
            value (float): The value to set for set point E. This is a percentage of F.S. pressure,
                           position for position set points, % of open for direct direction control,
                           or % of closed for reverse direction control.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"S5{value}"
        return self.send_command(command)

    def set_analog_setpoint(self, value):
        """
        Set the F.S. level of the analog set point.

        Args:
            value (int): The value to set for the analog set point. 
                0 = 100% of controlling transducer's range,
                1 = 10% of controlling transducer's range.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"S6{value}"
        return self.send_command(command)

    def select_setpoint_A(self):
        """
        Select set point A.

        Returns:
            str: The response from the pressure controller.
        """
        command = "D1"
        return self.send_command(command)

    def select_setpoint_B(self):
        """
        Select set point B.

        Returns:
            str: The response from the pressure controller.
        """
        command = "D2"
        return self.send_command(command)
    def select_setpoint_C(self):
        """
        Select set point C.

        Returns:
            str: The response from the pressure controller.
        """
        command = "D3"
        return self.send_command(command)

    def select_setpoint_D(self):
        """
        Select set point D.

        Returns:
            str: The response from the pressure controller.
        """
        command = "D4"
        return self.send_command(command)

    def select_setpoint_E(self):
        """
        Select set point E.

        Returns:
            str: The response from the pressure controller.
        """
        command = "D5"
        return self.send_command(command)

    def select_analog_setpoint(self):
        """
        Select analog set point.

        Returns:
            str: The response from the pressure controller.
        """
        command = "D6"
        return self.send_command(command)

    def set_sensor_range(self, value):
        """
        Set the sensor range value.

        Args:
            value (int): The sensor range value. Valid values are:
                         0 = 0.1, 1 = 0.2, 2 = 0.5, 3 = 1, 
                         4 = 2,   5 = 5,   6 = 10,  7 = 50,
                         8 = 100, 9 = 500, 10 = 1000, 11 = 5000, 
                         12 = 10000, 13 = 1.33, 14 = 2.66, 15 = 13.33, 
                         16 = 133.3, 17 = 1333, 18 = 6666, 19 = 13332.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"E{value}"
        return self.send_command(command)

    def set_pressure_units(self, value):
        """
        Set the pressure units value.

        Args:
            value (int): The pressure units value. Valid values are:
                         0 = Torr, 1 = mTorr, 2 = mbar, 3 = µbar, 4 = kPa, 5 = Pa,
                         6 = cmH2O, 7 = inH2O.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"F{value}"
        return self.send_command(command)

    def set_sensor_voltage_range(self, value):
        """
        Set the sensor voltage range value.

        Args:
            value (int): The sensor voltage range value. Valid values are:
                         0 = 1 Volt, 1 = 5 Volts, 2 = 10 Volts.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"G{value}"
        return self.send_command(command)

    def open_valve(self):
        """
        Open the valve.

        Returns:
            str: The response from the pressure controller.
        """
        command = "O"
        return self.send_command(command)

    def close_valve(self):
        """
        Close the valve.

        Returns:
            str: The response from the pressure controller.
        """
        command = "C"
        return self.send_command(command)

    def hold_valve(self):
        """
        Hold the valve.

        Returns:
            str: The response from the pressure controller.
        """
        command = "H"
        return self.send_command(command)

    def set_softstart_rate(self, point, value):
        """
        Set the softstart rate of a set point or control.
        Setpoints: A, B, C, D, E, analog
        Control: open valve, close valve

        Args:
            point (str): The point to set the softstart rate for. Valid values are 'A', 'B', 'C', 'D', 'E', 'analog', 'open', 'close'.
            value (float): The softstart rate value to set.

        Returns:
            str: The response from the pressure controller.
        """
        points = {
            'A': 'I1',
            'B': 'I2',
            'C': 'I3',
            'D': 'I4',
            'E': 'I5',
            'analog': 'I6',
            'open': 'I7',
            'close': 'I8'
        }

        if point in points:
            command = f"{points[point]}{value}"
            return self.send_command(command)
        else:
            raise ValueError("Invalid set point. Choose from 'A', 'B', 'C', 'D', 'E', 'analog', 'open', 'close'.")


    def set_lowthreshold_PL1(self, value):     
        """
        Set the low threshold for Process Limit 1.

        Args:
            value (int): value is % of full scale 

        Returns:
            str: The response from the pressure controller.
        """
        command = f"P1{value}"
        return self.send_command(command)
    
    def set_highthreshold_PL1(self, value):     
        """
        Set the high threshold for Process Limit 1.

        Args:
            value (int): value is % of full scale 

        Returns:
            str: The response from the pressure controller.
        """
        command = f"P2{value}"
        return self.send_command(command)

    def set_lowthreshold_PL2(self, value):     
        """
        Set the low threshold for Process Limit 2.
 
        Args:
            value (int): value is % of full scale 

        Returns:
            str: The response from the pressure controller.
        """
        command = f"P3{value}"
        return self.send_command(command)
    
    def set_highthreshold_PL2(self, value):     
        """
        Set the high threshold for Process Limit 2.

        Args:
            value (int): value is % of full scale 

        Returns:
            str: The response from the pressure controller.
        """
        command = f"P4{value}"
        return self.send_command(command)

    def zero_sensor(self):
        """
        Zero the sensor.

        Returns:
            str: The response from the pressure controller.
        """
        return self.send_command("Z1")

    def special_zero(self,value):
        """
        Special zero the sensor.

        Args:
            value (int): value is % of full scale of the pressure reading.

        Returns:
            str: The response from the pressure controller.
        """
        command = f"Z2{value}"
        return self.send_command(command)
    
    def remove_zero_correction(self):
        """Remove zero correction factors"""
        return self.send_command("Z3")

    def learn_zero_analog_set_point(self):
        """Learn zero of the analog set point"""
        return self.send_command("Z4")
    
    def calibrate_span_ad_converter(self, value):
        """
        Calibrate span of A/D converter and zeroed pressure output.

        Parameters:
        value (int): The value to assign to the converter reading of the pressure channel.

        Returns:
        str: The response from the controller.
        """
        command = f"Y1 {value}"
        return self.send_command(command)

    def learn_full_scale_analog_set_point(self):
        """
        Learn the full scale of the analog set point.

        Returns:
        str: The response from the controller.
        """
        return self.send_command("Y2")

    def learn_system(self):
        """
        Learn the system (Self-Tuning control).

        Returns:
        str: The response from the controller.
        """
        return self.send_command("L")

    def stop_learn_function(self):
        """
        Stop the learn function (while in process).

        Returns:
        str: The response from the controller.
        """
        return self.send_command("Q")

    def calibrate_valve(self, value):
        """
        Calibrate the valve.

        Parameters:
        value (int): 1 = Std 253, 2 = Fast 253, 3 = 653.

        Returns:
        str: The response from the controller.
        """
        if value in [1, 2, 3]:
            command = f"J {value}"
            return self.send_command(command)
        else:
            raise ValueError("Invalid value. Choose from 1, 2, 3.")

    def set_analog_set_point_range(self, value):
        """
        Set analog set point range.

        Parameters:
        value (int): 0 = 5 Volts, 1 = 10 Volts.

        Returns:
        str: The response from the controller.
        """
        if value in [0, 1]:
            command = f"A {value}"
            return self.send_command(command)
        else:
            raise ValueError("Invalid value. Choose from 0, 1.")

    def set_point_type(self, point, value):
        """
        Set point type for A, B, C, D, E.

        Parameters:
        point (str): The set point (A, B, C, D, E).
        value (int): 0 = position, 1 = pressure.

        Returns:
        str: The response from the controller.
        """
        points = {'A':'1', 'B':'2', 'C':'3', 'D':'4', 'E':'5'}

        if point in points and value in [0, 1]:
            command = f"T{points[point]} {value}"
            return self.send_command(command)
        else:
            raise ValueError("Invalid point or value. Choose from A, B, C, D for point and 0, 1 for value.")

    def set_valve_position_output_range(self, value):
        """
        Set valve position output range.

        Parameters:
        value (int): 0 = 5 Volts, 1 = 10 Volts.

        Returns:
        str: The response from the controller.
        """
        if value in [0, 1]:
            command = f"B {value}"
            return self.send_command(command)
        else:
            raise ValueError("Invalid value. Choose from 0, 1.")

    def set_direct_reverse_control(self, value):
        """
        Set direct/reverse control.

        Parameters:
        value (int): 0 = direct, 1 = reverse.

        Returns:
        str: The response from the controller.
        """
        if value in [0, 1]:
            command = f"N {value}"
            return self.send_command(command)
        else:
            raise ValueError("Invalid value. Choose from 0, 1.")

    def set_sensor_type(self, value):
        """
        Set sensor type.

        Parameters:
        value (int): 0 = Absolute, 1 = Differential.

        Returns:
        str: The response from the controller.
        """
        if value in [0, 1]:
            command = f"U {value}"
            return self.send_command(command)
        else:
            raise ValueError("Invalid value. Choose from 0, 1.")

    def set_lead(self, point, value):
        """
        Set lead of a set point (A, B, C, D, E).

        Parameters:
        point (str): The set point (A, B, C, D, E).
        value (int): The lead value in seconds.

        Returns:
        str: The response from the controller.
        """
        if point in ['A', 'B', 'C', 'D', 'E']:
            command = f"X{point} {value}"
            return self.send_command(command)
        else:
            raise ValueError("Invalid set point. Choose from A, B, C, D, E.")

    def set_gain(self, point, value):
        """
        Set gain of a set point (A, B, C, D, E).

        Parameters:
        point (str): The set point (A, B, C, D, E).
        value (int): The gain value as a percentage.

        Returns:
        str: The response from the controller.
        """
        if point in ['A', 'B', 'C', 'D', 'E']:
            command = f"M{point} {value}"
            return self.send_command(command)
        else:
            raise ValueError("Invalid set point. Choose from A, B, C, D, E.")

    def select_self_tuning_control(self):
        """
        Select Self-Tuning control.

        Returns:
        str: The response from the controller.
        """
        return self.send_command("V0")

    def select_pid_control(self):
        """
        Select PID control.

        Returns:
        str: The response from the controller.
        """
        return self.send_command("V1")

    def close(self):
        """
        Close the serial connection to the pressure controller.
        """
        self.ser.close()
