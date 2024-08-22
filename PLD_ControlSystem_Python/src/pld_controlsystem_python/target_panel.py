import panel as pn
from target_ctrl import TargetControls
from serial.tools import list_ports

# Initialize Panel
pn.extension()

# Initialize variables
carousel = None
connection_status = pn.pane.Markdown('', width=300)
action_status = pn.pane.Markdown('', width=300)

# Define GUI components
available_ports = [port.device for port in list_ports.comports()]
com_port_selector = pn.widgets.Select(name='COM Port', options=available_ports, value=available_ports[0] if available_ports else 'COM7')

start_button = pn.widgets.Button(name='Start Connection', button_type='primary')

home_raster_button = pn.widgets.Button(name='Home Raster Motor', button_type='primary')
raster_angle_input = pn.widgets.FloatInput(name='Raster Angle (deg)', value=5, step=0.1)
raster_speed_input = pn.widgets.FloatInput(name='Raster Motor Speed (deg/s)', value=10, step=1)
set_raster_speed_button = pn.widgets.Button(name='Set Raster Speed', button_type='primary')
begin_raster_button = pn.widgets.Button(name='Begin Raster', button_type='primary')
stop_raster_button = pn.widgets.Button(name='Stop Raster', button_type='primary')
step_raster_cw_button = pn.widgets.Button(name='Step Raster CW', button_type='primary')
step_raster_ccw_button = pn.widgets.Button(name='Step Raster CCW', button_type='primary')

current_target_input = pn.widgets.TextInput(name='Current Target', value='0', disabled=True)
target_input = pn.widgets.FloatInput(name='Move to Target', value=1, step=1, start=0, end=6)
move_to_target_button = pn.widgets.Button(name='Move to target', button_type='primary')

self_rotation_angle_input = pn.widgets.FloatInput(name='Self-Rotation Angle', value=0, step=0.1)
rotate_to_button = pn.widgets.Button(name='Rotate To', button_type='primary')

rotation_speed_input = pn.widgets.FloatInput(name='Rotation Speed (deg/s)', value=10, step=1)
set_rotation_speed_button = pn.widgets.Button(name='Set', button_type='primary')
start_rotation_button = pn.widgets.Button(name='Start Rotation', button_type='primary')
stop_rotation_button = pn.widgets.Button(name='Stop Rotation', button_type='primary')

stop_button = pn.widgets.Button(name='STOP', button_type='danger', width=200)

# Define actions
def start_connection(event):
    global carousel
    try:
        carousel = TargetControls(port=com_port_selector.value)
        connection_status.object = "<div style='color:green'><strong>Serial connection established successfully!</strong></div>"
    except Exception as e:
        connection_status.object = f"<div style='color:red'><strong>Error:</strong> {str(e)}</div>"

def update_action_status(message, success=True):
    color = 'green' if success else 'red'
    action_status.object = f"<div style='color:{color}'>{message}</div>"

def home_raster(event):
    if carousel:
        carousel.home_raster()
        update_action_status("Home Raster Motor executed successfully.")

def set_raster_speed(event):
    if carousel:
        speed = raster_speed_input.value
        carousel.set_raster_speed(speed)
        update_action_status("Raster Speed set successfully.")

def begin_raster(event):
    if carousel:
        angle = raster_angle_input.value
        carousel.start_raster(angle)
        update_action_status("Begin Raster executed successfully.")

def stop_raster(event):
    if carousel:
        carousel.stop_raster()
        update_action_status("Stop Raster executed successfully.")

def step_raster_cw(event):
    if carousel:
        carousel.step_raster_cw()
        update_action_status("Step Raster CW executed successfully.")

def step_raster_ccw(event):
    if carousel:
        carousel.step_raster_ccw()
        update_action_status("Step Raster CCW executed successfully.")

def move_to_target(event):
    if carousel:
        target = target_input.value
        carousel.move_to_target(target)
        current_target_input.value = str(target)
        update_action_status(f"Moved to target {target} successfully.")

def rotate_to(event):
    if carousel:
        angle = self_rotation_angle_input.value
        carousel.rotate_to_angle(angle)
        update_action_status(f"Rotated to angle {angle} successfully.")

def set_rotation_speed(event):
    if carousel:
        speed = rotation_speed_input.value
        carousel.set_rotation_speed(speed)
        update_action_status("Rotation Speed set successfully.")

def start_rotation(event):
    if carousel:
        carousel.start_rotate()
        update_action_status("Start Rotation executed successfully.")

def stop_rotation(event):
    if carousel:
        carousel.stop_rotation()
        update_action_status("Stop Rotation executed successfully.")

def stop_all(event):
    if carousel:
        carousel.close()
        update_action_status("All operations stopped and serial connection closed.")    

# Link buttons to callback functions
start_button.on_click(start_connection)
home_raster_button.on_click(home_raster)
set_raster_speed_button.on_click(set_raster_speed)
begin_raster_button.on_click(begin_raster)
stop_raster_button.on_click(stop_raster)
step_raster_cw_button.on_click(step_raster_cw)
step_raster_ccw_button.on_click(step_raster_ccw)
move_to_target_button.on_click(move_to_target)
rotate_to_button.on_click(rotate_to)
set_rotation_speed_button.on_click(set_rotation_speed)
start_rotation_button.on_click(start_rotation)
stop_rotation_button.on_click(stop_rotation)
stop_button.on_click(stop_all)

# Arrange the layout
layout = pn.Column(
    pn.pane.Markdown("### Multi-Target-Carousel-Controller Control System"),
    pn.Row(pn.pane.Markdown("**COM Port**"), com_port_selector, start_button),
    connection_status,
    pn.Row(current_target_input, target_input, move_to_target_button),
    pn.Row( raster_angle_input, raster_speed_input),
    pn.Row(home_raster_button, set_raster_speed_button),
    pn.Row(begin_raster_button, stop_raster_button),
    pn.Row(step_raster_cw_button, step_raster_ccw_button),
    pn.Row(self_rotation_angle_input, rotate_to_button),
    pn.Row(rotation_speed_input, set_rotation_speed_button),
    pn.Row(start_rotation_button, stop_rotation_button),
    pn.Row(stop_button),
    action_status
)

# Serve the panel
pn.serve(layout, show=True)
