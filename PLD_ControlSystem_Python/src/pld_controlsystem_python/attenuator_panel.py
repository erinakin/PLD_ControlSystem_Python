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
        self.laser_state = False    # Laser state is off by default, False = OFF, True = ON
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

    def toggle_laser(self):
        """
        Toggle the laser state.
        """
        if self.laser_state:
            self.block_laser()
            self.laser_state = False
            laser_status_text.object = "<b style='color: red;'>Laser off</b>"
            laser_toggle_button.name = 'Laser OFF'
            laser_toggle_button.button_type = 'danger'

        else:
            self.clear_laser()
            self.laser_state = True
            laser_status_text.object = "<b style='color: green;'>Laser on</b>"
            laser_toggle_button.name = 'Laser ON'
            laser_toggle_button.button_type = 'success'
        
        update_action_message(f"<b>{laser_status_text.object}</b>")


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
            connection_text.object = "**Not Connected**"
            print(f"Serial connection on {self.port} closed.")


# Initialize Panel
pn.extension()

# UI components
available_ports = [port.device for port in list_ports.comports()]
com_port = pn.widgets.Select(name='', options=available_ports, value='COM11' if available_ports else available_ports[0])
start_button = pn.widgets.Button(name='Start', button_type='success')
home_button = pn.widgets.Button(name='Home Attenuator', button_type='primary')
angle_input = pn.widgets.FloatInput(name='', value=0, step=1, start=0, end=360)
rotate_button = pn.widgets.Button(name='Rotate To', button_type='primary')
speed_input = pn.widgets.FloatInput(name='', value=5, step=1, start=1, end=8)
set_speed_button = pn.widgets.Button(name='Set Speed', button_type='primary')
laser_toggle_button = pn.widgets.Button(name='Laser OFF', button_type='primary')
stop_button = pn.widgets.Button(name='STOP', button_type='danger')

# Status Indicators
connection_status = pn.indicators.BooleanStatus(value=False, color='success')
connection_text = pn.pane.Markdown("<b style='color: red;'>Not Connected</b>")
command_status = pn.indicators.BooleanStatus(value=False, color='success')
command_text = pn.pane.Markdown("<b style='color: red;'>Command Not Sent</b>")
laser_status_text = pn.pane.Markdown("<b style='color: red;'>Laser off</b>")
action_message = pn.pane.Markdown("<div id='message-box' style='border: 1px solid black; padding: 10px; border-radius: 5px;'> </div>", width=400)    # Pane to display action messages

# Initialize the Attenuator Controls
attenuator = AttenuatorControls()

# Define actions
def update_action_message(text):
    action_message.object = f"""
    <div id='message-box' style='border: 1px solid black; padding: 20px; border-radius: 5px;'>{text}</div>
    """

def on_start_click(event):
    attenuator.port = com_port.value
    attenuator.open_connection()
    attenuator.laser_state = False
    attenuator.block_laser() # Block the laser/Laser OFF by default at start  
    update_action_message(f"Laser Attenuator connected on {attenuator.port}. Laser is OFF ")

def on_home_click(event):
    attenuator.home_attenuator()
    update_action_message("Laser Attenuator Homed")

def on_rotate_click(event):
    attenuator.rotate_to_angle(angle_input.value)
    update_action_message(f"Rotated to {angle_input.value} degrees")

def on_set_speed_click(event):
    attenuator.set_rotation_speed(speed_input.value)
    update_action_message(f"Speed set to {speed_input.value} deg/sec")

def on_laser_toggle_click(event):
    attenuator.toggle_laser()

def on_stop_click(event):
    attenuator.close()
    update_action_message(f"All Operations Stopped and Serial Connection on {attenuator.port} Closed")

# Link actions to buttons
start_button.on_click(on_start_click)
home_button.on_click(on_home_click)
rotate_button.on_click(on_rotate_click)
set_speed_button.on_click(on_set_speed_click)
laser_toggle_button.on_click(on_laser_toggle_click)
stop_button.on_click(on_stop_click)


# Components Layout
layout = pn.Column(
    pn.pane.Markdown("### Laser Attenuator Control System"),
    pn.Row(pn.pane.Markdown("**COM Port**"), com_port),
    pn.Row(start_button, connection_status),
    home_button,
    pn.Spacer(height=20),
    pn.Row(pn.pane.Markdown("**Angle:** 0° to 360°")),
    pn.Row(angle_input, rotate_button),
    pn.Spacer(height=20),
    pn.Row(pn.pane.Markdown("**Set Rotation Speed (deg/sec):** 1°/sec to 8°/sec")),
    pn.Row(speed_input, set_speed_button),
    pn.Spacer(height=20),
    pn.Row(laser_toggle_button),
    pn.Spacer(height=20),
    action_message,
    pn.Spacer(height=20),
    pn.Row(stop_button),
    width=400
)

# Serve the panel
pn.serve(layout, show=True)   

# If running in Jupyter, use this:
layout