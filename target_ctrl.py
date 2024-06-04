import serial
import time

class  TargetControls:
    """
    A class to with functions to control multi-target carousel controller for Neccera PLD System
    A pythonized version of preexisting Labview Multi-Target-Carousel-Controler VI code.
    """

    def __init__(self, port='COM2', baudrate=9600, timeout=1):
        """
        Initialize the serial connection to the multi-target carousel controller.

        :param port: The COM port to use for the serial connection.
        :param baudrate: The baud rate for the serial communication.
        :param timeout: The timeout for the serial communication.
        """
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.current_target = 0

    def send_command(self, command):
        """
        Send a command to the controller and read the response.

        :param command: The command string to send.
        """
        self.ser.write(command.encode())
        # response = self.ser.readline().decode()
        # print("Response:", response)
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

    def step_raster_cw(self):
        """
        Step the carousel in the clockwise direction.
        """
        command = '>\n'
        self.send_command(command)

    def step_raster_ccw(self):
        """
        Step the carousel in the counter-clockwise direction.
        """
        command = '<\n'
        self.send_command(command)

    def home_raster(self):
        """
        Home the carousel.
        """
        command = 'o\n'
        self.send_command(command)

    def set_raster_speed(self,speed):
        """
        Set the rotation speed.

        :param speed: The rotation speed in degrees per second.
        
        """
        # Convert possible float speed to nearest integer speed
        speed_int = round(speed)
        command = f"'{speed_int}\n"
        self.send_command(command)

    def start_raster(self, raster_angle):
        """
        Begin rastering. Enter raster angle(deg)
        """
        raster_angle_int = round(raster_angle)
        command = f"s{raster_angle}\n"
        self.send_command(command)

    def stop_raster(self):
        """
        Stop rastering.
        """
        command = 'h\n'
        self.send_command(command)

    def start_rotate(self):
        """
        Start rotating the carousel.
        """
        command = 'g\n'
        self.send_command(command)

    def stop_rotation(self):
        """
        Home the attenuator.
        """
        command = 'r\n'
        self.send_command(command)

    def set_rotation_speed(self, speed):
        """
        Set the rotation speed (deg/s).
        
        """
        # Convert possible float speed to nearest integer speed
        speed_int = round(speed)
        command = f'#{speed_int}\n'
        self.send_command(command)

    def move_to_target(self, target):
        """
        Move to a specified target.
        Options are 0(Default,) 1, 2, 3, 4, 5, 6.
        send serial command to move to target position.
        """
        if target == 0:
            target_serial = 0
        elif target == 1:
            target_serial = 14
        elif target == 2:
            target_serial = 74
        elif target == 3:
            target_serial = 134
        elif target == 4:
            target_serial = 194
        elif target == 5:
            target_serial = 254
        elif target == 6:
            target_serial = 314
        else:
            print("Invalid target. Please enter a valid target.")
            return

        self.current_target = target 
        command = f"t{target_serial}\n"
        self.send_command(command)

    def close(self):
        """
        Close the serial connection.
        """
        self.ser.close()

def main():
    # Create an instance of the AttenuatorControls class
    carousel = TargetControls()

    
    angle = 45
    
    speed = 5

    # Execute the sequence of operations
    carousel.step_raster_cw()
    carousel.step_raster_ccw()
    carousel.home_raster()
    carousel.set_raster_speed(speed)

    carousel.start_raster(45)
    carousel.stop_raster()

    carousel.start_rotate()
    carousel.stop_rotation()
    carousel.rotate_to_angle(angle)
    carousel.set_rotation_speed(speed)
    carousel.move_to_target(1)

    
    

    # Close the serial connection
    carousel.close()

if __name__ == "__main__":
    main()
