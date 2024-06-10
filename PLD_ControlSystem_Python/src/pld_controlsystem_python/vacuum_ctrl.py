import serial
import time

class VacuumControls:
    def __init__(self, port='COM6', baudrate=9600, address_of_unit=1):
        self.port = port
        self.baudrate = baudrate
        self.address_of_unit = address_of_unit
        self.ser = None

    def send_command(self, command):
        """
        Send a command to the controller and read the response.

        :param command: The command string to send.
        """
        
        self.ser.write(command.encode())
        # response = self.ser.readline().decode()
        # print("Response:", response)
        time.sleep(0.01)  # Slight delay to ensure command is processed    
    
    def initialize(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            initialize_command = f'INIT {self.address_of_unit}\n'
            self.ser.write(initialize_command.encode())
            time.sleep(1)
            print("Initialization successful")
        except Exception as e:
            print(f'Error initializing: {e}')

    def read_data(self, parameter=0):
        try:
            if self.ser is None:
                raise Exception("Serial port not initialized")
            
            read_command = f'READ? {self.address_of_unit} {parameter}\n'
            self.ser.write(read_command.encode())
            response = self.ser.readline().decode().strip()
            return print(response)
        except Exception as e:
            print(f'Error reading data: {e}')
            return None

    def close(self):
        if self.ser is not None:
            self.ser.close()
            print("Serial port closed")

def mbar_to_torr(mbar):
    return mbar * 0.750062

if __name__ == "__main__":
    vc = VacuumControls()
    vc.initialize()
    response_mbar = vc.read_data(parameter=0)
    
    if response_mbar:
        response_mbar = float(response_mbar)
        response_torr = mbar_to_torr(response_mbar)
        print(f'Response: {response_mbar} mbar')
        print(f'Response: {response_torr} Torr')
    
    vc.close()
