import panel as pn
from motion_ctrl import MotionController, XPSException

# Initialize an empty motion controller variable
controller = None

# Initialize Panel
pn.extension()

# UI components
initialize_button = pn.widgets.Button(name='Initialize & Home', button_type='primary')
stop_button = pn.widgets.Button(name='Stop Controller', button_type='danger')
stage_selector = pn.widgets.Select(name='Stage', options=[])
position_input = pn.widgets.FloatInput(name='Position', value=0.0, step=0.1, start=-50.0, end=50.0)
set_position_button = pn.widgets.Button(name='Set Position', button_type='primary')
velocity_input = pn.widgets.FloatInput(name='Velocity', value=500.0, step=1.0, start=0.0, end=500.0)
set_velocity_button = pn.widgets.Button(name='Set Velocity', button_type='primary')

# Status Indicators
status_display = pn.widgets.StaticText(name='Status', value='')
error_display = pn.pane.Markdown('')
action_message = pn.pane.Markdown("<div id='message-box' style='border: 1px solid black; padding: 10px; border-radius: 5px;'> </div>", width=400)

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

# Define actions
def update_action_message(text):
    action_message.object = f"""
    <div id='message-box' style='border: 1px solid black; padding: 20px; border-radius: 5px;'>{text}</div>
    """

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

def set_position_click(event):
    global controller
    try:
        if controller is not None:
            position = position_input.value
            stage = stage_selector.value
            controller.set_position(stage, position)
            update_action_message(f"Position of {stage} set to {position}")
            error_display.object = ''
        else:
            error_display.object = "<div style='color:red'><strong>Error:</strong> Motion controller not initialized.</div>"
    except XPSException as e:
        error_display.object = f"<div style='color:red'><strong>Error:</strong> {str(e)}</div>"
def set_velocity_click(event):
    global controller
    try:
        if controller is not None:
            velocity = velocity_input.value
            stage = stage_selector.value
            controller.set_velocity(stage, velocity)
            update_action_message(f"Velocity of {stage} set to {velocity}")
            error_display.object = ''
        else:
            error_display.object = "<div style='color:red'><strong>Error:</strong> Motion controller not initialized.</div>"
    except XPSException as e:
        error_display.object = f"<div style='color:red'><strong>Error:</strong> {str(e)}</div>"

# Link buttons to callback functions
initialize_button.on_click(initialize_and_home)
stop_button.on_click(stop_controller)
set_position_button.on_click(set_position_click)
set_velocity_button.on_click(set_velocity_click)

# Arrange components in a layout
layout = pn.Column(pn.pane.Markdown("### Stage Motion Control System"),
    pn.Row(initialize_button, stop_button),
    pn.Row(stage_selector),
    pn.Row(position_input, set_position_button),
    pn.Row(velocity_input, set_velocity_button),
    status_display,
    action_message,
    error_display
)

# Display the GUI
pn.serve(layout, show=True)
