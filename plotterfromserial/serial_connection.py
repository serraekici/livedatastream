# serial_connection.py
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

    def connect_to_port(self, connection_status, connection_indicator, indicator_circle, root):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            # Seri portu COM8 ve baudrate'i 115200 olarak ayarlıyoruz, timeout'u 5 saniye yapıyoruz
            self.ser = serial.Serial('COM8', baudrate=115200, timeout=5)
            # Bağlantı durumu ile ilgili mesajları devre dışı bırakıyoruz
            if connection_status:
                connection_status.config(text="Connected", fg='green')
            if connection_indicator and indicator_circle:
                connection_indicator.itemconfig(indicator_circle, fill='green')
            messagebox.showinfo("Bağlantı Başarıyla Kuruldu", "Connected to COM8 at baudrate 115200")
        except serial.SerialException as e:
            if connection_status:
                connection_status.config(text="Disconnected", fg='red')
            if connection_indicator and indicator_circle:
                connection_indicator.itemconfig(indicator_circle, fill='red')
            root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
            messagebox.showerror("Bağlantı Hatası", f"Failed to connect to COM8: {e}")

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
        if self.ser and self.ser.is_open:
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode('utf-8').strip()
                print(f"Seriden gelen veri: {data}")
                return data
            else:
                print("Seri porttan veri bekleniyor...")
        return None

    def animate_connection_indicator(self, connection_indicator, indicator_circle, root):
        current_color = connection_indicator.itemcget(indicator_circle, "fill")
        next_color = 'green' if current_color == 'red' else 'red'
        connection_indicator.itemconfig(indicator_circle, fill=next_color)
        root.after(500, lambda: self.animate_connection_indicator(connection_indicator, indicator_circle, root))
