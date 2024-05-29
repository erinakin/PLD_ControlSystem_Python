import serial
import time

class AttenuatorControls:
    """
    A class to control the attenuator via serial commands to an Arduino.

    Attributes:
        ser (serial.Serial): Serial communication object.
        steps_rotate_per_rev (int): Steps required for one revolution.
        max_angle (int): Maximum allowed angle for attenuator.
        steps_per_deg (int): Steps per degree.
        steps_max_angle (int): Steps to maximum angle.
        curr_angle (float): Current angle.
        dest_angle (float): Destination angle.
        angle_rotate (float): Degrees to rotate to reach destination angle.
        steps_rotate (int): Steps to rotate to reach destination.
        calibration_counter (int): Calibration counter.
        command (str): Command from user.
        delay (int): Delay in seconds to achieve desired angular velocity.
    """

    def __init__(self, port='COM3', baudrate=9600, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.steps_rotate_per_rev = 1273808
        self.max_angle = 90
        self.steps_per_deg = 3538
        self.steps_max_angle = self.max_angle * self.steps_per_deg
        self.curr_angle = 0
        self.dest_angle = -1
        self.angle_rotate = -1
        self.steps_rotate = 0
        self.calibration_counter = 0
        self.command = ''
        self.delay = 0
        self.CW = True
        self.CCW = False
        self.MIN_SPEED = 1
        self.MAX_SPEED = 8

    def set_rotation_speed(self, new_rotation_speed):
        """
        Calculate the delay in seconds required to achieve the desired rotation speed.

        Args:
            new_rotation_speed (float): The new desired rotation speed in degrees per second.

        Returns:
            int: The delay in seconds to achieve the desired speed or -1 if the speed is invalid.
        """
        if self.MIN_SPEED <= new_rotation_speed <= self.MAX_SPEED:
            return int(1 / (self.steps_per_deg * new_rotation_speed))
        else:
            print(f"Error: Speed must be between {self.MIN_SPEED} and {self.MAX_SPEED} degrees per second.")
            return -1

    def set_direction(self, direction):
        """
        Send a command to the Arduino to set the rotation direction.

        Args:
            direction (bool): Direction to set (CW for clockwise, CCW for counter-clockwise).
        """
        if direction == self.CW:
            self.ser.write(b'DIR HIGH\n')
        else:
            self.ser.write(b'DIR LOW\n')

    def block_laser(self):
        """
        Send a command to block the laser path.
        """
        self.ser.write(b'LASER_BLOCK LOW\n')

    def clear_laser(self):
        """
        Send a command to clear the laser path.
        """
        self.ser.write(b'LASER_BLOCK HIGH\n')

    def step(self):
        """
        Perform a single step by sending the appropriate commands to the Arduino,
        then wait for the specified delay.
        """
        self.ser.write(b'STEP HIGH\n')
        self.ser.write(b'STEP LOW\n')
        # Time in seconds
        time.sleep(self.delay)

    def setup(self):
        """
        Initialize the Arduino by sending the INIT command and set the initial rotation speed.
        """
        self.ser.write(b'INIT\n')
        self.delay = self.set_rotation_speed(5)
        if self.delay == -1:
            self.delay = self.set_rotation_speed(self.MIN_SPEED)

    def rotate_to(self, angle):
        """
        Move the attenuator to a specified angle.

        Args:
            angle (float): The destination angle in degrees.
        """
        if 0 <= angle <= self.max_angle:
            self.dest_angle = angle
            if self.dest_angle != self.curr_angle:
                self.angle_rotate = abs(self.curr_angle - self.dest_angle)
                self.set_direction(self.CW if self.curr_angle < self.dest_angle else self.CCW)
                self.curr_angle = self.dest_angle
                self.steps_rotate = int((self.angle_rotate / self.max_angle) * self.steps_max_angle)
                
                self.ser.write(b'\0')
                for _ in range(self.steps_rotate):
                    self.step()


    def home_attenuator(self):
        """
        Move the attenuator to the home position.
        """
        self.set_direction(self.CW)
        while True:
            self.ser.write(b'\0')
            if self.ser.read() == b'1':  # Assuming '1' means HOME_SWITCH is triggered
                self.curr_angle = 0
                break
            self.step()

    def calibrate_attenuator(self):
        """
        Calibrate the attenuator by counting steps to home position.
        """
        self.set_direction(self.CW)
        while True:
            if self.ser.read() == b'1':  # Assuming '1' means HOME_SWITCH is triggered
                self.ser.write(str(self.calibration_counter).encode())
                self.calibration_counter = 0
                break
            self.step()
            self.calibration_counter += 1

if __name__ == "__main__":
    attenuator = AttenuatorControls()
    attenuator.setup()
