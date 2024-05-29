import serial
import time

def test_serial_communication(port='COM3', baudrate=9600, timeout=1):
    try:
        # Initialize the serial connection
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Connected to {port} at {baudrate} baud.")
        
        # Wait for the connection to establish
        time.sleep(2)
        
        # Send a test command
        test_command = b'PING\n'
        ser.write(test_command)
        print(f"Sent: {test_command.decode().strip()}")
        
        # Wait for a response
        time.sleep(1)
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            print(f"Received: {response}")
        else:
            print("No response received.")
        
        # Close the serial connection
        ser.close()
        print("Connection closed.")
    
    except Exception as e:
        print(f"Error: {e}")

# Run the test
test_serial_communication()
