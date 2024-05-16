

from newportxps.newportxps import NewportXPS
from newportxps.XPS_C8_drivers import XPSException
from typing import Any, Literal

parameters = Literal["Velocity", "Position"]

class MotionController(NewportXPS):
    def __init__(self, host, group=None, username='Administrator', password='Administrator',
                port=5001, timeout=10, extra_triggers=0, outputs=('CurrentPosition', 'SetpointPosition')):
        super().__init__(host, group=group, username=username, password=password,
                        port=port, timeout=timeout, extra_triggers=extra_triggers,
                        outputs=outputs)
        # Note that the following attributes are not part of the NewportXPS class
        self._velocity = 0
        self._position = 0

    def show_status(self) -> str:
        """
        Show the status report of the motion controller.
        """
        return self.status_report()

    def initialize_and_home(self, home=True):
        """
        Initialize all the groups and home the motion controller.
        """
        
        for g in self.groups:
            try:
                self.initialize_group(group=g, home=home)
                
            except XPSException:
                print(f" '{g}' already initialized so will kill and reinitialize ")
                self.kill_group(group=g)
                self.initialize_group(group=g)
                self.home_group(group=g)
            
    def stop_controller(self, group=None):
        """
        Stop the motion controller.
        """
        self.kill_group(group=group)

    def set_position(self, stage: str, position: float, relative: bool = False):
        """
        Set the position of the specified stage.

        Args:
            stage (str): The name of the stage.
            position (float): The target position.
            relative (bool): Whether the move is relative or absolute. Default is False.
        """
        # To extract the name of the stages (sname)
        # sname in self.stages.items()
        
        self.move_stage(stage, position, relative=relative)
        return print('The position is now set to', self.get_position(stage), 'Units')

    def set_velocity(self, stage: str, velocity: float):
        """
        Set the velocity parameters for the specified stage.

        Args:
            stage (str): The name of the stage.
            velocity (float): The target velocity.
           
        """
        self.set_velocity(stage, velocity)
        return print('The velocity is now set to', self.get_velocity(stage), 'Units/sec')

    def get_position(self, stage: str):
        """_summary_

        Args:
            stage (str): The name of the stage.

        Returns:
            _type_: _description_
        """
        
        return print('The current position of',stage, 'is', self.get_stage_position(stage))
        
    def get_velocity(self, stage:str):
        """
        Get the value of the specified parameter.

        Args:
            parameter (Literal["Velocity", "Position"]): The parameter to get.

        Returns:
            Any: The value of the specified parameter.
        """
        if parameter == "Velocity":
            return self._velocity
        elif parameter == "Position":
            return self._position
        else:
            raise ValueError("Invalid parameter name.")    

# Example usage:
if __name__ == "__main__":
    import sys
    hostip = sys.argv[1]
    # Initialize motion controller with host IP address and optional group name
    controller = MotionController(host="192.168.1.100", group="GROUP1")
    
    # Show status report
    print(controller.show_status())
    
    # Initialize and home the motion controller
    controller.initialize_and_home()
    
    # Set position of a stage
    controller.set_position(stage="STAGE1", position=100.0)
    
    # Set velocity parameters for a stage
    controller.set_velocity_parameters(stage="STAGE1", velocity=500.0, acceleration=2000.0)
    
    # Stop the motion controller
    controller.stop_controller()
