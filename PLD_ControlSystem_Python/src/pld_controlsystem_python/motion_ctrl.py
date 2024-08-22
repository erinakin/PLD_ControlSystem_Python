# This code utilizes the `NewportXPS` from `newportxps` by `pyepics`.
# Source: https://github.com/pyepics/newportxps

from PLD_ControlSystem_Python.src.pld_controlsystem_python.newportxps import NewportXPS
from PLD_ControlSystem_Python.src.pld_controlsystem_python.XPS_C8_drivers import XPSException


class MotionController(NewportXPS):
    """A class representing a motion controller.

    Args:
        NewportXPS (type): The base class for the motion controller.
    """
    def __init__(self, host, group=None, username='Administrator', password='Administrator',
                port=5001, timeout=10, extra_triggers=0, outputs=('CurrentPosition', 'SetpointPosition')):
        super().__init__(host, group=group, username=username, password=password,
                        port=port, timeout=timeout, extra_triggers=extra_triggers,
                        outputs=outputs)
        # Note that the following attributes are not part of the NewportXPS class
        

    def show_status(self):
        """
        Show the status report of the motion controller.
        """
        return self.status_report()

    def initialize_and_home(self, home=True):
        """
        Initialize all the groups and home the motion controller.
        Only one Group is used in this case. so we can use the group name as 'Group1.Pos'
        Inputs: home (bool): Whether to home the stages after initialization. Default is True.
            
        """
        
        for g in self.groups:
            try:
                self.initialize_group(group=g, home=home)
                
            except XPSException:
                print(f" '{g}' already initialized so will kill and reinitialize ")
                self.kill_group(group=g)
                self.initialize_group(group=g)
                self.home_group(group=g)
        return self.status_report()
            
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
            relative (bool): Whether the move is relative or absolute. Default is False(Absolute).
        """
        # To extract the name of the stages (sname)
        # sname in self.stages.items()
        
        self.move_stage(stage, position, relative=relative)
        return self.get_position(stage)

    def set_velocity(self, stage: str, velocity: float):
        """
        Set the velocity parameters for the specified stage.

        Args:
            stage (str): The name of the stage.
            velocity (float): The target velocity. Default = 500 units/sec
           
        """
        self.set_velocity_parameters(stage=stage, velo=velocity)
        return self.get_velocity(stage)

    def get_position(self, stage: str):
        """Get the current position of the specified stage.

        Args:
            stage (str): The name of the stage.

        Returns:
            float: The current position of the stage.
        """
        
        return print('The current position of',stage, 'is', self.get_stage_position(stage))
        
    def get_velocity(self, stage:str):
        """
        Get the current velocity of the specified stage.

        Args:
            stage (str): The name of the stage.

        Returns:
            float: The current velocity of the stage.
        """
        if stage not in self.stages:
           print("Stage '%s' not found" % stage)
           return
        ret, v_cur, a_cur, jt0_cur, jt1_cur = \
             self._xps.PositionerSGammaParametersGet(self._sid, stage)    
        return print('The current velocity of', stage, 'is', v_cur, 'Units/sec')
    


if __name__ == "__main__":
    import sys
    hostip = sys.argv[1]
    # Initialize motion controller with host IP address and optional group name
    controller = MotionController(host="192.168.254.254", username='Administrator', password='Administrator')
    
    # # Show status report
    # print(controller.show_status())
    
    # # Initialize and home the motion controller
    # controller.initialize_and_home()
    
    # # Set position of a stage
    # controller.set_position(stage="STAGE1", position=100.0)
    
    # # Set velocity parameters for a stage
    # controller.set_velocity_parameters(stage="STAGE1", velocity=500.0, acceleration=2000.0)
    
    # # Stop the motion controller
    # controller.stop_controller()
