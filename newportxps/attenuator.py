import serial
import time

class AttenuatorControls:
    """
    A class to control the laser attenuator via an ATmega328p microcontroller.
    A pythonized version of preexisting Labview Attenuator VI code.
    """

    def __init__(self, port='COM3', baudrate=9600, timeout=1):
        """
        Initialize the serial connection to the microcontroller.

        :param port: The COM port to use for the serial connection.
        :param baudrate: The baud rate for the serial communication.
        :param timeout: The timeout for the serial communication.
        """
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

    def send_command(self, command):
        """
        Send a command to the microcontroller and read the response.

        :param command: The command string to send.
        """
        self.ser.write(command.encode())
        response = self.ser.readline().decode()
        print("Response:", response)
        time.sleep(0.01)  # Slight delay to ensure command is processed

    def rotate_to_angle(self, angle):
        """
        Rotate to a specified angle.

        :param angle: The angle to rotate to.
        """
        #Convert possible float angle to nearest integer angle 
        angle_int = round(angle)        

        command = f',{angle_int}\n'
        self.send_command(command)

    def clear_laser(self):
        """
        Clear the laser.
        """
        command = 'f\n'
        self.send_command(command)

    def block_laser(self):
        """
        Block the laser.
        """
        command = 'g\n'
        self.send_command(command)

    def home_attenuator(self):
        """
        Home the attenuator.
        """
        command = 'o\n'
        self.send_command(command)

    def set_rotation_speed(self, speed):
        """
        Set the rotation speed.

        :param speed: The rotation speed in degrees per second.
        """
        # Convert possible float speed to nearest integer speed
        speed_int = round(speed)
        command = f'#{speed_int}\n'
        self.send_command(command)

    def close(self):
        """
        Close the serial connection.
        """
        self.ser.close()

def main():
    # Create an instance of the AttenuatorControls class
    attenuator = AttenuatorControls()

    
    angle = 123
    speed = 123

    # Execute the sequence of operations
    attenuator.rotate_to_angle(angle)
    attenuator.clear_laser()
    attenuator.block_laser()
    attenuator.home_attenuator()
    attenuator.set_rotation_speed(speed)

    # Close the serial connection
    attenuator.close()

if __name__ == "__main__":
    main()
