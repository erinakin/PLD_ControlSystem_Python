import panel as pn
from pressure_ctrl import PressureControls
from serial.tools import list_ports

# Initialize Panel
pn.extension()

controller = None

# Section 1: Connection & Status
available_ports = [port.device for port in list_ports.comports()]
com_port_selector = pn.widgets.Select(name='COM Port', options=available_ports, value= 'COM7' if available_ports else available_ports[0])
connect_button = pn.widgets.Button(name="Connect", button_type="primary")
disconnect_button = pn.widgets.Button(name="Disconnect", button_type="danger")
connection_status = pn.pane.Markdown("Status: Disconnected")

def connect(event):
    global controller
    try:
        controller = PressureControls(port=com_port_selector.value)
        connection_status.object = "<div style='color:green'><strong>Serial connection established successfully!</strong></div>"
    except Exception as e:
        connection_status.object = f"<div style='color:red'><strong>Error:</strong> {str(e)}</div>"


def disconnect(event):
    controller.close()
    connection_status.object = "Status: Disconnected"

connect_button.on_click(connect)
disconnect_button.on_click(disconnect)

software_version_button = pn.widgets.Button(name="Get Software Version")
status_button = pn.widgets.Button(name="Get Status")
software_version_display = pn.pane.Markdown()
status_display = pn.pane.Markdown()

def update_software_version_display(event):
    software_version_display.object = f"Software Version: {controller.software_version_request()}"
software_version_button.on_click(update_software_version_display)

def update_status_display(event):
    status_display.object = f"Status: {controller.status_request()}"
status_button.on_click(update_status_display)

connection_status_section = pn.Column(
    pn.pane.HTML("<h3 style='font-weight: bold; font-size: 16px;'>Connection & Status</h3>"),
    com_port_selector,
    pn.Row(connect_button, disconnect_button),
    connection_status,
    pn.Row(software_version_button, software_version_display),
    pn.Row(status_button, status_display)
)

# Section 2: Setpoint Controls
setpoint_selector = pn.widgets.Select(name="Select Setpoint", options=["A", "B", "C", "D", "E"])
setpoint_action = pn.widgets.RadioButtonGroup(name="Action", options=["Get", "Set"])
setpoint_value_input = pn.widgets.FloatInput(name="Setpoint Value", placeholder="Enter value")
control_type_selector = pn.widgets.RadioButtonGroup(name="Control Type", options=["position", "pressure"])
pressure_unit_display = pn.pane.Markdown("")


# Function to update the pressure unit display based on the control type
def update_pressure_unit_display(event):
    if control_type_selector.value == "pressure":
        current_unit = controller.pressure_units('get')
        pressure_unit_display.object = f"Units: {current_unit}"
    else:
        pressure_unit_display.object = ""

control_type_selector.param.watch(update_pressure_unit_display, 'value')

setpoint_button = pn.widgets.Button(name="Submit", button_type="primary")
activate_setpoint_button = pn.widgets.Button(name="Activate Setpoint", button_type="success")
setpoint_display = pn.pane.Markdown()

def setpoint_action_handler(event):
    setpoint = setpoint_selector.value
    action = setpoint_action.value.lower()
    if action == "get":
        result = controller.setpoint_value("get", setpoint)
        setpoint_display.object = f"Current setpoint {setpoint} value: {result['setpoint_value']} \n  {result['control_type']}"
    elif action == "set":
        value = setpoint_value_input.value
        control_type = control_type_selector.value
        result = controller.setpoint_value("set", setpoint, value, control_type)
        setpoint_display.object = result

def activate_setpoint_handler(event):
    setpoint = setpoint_selector.value
    result = controller.select_setpoint(setpoint)
    setpoint_display.object = result

setpoint_button.on_click(setpoint_action_handler)
activate_setpoint_button.on_click(activate_setpoint_handler)

setpoint_controls_section = pn.Column(
    pn.pane.HTML("<h3 style='font-weight: bold; font-size: 16px;'>Setpoint Controls</h3>"),
    pn.Row(setpoint_selector, setpoint_action),
    pn.Row(setpoint_value_input, control_type_selector, pressure_unit_display),
    pn.Row(setpoint_button, activate_setpoint_button),
    setpoint_display
)

# Section 3: Valve Controls
open_valve_button = pn.widgets.Button(name="Open Valve")
close_valve_button = pn.widgets.Button(name="Close Valve")
hold_valve_button = pn.widgets.Button(name="Hold Valve")
valve_position_button = pn.widgets.Button(name="Get Valve Position")
valve_position_display = pn.pane.Markdown()

def open_valve_handler(event):
    valve_position_display.object = controller.open_valve()
open_valve_button.on_click(open_valve_handler)

def close_valve_handler(event):
    valve_position_display.object = controller.close_valve()
close_valve_button.on_click(close_valve_handler)

def hold_valve_handler(event):
    valve_position_display.object = controller.hold_valve()
hold_valve_button.on_click(hold_valve_handler)

def valve_position_handler(event):
    valve_position_display.object = f"Valve Position: {controller.valve_position()}"
valve_position_button.on_click(valve_position_handler)

valve_controls_section = pn.Column(
    pn.pane.HTML("<h3 style='font-weight: bold; font-size: 16px;'>Valve Controls</h3>"),
    pn.Row(open_valve_button, close_valve_button, hold_valve_button),
    pn.Row(valve_position_button, valve_position_display)
)

# Section 4: Pressure & Tuning
pressure_request_button = pn.widgets.Button(name="Get Pressure")
pressure_units_selector = pn.widgets.Select(name="Set Pressure Units", options=["Torr", "mTorr", "mbar", "Pa", "kPa"])
pressure_units_button = pn.widgets.Button(name="Set Pressure Units")
pressure_display = pn.pane.Markdown()
pressure_units_display = pn.pane.Markdown()

def pressure_request_handler(event):
    pressure_display.object = f"Pressure: {controller.pressure_request()}"
pressure_request_button.on_click(pressure_request_handler)

def pressure_units_handler(event):
    pressure_units_display.object = controller.pressure_units('set', pressure_units_selector.value)
pressure_units_button.on_click(pressure_units_handler)

self_tune_button = pn.widgets.Button(name="Start Self-Tuning")
stop_self_tune_button = pn.widgets.Button(name="Stop Self-Tuning")
control_mode_selector = pn.widgets.RadioButtonGroup(name="Control Mode", options=["self-tuning", "pid"])
set_control_mode_button = pn.widgets.Button(name="Set Control Mode")
self_tune_display = pn.pane.Markdown()
control_mode_display = pn.pane.Markdown()

def start_self_tune_handler(event):
    self_tune_display.object = controller.self_tune()
self_tune_button.on_click(start_self_tune_handler)

def stop_self_tune_handler(event):
    self_tune_display.object = controller.stop_self_tune()
stop_self_tune_button.on_click(stop_self_tune_handler)

def set_control_mode_handler(event):
    control_mode_display.object = controller.control_mode("set", control_mode_selector.value)
set_control_mode_button.on_click(set_control_mode_handler)

pressure_tuning_section = pn.Column(
    pn.pane.HTML("<h3 style='font-weight: bold; font-size: 16px;'>Pressure & Tuning</h3>"),
    pn.Row(pressure_request_button, pressure_display),
    pn.Row(pressure_units_selector, pressure_units_button, pressure_units_display),
    pn.Row(self_tune_button, stop_self_tune_button, self_tune_display),
    pn.Row(control_mode_selector, set_control_mode_button, control_mode_display)
)

# Combine all sections into a single layout with uniform spacing and alignment
layout = pn.Column(
    pn.pane.HTML("<h1 style='text-align: center; font-size: 24px;'>Pressure Controller Interface</h1>"),
    pn.layout.Divider(),
    pn.Spacer(height=10),
    # Row 1: Connection & Status, Spacer, Setpoint Controls
    pn.Row(connection_status_section, pn.Spacer(width=20), setpoint_controls_section),
    pn.Spacer(height=20),
    # Row 2: Valve Controls, Spacer, Pressure & Tuning
    pn.Row(valve_controls_section, pn.Spacer(width=20), pressure_tuning_section),
    pn.Spacer(height=20)
)
# Display the interface
layout.servable("Pressure Controller Interface")

#Serve the Panel
pn.serve(layout, show=True)
