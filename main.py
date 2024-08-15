import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from serial_connection import SerialConnection
from time_manager import TimeManager
from import_from_file import ImportFromFile
from global_settings import GlobalSettings  

# Tkinter Ana Pencere Ayarları
root = tk.Tk()
root.title("Live Data Plotter")
root.geometry("1200x800")
root.configure(bg='#1c1c1c')

settings = GlobalSettings()
settings.serial_conn = SerialConnection()  # Singleton instance
settings.time_manager = TimeManager()  # Singleton instance
settings.grid_on = tk.BooleanVar(value=True)  # BooleanVar tanımı root'tan sonra yapıldı

# Kullanıcıya İlk Ekranı Sunan Fonksiyon
def show_startup_screen():
    startup_screen = tk.Frame(root, bg='#2b2b2b')
    startup_screen.pack(expand=True, fill=tk.BOTH)

    welcome_label = tk.Label(startup_screen, text="Welcome", font=("Arial", 24), fg='white', bg='#2b2b2b')
    welcome_label.pack(pady=(40, 20))

    subtext_label = tk.Label(startup_screen, text="How Can We Help You?", font=("Arial", 12), fg='#bbbbbb', bg='#2b2b2b')
    subtext_label.pack(pady=(0, 40))

    options_frame = tk.Frame(startup_screen, bg='#2b2b2b')
    options_frame.pack(pady=20)

    file_frame = tk.Frame(options_frame, bg='#333', bd=2, relief=tk.RAISED)
    file_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.BOTH, expand=True)

    serial_frame = tk.Frame(options_frame, bg='#333', bd=2, relief=tk.RAISED)
    serial_frame.pack(side=tk.RIGHT, padx=20, pady=10, fill=tk.BOTH, expand=True)

    file_label = tk.Label(file_frame, text="📂", font=("Arial", 64), bg='#333', fg='#5e97f6')
    file_label.pack(pady=(10, 10))

    file_text = tk.Label(file_frame, text="Dosyadan Aktarım", font=("Arial", 14), fg='white', bg='#333')
    file_text.pack()

    serial_label = tk.Label(serial_frame, text="🔌", font=("Arial", 64), bg='#333', fg='#9c27b0')
    serial_label.pack(pady=(10, 10))

    serial_text = tk.Label(serial_frame, text="USB Serial Device", font=("Arial", 14), fg='white', bg='#333')
    serial_text.pack()

    file_frame.bind("<Button-1>", lambda e: start_from_file(startup_screen))
    serial_frame.bind("<Button-1>", lambda e: start_from_serial(startup_screen))

def start_from_file(startup_screen):
    startup_screen.pack_forget()
    import_from_file = ImportFromFile(root, ax, canvas)
    import_from_file.load_data_from_file()
    port_frame.pack_forget()
    connect_frame.pack_forget()
    show_graph()

def start_from_serial(startup_screen):
    startup_screen.pack_forget()
    show_graph()

# Matplotlib Grafiği Kurma
fig, ax = plt.subplots(facecolor='#2b2b2b')
ax.set_facecolor('#abab9a')
ax.grid(True, color='#888888', linestyle='--', linewidth=0.5)

canvas = FigureCanvasTkAgg(fig, master=root)

def show_graph():
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Stil Seçme Fonksiyonu
def get_line_style():
    styles = {
        'Solid': '-',
        'Dashed': '--',
        'Dotted': ':',
        'Dashdot': '-.'
    }
    return styles.get(line_style_combobox.get(), '-')

# Kanal Seçme Fonksiyonu
def update_selected_channels():
    settings.selected_channels = [i for i, var in enumerate(channel_vars) if var.get() == 1]
    update_data(None)

# Kanal İsimlerini Güncelleme Fonksiyonu
def update_channel_name(idx, event):
    settings.channel_names[idx] = channel_entries[idx].get()
    update_data(None)

# Canlı Veri Takibi ve Güncelleme Fonksiyonları
def update_data(frame):
    data = settings.serial_conn.read_data()
    if data:
        values = data.split(',')
        if all(v.replace('.', '', 1).isdigit() for v in values) and len(values) == settings.num_channels:
            settings.data_list.append([float(v) for v in values])
            update_terminal(data)

        if settings.data_list:
            data_array = np.array(settings.data_list, dtype=float)
            ax.clear()
            line_style = get_line_style()
            for channel in settings.selected_channels:
                ax.plot(data_array[:, channel], label=settings.channel_names[channel], linestyle=line_style, linewidth=3)
            ax.set_title('Selected Channels', color='white')
            ax.set_xlabel('Sample', color='white')
            ax.set_ylabel('Value', color='white')
            ax.legend(loc='upper right', facecolor='#3f3f3f')
            ax.grid(settings.grid_on.get(), color='#888888', linestyle='--', linewidth=0.5)

            try:
                ax.set_xlim([int(x_start_entry.get()), int(x_end_entry.get())])
            except ValueError:
                pass

            try:
                ax.set_ylim([int(y_start_entry.get()), int(y_end_entry.get())])
            except ValueError:
                pass

            canvas.draw()

def update_terminal(data):
    terminal_text.config(state='normal')
    terminal_text.insert(tk.END, f"Data: {data}\n")
    terminal_text.see(tk.END)
    terminal_text.config(state='disabled')

def clear_graph():
    settings.data_list.clear()
    ax.clear()
    ax.set_title('Selected Channels', color='white')
    ax.set_xlabel('Sample', color='white')
    ax.set_ylabel('Value', color='white')
    ax.grid(settings.grid_on.get(), color='#888888', linestyle='--', linewidth=0.5)
    canvas.draw()

    terminal_text.config(state='normal')
    terminal_text.delete(1.0, tk.END)
    terminal_text.config(state='disabled')

def refresh_ports():
    ports = settings.serial_conn.list_serial_ports()
    port_combobox['values'] = ports

# UI Elemanları ve Ana Çerçeveler
appbar = tk.Frame(root, relief=tk.RAISED, bd=2, bg='#333', highlightbackground='#555', highlightthickness=1)
appbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

logo = tk.Label(appbar, text="LiveDataStream", bg='#333', fg='white', font=("Arial", 16))
logo.pack(side=tk.LEFT, padx=10)

time_label = tk.Label(appbar, text="", bg='#333', fg='white', font=("Arial", 14))
time_label.pack(side=tk.RIGHT, padx=10)

def update_time():
    current_time = settings.time_manager.update_time()  # Zamanı güncelle
    time_label.config(text=current_time)  # Ekrandaki label'a yaz
    root.after(1000, update_time)  # Bu fonksiyonu 1 saniye sonra tekrar çağır

update_time()  # Zaman güncelleme fonksiyonunu başlat

port_frame = tk.Frame(root, bg='#333')
port_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

port_label = tk.Label(port_frame, text="Select Port", bg='#333', fg='white', font=("Arial", 14))
port_label.pack(pady=(10, 5))

port_combobox = ttk.Combobox(port_frame, values=settings.serial_conn.list_serial_ports(), state="readonly")
port_combobox.pack(fill=tk.X, pady=(0, 5))

refresh_button = tk.Button(port_frame, text="Refresh COM Port List", command=refresh_ports, bg='#555', fg='white')
refresh_button.pack(fill=tk.X, pady=(0, 10))

baudrate_label = tk.Label(port_frame, text="Baud Rate", bg='#333', fg='white', font=("Arial", 14))
baudrate_label.pack(pady=(10, 5))

baudrate_combobox = ttk.Combobox(port_frame, values=[1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400], state="readonly")
baudrate_combobox.current(9)
baudrate_combobox.pack(fill=tk.X, pady=(0, 5))

connect_frame = tk.Frame(port_frame, bg='#333')
connect_frame.pack(pady=(10, 20))

connect_button = tk.Button(connect_frame, text="Connect", command=lambda: settings.serial_conn.connect_to_port(
    port_combobox.get(), baudrate_combobox.get(), connection_status, connection_indicator, indicator_circle, root), bg='#456', fg='white')
connect_button.pack(fill=tk.X, pady=(5, 5))

disconnect_button = tk.Button(connect_frame, text="Disconnect", command=lambda: settings.serial_conn.disconnect_from_port(
    connection_status, connection_indicator, indicator_circle, root), bg='#456', fg='white')
disconnect_button.pack(fill=tk.X, pady=(5, 5))

connection_status = tk.Label(connect_frame, text="Disconnected", bg='#333', fg='red', font=("Arial", 12))
connection_status.pack(pady=(5, 5))

connection_indicator = tk.Canvas(connect_frame, width=20, height=20, bg='#333', highlightthickness=0)
connection_indicator.pack(pady=(5, 10))
indicator_circle = connection_indicator.create_oval(2, 2, 18, 18, fill='red')

terminal_frame = tk.Frame(port_frame, bg='#2b2b2b')
terminal_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

terminal_text = tk.Text(terminal_frame, height=15, width=30, bg='#3e3e3e', fg='white', state='disabled')
terminal_text.pack(fill=tk.BOTH, expand=True)

xy_control_frame = tk.Frame(root, bg='#333')
xy_control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

x_start_label = tk.Label(xy_control_frame, text="X Start:", bg='#333', fg='white')
x_start_label.pack(side=tk.LEFT, padx=5)
x_start_entry = tk.Entry(xy_control_frame, width=5)
x_start_entry.pack(side=tk.LEFT, padx=5)

x_end_label = tk.Label(xy_control_frame, text="X End:", bg='#333', fg='white')
x_end_label.pack(side=tk.LEFT, padx=5)
x_end_entry = tk.Entry(xy_control_frame, width=5)
x_end_entry.pack(side=tk.LEFT, padx=5)

y_start_label = tk.Label(xy_control_frame, text="Y Start:", bg='#333', fg='white')
y_start_label.pack(side=tk.LEFT, padx=5)
y_start_entry = tk.Entry(xy_control_frame, width=5)
y_start_entry.pack(side=tk.LEFT, padx=5)

y_end_label = tk.Label(xy_control_frame, text="Y End:", bg='#333', fg='white')
y_end_entry = tk.Entry(xy_control_frame, width=5)
y_end_entry.pack(side=tk.LEFT, padx=5)

line_style_label = tk.Label(xy_control_frame, text="Line Style:", bg='#333', fg='white')
line_style_label.pack(side=tk.LEFT, padx=5)

line_style_combobox = ttk.Combobox(xy_control_frame, values=['Solid', 'Dashed', 'Dotted', 'Dashdot'], state="readonly")
line_style_combobox.current(0)
line_style_combobox.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(xy_control_frame, text="Clear Graph", bg='#456', fg='white', command=clear_graph)
clear_button.pack(side=tk.RIGHT, padx=10)

grid_switch = ttk.Checkbutton(xy_control_frame, text="Grid On/Off", variable=settings.grid_on, command=lambda: update_data(None))
grid_switch.pack(side=tk.RIGHT, padx=10)

channel_selection_frame = tk.Frame(root, bg='#2b2b2b')
channel_selection_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

channel_vars = []
channel_entries = []
for i in range(settings.num_channels):
    var = tk.IntVar()
    var.set(0) 
    channel_vars.append(var)
    cb = ttk.Checkbutton(channel_selection_frame, text=f"Channel {i+1}", variable=var, command=update_selected_channels)
    cb.pack(anchor='w')

    entry = tk.Entry(channel_selection_frame, width=15)
    entry.insert(0, settings.channel_names[i])
    entry.pack(padx=5, pady=2)
    entry.bind("<KeyRelease>", lambda event, idx=i: update_channel_name(idx, event))
    channel_entries.append(entry)

ani = animation.FuncAnimation(fig, update_data, interval=1000, cache_frame_data=False)

# Başlangıç Ekranını Göster
show_startup_screen()

# Ana Döngü
try:
    root.mainloop()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    if settings.serial_conn.ser.is_open:
        settings.serial_conn.ser.close()
