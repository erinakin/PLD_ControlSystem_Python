import panel as pn
from serial.tools import list_ports
from vacuum_ctrl import VacuumControls

# Initialize Panel
pn.extension()

# Initialize variables
vacuum_controller = None
connection_status = pn.pane.Markdown('', width=300)
action_status = pn.pane.Markdown('', width=300)
pressure_update_periodic = None

# Define GUI components
correct_port = VacuumControls.find_vacuum_controller_port()
available_ports = [port.device for port in list_ports.comports()]


# Set the default COM Port to the found port or use a fallback
com_port_selector = pn.widgets.Select(name='', options=available_ports, value='COM6' if available_ports else available_ports[0])
address_input = pn.widgets.FloatInput(name='Address of unit', value=1, step=1)
start_button = pn.widgets.Button(name='Start Connection', button_type='success')
stop_button = pn.widgets.Button(name='STOP', button_type='danger', width=100)

pressure_display = pn.widgets.StaticText(name='Current Pressure', value="---")
start_reading_button = pn.widgets.Toggle(name='Start Continuous Pressure Reading', button_type='primary')

correction_factor_display = pn.widgets.StaticText(name='Current Correction Factor', value='---')
setpoint_display = pn.widgets.StaticText(name='Current Setpoint', value='---')
pressure_setpoint_input = pn.widgets.Select(name='Pressure set point', options={'Low Pressure': '0', 'Atmospheric Pressure': '1'})
set_pressure_button = pn.widgets.Button(name='Set Pressure Setpoint', button_type='primary')

correction_factor_input = pn.widgets.FloatInput(name='Correction factor (0.2 - 8.0)', value=1.0, step=0.1)
set_correction_factor_button = pn.widgets.Button(name='Set Correction Factor', button_type='primary')

error_display = pn.pane.Markdown('', width=300)

# Define callbacks
def start_connection(event):
    global vacuum_controller
    try:
        vacuum_controller = VacuumControls(port=com_port_selector.value, address=int(address_input.value))
        connection_status.object = "<div style='color:green'><strong>Serial connection established successfully!</strong></div>"
        
        # Display current pressure and setpoint immediately after connection
        pressure_display.value = f"{vacuum_controller.pressure_hpa} hPa or mbar, {vacuum_controller.pressure_torr} Torr"
        correction_factor_display.value = vacuum_controller.correction_factor()
        setpoint_display.value = vacuum_controller.current_setpoint
    except Exception as e:
        connection_status.object = f"<div style='color:red'><strong>Error:</strong> {str(e)}</div>"

def update_action_status(message, success=True):
    color = 'green' if success else 'red'
    action_status.object = f"<div style='color:{color}'>{message}</div>"

def read_pressure(event=None):
    if vacuum_controller:
        vacuum_controller.read_pressure()
        pressure_hpa, pressure_torr = vacuum_controller.pressure_hpa, vacuum_controller.pressure_torr
        pressure_display.value = f"{pressure_hpa} hPa or mbar, {pressure_torr} Torr"

def toggle_pressure_reading(event):
    global pressure_update_periodic
    if event.new:  # If the button is toggled on
        pressure_update_periodic = pn.state.add_periodic_callback(read_pressure, period=500)  # Update every 0.5 seconds
        update_action_status("Continuous pressure reading started.")
    else:  # If the button is toggled off
        if pressure_update_periodic:
            pressure_update_periodic.stop()
            pressure_update_periodic = None
        update_action_status("Continuous pressure reading stopped.")

def set_pressure(event):
    if vacuum_controller:
        option = pressure_setpoint_input.value
        result = vacuum_controller.pressure_setpoint(option)
        update_action_status(result)

def set_correction_factor(event):
    if vacuum_controller:
        new_factor = correction_factor_input.value
        result = vacuum_controller.correction_factor(new_factor)
        correction_factor_display.value = f"{result}"
        update_action_status(result)

def stop_connection(event):
    global vacuum_controller, pressure_update_periodic
    if vacuum_controller:
        vacuum_controller.close()
        update_action_status("All operations stopped and serial connection closed.")
        vacuum_controller = None
        connection_status.object = "<div style='color:red'><strong>Serial connection closed successfully!</strong></div>"
        action_status.object = ''
        pressure_display.value = '---'
        correction_factor_display.value = '---'
        setpoint_display.value = '---'
        if pressure_update_periodic:
            pressure_update_periodic.stop()
            pressure_update_periodic = None

# Link buttons to callback functions
start_button.on_click(start_connection)
set_pressure_button.on_click(set_pressure)
set_correction_factor_button.on_click(set_correction_factor)
start_reading_button.param.watch(toggle_pressure_reading, 'value')
stop_button.on_click(stop_connection)

# Arrange the layout
layout = pn.Column(
    pn.pane.Markdown("### Pfeiffer Vacuum Sensor Control Panel"),
    pn.Row(pn.pane.Markdown("**COM Port**"), com_port_selector, address_input),
    start_button,
    connection_status,
    pn.Row(pressure_setpoint_input, set_pressure_button),
    pn.Row(correction_factor_input, set_correction_factor_button),
    pn.pane.Markdown("#### Parameters"),
    pn.Row(pressure_display, start_reading_button),
    pn.Row(correction_factor_display),
    pn.Row(setpoint_display),

    action_status,
    error_display,
    stop_button
)

# Serve the panel
pn.serve(layout, show=True)
