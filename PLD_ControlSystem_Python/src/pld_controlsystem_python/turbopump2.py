import serial
import struct

# Serial port configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Update as needed
BAUDRATE = 9600
TIMEOUT = 1

# Frame structure constants
START_BYTE = 0x02
STOP_BYTE = 0x03

# Example drive current query parameters
DEVICE_ADDRESS = 0x00  # Replace with the actual device address if required
COMMAND_QUERY = 0x06  # Assuming 0x06 represents "Query" based on protocol
DRIVE_CURRENT_CODE = 0x20  # Replace with actual code for "Drive Current"


def calculate_checksum(frame):
    """Calculate checksum for a given frame."""
    return sum(frame) & 0xFF


def build_query_frame():
    """Build the telegram frame for querying drive current."""
    frame = [
        START_BYTE,
        DEVICE_ADDRESS,
        COMMAND_QUERY,
        DRIVE_CURRENT_CODE,
        STOP_BYTE
    ]
    checksum = calculate_checksum(frame)
    frame.append(checksum)
    return bytearray(frame)


def parse_response(response):
    """Parse the response to extract the drive current."""
    if len(response) < 6:
        raise ValueError("Incomplete response received")

    # Assuming the drive current is encoded in bytes 3 and 4
    data_bytes = response[3:5]
    drive_current = struct.unpack('>H', bytes(data_bytes))[0]  # Big-endian 2-byte integer
    return drive_current / 10.0  # Example: Convert to correct units if necessary


def query_drive_current():
    """Query the drive current from the turbopump."""
    frame = build_query_frame()

    with serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=TIMEOUT) as ser:
        ser.write(frame)
        response = ser.read(ser.in_waiting or 256)  # Adjust buffer size as needed

    if not response:
        raise TimeoutError("No response received from the turbopump")

    if response[0] != START_BYTE or response[-2] != STOP_BYTE:
        raise ValueError("Invalid response frame received")

    checksum = calculate_checksum(response[:-1])
    if checksum != response[-1]:
        raise ValueError("Checksum mismatch in response")

    return parse_response(response)


if __name__ == "__main__":
    try:
        drive_current = query_drive_current()
        print(f"Drive Current: {drive_current} A")
    except Exception as e:
        print(f"Error: {e}")
