import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import time

# Port açılımı
ser = serial.Serial(baudrate=115200, timeout=1)

# Verileri depolamak için liste
data_list = []
selected_channels = []
num_channels = 10
channel_names = [f'Channel {i+1}' for i in range(num_channels)]

# Tkinter ana penceresi
root = tk.Tk()
root.title("Live Data Plotter")
root.geometry("1200x800")
root.configure(bg='#1c1c1c')

# Grid durumu
grid_on = tk.BooleanVar(value=True)

# Bağlantı durumunu gösteren değişken
connected = False

def animate_connection_indicator():
    if not connected:
        current_color = connection_indicator.itemcget(indicator_circle, "fill")
        next_color = 'green' if current_color == 'red' else 'red'
        connection_indicator.itemconfig(indicator_circle, fill=next_color)
        root.after(500, animate_connection_indicator)

# Kullanıcıya ilk ekranı sunmak için pop-up yerine gelen yeni pencere
def show_startup_screen():
    startup_screen = tk.Frame(root, bg='#2b2b2b')
    startup_screen.pack(expand=True, fill=tk.BOTH)

    # Üst metin
    welcome_label = tk.Label(startup_screen, text="Welcome", font=("Arial", 24), fg='white', bg='#2b2b2b')
    welcome_label.pack(pady=(40, 20))

    subtext_label = tk.Label(startup_screen, text="How Can We Help You?", font=("Arial", 12), fg='#bbbbbb', bg='#2b2b2b')
    subtext_label.pack(pady=(0, 40))

    # Seçenek kutuları
    options_frame = tk.Frame(startup_screen, bg='#2b2b2b')
    options_frame.pack(pady=20)

    def start_from_file():
        startup_screen.pack_forget()
        file_path = filedialog.askopenfilename(title="Veri Dosyasını Seçin")
        if file_path:
            load_data_from_file(file_path)
        # Port girişlerini gizleme
        port_frame.pack_forget()
        connect_frame.pack_forget()
        show_graph()

    def start_from_serial():
        startup_screen.pack_forget()
        show_graph()

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

    file_frame.bind("<Button-1>", lambda e: start_from_file())
    file_label.bind("<Button-1>", lambda e: start_from_file())
    file_text.bind("<Button-1>", lambda e: start_from_file())

    serial_frame.bind("<Button-1>", lambda e: start_from_serial())
    serial_label.bind("<Button-1>", lambda e: start_from_serial())
    serial_text.bind("<Button-1>", lambda e: start_from_serial())

# Grafik alanını gösterme
def show_graph():
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Dosyadan veri yükleme
def load_data_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                values = line.strip().split(',')
                if all(v.replace('.', '', 1).isdigit() for v in values) and len(values) == num_channels:
                    data_list.append([float(v) for v in values])
        plot_static_data()
    except Exception as e:
        messagebox.showerror("Hata", f"Veri dosyasını yüklerken bir hata oluştu: {e}")

# Statik veriyi grafikte gösterme
def plot_static_data():
    ax.clear()
    data_array = np.array(data_list, dtype=float)
    for channel in range(num_channels):
        ax.plot(data_array[:, channel], label=channel_names[channel], linewidth=3)
    ax.set_title('Loaded Data from File', color='white')
    ax.set_xlabel('Sample', color='white')
    ax.set_ylabel('Value', color='white')
    ax.legend(loc='upper right', facecolor='#3f3f3f')
    ax.grid(grid_on.get(), color='#888888', linestyle='--', linewidth=0.5)
    canvas.draw()

# Canlı veri takibi
def update_data(frame):
    if ser.is_open and ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        values = data.split(',')
        
        if all(v.replace('.', '', 1).isdigit() for v in values) and len(values) == num_channels:
            data_list.append([float(v) for v in values])
            update_terminal(data)
        
        if len(data_list) > 0:
            data_array = np.array(data_list, dtype=float)
            ax.clear()
            line_style = get_line_style()
            for channel in selected_channels:
                ax.plot(data_array[:, channel], label=channel_names[channel], linestyle=line_style, linewidth=3)
            ax.set_title('Selected Channels', color='white')
            ax.set_xlabel('Sample', color='white')
            ax.set_ylabel('Value', color='white')
            ax.legend(loc='upper right', facecolor='#3f3f3f')
            ax.grid(grid_on.get(), color='#888888', linestyle='--', linewidth=0.5)

            try:
                x_start = int(x_start_entry.get())
                x_end = int(x_end_entry.get())
                ax.set_xlim([x_start, x_end])
            except ValueError:
                pass

            try:
                y_start = int(y_start_entry.get())
                y_end = int(y_end_entry.get())
                ax.set_ylim([y_start, y_end])
            except ValueError:
                pass

            canvas.draw()

# Terminal verilerini güncelleme fonksiyonu
def update_terminal(data):
    terminal_text.config(state='normal')
    terminal_text.insert(tk.END, f"Data: {data}\n")
    terminal_text.see(tk.END)
    terminal_text.config(state='disabled')

# Grafiği ve terminali temizleme fonksiyonu
def clear_graph():
    global data_list
    data_list.clear()
    ax.clear()
    ax.set_title('Selected Channels', color='white')
    ax.set_xlabel('Sample', color='white')
    ax.set_ylabel('Value', color='white')
    ax.legend(loc='upper right', facecolor='#3f3f3f')
    ax.grid(grid_on.get(), color='#888888', linestyle='--', linewidth=0.5)
    canvas.draw()
    
    terminal_text.config(state='normal')
    terminal_text.delete(1.0, tk.END)
    terminal_text.config(state='disabled')

# Port bağlantısını kurma fonksiyonu
def connect_to_port():
    global ser, connection_status, connection_indicator, connected
    port = port_combobox.get()
    baudrate = baudrate_combobox.get()

    if not port:
        messagebox.showerror("Hata", "Lütfen bir seri port seçin.")
        return

    try:
        if ser.is_open:
            ser.close()
        
        ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        connection_status.config(text="Connected", fg='green')
        connection_indicator.itemconfig(indicator_circle, fill='green')
        connected = True
        messagebox.showinfo("Bağlantı Başarıyla Kuruldu", f"{port} portuna bağlantı sağlandı.")
        
    except serial.SerialException as e:
        connection_status.config(text="Disconnected", fg='red')
        connection_indicator.itemconfig(indicator_circle, fill='red')
        connected = False
        animate_connection_indicator()
        messagebox.showerror("Bağlantı Hatası", f"Porta bağlanırken bir hata oluştu: {e}")

# Port bağlantısını kapatma fonksiyonu
def disconnect_from_port():
    global ser, connection_status, connection_indicator, connected
    if ser.is_open:
        ser.close()
        connection_status.config(text="Disconnected", fg='red')
        connection_indicator.itemconfig(indicator_circle, fill='red')
        connected = False
        animate_connection_indicator()
        messagebox.showinfo("Bağlantı Kesildi", "Seri bağlantı güvenli bir şekilde kapatıldı.")

# Seri portları listeleme fonksiyonu
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Seçilen kanalları güncelleme fonksiyonu
def update_selected_channels():
    global selected_channels
    selected_channels = [i for i, var in enumerate(channel_vars) if var.get() == 1]
    update_data(None)

# Kanal isimlerini güncelleme fonksiyonu
def update_channel_name(idx, event):
    channel_names[idx] = channel_entries[idx].get()
    update_data(None)

# Line style seçenekleri
def get_line_style():
    styles = {
        'Solid': '-',
        'Dashed': '--',
        'Dotted': ':',
        'Dashdot': '-.'
    }
    return styles.get(line_style_combobox.get(), '-')

# Üst menü çubuğu oluşturma
appbar = tk.Frame(root, relief=tk.RAISED, bd=2, bg='#333', highlightbackground='#555', highlightthickness=1)
appbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

# Üst menü içeriği: Logo ve tarih/saat
logo = tk.Label(appbar, text="LiveDataStream", bg='#333', fg='white', font=("Arial", 16))
logo.pack(side=tk.LEFT, padx=10)

def update_time():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    time_label.config(text=current_time)
    root.after(1000, update_time)

time_label = tk.Label(appbar, text="", bg='#333', fg='white', font=("Arial", 14))
time_label.pack(side=tk.RIGHT, padx=10)
update_time()

# Sol dikey menü: Port seçimleri, baudrate, connect/disconnect butonları ve terminal
port_frame = tk.Frame(root, bg='#333')
port_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

port_label = tk.Label(port_frame, text="Select Port", bg='#333', fg='white', font=("Arial", 14))
port_label.pack(pady=(10, 5))

def refresh_ports():
    ports = list_serial_ports()
    port_combobox['values'] = ports

port_combobox = ttk.Combobox(port_frame, values=list_serial_ports(), state="readonly")
port_combobox.pack(fill=tk.X, pady=(0, 5))

refresh_button = tk.Button(port_frame, text="Refresh COM Port List", command=refresh_ports, bg='#555', fg='white')
refresh_button.pack(fill=tk.X, pady=(0, 10))

baudrate_label = tk.Label(port_frame, text="Baud Rate", bg='#333', fg='white', font=("Arial", 14))
baudrate_label.pack(pady=(10, 5))

baudrate_combobox = ttk.Combobox(port_frame, values=[
    1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400
], state="readonly")
baudrate_combobox.current(9)
baudrate_combobox.pack(fill=tk.X, pady=(0, 5))

connect_frame = tk.Frame(port_frame, bg='#333')
connect_frame.pack(pady=(10, 20))

connect_button = tk.Button(connect_frame, text="Connect", command=connect_to_port, bg='#456', fg='white')
connect_button.pack(fill=tk.X, pady=(5, 5))

disconnect_button = tk.Button(connect_frame, text="Disconnect", command=disconnect_from_port, bg='#456', fg='white')
disconnect_button.pack(fill=tk.X, pady=(5, 5))

connection_status = tk.Label(connect_frame, text="Disconnected", bg='#333', fg='red', font=("Arial", 12))
connection_status.pack(pady=(5, 5))

connection_indicator = tk.Canvas(connect_frame, width=20, height=20, bg='#333', highlightthickness=0)
connection_indicator.pack(pady=(5, 10))
indicator_circle = connection_indicator.create_oval(2, 2, 18, 18, fill='red')

# Terminal benzeri alanı eklemek için bir Text widget'ı oluşturuyoruz
terminal_frame = tk.Frame(port_frame, bg='#2b2b2b')
terminal_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

terminal_text = tk.Text(terminal_frame, height=15, width=30, bg='#3e3e3e', fg='white', state='disabled')
terminal_text.pack(fill=tk.BOTH, expand=True)

# Üst menü altındaki XY limitlerini belirlemek için menü
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
y_end_label.pack(side=tk.LEFT, padx=5)
y_end_entry = tk.Entry(xy_control_frame, width=5)
y_end_entry.pack(side=tk.LEFT, padx=5)

line_style_label = tk.Label(xy_control_frame, text="Line Style:", bg='#333', fg='white')
line_style_label.pack(side=tk.LEFT, padx=5)

line_style_combobox = ttk.Combobox(xy_control_frame, values=['Solid', 'Dashed', 'Dotted', 'Dashdot'], state="readonly")
line_style_combobox.current(0)
line_style_combobox.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(xy_control_frame, text="Clear Graph", bg='#456', fg='white', command=clear_graph)
clear_button.pack(side=tk.RIGHT, padx=10)

grid_switch = ttk.Checkbutton(xy_control_frame, text="Grid On/Off", variable=grid_on, command=lambda: update_data(None))
grid_switch.pack(side=tk.RIGHT, padx=10)

# Kanal seçimi için dikey menü
channel_selection_frame = tk.Frame(root, bg='#2b2b2b')
channel_selection_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

channel_vars = []
channel_entries = []
for i in range(num_channels):
    var = tk.IntVar()
    channel_vars.append(var)
    cb = ttk.Checkbutton(channel_selection_frame, text=f"Channel {i+1}", variable=var, command=lambda: update_selected_channels(), style="Custom.TCheckbutton")
    cb.pack(anchor='w')

    entry = tk.Entry(channel_selection_frame, width=15)
    entry.insert(0, channel_names[i])
    entry.pack(padx=5, pady=2)
    entry.bind("<KeyRelease>", lambda event, idx=i: update_channel_name(idx, event))
    channel_entries.append(entry)

# Figure oluşturma
fig, ax = plt.subplots(facecolor='#2b2b2b')
ax.set_facecolor('#abab9a')
ax.grid(True, color='#888888', linestyle='--', linewidth=0.5)

# Figure'ü tkinter penceresine gömmek için canvas
canvas = FigureCanvasTkAgg(fig, master=root)

ani = animation.FuncAnimation(fig, update_data, interval=1000, cache_frame_data=False)

# Bağlantı durumu göstergesini animasyonla renklendirme
animate_connection_indicator()

# Başlangıç ekranını göster
show_startup_screen()

try:
    root.mainloop()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()