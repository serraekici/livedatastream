import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# Port açılımı
ser = serial.Serial(baudrate=115200, timeout=1)

# Verileri depolamak için liste
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
root.geometry("800x600")  # Pencere boyutunu belirleyelim
root.configure(bg='#54544e')

# Grid durumu
grid_on = tk.BooleanVar(value=True)  # Grid'in açık/kapalı durumunu tutan değişken

# Kullanıcıya seçim sunmak için pop-up penceresi
def user_selection():
    selection_window = tk.Toplevel(root)
    selection_window.title("Veri Kaynağı Seçimi")
    
    tk.Label(selection_window, text="Veri Kaynağınızı Seçin:", font=("Arial", 14)).pack(pady=10)
    
    def from_file():
        selection_window.destroy()
        file_path = filedialog.askopenfilename(title="Veri Dosyasını Seçin")
        if file_path:
            load_data_from_file(file_path)
    
    def from_serial():
        selection_window.destroy()
        root.deiconify()  # Ana pencereyi göster

    tk.Button(selection_window, text="Dosyadan Aktarım", command=from_file, width=30).pack(pady=10)
    tk.Button(selection_window, text="USB Serial Device", command=from_serial, width=30).pack(pady=10)
    
    selection_window.geometry("300x200")
    selection_window.grab_set()  # Pop-up penceresi odaklı
    root.withdraw()  # Ana pencereyi gizler
    selection_window.mainloop()

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
        root.quit()

# Statik veriyi grafikte gösterme
def plot_static_data():
    ax.clear()
    data_array = np.array(data_list, dtype=float)
    for channel in range(num_channels):
        ax.plot(data_array[:, channel], label=channel_names[channel], linewidth=3)  # Linewidth artırıldı
    ax.set_title('Loaded Data from File', color='white')
    ax.set_xlabel('Sample', color='white')
    ax.set_ylabel('Value', color='white')
    ax.legend(loc='upper right', facecolor='#3f3f3f')
    ax.grid(grid_on.get())
    canvas.draw()

# Canlı veri takibi
def update_data(frame):
    if ser.is_open and ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print(f"data: {data}")
        values = data.split(',')
        
        if all(v.replace('.', '', 1).isdigit() for v in values) and len(values) == num_channels:
            data_list.append([float(v) for v in values])
            update_terminal(data)  # Terminal verilerini güncelle
        
        if len(data_list) > 0:
            data_array = np.array(data_list, dtype=float)
            ax.clear()
            line_style = get_line_style()
            for channel in selected_channels:
                ax.plot(data_array[:, channel], label=channel_names[channel], linestyle=line_style, linewidth=3)  # Linewidth artırıldı
            ax.set_title('Selected Channels', color='white')
            ax.set_xlabel('Sample', color='white')
            ax.set_ylabel('Value', color='white')
            ax.legend(loc='upper right', facecolor='#3f3f3f')
            ax.grid(grid_on.get())

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
    terminal_text.config(state='normal')  # Düzenlemeyi aç
    terminal_text.insert(tk.END, f"Data: {data}\n")
    terminal_text.see(tk.END)  # Scroll'u sona kaydır
    terminal_text.config(state='disabled')  # Düzenlemeyi kapat

# Grafiği ve terminali temizleme fonksiyonu
def clear_graph():
    global data_list
    data_list.clear()  # Verileri temizle
    ax.clear()  # Grafiği temizle
    ax.set_title('Selected Channels', color='white')
    ax.set_xlabel('Sample', color='white')
    ax.set_ylabel('Value', color='white')
    ax.legend(loc='upper right', facecolor='#3f3f3f')
    ax.grid(grid_on.get())
    canvas.draw()
    
    # Terminali temizle
    terminal_text.config(state='normal')
    terminal_text.delete(1.0, tk.END)
    terminal_text.config(state='disabled')

# Arka plan rengini ayarla
root.configure(bg='#54544e')

# Menü çubuğu oluşturma
appbar = tk.Frame(root, relief=tk.RAISED, bd=2, bg='#1e1741')
appbar.pack(side=tk.TOP, fill=tk.X)

# Logo
logo = tk.Label(appbar, text="😎", bg='#1e1741', fg='white', font=("Arial", 16))
logo.pack(side=tk.LEFT, padx=5)

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

# Clear button ekleme
clear_button = tk.Button(appbar, text="Clear", bg='#abab9a', fg='black', command=clear_graph)
clear_button.pack(side=tk.RIGHT, padx=10, pady=5)

# Connect butonu ve durum göstergesi
connect_button = tk.Button(appbar, text="Connect", bg='#abab9a', fg='black', command=lambda: connect_to_port())
connect_button.pack(side=tk.LEFT, padx=5)

connection_status = tk.Label(appbar, text="Disconnected", bg='#1e1741', fg='red')
connection_status.pack(side=tk.LEFT, padx=5)

connection_indicator = tk.Canvas(appbar, width=20, height=20, bg='#1e1741', highlightthickness=0)
connection_indicator.pack(side=tk.LEFT, padx=5)
indicator_circle = connection_indicator.create_oval(2, 2, 18, 18, fill='red')

# Disconnect butonu ekleme
disconnect_button = tk.Button(appbar, text="Disconnect", bg='#abab9a', fg='black', command=lambda: disconnect_from_port())
disconnect_button.pack(side=tk.LEFT, padx=5)

# Kanal seçimi için stil tanımlama
style = ttk.Style()
style.configure("Custom.TCheckbutton", background='#54544e', foreground='white')

# Kanal seçimi için listeyi sol tarafa taşıma
channel_selection_frame = tk.Frame(root, bg='#54544e')
channel_selection_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)

channel_vars = []
channel_entries = []
for i in range(num_channels):
    var = tk.IntVar()
    channel_vars.append(var)
    cb = ttk.Checkbutton(channel_selection_frame, text=f"Channel {i+1}", variable=var, command=lambda: update_selected_channels(), style="Custom.TCheckbutton")
    cb.pack(anchor='w')

    entry = tk.Entry(channel_selection_frame, width=15)  # Genişlik artırıldı
    entry.insert(0, channel_names[i])
    entry.pack(padx=5, pady=2)  # Yüksekliği biraz artırdık
    entry.bind("<KeyRelease>", lambda event, idx=i: update_channel_name(idx, event))
    channel_entries.append(entry)

# Terminal benzeri alanı eklemek için bir Text widget'ı oluşturuyoruz
terminal_frame = tk.Frame(root, bg='#54544e')
terminal_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

terminal_text = tk.Text(terminal_frame, height=15, width=30, bg='#1e1741', fg='white', state='disabled')
terminal_text.pack(fill=tk.BOTH, expand=True)

# Seçilen kanalları güncelleme fonksiyonu
def update_selected_channels():
    global selected_channels
    selected_channels = [i for i, var in enumerate(channel_vars) if var.get() == 1]
    print(f"Selected channels: {selected_channels}")
    update_data(None)

# Kanal isimlerini güncelleme fonksiyonu
def update_channel_name(idx, event):
    channel_names[idx] = channel_entries[idx].get()
    update_data(None)

# Port bağlantısını kurma
def connect_to_port():
    global ser, connection_status, connection_indicator
    port = port_combobox.get()
    baudrate = baudrate_combobox.get()

    if not port:
        messagebox.showerror("Hata", "Lütfen bir seri port seçin.")
        return

    try:
        # Seri bağlantıyı kapalıysa açma
        if ser.is_open:
            ser.close()
        
        # Yeni seri bağlantıyı açma
        ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        connection_status.config(text="Connected", fg='green')
        connection_indicator.itemconfig(indicator_circle, fill='green')
        messagebox.showinfo("Bağlantı Başarıyla Kuruldu", f"{port} portuna bağlantı sağlandı.")
        
    except serial.SerialException as e:
        connection_status.config(text="Disconnected", fg='red')
        connection_indicator.itemconfig(indicator_circle, fill='red')
        messagebox.showerror("Bağlantı Hatası", f"Porta bağlanırken bir hata oluştu: {e}")

# Port bağlantısını kapatma fonksiyonu
def disconnect_from_port():
    global ser, connection_status, connection_indicator
    if ser.is_open:
        ser.close()
        connection_status.config(text="Disconnected", fg='red')
        connection_indicator.itemconfig(indicator_circle, fill='red')
        messagebox.showinfo("Bağlantı Kesildi", "Seri bağlantı güvenli bir şekilde kapatıldı.")

# Line style seçenekleri
def get_line_style():
    styles = {
        'Solid': '-',
        'Dashed': '--',
        'Dotted': ':',
        'Dashdot': '-.'
    }
    return styles.get(line_style_combobox.get(), '-')

# Line style seçimini içeren menüyü oluşturma
line_style_label = tk.Label(appbar, text="Line Style:", bg='#1e1741', fg='white')
line_style_label.pack(side=tk.LEFT, padx=5)

line_style_combobox = ttk.Combobox(appbar, values=['Solid', 'Dashed', 'Dotted', 'Dashdot'], state="readonly")
line_style_combobox.current(0)  # İlk olarak 'Solid' seçili
line_style_combobox.pack(side=tk.LEFT, padx=5)

# Figure oluşturma
fig, ax = plt.subplots(facecolor='#54544e')  # Grafiklerin arka planı biraz daha açık gri
ax.set_facecolor('#abab9a')  # Grafiklerin çizim alanı

# Figure'ü tkinter penceresine gömmek için canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

ani = animation.FuncAnimation(fig, update_data, interval=1000, cache_frame_data=False)

# Pop-up penceresini göster
user_selection()

try:
    root.mainloop()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
