import serial.tools.list_ports
import threading

class SerialConnection:
    def __init__(self):
        self.ser = None

    def refresh_ports(self, port_combobox):
        """Refresh the list of available serial ports."""
        ports = list(serial.tools.list_ports.comports())
        port_combobox['values'] = [port.device for port in ports]
        if ports:
            port_combobox.current(0)  # Select the first port by default
        print(f"Available ports: {[port.device for port in ports]}")  # Debugging: Print available ports

    def connect_to_port(self, port, baudrate, connection_status, connection_indicator, indicator_circle, root):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            if self.ser.is_open:
                connection_status.config(text="Connected", fg='green')
                connection_indicator.itemconfig(indicator_circle, fill='green')
                print(f"Connected to {port} at {baudrate} baud.")  # Debugging: Confirm connection
                threading.Thread(target=self.read_serial_data, args=(root,)).start()
            else:
                raise serial.SerialException("Port opened but not functional.")
        except serial.SerialException as e:
            connection_status.config(text="Failed to Connect", fg='red')
            connection_indicator.itemconfig(indicator_circle, fill='red')
            print(f"Error: {e}")
            self.ser = None

    def read_serial_data(self, root):
        if self.ser is None:
            print("Serial connection not established.")
            return
        
        while self.ser.is_open:
            try:
                data = self.ser.readline().decode('utf-8').strip()
                if data:
                    # Display the raw data in the terminal section of your application
                    root.terminal.insert('end', f"{data}\n")  # Insert the raw data into the terminal
                    root.terminal.see('end')  # Auto-scroll to the latest data

                    print(f"Data received: {data}")  # Debugging: Print the received data

                    try:
                        values = list(map(float, data.split(',')))
                        root.data_list.append(values)
                        print(f"Data list updated: {root.data_list[-1]}")  # Debugging: Print the last appended data
                        root.update_graph()  # Immediately update the graph with new data
                    except ValueError:
                        print(f"Received data could not be parsed: {data}")  # Debugging: Log parse errors
            except Exception as e:
                print(f"Error reading serial data: {e}")
                root.connection_status.config(text="Disconnected", fg='red')
                break

    def disconnect_from_port(self, connection_status, connection_indicator, indicator_circle, root):
        if self.ser and self.ser.is_open:
            self.ser.close()
            connection_status.config(text="Disconnected", fg='red')
            connection_indicator.itemconfig(indicator_circle, fill='red')
            self.ser = None
            print("Disconnected from serial port.")  # Debugging: Confirm disconnection
