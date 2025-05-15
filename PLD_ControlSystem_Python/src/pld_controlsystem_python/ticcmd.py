import subprocess
import yaml

class TicCmd:
    """
    Static utility class for running `ticcmd` commands via subprocess.
    Provides general-purpose wrappers for invoking commands with or without device serial numbers.
    """

    @staticmethod
    def run(*args, capture_output=True):
        """
        Executes a `ticcmd` command.

        Args:
            *args: Command-line arguments passed to `ticcmd`.
            capture_output (bool): Whether to capture stdout (default: True).

        Returns:
            str: Standard output of the command.

        Raises:
            subprocess.CalledProcessError: If the command fails.
        """
        try:
            result = subprocess.run(["ticcmd"] + list(args),
                                    capture_output=capture_output,
                                    text=True,
                                    check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"[TicCmd Error] Command failed: ticcmd {' '.join(args)}")
            print(e.stderr)
            raise

    @staticmethod
    def run_with_serial(serial, *args, capture_output=True):
        """
        Executes a `ticcmd` command targeting a specific device by serial number.

        Args:
            serial (str): Serial number of the Tic device.
            *args: Additional arguments passed to `ticcmd`.
            capture_output (bool): Whether to capture stdout (default: True).

        Returns:
            str: Standard output of the command.
        """
        return TicCmd.run("-d", serial, *args, capture_output=capture_output)
    

class TicCmdController:
    """
    High-level interface for controlling a single Tic stepper motor controller.
    Each method wraps a specific `ticcmd` command for safe and structured control.
    """

    def __init__(self, serial=None):
        """Initializes the controller with a given or auto-detected serial number."""
        self.serial = serial or self._get_first_serial()
        if self.serial is None:
            raise RuntimeError("No Tic device found.")

    @staticmethod
    def list_devices():
        """Returns a list of connected Tic device serial numbers."""
        output = TicCmd.run("--list")
        return [line.split(",")[0].strip() for line in output.strip().splitlines() if line.strip()]

    def _get_first_serial(self):
        """Retrieves the first connected Tic device's serial number."""
        devices = self.list_devices()
        return devices[0] if devices else None

    def get_status(self, full=True, parsed=True):
        """Returns the current device status, optionally parsed from YAML format."""
        args = ["--status"]
        if full:
            args.append("--full")
        output = TicCmd.run_with_serial(self.serial, *args)
        return yaml.safe_load(output) if parsed else output

    def pause(self):
        """Pauses the program after executing the command."""
        TicCmd.run_with_serial(self.serial, "--pause")

    def pause_on_error(self):
        """Pauses the program only if an error occurs."""
        TicCmd.run_with_serial(self.serial, "--pause-on-error")

    def show_help(self):
        """Displays the `ticcmd` help information."""
        print(TicCmd.run("--help"))

    def set_position(self, pos):
        """Sets the target position in microsteps."""
        TicCmd.run_with_serial(self.serial, "--exit-safe-start", "--position", str(pos), capture_output=False)

    def set_position_relative(self, delta):
        """Sets the target position relative to the current position."""
        TicCmd.run_with_serial(self.serial, "--position-relative", str(delta), capture_output=False)

    def set_velocity(self, velocity):
        """Sets the target velocity in microsteps/10000s."""
        TicCmd.run_with_serial(self.serial, "--velocity", str(velocity), capture_output=False)

    def halt_and_set_position(self, pos):
        """Stops the motor and updates the internal position counter."""
        TicCmd.run_with_serial(self.serial, "--halt-and-set-position", str(pos))

    def halt_and_hold(self):
        """Abruptly stops the motor and maintains its position."""
        TicCmd.run_with_serial(self.serial, "--halt-and-hold")

    def home(self, direction):
        """Initiates homing to a limit switch in the given direction ('fwd' or 'rev')."""
        assert direction in ["fwd", "rev"]
        TicCmd.run_with_serial(self.serial, "--home", direction)

    def reset_command_timeout(self):
        """Clears the command timeout error."""
        TicCmd.run_with_serial(self.serial, "--reset-command-timeout")

    def deenergize(self):
        """Disables the motor driver."""
        TicCmd.run_with_serial(self.serial, "--deenergize")

    def energize(self):
        """Enables the motor driver without starting motion."""
        TicCmd.run_with_serial(self.serial, "--energize")

    def exit_safe_start(self):
        """Exits safe start mode, allowing motion commands."""
        TicCmd.run_with_serial(self.serial, "--exit-safe-start")

    def resume(self):
        """Equivalent to energize and exit-safe-start combined."""
        TicCmd.run_with_serial(self.serial, "--resume")

    def enter_safe_start(self):
        """Places the device into safe start mode."""
        TicCmd.run_with_serial(self.serial, "--enter-safe-start")

    def reset(self):
        """Resets the controller's current state."""
        TicCmd.run_with_serial(self.serial, "--reset")

    def clear_driver_error(self):
        """Attempts to clear any driver error flags."""
        TicCmd.run_with_serial(self.serial, "--clear-driver-error")

    def set_max_speed(self, val):
        """Sets the maximum speed limit (in microsteps/10k s)."""
        TicCmd.run_with_serial(self.serial, "--max-speed", str(val))

    def set_starting_speed(self, val):
        """Sets the starting speed (in microsteps/10k s)."""
        TicCmd.run_with_serial(self.serial, "--starting-speed", str(val))

    def set_max_accel(self, val):
        """Sets the maximum acceleration limit."""
        TicCmd.run_with_serial(self.serial, "--max-accel", str(val))

    def set_max_decel(self, val):
        """Sets the maximum deceleration limit."""
        TicCmd.run_with_serial(self.serial, "--max-decel", str(val))

    def set_step_mode(self, mode):
        """Sets the step mode (e.g., 'full', 'half', '1', '2_100p')."""
        TicCmd.run_with_serial(self.serial, "--step-mode", mode)

    def set_current_limit(self, milliamps):
        """Sets the motor current limit in milliamps."""
        TicCmd.run_with_serial(self.serial, "--current", str(milliamps))

    def set_decay_mode(self, mode):
        """Sets the decay mode (e.g., 'slow', 'mixed', 'fast')."""
        TicCmd.run_with_serial(self.serial, "--decay", mode)

    def set_agc_mode(self, mode):
        """Sets the AGC mode ('on', 'off', 'active_off')."""
        TicCmd.run_with_serial(self.serial, "--agc-mode", mode)

    def set_agc_bottom_current_limit(self, val):
        """Sets the AGC bottom current limit percentage (45-80)."""
        TicCmd.run_with_serial(self.serial, "--agc-bottom-current-limit", str(val))

    def set_agc_boost_steps(self, steps):
        """Sets the AGC boost steps (5, 7, 9, 11)."""
        TicCmd.run_with_serial(self.serial, "--agc-current-boost-steps", str(steps))

    def set_agc_freq_limit(self, hz):
        """Sets the AGC frequency limit ('off', 225, 450, 675)."""
        TicCmd.run_with_serial(self.serial, "--agc-frequency-limit", str(hz))

    def restore_defaults(self):
        """Restores the device to factory default settings."""
        TicCmd.run_with_serial(self.serial, "--restore-defaults")

    def load_settings_from_file(self, filename):
        """Loads configuration settings from a specified file."""
        TicCmd.run_with_serial(self.serial, "--settings", filename)

    def save_settings_to_file(self, filename):
        """Saves current settings to the given file."""
        TicCmd.run_with_serial(self.serial, "--get-settings", filename)

    def fix_settings_file(self, infile, outfile):
        """Attempts to correct a settings file and save the result to another file."""
        TicCmd.run("--fix-settings", infile, outfile)
