from enum import Enum


class InvalidCharError(Exception):
    """Custom exception for invalid characters."""
    pass


class PfeifferVacuumProtocol:
    _filter_invalid_char = False

    @classmethod
    def enable_valid_char_filter(cls):
        """Globally enable the filter to ignore invalid characters."""
        cls._filter_invalid_char = True

    @classmethod
    def disable_valid_char_filter(cls):
        """Globally disable the filter to ignore invalid characters."""
        cls._filter_invalid_char = False

    class ErrorCode(Enum):
        """Error states for vacuum gauges."""
        NO_ERROR = 1
        FILAMENT_1_DEFECTIVE_IN_AUTO = 2
        DEFECTIVE_GAUGE = 3
        DEFECTIVE_MEMORY = 4
        FILAMENT_1_DEFECTIVE = 5
        FILAMENT_2_DEFECTIVE = 6
        BOTH_FILAMENTS_DEFECTIVE = 7

    @staticmethod
    def _send_data_request(s, addr, param_num):
        """Send a data request to the gauge."""
        c = "{:03d}00{:03d}02=?".format(addr, param_num)
        c += "{:03d}\r".format(sum([ord(x) for x in c]) % 256)
        s.write(c.encode())

    @staticmethod
    def _send_control_command(s, addr, param_num, data_str):
        """Send a control command to the gauge."""
        c = "{:03d}10{:03d}{:02d}{:s}".format(addr, param_num, len(data_str), data_str)
        c += "{:03d}\r".format(sum([ord(x) for x in c]) % 256)
        return s.write(c.encode())

    @classmethod
    def _read_gauge_response(cls, s, valid_char_filter=None):
        """Read the gauge response."""
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
                    "`PfeifferVacuumProtocol.enable_valid_char_filter()`."
                )

            if c == b"\r":
                break

        if len(r) < 14:
            raise ValueError("gauge response too short to be valid")
        if r[-1] != "\r":
            raise ValueError("gauge response incorrectly terminated")
        if int(r[-4:-1]) != (sum([ord(x) for x in r[:-4]]) % 256):
            raise ValueError("invalid checksum in gauge response")

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
        """Read the error code from the gauge."""
        cls._send_data_request(s, addr, 303)
        raddr, rw, rparam_num, rdata = cls._read_gauge_response(s, valid_char_filter=valid_char_filter)

        if raddr != addr or rw != 1 or rparam_num != 303:
            raise ValueError("invalid response from gauge")

        if rdata == "000000":
            return cls.ErrorCode.NO_ERROR
        elif rdata == "Wrn001":
            return cls.ErrorCode.FILAMENT_1_DEFECTIVE_IN_AUTO
        elif rdata == "Err001":
            return cls.ErrorCode.DEFECTIVE_GAUGE
        elif rdata == "Err002":
            return cls.ErrorCode.DEFECTIVE_MEMORY
        elif rdata == "Err003":
            return cls.ErrorCode.FILAMENT_1_DEFECTIVE
        elif rdata == "Err004":
            return cls.ErrorCode.FILAMENT_2_DEFECTIVE
        elif rdata == "Err005":
            return cls.ErrorCode.BOTH_FILAMENTS_DEFECTIVE
        else:
            raise ValueError("unexpected error code from gauge")

    @classmethod
    def read_software_version(cls, s, addr, valid_char_filter=None):
        """Read the firmware version of the gauge."""
        cls._send_data_request(s, addr, 312)
        raddr, rw, rparam_num, rdata = cls._read_gauge_response(s, valid_char_filter=valid_char_filter)

        if raddr != addr or rw != 1 or rparam_num != 312:
            raise ValueError("invalid response from gauge")

        return int(rdata[0:2]), int(rdata[2:4]), int(rdata[4:])

    @classmethod
    def read_gauge_type(cls, s, addr, valid_char_filter=None):
        """Read the gauge type."""
        cls._send_data_request(s, addr, 349)
        raddr, rw, rparam_num, rdata = cls._read_gauge_response(s, valid_char_filter=valid_char_filter)

        if raddr != addr or rw != 1 or rparam_num != 349:
            raise ValueError("invalid response from gauge")

        gauge_types = {
            "    A1": "CPT 200",
            "    A2": "RPT 200",
            "    A3": "PPT 200",
            "    A4": "HPT 200",
            "    A5": "MPT 200",
        }

        return gauge_types.get(rdata, "unrecognized gauge type")

    @classmethod
    def read_pressure(cls, s, addr, valid_char_filter=None):
        """Read the pressure from the gauge in bars."""
        cls._send_data_request(s, addr, 740)
        raddr, rw, rparam_num, rdata = cls._read_gauge_response(s, valid_char_filter=valid_char_filter)

        if raddr != addr or rw != 1 or rparam_num != 740:
            raise ValueError("invalid response from gauge")

        mantissa = int(rdata[:4])
        exponent = int(rdata[4:])
        return float(mantissa * 10 ** (exponent - 23))

    @classmethod
    def write_pressure_setpoint(cls, s, addr, val, valid_char_filter=None):
        """Set the vacuum setpoint on the gauge."""
        data = "{:03d}".format(val)
        cls._send_control_command(s, addr, 741, data)
        raddr, rw, rparam_num, rdata = cls._read_gauge_response(s, valid_char_filter=valid_char_filter)

        if raddr != addr or rw != 1 or rparam_num != 741:
            raise ValueError("invalid response from gauge")
        if rdata != data:
            raise ValueError("invalid acknowledgment from gauge")

    @classmethod
    def read_correction_value(cls, s, addr, valid_char_filter=None):
        """Read the current Pirani correction value used to adjust pressure measurements."""
        cls._send_data_request(s, addr, 742)
        raddr, rw, rparam_num, rdata = cls._read_gauge_response(s, valid_char_filter=valid_char_filter)

        if raddr != addr or rw != 1 or rparam_num != 742:
            raise ValueError("invalid response from gauge")

        return float(rdata) / 100

    @classmethod
    def write_correction_value(cls, s, addr, val, valid_char_filter=None):
        """Set the Pirani correction value on the gauge."""
        # Check if the correction factor is within the valid range (0.2 to 0.8)
        if not (0.2 <= val <= 8.0):
            raise ValueError("Correction factor out of range. Must be between 0.2 and 0.8.")
        
        # Convert the correction value to an integer and format it as a 6-digit string
        data = "{:06d}".format(int(val * 100))

        cls._send_control_command(s, addr, 742, data)
       
        # Read the gauge's response
        raddr, rw, rparam_num, rdata = cls._read_gauge_response(s, valid_char_filter=valid_char_filter)

        if raddr != addr or rw != 1 or rparam_num != 742:
            raise ValueError("invalid response from gauge")
        if rdata != data:
            raise ValueError("invalid acknowledgment from gauge")
