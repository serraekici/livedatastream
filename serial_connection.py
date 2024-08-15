import serial
import serial.tools.list_ports
from tkinter import messagebox

class SerialConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SerialConnection, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'ser'):
            self.ser = None

    def connect_to_port(self, port, baudrate, connection_status, connection_indicator, indicator_circle, root):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.ser = serial.Serial(port, baudrate=int(baudrate), timeout=1)
            connection_status.config(text="Connected", fg='green')
            connection_indicator.itemconfig(indicator_circle, fill='green')
            messagebox.showinfo("Bağlantı Başarıyla Kuruldu", f"Connected to {port} at baudrate {baudrate}")
        except serial.SerialException as e:
            connection_status.config(text="Disconnected", fg='red')
            connection_indicator.itemconfig(indicator_circle, fill='red')
            root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
            messagebox.showerror("Bağlantı Hatası", f"Failed to connect to port: {e}")

    def disconnect_from_port(self, connection_status, connection_indicator, indicator_circle, root):
        if self.ser and self.ser.is_open:
            self.ser.close()
            connection_status.config(text="Disconnected", fg='red')
            connection_indicator.itemconfig(indicator_circle, fill='red')
            root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
            messagebox.showinfo("Bağlantı Kesildi", "Serial connection closed.")
        else:
            messagebox.showerror("Hata", "No open serial connection to close.")

    def read_data(self):
        if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
            return self.ser.readline().decode('utf-8').strip()
        return None

    def list_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def animate_connection_indicator(self, connection_indicator, indicator_circle, root):
        current_color = connection_indicator.itemcget(indicator_circle, "fill")
        next_color = 'green' if current_color == 'red' else 'red'
        connection_indicator.itemconfig(indicator_circle, fill=next_color)
        root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
