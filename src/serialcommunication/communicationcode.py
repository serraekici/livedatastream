import serial
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# port açılımı
ser = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=1)

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

# Grid durumu
grid_on = tk.BooleanVar(value=True)

# Uygulama çubuğu oluşturma
appbar = tk.Frame(root, relief=tk.RAISED, bd=2)
appbar.pack(side=tk.TOP, fill=tk.X)

# Grid switch ekleme
grid_switch = ttk.Checkbutton(appbar, text="Grid On/Off", variable=grid_on, command=lambda: update_data(None))
grid_switch.pack(side=tk.RIGHT, padx=10, pady=5)

# X start ve X end giriş alanları ekleme
x_start_label = tk.Label(appbar, text="X Start:")
x_start_label.pack(side=tk.LEFT, padx=5)
x_start_entry = tk.Entry(appbar, width=5)
x_start_entry.pack(side=tk.LEFT, padx=5)

x_end_label = tk.Label(appbar, text="X End:")
x_end_label.pack(side=tk.LEFT, padx=5)
x_end_entry = tk.Entry(appbar, width=5)
x_end_entry.pack(side=tk.LEFT, padx=5)

# Y start ve Y end giriş alanları ekleme
y_start_label = tk.Label(appbar, text="Y Start:")
y_start_label.pack(side=tk.LEFT, padx=5)
y_start_entry = tk.Entry(appbar, width=5)
y_start_entry.pack(side=tk.LEFT, padx=5)

y_end_label = tk.Label(appbar, text="Y End:")
y_end_label.pack(side=tk.LEFT, padx=5)
y_end_entry = tk.Entry(appbar, width=5)
y_end_entry.pack(side=tk.LEFT, padx=5)

# Giriş alanlarındaki değişiklikleri izleme
x_start_entry.bind("<KeyRelease>", lambda event: update_data(None))
x_end_entry.bind("<KeyRelease>", lambda event: update_data(None))
y_start_entry.bind("<KeyRelease>", lambda event: update_data(None))
y_end_entry.bind("<KeyRelease>", lambda event: update_data(None))

# Kanal seçimi için radyo düğmeleri ve isim giriş alanları ekleme
channel_selection_frame = tk.Frame(appbar)
channel_selection_frame.pack(side=tk.LEFT, padx=5)

channel_vars = []
channel_entries = []
for i in range(num_channels):
    var = tk.IntVar()
    channel_vars.append(var)
    cb = tk.Checkbutton(channel_selection_frame, text=f"Channel {i+1}", variable=var, command=lambda: update_selected_channels())
    cb.grid(row=i, column=0, sticky='w')

    entry = tk.Entry(channel_selection_frame, width=10)
    entry.insert(0, channel_names[i])
    entry.grid(row=i, column=1, padx=5)
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
fig, ax = plt.subplots()

# Figure'ü tkinter penceresine gömmek için canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Verileri güncellemek için fonksiyon
def update_data(frame):
    if ser.in_waiting > 0:
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
            ax.set_title('Selected Channels')
            ax.set_xlabel('Sample')
            ax.set_ylabel('Value')
            ax.legend(loc='upper right')

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
