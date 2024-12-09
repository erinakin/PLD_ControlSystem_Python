from enum import Enum


class InvalidCharError(Exception):
    """Custom exception for invalid characters."""
    pass


class PfeifferTurbopumpProtocol:
    _filter_invalid_char = False

    @classmethod
    def enable_valid_char_filter(cls):
        """Globally enable the filter to ignore invalid characters."""
        cls._filter_invalid_char = True

    @classmethod
    def disable_valid_char_filter(cls):
        """Globally disable the filter to ignore invalid characters."""
        cls._filter_invalid_char = False

    # Define an enum class for error codes Look into this more and try to modify to match manual properly
    class ErrorCode(Enum):
        NO_ERROR = "No error"
        EXCESS_ROTATION_SPEED = "Excess rotation speed"
        EXCESS_VOLTAGE = "Excess voltage"
        RUN_UP_ERROR = "Run-up error"
        OPERATING_FLUID_LOW = "Operating fluid low"
        CONNECTION_FAULTY = "Electronic drive unit - turbopump connection faulty"
        INTERNAL_DEVICE_ERROR = "Internal device error"
        SOFTWARE_VERSION_INCOMPATIBLE = "Electronic drive unit version incompatible"
        DRIVE_FAULT = "Drive fault"
        INTERNAL_CONFIGURATION_ERROR = "Internal configuration error"
        EXCESS_TEMPERATURE_ELECTRONICS = "Excess temperature, electronics"
        EXCESS_TEMPERATURE_MOTOR = "Excess temperature, motor"
        INITIALIZATION_ERROR = "Internal initialization error"
        MAGNETIC_BEARING_OVERLOAD_AXIAL = "Axial magnetic bearing overload"
        MAGNETIC_BEARING_OVERLOAD_RADIAL = "Radial magnetic bearing overload"
        ROTOR_INSTABLE = "Rotor instable"
        UNKNOWN_CONNECTION_PANEL = "Unknown connection panel"
        TEMPERATURE_EVALUATION_FAULTY = "Temperature evaluation faulty"
        INTERNAL_COMMUNICATION_ERROR = "Internal communication error"
        HIGH_ROTOR_TEMPERATURE = "High rotor temperature"
        FINAL_STAGE_GROUP_ERROR = "Final stage group error"
        ROTATION_SPEED_MEASUREMENT_FAULTY = "Rotation speed measurement faulty"
        SOFTWARE_NOT_RELEASED = "Software not released"
        OPERATING_FLUID_SENSOR_FAULTY = "Operating fluid sensor faulty"
        PUMP_COMMUNICATION_ERROR = "Operating fluid pump communication error"
        ROTOR_TEMPERATURE_EVALUATION_FAULTY = "Rotor temperature evaluation faulty"
        FINAL_STAGE_TEMPERATURE_FAULTY = "Final stage temperature evaluation faulty"
        HIGH_DELAY = "High delay"
        BEARING_TEMPERATURE_HIGH = "Bearing high temperature"
        CALIBRATION_REQUIRED = "Calibration requirement"
        SAFETY_BEARING_WEAR_HIGH = "Safety bearing wear too high"
        HIGH_ROTOR_IMBALANCE = "High rotor imbalance"
        # Add additional error codes as needed based on the full list

    @staticmethod
    def _send_data_request(s, addr, param_num):
        """Send a data request to the turbopump."""
        c = "{:03d}00{:03d}02=?".format(addr, param_num)
        c += "{:03d}\r".format(sum([ord(x) for x in c]) % 256)
        s.write(c.encode())

    @staticmethod
    def _send_control_command(s, addr, param_num, data_str):
        """Send a control command to the turbopump."""
        c = "{:03d}10{:03d}{:02d}{:s}".format(addr, param_num, len(data_str), data_str)
        c += "{:03d}\r".format(sum([ord(x) for x in c]) % 256)
        return s.write(c.encode())

    @classmethod
    def _read_pump_response(cls, s, valid_char_filter=None):
        """Read the pump response."""
        if valid_char_filter is None:
            valid_char_filter = cls._filter_invalid_char

        r = ""
        for _ in range(64):
            c = s.read(1)
            if c == b"":
                break

            try:
                r += c.decode("ascii")
            except UnicodeDecodeError:
                if valid_char_filter:
                    continue
                raise InvalidCharError(
                    "Cannot decode character. Enable the filter globally by running the function "
                    "`PfeifferTurbopumpProtocol.enable_valid_char_filter()`."
                )

            if c == b"\r":
                break

        if len(r) < 14:
            raise ValueError("pump response too short to be valid")
        if r[-1] != "\r":
            raise ValueError("pump response incorrectly terminated")
        if int(r[-4:-1]) != (sum([ord(x) for x in r[:-4]]) % 256):
            raise ValueError("invalid checksum in pump response")

        addr = int(r[:3])
        rw = int(r[3:4])
        param_num = int(r[5:8])
        data = r[10:-4]

        if data == "NO_DEF":
            raise ValueError("undefined parameter number")
        if data == "_RANGE":
            raise ValueError("data is out of range")
        if data == "_LOGIC":
            raise ValueError("logic access violation")

        return addr, rw, param_num, data

    @classmethod
    def read_error_code(cls, s, addr, valid_char_filter=None):
        """Read the error code from the turbopump and return the corresponding ErrorCode enum."""
        cls._send_data_request(s, addr, 303)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter=valid_char_filter)

        if raddr != addr or rw != 1 or rparam_num != 303:
            raise ValueError("Invalid response from pump")

        error_code_mapping = {
            "000000": cls.ErrorCode.NO_ERROR,
            "Err001": cls.ErrorCode.EXCESS_ROTATION_SPEED,
            "Err002": cls.ErrorCode.EXCESS_VOLTAGE,
            "Err006": cls.ErrorCode.RUN_UP_ERROR,
            "Err007": cls.ErrorCode.OPERATING_FLUID_LOW,
            "Err008": cls.ErrorCode.CONNECTION_FAULTY,
            "Err010": cls.ErrorCode.INTERNAL_DEVICE_ERROR,
            "Err021": cls.ErrorCode.SOFTWARE_VERSION_INCOMPATIBLE,
            "Err041": cls.ErrorCode.DRIVE_FAULT,
            "Err043": cls.ErrorCode.INTERNAL_CONFIGURATION_ERROR,
            "Err044": cls.ErrorCode.EXCESS_TEMPERATURE_ELECTRONICS,
            "Err045": cls.ErrorCode.EXCESS_TEMPERATURE_MOTOR,
            "Err046": cls.ErrorCode.INITIALIZATION_ERROR,
            "Err073": cls.ErrorCode.MAGNETIC_BEARING_OVERLOAD_AXIAL,
            "Err074": cls.ErrorCode.MAGNETIC_BEARING_OVERLOAD_RADIAL,
            "Err089": cls.ErrorCode.ROTOR_INSTABLE,
            "Err091": cls.ErrorCode.INTERNAL_DEVICE_ERROR,
            "Err092": cls.ErrorCode.UNKNOWN_CONNECTION_PANEL,
            "Err093": cls.ErrorCode.TEMPERATURE_EVALUATION_FAULTY,
            "Err098": cls.ErrorCode.INTERNAL_COMMUNICATION_ERROR,
            "Err106": cls.ErrorCode.HIGH_ROTOR_TEMPERATURE,
            "Err107": cls.ErrorCode.FINAL_STAGE_GROUP_ERROR,
            "Err108": cls.ErrorCode.ROTATION_SPEED_MEASUREMENT_FAULTY,
            "Err109": cls.ErrorCode.SOFTWARE_NOT_RELEASED,
            "Err110": cls.ErrorCode.OPERATING_FLUID_SENSOR_FAULTY,
            "Err111": cls.ErrorCode.PUMP_COMMUNICATION_ERROR,
            "Err113": cls.ErrorCode.ROTOR_TEMPERATURE_EVALUATION_FAULTY,
            "Err114": cls.ErrorCode.FINAL_STAGE_TEMPERATURE_FAULTY,
            "Wrn089": cls.ErrorCode.HIGH_DELAY,
            "Wrn119": cls.ErrorCode.BEARING_TEMPERATURE_HIGH,
            "Wrn807": cls.ErrorCode.CALIBRATION_REQUIRED,
            "Wrn890": cls.ErrorCode.SAFETY_BEARING_WEAR_HIGH,
            "Wrn891": cls.ErrorCode.HIGH_ROTOR_IMBALANCE,
            # Add additional mappings as needed
        }

        if rdata in error_code_mapping:
            return error_code_mapping[rdata]
        else:
            raise ValueError("Unexpected error code from pump")

    # Control Commands
    
    @classmethod
    def heating(cls, s, addr, on=None, read=False, valid_char_filter=None):
        """
        Enable or disable the heating function, or get the current heating status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - on: Boolean indicating whether to turn heating on (True) or off (False) when writing.
        - read: Boolean indicating whether to read (True) or write (False) the heating status.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current heating status if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 1  # Parameter number for Heating

        if read:
            # Read the current heating status
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for heating read command")
            return bool(int(rdata))
        else:
            # Write the heating status
            if on is None:
                raise ValueError("On value must be provided for write operation.")
            data = "1" if on else "0"
            cls._send_control_command(s, addr, param_num, data)
            
            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for heating write command")


    @classmethod
    def standby(cls, s, addr, on=None, read=False, valid_char_filter=None):
        """
        Enable or disable the standby mode, or get the current standby status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - on: Boolean indicating whether to turn standby mode on (True) or off (False) when writing.
        - read: Boolean indicating whether to read (True) or write (False) the standby status.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current standby status if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 2  # Parameter number for Standby

        if read:
            # Read the current standby status
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for standby read command")
            return bool(int(rdata))
        else:
            # Write the standby status
            if on is None:
                raise ValueError("On value must be provided for write operation.")
            data = "1" if on else "0"
            cls._send_control_command(s, addr, param_num, data)
            
            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for standby write command")


    @classmethod
    def run_up_time_control(cls, s, addr, on=None, read=False, valid_char_filter=None):
        """
        Enable or disable run-up time control, or get the current run-up time control status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - on: Boolean indicating whether to enable (True) or disable (False) run-up time control when writing.
        - read: Boolean indicating whether to read (True) or write (False) the run-up time control status.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current run-up time control status if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 4  # Parameter number for Run-up time control

        if read:
            # Read the current run-up time control status
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for run-up time control read command")
            return bool(int(rdata))
        else:
            # Write the run-up time control status
            if on is None:
                raise ValueError("On value must be provided for write operation.")
            data = "1" if on else "0"
            cls._send_control_command(s, addr, param_num, data)
            
            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for run-up time control write command")


    @classmethod
    def acknowledge_error(cls, s, addr, valid_char_filter=None):
        """
        Acknowledge an error or check the current error acknowledgment status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating if error acknowledgment is active if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 9  # Parameter number for Error Acknowledge

        # Send error acknowledgment
        data = "1"  # 1 indicates error acknowledgment
        cls._send_control_command(s, addr, param_num, data)
            
        # Read and validate response
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
            raise ValueError("Invalid response from pump for error acknowledgment write command")


    @classmethod
    def pumping_station(cls, s, addr, on=None, read=False, valid_char_filter=None):
        """
        Enable or disable the pumping station function, or get the current pumping station status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - on: Boolean indicating whether to enable (True) or disable (False) the pumping station when writing.
        - read: Boolean indicating whether to read (True) or write (False) the pumping station status.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current pumping station status if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 10  # Parameter number for Pumping Station

        if read:
            # Read the current pumping station status
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for pumping station read command")
            return bool(int(rdata))
        else:
            # Write the pumping station status
            if on is None:
                raise ValueError("On value must be provided for write operation.")
            data = "1" if on else "0"
            cls._send_control_command(s, addr, param_num, data)
            
            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for pumping station write command")


    @classmethod
    def enable_vent(cls, s, addr, enable=None, read=False, valid_char_filter=None):
        """
        Enable or disable the venting function, or get the current venting status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - enable: Boolean indicating whether to enable (True) or disable (False) venting when writing.
        - read: Boolean indicating whether to read (True) or write (False) the venting status.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current venting status if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 12  # Parameter number for Enable Venting

        if read:
            # Read the current venting status
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for enable venting read command")
            return bool(int(rdata))
        else:
            # Write the venting status
            if enable is None:
                raise ValueError("Enable value must be provided for write operation.")
            data = "1" if enable else "0"
            cls._send_control_command(s, addr, param_num, data)
            
            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for enable venting write command")


    @classmethod
    def config_speed_switch_point(cls, s, addr, point=None, read=False, valid_char_filter=None):
        """
        Set or get the rotation speed switch point.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - point: Integer (0 or 1) indicating the switch point when writing.
        - read: Boolean indicating whether to read (True) or write (False) the rotation speed switch point.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current switch point if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if point is out of range when writing.
        """
        param_num = 17  # Parameter number for Config Rotation Speed Switch Point

        if read:
            # Read the current switch point
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for config speed switch point read command")
            return int(rdata)
        else:
            # Write the switch point
            if point not in [0, 1]:
                raise ValueError("Point value out of range. Must be 0 or 1.")
            data = str(point)
            cls._send_control_command(s, addr, param_num, data)
            
            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for config speed switch point write command")


    @classmethod
    def cfg_do2(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get the configuration for DO2 output.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 22) indicating the desired DO2 configuration when writing.
        - read: Boolean indicating whether to read (True) or write (False) the DO2 configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current DO2 configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 19  # Parameter number for Cfg DO2

        if read:
            # Read the current DO2 configuration
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg DO2 read command")
            return int(rdata)
        else:
            # Write the DO2 configuration
            if config_value is None or not (0 <= config_value <= 22):
                raise ValueError("Config value out of range. Must be between 0 and 22.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg DO2 write command")


    @classmethod
    def motor_pump(cls, s, addr, on=None, read=False, valid_char_filter=None):
        """
        Enable or disable the motor vacuum pump, or get the current motor pump status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - on: Boolean indicating whether to turn the motor pump on (True) or off (False) when writing.
        - read: Boolean indicating whether to read (True) or write (False) the motor pump status.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current motor pump status if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 23  # Parameter number for MotorPump

        if read:
            # Read the current motor pump status
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for motor pump read command")
            return bool(int(rdata))
        else:
            # Write the motor pump status
            if on is None:
                raise ValueError("On value must be provided for write operation.")
            data = "1" if on else "0"
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for motor pump write command")


    @classmethod
    def cfg_do1(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get the configuration for DO1 output.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 22) indicating the desired DO1 configuration when writing.
        - read: Boolean indicating whether to read (True) or write (False) the DO1 configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current DO1 configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 24  # Parameter number for Cfg DO1

        if read:
            # Read the current DO1 configuration
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg DO1 read command")
            return int(rdata)
        else:
            # Write the DO1 configuration
            if config_value is None or not (0 <= config_value <= 22):
                raise ValueError("Config value out of range. Must be between 0 and 22.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg DO1 write command")


    @classmethod
    def opmode_bkp(cls, s, addr, mode=None, read=False, valid_char_filter=None):
        """
        Set or get the operation mode for the backup pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - mode: Integer (0 to 3) specifying the operation mode when writing:
            - 0: Continuous operation
            - 1: Interval operation
            - 2: Delayed switching on
            - 3: Delayed interval operation
        - read: Boolean indicating whether to read (True) or write (False) the operation mode.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current operation mode if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if mode is out of range when writing.
        """
        param_num = 25  # Parameter number for OpMode BKP

        if read:
            # Read the current operation mode for the backup pump
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for OpMode BKP read command")
            return int(rdata)
        else:
            # Write the operation mode for the backup pump
            if mode is None or not (0 <= mode <= 3):
                raise ValueError("Mode value out of range. Must be between 0 and 3.")
            data = "{:01d}".format(mode)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for OpMode BKP write command")


    @classmethod
    def spd_set_mode(cls, s, addr, on=None, read=False, valid_char_filter=None):
        """
        Enable or disable rotation speed setting mode, or get the current status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - on: Boolean indicating whether to enable (True) or disable (False) speed setting mode when writing.
        - read: Boolean indicating whether to read (True) or write (False) the speed setting mode.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current speed setting mode if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 26  # Parameter number for SpdSetMode

        if read:
            # Read the current speed setting mode
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for SpdSetMode read command")
            return bool(int(rdata))
        else:
            # Write the speed setting mode
            if on is None:
                raise ValueError("On value must be provided for write operation.")
            data = "1" if on else "0"
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for SpdSetMode write command")


    @classmethod
    def gas_mode(cls, s, addr, mode=None, read=False, valid_char_filter=None):
        """
        Set or get the gas mode for the pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - mode: Integer (0 to 2) specifying the gas mode when writing:
            - 0: Heavy gases
            - 1: Light gases
            - 2: Helium
        - read: Boolean indicating whether to read (True) or write (False) the gas mode.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current gas mode if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if mode is out of range when writing.
        """
        param_num = 27  # Parameter number for GasMode

        if read:
            # Read the current gas mode
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for GasMode read command")
            return int(rdata)
        else:
            # Write the gas mode
            if mode is None or not (0 <= mode <= 2):
                raise ValueError("Mode value out of range. Must be between 0 and 2.")
            data = "{:01d}".format(mode)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for GasMode write command")


    @classmethod
    def cfg_remote(cls, s, addr, mode=None, read=False, valid_char_filter=None):
        """
        Set or get the remote control configuration for the pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - mode: Integer (0 to 4) specifying the remote control configuration when writing:
            - 0: Standard
            - 3: Relay, inverted
            - 4: Other custom configurations
        - read: Boolean indicating whether to read (True) or write (False) the remote control configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current remote control configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if mode is out of range when writing.
        """
        param_num = 28  # Parameter number for Cfg Remote

        if read:
            # Read the current remote control configuration
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg Remote read command")
            return int(rdata)
        else:
            # Write the remote control configuration
            if mode is None or not (0 <= mode <= 4):
                raise ValueError("Mode value out of range. Must be between 0 and 4.")
            data = "{:01d}".format(mode)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg Remote write command")


    @classmethod
    def vent_mode(cls, s, addr, mode=None, read=False, valid_char_filter=None):
        """
        Set or get the venting mode for the pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - mode: Integer (0 to 2) specifying the venting mode when writing:
            - 0: Delayed venting
            - 1: No venting
            - 2: Direct venting
        - read: Boolean indicating whether to read (True) or write (False) the venting mode.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current venting mode if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if mode is out of range when writing.
        """
        param_num = 30  # Parameter number for VentMode

        if read:
            # Read the current venting mode
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for VentMode read command")
            return int(rdata)
        else:
            # Write the venting mode
            if mode is None or not (0 <= mode <= 2):
                raise ValueError("Mode value out of range. Must be between 0 and 2.")
            data = "{:01d}".format(mode)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for VentMode write command")


    @classmethod
    def cfg_acc_a1(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get configuration for accessory connection A1.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 14) specifying the configuration for accessory connection A1 when writing:
            - 0: Fan
            - 1: Venting valve, closed without current
            - 2: Heating
            - 3: Backing pump
            - 4: Fan (temperature controlled)
            - 5: Sealing gas
            - 6: Always "0"
            - 7: Always "1"
            - 8: Power failure venting unit
            - 9: TMS Heating
            - 10: TMS Cooling
            - 11: Second venting valve
            - 12: Sealing gas monitoring
            - 13: Sealing gas monitoring
            - 14: Heating (bottom part temperature controlled)
        - read: Boolean indicating whether to read (True) or write (False) the configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 35  # Parameter number for Cfg Acc A1

        if read:
            # Read the current configuration of accessory connection A1
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg Acc A1 read command")
            return int(rdata)
        else:
            # Write the configuration for accessory connection A1
            if config_value is None or not (0 <= config_value <= 14):
                raise ValueError("Config value out of range. Must be between 0 and 14.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg Acc A1 write command")


    @classmethod
    def cfg_acc_b1(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get configuration for accessory connection B1.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 14) specifying the configuration for accessory connection B1 when writing.
        - read: Boolean indicating whether to read (True) or write (False) the configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 36  # Parameter number for Cfg Acc B1

        if read:
            # Read the current configuration of accessory connection B1
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg Acc B1 read command")
            return int(rdata)
        else:
            # Write the configuration for accessory connection B1
            if config_value is None or not (0 <= config_value <= 14):
                raise ValueError("Config value out of range. Must be between 0 and 14.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg Acc B1 write command")


    @classmethod
    def cfg_acc_a2(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get configuration for accessory connection A2.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 3) specifying the configuration for accessory connection A2 when writing.
        - read: Boolean indicating whether to read (True) or write (False) the configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 37  # Parameter number for Cfg Acc A2

        if read:
            # Read the current configuration of accessory connection A2
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg Acc A2 read command")
            return int(rdata)
        else:
            # Write the configuration for accessory connection A2
            if config_value is None or not (0 <= config_value <= 3):
                raise ValueError("Config value out of range. Must be between 0 and 3.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg Acc A2 write command")


    @classmethod
    def cfg_acc_b2(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get configuration for accessory connection B2.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 14) specifying the configuration for accessory connection B2 when writing.
        - read: Boolean indicating whether to read (True) or write (False) the configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 38  # Parameter number for Cfg Acc B2

        if read:
            # Read the current configuration of accessory connection B2
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg Acc B2 read command")
            return int(rdata)
        else:
            # Write the configuration for accessory connection B2
            if config_value is None or not (0 <= config_value <= 14):
                raise ValueError("Config value out of range. Must be between 0 and 14.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg Acc B2 write command")

    @classmethod
    def press_hv_en(cls, s, addr, mode=None, read=False, valid_char_filter=None):
        """
        Set or get the HV sensor mode (IKT only).

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - mode: Integer (0 to 3) specifying the HV sensor mode when writing:
            - 0: Off
            - 1: On
            - 2: On when rotation speed switch point is reached
            - 3: On when pressure switch point underrun occurs
        - read: Boolean indicating whether to read (True) or write (False) the HV sensor mode.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current HV sensor mode if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if mode is out of range when writing.
        """
        param_num = 41  # Parameter number for Press1HVEn

        if read:
            # Read the current HV sensor mode
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Press1HVEn read command")
            return int(rdata)
        else:
            # Write the HV sensor mode
            if mode is None or not (0 <= mode <= 3):
                raise ValueError("Mode value out of range. Must be between 0 and 3.")
            data = "{:01d}".format(mode)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Press1HVEn write command")


    @classmethod
    def sealing_gas(cls, s, addr, enable=None, read=False, valid_char_filter=None):
        """
        Enable or disable sealing gas, or get the current sealing gas status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - enable: Boolean indicating whether to enable (True) or disable (False) sealing gas when writing.
        - read: Boolean indicating whether to read (True) or write (False) the sealing gas status.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current sealing gas status if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 50  # Parameter number for SealingGas

        if read:
            # Read the current sealing gas status
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for SealingGas read command")
            return bool(int(rdata))
        else:
            # Write the sealing gas status
            if enable is None:
                raise ValueError("Enable value must be provided for write operation.")
            data = "1" if enable else "0"
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for SealingGas write command")


    @classmethod
    def cfg_output_ao1(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get configuration for output AO1.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 8) specifying the configuration for output AO1 when writing:
            - 0: Actual rotation speed
            - 1: Output
            - 2: Current
            - 3: Always 0 V
            - 4: Always 10 V
            - 5: Follows AI1
            - 6: Pressure value 1
            - 7: Pressure value 2
            - 8: Fore-vacuum control
        - read: Boolean indicating whether to read (True) or write (False) the configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 55  # Parameter number for Cfg AO1

        if read:
            # Read the current configuration of AO1
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg AO1 read command")
            return int(rdata)
        else:
            # Write the configuration for AO1
            if config_value is None or not (0 <= config_value <= 8):
                raise ValueError("Config value out of range. Must be between 0 and 8.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg AO1 write command")


    @classmethod
    def cfg_input_ai1(cls, s, addr, enable=None, read=False, valid_char_filter=None):
        """
        Enable or disable configuration input AI1, or get the current status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - enable: Boolean indicating whether to enable (True) or disable (False) configuration input AI1 when writing.
        - read: Boolean indicating whether to read (True) or write (False) the configuration input status.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current status if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 57  # Parameter number for Cfg AI1

        if read:
            # Read the current configuration status of AI1
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg AI1 read command")
            return bool(int(rdata))
        else:
            # Write the configuration status for AI1
            if enable is None:
                raise ValueError("Enable value must be provided for write operation.")
            data = "1" if enable else "0"
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg AI1 write command")


    @classmethod
    def ctrl_via_int(cls, s, addr, mode=None, read=False, valid_char_filter=None):
        """
        Set or get the control interface for the pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - mode: Integer (1 to 255) specifying the control interface when writing:
            - 1: Remote
            - 2: RS-485
            - 4: PV.can
            - 8: Fieldbus
            - 16: E74
            - 255: Unlock interface selection
        - read: Boolean indicating whether to read (True) or write (False) the control interface setting.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current control interface if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if mode is out of range when writing.
        """
        param_num = 60  # Parameter number for CtrlViaInt

        if read:
            # Read the current value of the control interface
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for CtrlViaInt read command")
            return int(rdata)
        else:
            # Write the control interface setting
            if mode is None or not (1 <= mode <= 255):
                raise ValueError("Mode value out of range. Must be between 1 and 255.")
            data = "{:03d}".format(mode)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for CtrlViaInt write command")


    @classmethod
    def int_sel_lckd(cls, s, addr, lock=None, read=False, valid_char_filter=None):
        """
        Lock or unlock the interface selection, or get the current lock status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - lock: Boolean indicating whether to lock (True) or unlock (False) the interface selection when writing.
        - read: Boolean indicating whether to read (True) or write (False) the interface selection lock status.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating the current lock status if reading.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 61  # Parameter number for IntSelLckd

        if read:
            # Read the current interface lock status
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for IntSelLckd read command")
            return bool(int(rdata))
        else:
            # Write the interface lock status
            if lock is None:
                raise ValueError("Lock value must be provided for write operation.")
            data = "1" if lock else "0"
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for IntSelLckd write command")


    @classmethod
    def cfg_di1(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get configuration for input DI1.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 7) specifying the configuration for input DI1 when writing:
            - 0: Deactivated
            - 1: Enable venting
            - 2: Heating
            - 3: Sealing gas
            - 4: Run-up time monitoring
            - 5: Rotation speed mode
            - 7: Enable HV sensor
        - read: Boolean indicating whether to read (True) or write (False) the DI1 configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 62  # Parameter number for Cfg DI1

        if read:
            # Read the current configuration of DI1
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg DI1 read command")
            return int(rdata)
        else:
            # Write the DI1 configuration
            if config_value is None or not (0 <= config_value <= 7):
                raise ValueError("Config value out of range. Must be between 0 and 7.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg DI1 write command")


    @classmethod
    def cfg_di2(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get configuration for input DI2.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 7) specifying the configuration for input DI2 when writing.
        - read: Boolean indicating whether to read (True) or write (False) the DI2 configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 63  # Parameter number for Cfg DI2

        if read:
            # Read the current configuration of DI2
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg DI2 read command")
            return int(rdata)
        else:
            # Write the DI2 configuration
            if config_value is None or not (0 <= config_value <= 7):
                raise ValueError("Config value out of range. Must be between 0 and 7.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg DI2 write command")


    @classmethod
    def cfg_di3(cls, s, addr, config_value=None, read=False, valid_char_filter=None):
        """
        Set or get configuration for input DI3.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - config_value: Integer (0 to 7) specifying the configuration for input DI3 when writing.
        - read: Boolean indicating whether to read (True) or write (False) the DI3 configuration.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer value of the current configuration if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if config_value is out of range when writing.
        """
        param_num = 64  # Parameter number for Cfg DI3

        if read:
            # Read the current configuration of DI3
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Cfg DI3 read command")
            return int(rdata)
        else:
            # Write the DI3 configuration
            if config_value is None or not (0 <= config_value <= 7):
                raise ValueError("Config value out of range. Must be between 0 and 7.")
            data = "{:01d}".format(config_value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Cfg DI3 write command")

    @classmethod
    def get_remote_priority(cls, s, addr, valid_char_filter=None):
        """
        Get the remote priority status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating if remote priority is enabled.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 300  # Parameter number for RemotePri
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for remote priority request")
        return bool(int(rdata))


    @classmethod
    def get_rotation_speed_switchpoint(cls, s, addr, valid_char_filter=None):
        """
        Get the rotation speed switchpoint status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating if rotation speed switchpoint is reached.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 302  # Parameter number for SpdSwPtAtt
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for rotation speed switchpoint request")
        return bool(int(rdata))


    @classmethod
    def get_error_code(cls, s, addr, valid_char_filter=None):
        """
        Get the current error code.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the current error code.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 303  # Parameter number for Error code
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code request")
        return int(rdata)


    @classmethod
    def get_overtemp_electronics(cls, s, addr, valid_char_filter=None):
        """
        Get the overtemperature status of the electronics.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating if the electronics are overheating.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 304  # Parameter number for OvTempElec
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for overtemperature electronics request")
        return bool(int(rdata))

    @classmethod
    def get_overtemp_pump(cls, s, addr, valid_char_filter=None):
        """
        Get the overtemperature status of the vacuum pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating if the vacuum pump is overheating.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 305  # Parameter number for OvTempPump
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for overtemperature pump request")
        return bool(int(rdata))


    @classmethod
    def get_set_speed_attained(cls, s, addr, valid_char_filter=None):
        """
        Get the target speed attained status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating if the target speed has been reached.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 306  # Parameter number for SetSpdAtt
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for set speed attained request")
        return bool(int(rdata))


    @classmethod
    def get_pump_accelerating(cls, s, addr, valid_char_filter=None):
        """
        Get the vacuum pump accelerating status.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Boolean indicating if the vacuum pump is accelerating.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 307  # Parameter number for PumpAccel
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for pump accelerating request")
        return bool(int(rdata))


    @classmethod
    def get_set_rotation_speed(cls, s, addr, valid_char_filter=None):
        """
        Get the set rotation speed of the pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the set rotation speed (Hz).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 308  # Parameter number for SetRotSpd
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for set rotation speed request")
        return int(rdata)


    @classmethod
    def get_actual_rotation_speed(cls, s, addr, valid_char_filter=None):
        """
        Get the actual rotation speed of the pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the actual rotation speed (Hz).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 309  # Parameter number for ActualSpd
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for actual rotation speed request")
        return int(rdata)


    @classmethod
    def get_drive_current(cls, s, addr, valid_char_filter=None):
        """
        Get the current drive current value.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Float representing the drive current (A).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 310  # Parameter number for DrvCurrent
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for drive current request")
        return float(rdata) / 100  # Adjust scaling if needed

    @classmethod
    def get_operating_hours(cls, s, addr, valid_char_filter=None):
        """
        Get the operating hours of the vacuum pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the operating hours.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 311  # Parameter number for OpHrsPump
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for operating hours request")
        return int(rdata)

    @classmethod
    def get_firmware_version(cls, s, addr, valid_char_filter=None):
        """
        Get the firmware version of the electronic drive unit.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - String representing the firmware version.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 312  # Parameter number for Fw version
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for firmware version request")
        return rdata


    @classmethod
    def get_drive_voltage(cls, s, addr, valid_char_filter=None):
        """
        Get the current drive voltage value.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Float representing the drive voltage (V).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 313  # Parameter number for DrvVoltage
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for drive voltage request")
        return float(rdata) / 100  # Adjust scaling if needed

    @classmethod
    def get_operating_hours_electronics(cls, s, addr, valid_char_filter=None):
        """
        Get the operating hours of the electronic drive unit.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the operating hours of the electronic drive unit.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 314  # Parameter number for OpHrsElec
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for operating hours electronics request")
        return int(rdata)


    @classmethod
    def get_nominal_speed(cls, s, addr, valid_char_filter=None):
        """
        Get the nominal rotational speed of the pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the nominal rotational speed (Hz).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 315  # Parameter number for Nominal Spd
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for nominal speed request")
        return int(rdata)


    @classmethod
    def get_drive_power(cls, s, addr, valid_char_filter=None):
        """
        Get the drive power of the pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Float representing the drive power (W).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 316  # Parameter number for DrvPower
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for drive power request")
        return float(rdata) / 100  # Adjust scaling if needed


    @classmethod
    def get_pump_cycles(cls, s, addr, valid_char_filter=None):
        """
        Get the number of pump cycles.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the number of pump cycles.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 319  # Parameter number for PumpCycles
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for pump cycles request")
        return int(rdata)


    @classmethod
    def get_temperature_electronics(cls, s, addr, valid_char_filter=None):
        """
        Get the temperature of the pump electronics.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Float representing the temperature of the electronics (°C).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 326  # Parameter number for TempElec
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for temperature electronics request")
        return float(rdata) / 10  # Adjust scaling if needed


    @classmethod
    def get_temperature_pump_bottom(cls, s, addr, valid_char_filter=None):
        """
        Get the temperature of the pump bottom part.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Float representing the temperature of the pump bottom part (°C).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 330  # Parameter number for TempPmpBot
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for temperature pump bottom part request")
        return float(rdata) / 10  # Adjust scaling if needed

    @classmethod
    def get_accel_decel(cls, s, addr, valid_char_filter=None):
        """
        Get the acceleration/deceleration rate of the pump.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Float representing the acceleration/deceleration rate (rpm/s).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 336  # Parameter number for AccelDecel
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for acceleration/deceleration request")
        return float(rdata) / 10  # Adjust scaling if needed


    @classmethod
    def get_sealing_gas_flow(cls, s, addr, valid_char_filter=None):
        """
        Get the sealing gas flow rate.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Float representing the sealing gas flow rate (sccm).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 337  # Parameter number for SealGasFlw
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for sealing gas flow request")
        return float(rdata) / 10  # Adjust scaling if needed


    @classmethod
    def get_temperature_bearing(cls, s, addr, valid_char_filter=None):
        """
        Get the temperature of the bearing.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Float representing the temperature of the bearing (°C).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 342  # Parameter number for TempBearng
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for temperature bearing request")
        return float(rdata) / 10  # Adjust scaling if needed


    @classmethod
    def get_temperature_motor(cls, s, addr, valid_char_filter=None):
        """
        Get the temperature of the motor.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Float representing the temperature of the motor (°C).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 346  # Parameter number for TempMotor
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for temperature motor request")
        return float(rdata) / 10  # Adjust scaling if needed


    @classmethod
    def get_electronics_name(cls, s, addr, valid_char_filter=None):
        """
        Get the name of the electronic drive unit.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - String representing the name of the electronic drive unit.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 349  # Parameter number for ElecName
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for electronics name request")
        return rdata


    @classmethod
    def get_hardware_version(cls, s, addr, valid_char_filter=None):
        """
        Get the hardware version of the electronic drive unit.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - String representing the hardware version.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 354  # Parameter number for HW Version
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for hardware version request")
        return rdata

    @classmethod
    def get_error_code_history_1(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 1.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 1.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 360  # Parameter number for ErrHist1
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 1 request")
        return int(rdata)


    @classmethod
    def get_error_code_history_2(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 2.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 2.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 361  # Parameter number for ErrHist2
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 2 request")
        return int(rdata)


    @classmethod
    def get_error_code_history_3(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 3.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 3.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 362  # Parameter number for ErrHist3
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 3 request")
        return int(rdata)


    @classmethod
    def get_error_code_history_4(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 4.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 4.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 363  # Parameter number for ErrHist4
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 4 request")
        return int(rdata)


    @classmethod
    def get_error_code_history_5(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 5.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 5.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 364  # Parameter number for ErrHist5
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 5 request")
        return int(rdata)


    @classmethod
    def get_error_code_history_6(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 6.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 6.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 365  # Parameter number for ErrHist6
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 6 request")
        return int(rdata)


    @classmethod
    def get_error_code_history_7(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 7.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 7.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 366  # Parameter number for ErrHist7
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 7 request")
        return int(rdata)


    @classmethod
    def get_error_code_history_8(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 8.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 8.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 367  # Parameter number for ErrHist8
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 8 request")
        return int(rdata)


    @classmethod
    def get_error_code_history_9(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 9.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 9.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 368  # Parameter number for ErrHist9
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 9 request")
        return int(rdata)


    @classmethod
    def get_error_code_history_10(cls, s, addr, valid_char_filter=None):
        """
        Get error code history item 10.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing error code history item 10.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 369  # Parameter number for ErrHist10
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for error code history item 10 request")
        return int(rdata)

    @classmethod
    def get_set_rotation_speed_rpm(cls, s, addr, valid_char_filter=None):
        """
        Get the set rotation speed of the pump in rpm.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the set rotation speed (rpm).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 397  # Parameter number for SetRotSpd (rpm)
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for set rotation speed (rpm) request")
        return int(rdata)


    @classmethod
    def get_actual_rotation_speed_rpm(cls, s, addr, valid_char_filter=None):
        """
        Get the actual rotation speed of the pump in rpm.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the actual rotation speed (rpm).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 398  # Parameter number for ActualSpd (rpm)
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for actual rotation speed (rpm) request")
        return int(rdata)


    @classmethod
    def get_nominal_rotation_speed_rpm(cls, s, addr, valid_char_filter=None):
        """
        Get the nominal rotation speed of the pump in rpm.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the nominal rotation speed (rpm).

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 399  # Parameter number for NominalSpd (rpm)
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for nominal rotation speed (rpm) request")
        return int(rdata)

    # Set Value settings 
    @classmethod
    def get_sensor_1_name(cls, s, addr, valid_char_filter=None):
        """
        Get the name of sensor 1.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - String representing the name of sensor 1.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 739  # Parameter number for PrsSn1Name
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for sensor 1 name request")
        return rdata


    @classmethod
    def get_sensor_2_name(cls, s, addr, valid_char_filter=None):
        """
        Get the name of sensor 2.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - String representing the name of sensor 2.

        Raises:
        - ValueError if the response from the pump is invalid.
        """
        param_num = 749  # Parameter number for PrsSn2Name
        cls._send_data_request(s, addr, param_num)
        raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
        if raddr != addr or rw != 0 or rparam_num != param_num:
            raise ValueError("Invalid response from pump for sensor 2 name request")
        return rdata

    @classmethod
    def run_up_time(cls, s, addr, value=None, read=False, valid_char_filter=None):
        """
        Set or get the set value run-up time.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - value: Integer (1 to 120) specifying the run-up time in minutes when writing.
        - read: Boolean indicating whether to read (True) or write (False) the run-up time.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the run-up time if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if value is out of range when writing.
        """
        param_num = 700  # Parameter number for Run-up Time

        if read:
            # Read the current run-up time
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Run-up Time read command")
            return int(rdata)
        else:
            # Write the run-up time
            if value is None or not (1 <= value <= 120):
                raise ValueError("Run-up time value out of range. Must be between 1 and 120.")
            data = "{:03d}".format(value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Run-up Time write command")


    @classmethod
    def rotation_speed_switch_point_1(cls, s, addr, value=None, read=False, valid_char_filter=None):
        """
        Set or get rotation speed switch point 1.

        Parameters:
        - s: Serial connection to the pump.
        - addr: Pump address.
        - value: Integer (50 to 97) specifying the switch point in Hz when writing.
        - read: Boolean indicating whether to read (True) or write (False) the switch point.
        - valid_char_filter: Optional filter to handle invalid characters in response.

        Returns:
        - Integer representing the rotation speed switch point 1 if reading.

        Raises:
        - ValueError if the response from the pump is invalid or if value is out of range when writing.
        """
        param_num = 701  # Parameter number for Rotation Speed Switch Point 1

        if read:
            # Read the current switch point
            cls._send_data_request(s, addr, param_num)
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 0 or rparam_num != param_num:
                raise ValueError("Invalid response from pump for Rotation Speed Switch Point 1 read command")
            return int(rdata)
        else:
            # Write the switch point
            if value is None or not (50 <= value <= 97):
                raise ValueError("Switch point value out of range. Must be between 50 and 97.")
            data = "{:03d}".format(value)
            cls._send_control_command(s, addr, param_num, data)

            # Read and validate response
            raddr, rw, rparam_num, rdata = cls._read_pump_response(s, valid_char_filter)
            if raddr != addr or rw != 1 or rparam_num != param_num or rdata != data:
                raise ValueError("Invalid response from pump for Rotation Speed Switch Point 1 write command")
