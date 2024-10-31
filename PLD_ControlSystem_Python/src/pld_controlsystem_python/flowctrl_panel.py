import panel as pn
from serial.tools import list_ports
import asyncio
from flowctrl_driver import FlowController

# Initialize Panel 
pn.extension()

# Function to get available COM ports
def get_available_com_ports():
    return [port.device for port in list_ports.comports()]

# Function to initialize a flow controller
async def initialize_flow_controller(com_port, unit):
    controller = FlowController(address=com_port, unit=unit)
    flow_controller_name = f"Alicat Flow Controller"
    await controller.get()  # Dummy call to initialize the controller
    return controller, flow_controller_name

# Function to close a flow controller
async def close_flow_controller(controller):
    if controller:
        await controller.close()

# Function to update display with current measurements 
async def update_display(controller, displays):
    try:
        data = await controller.get()
        displays['pressure'].value = f"Pressure: {data['pressure']} psia"
        displays['temperature'].value = f"Temperature: {data['temperature']} °C"
        displays['volumetric_flow'].value = f"Volumetric Flow: {data['volumetric_flow']} units"
        displays['mass_flow'].value = f"Mass Flow: {data['mass_flow']} units"
        displays['setpoint'].value = f"Setpoint: {data['setpoint']} units"
        displays['gas'].value = f"Gas: {data['gas']}"
        
    except Exception as e:
        for display in displays.values():
            display.value = f"Error: {str(e)}"

# Function to change the setpoint
async def set_setpoint(controller, setpoint_input, setpoint_display):
    if controller and controller.control_point in ('mass flow', 'vol flow'):
        await controller.set_flow_rate(setpoint_input.value)
        units = 'SLPM'
        setpoint_display.value = f"Current Setpoint: {setpoint_input.value} {units}"

    elif controller and controller.control_point in ('abs pressure', 'gauge pressure', 'diff pressure'):
        await controller.set_pressure(setpoint_input.value)
        units = 'psia'
        setpoint_display.value = f"Current Setpoint: {setpoint_input.value} {units}"

    else:
        setpoint_display.value = "Setpoint not set. Please select a control point."

# Function to set the control point
async def set_control_point(controller, control_point_selector, control_point_display):
    if controller:
        await controller._set_control_point(control_point_selector.value)
        control_point_display.value = f" Current Control Point: {await controller._get_control_point()}"

# Function to create a panel layout for a single flow controller
def create_flow_controller_tab(com_port, unit):
    # Widgets specific to each tab
    status = pn.widgets.StaticText(value="Disconnected")
    name_display = pn.widgets.StaticText(value="Name: N/A")

    # Measurement displays
    displays = {
        'pressure': pn.widgets.StaticText(value="Pressure: N/A"),
        'temperature': pn.widgets.StaticText(value="Temperature: N/A"),
        'volumetric_flow': pn.widgets.StaticText(value="Volumetric Flow: N/A"),
        'mass_flow': pn.widgets.StaticText(value="Mass Flow: N/A"),
        'setpoint': pn.widgets.StaticText(value="Setpoint: N/A"),
        'gas': pn.widgets.StaticText(value="Gas: N/A")
    }

    # Control point selection
    control_point_selector = pn.widgets.Select(name='Control Point', options=['mass flow', 'vol flow', 'abs pressure', 'gauge pressure', 'diff pressure'])
    control_point_display = pn.widgets.StaticText(value="Control Point: N/A")
    
    # Setpoint input
    setpoint_input = pn.widgets.FloatInput(name='Setpoint', value=0.0, step=0.01)
    setpoint_display = pn.widgets.StaticText(value="Current Setpoint: N/A")
    controller = None
    
    # Callback to start the device
    async def start_device(event):
        nonlocal controller
        status.value = "Connecting..."
        controller, name = await initialize_flow_controller(com_port, unit)
        status.value = "Connected"
        name_display.value = f"Name: {name}"
        await update_display(controller, displays)

    # Callback to stop the device
    async def stop_device(event):
        nonlocal controller
        if controller is not None:
            status.value = "Disconnecting..."
            await close_flow_controller(controller)
            status.value = "Disconnected"
            name_display.value = "Name: N/A"
            for display in displays.values():
                display.value = "N/A"
            #control_point_display.value = "Current Control Point: N/A"
            controller = None
        else:
            status.value = "Controller not initialized"

    # Callback to set the control point
    async def confirm_control_point(event):
        nonlocal controller
        await set_control_point(controller, control_point_selector, control_point_display)            

    # Callback to set the control point
    async def confirm_setpoint(event):
        nonlocal controller
        await set_setpoint(controller, setpoint_input, setpoint_display)

    # Callback to update the display
    start_button = pn.widgets.Button(name="Start", button_type="success")
    start_button.on_click(start_device)
    
    stop_button = pn.widgets.Button(name="Stop", button_type="danger")
    stop_button.on_click(stop_device)

    control_point_button = pn.widgets.Button(name="Set Control Point Type", button_type="primary")
    control_point_button.on_click(confirm_control_point)

    setpoint_button =  pn.widgets.Button(name="Set Setpoint", button_type="primary")
    setpoint_button.on_click(confirm_setpoint)
    
    # Layout for the tab
    tab_layout = pn.Column(
        pn.widgets.Select(name='COM Port', options=get_available_com_ports(), value=com_port),
        name_display,
        pn.Row(start_button, stop_button),
        status,

        pn.Row(
        pn.Column(control_point_selector,
        control_point_button,
        control_point_display),

        pn.Column(setpoint_input,
        setpoint_button,
        setpoint_display)
        ),

        displays['pressure'],
        displays['temperature'],
        displays['volumetric_flow'],
        displays['mass_flow'],
        displays['setpoint'],
        displays['gas']
        
    )
    
    return tab_layout

# Set default COM ports
default_com_port1 = 'COM9' if 'COM9' in get_available_com_ports() else 'COM1'
default_com_port2 = 'COM10' if 'COM10' in get_available_com_ports() else 'COM2'

# Create com port selectors
com_port_selector1 = pn.widgets.Select(name='COM Port', options=get_available_com_ports(), value=default_com_port1)
com_port_selector2 = pn.widgets.Select(name='COM Port', options=get_available_com_ports(), value=default_com_port2)

# Bind the function to the selectors, ensuring it re-renders when the selector value changes
tab1 = pn.bind(create_flow_controller_tab, com_port=com_port_selector1.param.value, unit='A')
tab2 = pn.bind(create_flow_controller_tab, com_port=com_port_selector2.param.value, unit='A')

tabs = pn.Tabs(("Flow Controller 1", tab1), ("Flow Controller 2", tab2))

# Show the panel
pn.serve(tabs, show=True)