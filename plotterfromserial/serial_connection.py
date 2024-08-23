import serial
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

    def connect_to_port(self, connection_indicator, indicator_circle, connection_status, root):
        try:
            self.ser = serial.Serial(
                port='COM8',  # Ensure this is the correct COM port
                baudrate=115200,  # Ensure this matches the baud rate of the sending device
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
            print(f"Failed to connect to port: {e}")


    def disconnect_from_port(self, connection_status, connection_indicator, indicator_circle, root):
        if self.ser and self.ser.is_open:
            self.ser.close()
            if connection_status:
                connection_status.config(text="Disconnected", fg='red')
            if connection_indicator and indicator_circle:
                connection_indicator.itemconfig(indicator_circle, fill='red')
            root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
            messagebox.showinfo("Bağlantı Kesildi", "Serial connection closed.")
        else:
            messagebox.showerror("Hata", "No open serial connection to close.")

    def read_data(self):
        if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
            data = self.ser.readline().decode('utf-8').strip()
            print(f"Received data: {data}")  # Debug print to verify data reception
            return data
        else:
            print("No data available to read or connection not open.")
        return None

    def animate_connection_indicator(self, connection_indicator, indicator_circle, root):
        current_color = connection_indicator.itemcget(indicator_circle, "fill")
        next_color = 'green' if current_color == 'red' else 'red'
        connection_indicator.itemconfig(indicator_circle, fill=next_color)
        root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
