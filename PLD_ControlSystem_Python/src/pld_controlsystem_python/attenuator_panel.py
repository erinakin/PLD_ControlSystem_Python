import panel as pn
import serial
import time
from serial.tools import list_ports

class AttenuatorControls:
    """
    A class to control the laser attenuator via an ATmega328p microcontroller.
    A pythonized version of preexisting Labview Attenuator VI code.
    """

    def __init__(self, port=None, baudrate=9600, timeout=1):
        """
        Initialize the serial connection to the microcontroller.

        :param port: The COM port to use for the serial connection.
        :param baudrate: The baud rate for the serial communication.
        :param timeout: The timeout for the serial communication.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout    
        self.rotationSpeed = 0
        self.ser = None
        # Try to open the serial connection with retry logic
        

    def open_connection(self, retries=3, delay=1):
        """
        Attempt to open the serial connection with the specified number of retries.

        :param retries: Number of times to retry opening the connection if it fails.
        :param delay: Delay between retries in seconds.
        """

        for attempt in range(retries):
            try:
                if self.ser and self.ser.is_open:
                    self.ser.close()
                self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                connection_status.value = True # Update connection status indicator 
                connection_text.object = "<b style='color': '>Connected</b>"
                print(f"Serial connection opened on {self.port} with baudrate {self.baudrate} and timeout {self.timeout}.")
                break
            except serial.SerialException as e:
                connection_status.value = False # Update connection status indicator
                connection_text.object = "**Not Connected**"
                print(f"Attempt {attempt+1} to open port {self.port} failed: {e}")
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Failed to open serial connection. Exiting...")
                    raise e # Re-raise the exception if all retries fail
                

    def send_command(self, command):
        """
        Send a command to the microcontroller and read the response.

        :param command: The command string to send.
        """
        self.ser.write(command.encode())
        time.sleep(0.01)
        command_status.value = True # Update status indicator
        command_text.objct = "**Command Sent**"

    def rotate_to_angle(self, angle):
        """
        Rotate to a specified angle.

        :param angle: The angle to rotate to.
        """
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
        Default speed is 5 degrees per second 
        Max speed = 8 deg/second 
        Min speed = 1 deg/second
        """
        rotationSpeed_int = round(speed)
        command = f'#{rotationSpeed_int}\n'
        self.send_command(command)
        self.rotationSpeed = rotationSpeed_int

    def get_rotation_speed(self):
        """
        Get the rotation speed.
        """
        return self.rotationSpeed  

    def close(self):
        """
        Close the serial connection.

        """
        if self.ser is not None:
            self.ser.close()
            connection_status.value = False # Update connection status indicator
            connection_text.objct = "**Not Connected**"
            print(f"Serial connection on {self.port} closed.")


# Initialize Panel
pn.extension(template='fast')

# UI components
available_ports = [port.device for port in list_ports.comports()]
com_port = pn.widgets.Select(name='COM Port', options=available_ports, value=available_ports[0] if available_ports else 'COM5')
start_button = pn.widgets.Button(name='Start', button_type='success')
home_button = pn.widgets.Button(name='Home Attenuator', button_type='primary')
angle_input = pn.widgets.FloatInput(name='Angle', value=0, step=1)
rotate_button = pn.widgets.Button(name='Rotate To', button_type='primary')
speed_input = pn.widgets.FloatInput(name='Set Rotation Speed (deg/sec)', value=5, step=1)
set_speed_button = pn.widgets.Button(name='Set Speed', button_type='primary')
clear_laser_button = pn.widgets.Button(name='Clear Laser', button_type='default')
block_laser_button = pn.widgets.Button(name='Block Laser', button_type='default')
stop_button = pn.widgets.Button(name='STOP', button_type='danger')

# Status Indicators
connection_status = pn.indicators.BooleanStatus(value=False, color='success')
connection_text = pn.pane.Markdown("<b style='color: red;'>Not Connected</b>")
command_status = pn.indicators.BooleanStatus(value=False, color='success')
command_text = pn.pane.Markdown("<b style='color: red;'>Command Not Sent</b>")


# Initialize the Attenuator Controls
attenuator = AttenuatorControls()

# Define actions
def on_start_click(event):
    attenuator.port = com_port.value
    attenuator.open_connection()
    print("Attenuator connected.")

def on_home_click(event):
    attenuator.home_attenuator()
    print("Attenuator Homed")

def on_rotate_click(event):
    attenuator.rotate_to_angle(angle_input.value)
    print(f"Rotated to {angle_input.value} degrees")

def on_set_speed_click(event):
    attenuator.set_rotation_speed(speed_input.value)
    print(f"Speed set to {speed_input.value} deg/sec")

def on_clear_laser_click(event):
    attenuator.clear_laser()
    print("Laser Cleared")

def on_block_laser_click(event):
    attenuator.block_laser()
    print("Laser Blocked")

def on_stop_click(event):
    attenuator.close()
    print("All Operations Stopped and Serial Connection Closed")

# Link actions to buttons
start_button.on_click(on_start_click)
home_button.on_click(on_home_click)
rotate_button.on_click(on_rotate_click)
set_speed_button.on_click(on_set_speed_click)
clear_laser_button.on_click(on_clear_laser_click)
block_laser_button.on_click(on_block_laser_click)
stop_button.on_click(on_stop_click)

# Tooltip Information using HTML Pane
rotate_tooltip = pn.pane.Markdown("**Rotate To:** Max: 360°, Min: 0°", width=150)
speed_tooltip = pn.pane.Markdown("**Set Speed:** Max: 8°/sec, Min: 1°/sec", width=150)

# Components Layout
attenuator_controls = pn.Column(
    pn.pane.Markdown("### Laser Attenuator Control System"),
    pn.Row(pn.pane.Markdown("**COM Port**"), com_port),
    pn.Row(start_button, connection_status),
    home_button,
    pn.Row(angle_input, rotate_button),
    rotate_tooltip,
    pn.Row(speed_input, set_speed_button),
    speed_tooltip,
    pn.Row(clear_laser_button, block_laser_button),
    pn.Row(stop_button, command_status),
    width=400
)

# Serve the panel
pn.serve(attenuator_controls, show=True)

# If running in Jupyter, use this:
attenuator_controls.show()