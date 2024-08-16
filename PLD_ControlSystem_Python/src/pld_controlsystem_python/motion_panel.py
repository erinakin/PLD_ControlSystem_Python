import panel as pn
from motion_ctrl import MotionController, XPSException

# Initialize an empty motion controller variable
controller = None

# Define GUI components
initialize_button = pn.widgets.Button(name='Initialize & Home', button_type='primary')
stop_button = pn.widgets.Button(name='Stop Controller', button_type='danger')
stage_selector = pn.widgets.Select(name='Stage', options=[])
position_slider = pn.widgets.FloatSlider(name='Position', start=0, end=100, step=0.1)
velocity_slider = pn.widgets.FloatSlider(name='Velocity', start=0, end=1000, step=1)
status_display = pn.widgets.StaticText(name='Status', value='')
error_display = pn.pane.Markdown('')

# Function to extract stage names from the status message
def extract_stage_names(status_message):
    """
    Extract the stage names from the status message.

    Args:
    status_message (str): The status message.

    Returns:
    list: The list of stage names.
    """
    stages = []
    # Find the part of the message with the stages
    if "Stages:" in status_message and "Hardware Status:" in status_message:
        stages_part = status_message.split("Stages:")[1].split("Hardware Status:")[0].strip()
        # Split by spaces and remove the part in parentheses
        for stage_info in stages_part.split():
            stage_name = stage_info.split('(')[0]
            if stage_name:  # Add the stage name if it's not empty
                stages.append(stage_name)
    return stages

# Define callback functions
def initialize_and_home(event):
    
    global controller
    try:
        # Initialize the motion controller with the host info, username, and password
        controller = MotionController(host="192.168.254.254", username='Administrator', password='Administrator')
        controller.initialize_and_home()

        #Extract and parse the status message
        status_message = controller.show_status()
        status_display.value = status_message

        #Extract the stages from the status message
        stages = extract_stage_names(status_message)
        stage_selector.options = stages
        
        #Update the stage_sekecector options
        stage_selector.options = stages

        error_display.object = ''
    except XPSException as e:
        error_display.object = f"<div style='color:red'><strong>Error:</strong> {str(e)}</div>"

def stop_controller(event):
    global controller
    try:
        if controller is not None:
            controller.stop_controller()
            status_display.value = controller.show_status()
            error_display.object = ''
        else:
            error_display.object = "<div style='color:red'><strong>Error:</strong> Motion controller not initialized.</div>"
    except XPSException as e:
        error_display.object = f"<div style='color:red'><strong>Error:</strong> {str(e)}</div>"

def set_position(event):
    global controller
    try:
        if controller is not None:
            position = position_slider.value
            stage = stage_selector.value
            controller.set_position(stage, position)
            status_display.value = f"Position of {stage} set to {position}"
            error_display.object = ''
        else:
            error_display.object = "<div style='color:red'><strong>Error:</strong> Motion controller not initialized.</div>"
    except XPSException as e:
        error_display.object = f"<div style='color:red'><strong>Error:</strong> {str(e)}</div>"
def set_velocity(event):
    global controller
    try:
        if controller is not None:
            velocity = velocity_slider.value
            stage = stage_selector.value
            controller.set_velocity(stage, velocity)
            status_display.value = f"Velocity of {stage} set to {velocity}"
            error_display.object = ''
        else:
            error_display.object = "<div style='color:red'><strong>Error:</strong> Motion controller not initialized.</div>"
    except XPSException as e:
        error_display.object = f"<div style='color:red'><strong>Error:</strong> {str(e)}</div>"

# Link buttons to callback functions
initialize_button.on_click(initialize_and_home)
stop_button.on_click(stop_controller)
position_slider.param.watch(set_position, 'value')
velocity_slider.param.watch(set_velocity, 'value')

# Arrange components in a layout
layout = pn.Column(
    pn.Row(initialize_button, stop_button),
    pn.Row(stage_selector, position_slider, velocity_slider),
    status_display,
    error_display
)

# Display the GUI
pn.serve(layout, show=True)
