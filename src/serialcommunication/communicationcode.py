import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# port açılımı
ser = serial.Serial(baudrate=115200, timeout=1)

# verileri depolamak için liste
data_list = []

# Seçilen kanalları tutan liste
selected_channels = []

# Kanal sayısı
num_channels = 10

# Kanal isimleri
channel_names = [f'Channel {i+1}' for i in range(num_channels)]

# Tkinter ana penceresi
root = tk.Tk()
root.title("Live Data Plotter")

# Arka plan rengini ayarla
root.configure(bg='#54544e')  # Ana arka plan gri

# Grid durumu
grid_on = tk.BooleanVar(value=True)  # Grid'in açık/kapalı durumunu tutan değişken

# Menü çubuğu oluşturma
appbar = tk.Frame(root, relief=tk.RAISED, bd=2, bg='#1e1741')
appbar.pack(side=tk.TOP, fill=tk.X)

# Logo
logo = tk.Label(appbar, text="🐱", bg='#1e1741', fg='white', font=("Arial", 16))
logo.pack(side=tk.LEFT, padx=5)

# IMPORT butonu
import_button = tk.Button(appbar, text="IMPORT", bg='#abab9a', fg='black')
import_button.pack(side=tk.LEFT, padx=5)

# X-Y start-end giriş alanları
x_start_label = tk.Label(appbar, text="X Start:", bg='#1e1741', fg='white')
x_start_label.pack(side=tk.LEFT, padx=5)
x_start_entry = tk.Entry(appbar, width=5)
x_start_entry.pack(side=tk.LEFT, padx=5)

x_end_label = tk.Label(appbar, text="X End:", bg='#1e1741', fg='white')
x_end_label.pack(side=tk.LEFT, padx=5)
x_end_entry = tk.Entry(appbar, width=5)
x_end_entry.pack(side=tk.LEFT, padx=5)

y_start_label = tk.Label(appbar, text="Y Start:", bg='#1e1741', fg='white')
y_start_label.pack(side=tk.LEFT, padx=5)
y_start_entry = tk.Entry(appbar, width=5)
y_start_entry.pack(side=tk.LEFT, padx=5)

y_end_label = tk.Label(appbar, text="Y End:", bg='#1e1741', fg='white')
y_end_label.pack(side=tk.LEFT, padx=5)
y_end_entry = tk.Entry(appbar, width=5)
y_end_entry.pack(side=tk.LEFT, padx=5)

# Port ve Baudrate seçenekleri
port_label = tk.Label(appbar, text="PORT:", bg='#1e1741', fg='white')
port_label.pack(side=tk.LEFT, padx=5)

# Seri portları listeleme
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Seri portları combobox'a ekleme
port_combobox = ttk.Combobox(appbar, values=list_serial_ports(), state="readonly")
port_combobox.pack(side=tk.LEFT, padx=5)

baudrate_label = tk.Label(appbar, text="Baud Rate:", bg='#1e1741', fg='white')
baudrate_label.pack(side=tk.LEFT, padx=5)

baudrate_combobox = ttk.Combobox(appbar, values=[
    1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400
], state="readonly")
baudrate_combobox.current(9)  # 115200 seçili olarak gelir
baudrate_combobox.pack(side=tk.LEFT, padx=5)

# Grid switch ekleme
grid_switch = ttk.Checkbutton(appbar, text="Grid On/Off", variable=grid_on, command=lambda: update_data(None))
grid_switch.pack(side=tk.RIGHT, padx=10, pady=5)

# Connect butonu ve durum göstergesi
connect_button = tk.Button(appbar, text="Connect", bg='#abab9a', fg='black', command=lambda: connect_to_port())
connect_button.pack(side=tk.LEFT, padx=5)

connection_status = tk.Label(appbar, text="Disconnected", bg='#1e1741', fg='red')
connection_status.pack(side=tk.LEFT, padx=5)

connection_indicator = tk.Canvas(appbar, width=20, height=20, bg='#1e1741', highlightthickness=0)
indicator_circle = connection_indicator.create_oval(5, 5, 15, 15, fill='red')
connection_indicator.pack(side=tk.LEFT, padx=5)

# Port bağlantı durumu kontrol fonksiyonu
def connect_to_port():
    selected_port = port_combobox.get()
    if selected_port:
        ser.port = selected_port
        ser.baudrate = int(baudrate_combobox.get())
        ser.timeout = 1
        ser.open()
        connection_status.config(text="Connected", fg='green')
        connection_indicator.itemconfig(indicator_circle, fill='green')
    else:
        connection_status.config(text="Disconnected", fg='red')
        connection_indicator.itemconfig(indicator_circle, fill='red')

# Kanal seçimi için listeyi sol tarafa taşıma
channel_selection_frame = tk.Frame(root, bg='#54544e')
channel_selection_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)

channel_vars = []
channel_entries = []
for i in range(num_channels):
    var = tk.IntVar()
    channel_vars.append(var)
    cb = tk.Checkbutton(channel_selection_frame, text=f"Channel {i+1}", variable=var, command=lambda: update_selected_channels(), bg='#54544e', fg='white')
    cb.pack(anchor='w')

    entry = tk.Entry(channel_selection_frame, width=10)
    entry.insert(0, channel_names[i])
    entry.pack(padx=5)
    entry.bind("<KeyRelease>", lambda event, idx=i: update_channel_name(idx, event))
    channel_entries.append(entry)

# Seçilen kanalları güncelleme fonksiyonu
def update_selected_channels():
    global selected_channels
    selected_channels = [i for i, var in enumerate(channel_vars) if var.get() == 1]
    update_data(None)

# Kanal isimlerini güncelleme fonksiyonu
def update_channel_name(idx, event):
    channel_names[idx] = channel_entries[idx].get()
    update_data(None)

# Figure oluşturma
fig, ax = plt.subplots(facecolor='#54544e')  # Grafiklerin arka planı biraz daha açık gri
ax.set_facecolor('#abab9a')  # Grafiklerin çizim alanı

# Figure'ü tkinter penceresine gömmek için canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Verileri güncellemek için fonksiyon
def update_data(frame):
    if ser.is_open and ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print(f"data: {data}")
        values = data.split(',')
        
        # Boş veya sayısal olmayan değerleri kontrol et ve atla
        if all(v.replace('.', '', 1).isdigit() for v in values) and len(values) == num_channels:
            data_list.append(values)  # verileri virgülle ayrılmış şekilde parçalar
        else:
            print(f"Skipping invalid data: {data}")
        
        # Verileri NumPy dizisine dönüştür ve grafiği güncelle
        if len(data_list) > 0:
            data_array = np.array(data_list, dtype=float)

            ax.clear()
            for channel in selected_channels:
                ax.plot(data_array[:, channel], label=channel_names[channel])
            ax.set_title('Selected Channels', color='white')
            ax.set_xlabel('Sample', color='white')
            ax.set_ylabel('Value', color='white')
            ax.legend(loc='upper right', facecolor='#3f3f3f')

            # Grid durumu
            ax.grid(grid_on.get())

            # X ekseni aralığını güncelle
            try:
                x_start = int(x_start_entry.get())
                x_end = int(x_end_entry.get())
                ax.set_xlim([x_start, x_end])
            except ValueError:
                pass  # Geçersiz giriş varsa aralığı değiştirme

            # Y ekseni aralığını güncelle
            try:
                y_start = int(y_start_entry.get())
                y_end = int(y_end_entry.get())
                ax.set_ylim([y_start, y_end])
            except ValueError:
                pass  # Geçersiz giriş varsa aralığı değiştirme

            canvas.draw()

ani = animation.FuncAnimation(fig, update_data, interval=1000, cache_frame_data=False)

try:
    root.mainloop()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
