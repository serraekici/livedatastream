import serial
import serial.tools.list_ports

class SerialConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SerialConnection, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'ser'):
            self.ser = None

    def connect_to_port(self, port, baudrate):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.ser = serial.Serial(port, baudrate=int(baudrate), timeout=1)
            return True, f"Connected to {port} at baudrate {baudrate}"
        except serial.SerialException as e:
            return False, f"Failed to connect to port: {e}"

    def disconnect_from_port(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            return True, "Serial connection closed."
        return False, "No open serial connection to close."

    def read_data(self):
        if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
            return self.ser.readline().decode('utf-8').strip()
        return None

    def is_connected(self):
        return self.ser and self.ser.is_open

    def list_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
