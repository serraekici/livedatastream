import serial
from tkinter import messagebox
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

    def refresh_ports(self, port_combobox):
        ports = self.list_serial_ports()
        port_combobox['values'] = ports
        if ports:
            port_combobox.current(0)  # Automatically select the first port

    def connect_to_port(self, port, baudrate, connection_status, connection_indicator, indicator_circle, root):
        try:
            self.ser = serial.Serial(
                port=port,  # Set the port
                baudrate=baudrate,  # Set the baudrate
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            if self.ser.is_open:
                print("Serial port is open.")
                connection_status.config(text="Connected", fg='green')
                connection_indicator.itemconfig(indicator_circle, fill='green')
            else:
                print("Failed to open serial port.")
        except serial.SerialException as e:
            connection_status.config(text="Disconnected", fg='red')
            connection_indicator.itemconfig(indicator_circle, fill='red')
            root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
            messagebox.showerror("Error", f"Failed to connect to port: {e}")

    def disconnect_from_port(self, connection_status, connection_indicator, indicator_circle, root):
        if self.ser and self.ser.is_open:
            self.ser.close()
            connection_status.config(text="Disconnected", fg='red')
            connection_indicator.itemconfig(indicator_circle, fill='red')
            root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
            messagebox.showinfo("Disconnected", "Serial connection closed.")
        else:
            messagebox.showerror("Error", "No open serial connection to close.")

    def read_data(self):
        try:
            if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
                data = self.ser.readline().decode('utf-8').strip()
                print(f"Received data: {data}")
                return data
            else:
                print("No data available to read or connection not open.")
        except serial.SerialException as e:
            messagebox.showerror("Error", "Disconnected from port.")
            self.ser = None  # Invalidate the connection
            return None

    def list_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def animate_connection_indicator(self, connection_indicator, indicator_circle, root):
        current_color = connection_indicator.itemcget(indicator_circle, "fill")
        next_color = 'green' if current_color == 'red' else 'red'
        connection_indicator.itemconfig(indicator_circle, fill=next_color)
        root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
