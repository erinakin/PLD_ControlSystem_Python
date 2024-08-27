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

# Function to create a panel layout for a single flow controller
def create_flow_controller_tab(com_port, unit):
    # Widgets specific to each tab
    status = pn.widgets.StaticText(value="Disconnected")
    name_display = pn.widgets.StaticText(value="Name: N/A")
    
    controller = None
    
    # Callback to start the device
    async def start_device(event):
        nonlocal controller
        status.value = "Connecting..."
        controller, name = await initialize_flow_controller(com_port, unit)
        status.value = "Connected"
        name_display.value = f"Name: {name}"

    # Callback to stop the device
    async def stop_device(event):
        nonlocal controller
        if controller is not None:
            status.value = "Disconnecting..."
            await close_flow_controller(controller)
            status.value = "Disconnected"
            name_display.value = "Name: N/A"
            controller = None
        else:
            status.value = "Controller not initialized"

    start_button = pn.widgets.Button(name="Start", button_type="primary")
    start_button.on_click(start_device)
    
    stop_button = pn.widgets.Button(name="Stop", button_type="danger")
    stop_button.on_click(stop_device)
    
    # Layout for the tab
    tab_layout = pn.Column(
        pn.widgets.Select(name='COM Port', options=get_available_com_ports(), value=com_port),
        name_display,
        pn.Row(start_button, stop_button),
        status
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
