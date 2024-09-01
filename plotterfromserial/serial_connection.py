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

    def read_serial_data(self, terminal, data_list, update_graph, root):
        """Continuously read data from the serial port and update the graph."""
        if self.ser and self.ser.is_open:
            if self.ser.in_waiting > 0:  # Only read if there is data available
                try:
                    data = self.ser.readline().decode('utf-8').strip()  # Read and decode the data
                    if data:
                        print(f"Received data: {data}")  # Debugging: Print the data to the console
                        terminal.insert('end', f"{data}\n")  # Insert the data into the terminal
                        terminal.see('end')  # Scroll to the end to show the latest data
                        values = data.split(',')
                        if all(v.replace('.', '', 1).isdigit() for v in values):
                            float_values = [float(v) for v in values]
                            data_list.append(float_values)
                            print(f"Processed data: {float_values}")  # Debugging: Show processed data
                            update_graph()  # Update the graph immediately after receiving data
                except serial.SerialException as e:
                    print(f"Error reading data: {e}")
        root.after(100, lambda: self.read_serial_data(terminal, data_list, update_graph, root))

    def list_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def animate_connection_indicator(self, connection_indicator, indicator_circle, root):
        current_color = connection_indicator.itemcget(indicator_circle, "fill")
        next_color = 'green' if current_color == 'red' else 'red'
        connection_indicator.itemconfig(indicator_circle, fill=next_color)
        root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))