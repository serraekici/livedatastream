import serial
import time
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
            port_combobox.current(0)

    def list_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect_to_port(self, port, baudrate, connection_status, connection_indicator, indicator_circle, root, clear_graph_callback):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()

            self.ser = serial.Serial(port, baudrate, timeout=1)
            connection_status.config(text="Connected", fg="green")
            connection_indicator.itemconfig(indicator_circle, fill="green")

            # Bağlantı kurulduğunda grafiği temizle
            clear_graph_callback()

        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {port}.\n{str(e)}")
            connection_status.config(text="Disconnected", fg="red")
            connection_indicator.itemconfig(indicator_circle, fill="red")

    def disconnect_from_port(self, connection_status, connection_indicator, indicator_circle, root):
        if self.ser and self.ser.is_open:
            self.ser.close()
        connection_status.config(text="Disconnected", fg="red")
        connection_indicator.itemconfig(indicator_circle, fill="red")

    def read_serial_data(self, terminal, data_list, update_graph_callback, root):
        if self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    terminal.insert('end', f"Received data: {line}\n")
                    terminal.yview('end')

                    # Veriyi ayır ve her kanala ekle
                    values = [int(x) for x in line.split(',')]
                    for i, value in enumerate(values):
                        data_list[i].append(value)
                        if len(data_list[i]) > 1000:  # Çok fazla veri birikmesini önlemek için
                            data_list[i] = data_list[i][-1000:]

                    # data_list içeriğini terminale yazdır
                    print(f"Updated data_list for channel {i}: {data_list[i]}")

                    # Grafiği güncelle
                    update_graph_callback()

            except Exception as e:
                print(f"Error reading serial data: {e}")

        root.after(1000, self.read_serial_data, terminal, data_list, update_graph_callback, root)
