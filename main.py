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
from channel_activities import ChannelActivities  
from show_startup_screen import ShowStartupScreenSingleton
from line_style import LineStyle

# Tkinter Main Window Settings
root = tk.Tk()
root.title("Live Data Plotter")
root.geometry("1200x800")
root.configure(bg='#1c1c1c')

# GlobalSettings instance
settings = GlobalSettings()
settings.serial_conn = SerialConnection()  
settings.time_manager = TimeManager()  
settings.channel_activities = ChannelActivities(settings)  
settings.grid_on = tk.BooleanVar(value=True)

# UI Elements and Main Frames
appbar = tk.Frame(root, relief=tk.RAISED, bd=2, bg='#333', highlightbackground='#555', highlightthickness=1)
appbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

logo = tk.Label(appbar, text="LiveDataStream", bg='#333', fg='white', font=("Arial", 16))
logo.pack(side=tk.LEFT, padx=10)

# Import Menu
import_button = tk.Menubutton(appbar, text="IMPORT", bg='#333', fg='white', font=("Arial", 14), relief=tk.RAISED)
import_menu = tk.Menu(import_button, tearoff=0)
import_menu.add_command(label="From File", command=lambda: start_from_file())
import_menu.add_command(label="USB Serial Device", command=lambda: start_from_serial())
import_button.config(menu=import_menu)
import_button.pack(side=tk.LEFT, padx=10)

time_label = tk.Label(appbar, text="", bg='#333', fg='white', font=("Arial", 14))
time_label.pack(side=tk.RIGHT, padx=10)

settings.time_manager.update_time(time_label, root)

# Frames that are initially hidden
port_frame = tk.Frame(root, bg='#333')
connect_frame = tk.Frame(port_frame, bg='#333')
terminal_frame = tk.Frame(root, bg='#2b2b2b')
channel_selection_frame = tk.Frame(root, bg='#2b2b2b')

# Port Frame Elements
port_label = tk.Label(port_frame, text="Select Port", bg='#333', fg='white', font=("Arial", 14))
port_combobox = ttk.Combobox(port_frame, values=settings.serial_conn.list_serial_ports(), state="readonly")
refresh_button = tk.Button(port_frame, text="Refresh COM Port List", command=lambda: settings.serial_conn.refresh_ports(port_combobox), bg='#555', fg='white')
baudrate_label = tk.Label(port_frame, text="Baud Rate", bg='#333', fg='white', font=("Arial", 14))
baudrate_combobox = ttk.Combobox(port_frame, values=[1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400], state="readonly")
baudrate_combobox.current(9)

connect_button = tk.Button(connect_frame, text="Connect", bg='#456', fg='white', command=lambda: settings.serial_conn.connect_to_port(
    port_combobox.get(), baudrate_combobox.get(), connection_status, connection_indicator, indicator_circle, root))
disconnect_button = tk.Button(connect_frame, text="Disconnect", bg='#456', fg='white', command=lambda: settings.serial_conn.disconnect_from_port(
    connection_status, connection_indicator, indicator_circle, root))
connection_status = tk.Label(connect_frame, text="Disconnected", bg='#333', fg='red', font=("Arial", 12))
connection_indicator = tk.Canvas(connect_frame, width=20, height=20, bg='#333', highlightthickness=0)
indicator_circle = connection_indicator.create_oval(2, 2, 18, 18, fill='red')

terminal_text = tk.Text(terminal_frame, height=15, width=30, bg='#3e3e3e', fg='white', state='disabled')

# Add elements to port and connect frames
port_label.pack(pady=(10, 5))
port_combobox.pack(fill=tk.X, pady=(0, 5))
refresh_button.pack(fill=tk.X, pady=(0, 10))
baudrate_label.pack(pady=(10, 5))
baudrate_combobox.pack(fill=tk.X, pady=(0, 5))
connect_button.pack(fill=tk.X, pady=(5, 5))
disconnect_button.pack(fill=tk.X, pady=(5, 5))
connection_status.pack(pady=(5, 5))
connection_indicator.pack(pady=(5, 10))
terminal_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

# X-Y Control Frame
xy_control_frame = tk.Frame(root, bg='#333')
xy_control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

x_start_label = tk.Label(xy_control_frame, text="X Start:", bg='#333', fg='white', font=("Arial", 12))
x_start_label.pack(side=tk.LEFT, padx=5)
x_start_entry = tk.Entry(xy_control_frame, width=5)
x_start_entry.pack(side=tk.LEFT, padx=5)

x_end_label = tk.Label(xy_control_frame, text="X End:", bg='#333', fg='white', font=("Arial", 12))
x_end_label.pack(side=tk.LEFT, padx=5)
x_end_entry = tk.Entry(xy_control_frame, width=5)
x_end_entry.pack(side=tk.LEFT, padx=5)

y_start_label = tk.Label(xy_control_frame, text="Y Start:", bg='#333', fg='white', font=("Arial", 12))
y_start_label.pack(side=tk.LEFT, padx=5)
y_start_entry = tk.Entry(xy_control_frame, width=5)
y_start_entry.pack(side=tk.LEFT, padx=5)

y_end_label = tk.Label(xy_control_frame, text="Y End:", bg='#333', fg='white', font=("Arial", 12))
y_end_label.pack(side=tk.LEFT, padx=5)
y_end_entry = tk.Entry(xy_control_frame, width=5)
y_end_entry.pack(side=tk.LEFT, padx=5)

line_style_label = tk.Label(xy_control_frame, text="Line Style:", bg='#333', fg='white', font=("Arial", 12))
line_style_label.pack(side=tk.LEFT, padx=5)

line_style_combobox = ttk.Combobox(xy_control_frame, values=['Solid', 'Dashed', 'Dotted', 'Dashdot'], state="readonly")
line_style_combobox.current(0)
line_style_combobox.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(xy_control_frame, text="Clear Graph", bg='#456', fg='white', command=lambda: clear_graph())
clear_button.pack(side=tk.RIGHT, padx=10)

grid_switch = ttk.Checkbutton(xy_control_frame, text="Grid On/Off", variable=settings.grid_on, command=lambda: update_data(None))
grid_switch.pack(side=tk.RIGHT, padx=10)

# Channel Selection Frame
settings.channel_vars = []
settings.channel_entries = []
for i in range(settings.num_channels):
    var = tk.IntVar(value=0)
    settings.channel_vars.append(var)
    cb = ttk.Checkbutton(channel_selection_frame, text=f"Channel {i+1}", variable=var, command=settings.channel_activities.update_selected_channels)
    cb.pack(anchor='w')

    entry = tk.Entry(channel_selection_frame, width=15)
    entry.insert(0, settings.channel_names[i])
    entry.pack(padx=5, pady=2)
    entry.bind("<KeyRelease>", lambda event, idx=i: settings.channel_activities.update_channel_name(idx, event))
    settings.channel_entries.append(entry)

# Add LineStyle instance to GlobalSettings
settings.line_style = LineStyle(line_style_combobox)

# Store frames in frame_holder
frame_holder = {}

def show_frame(name):
    for frame in frame_holder.values():
        frame.pack_forget()
    frame_holder[name].pack(expand=True, fill=tk.BOTH)

def start_application():
    startup_screen = ShowStartupScreenSingleton(root, start_from_file, start_from_serial)
    startup_screen.show_startup_screen()
    frame_holder["startup"] = startup_screen.startup_screen
    show_frame("startup")

def start_from_serial():
    hide_startup_screen()
    # Display port selection and connection frames
    port_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
    terminal_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)  # Adjusted this to side=tk.LEFT for correct positioning
    connect_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
    show_channel_selection()
    show_frame("graph")

def start_from_file():
    hide_startup_screen()

    import_from_file = ImportFromFile(root, ax, canvas, settings)
    import_from_file.load_data_from_file()

    port_frame.pack_forget()
    connect_frame.pack_forget()
    terminal_frame.pack_forget()
    show_channel_selection()
    show_frame("graph")

    # Update the graph with loaded data
    settings.update_data(None)

def hide_startup_screen():
    frame_holder["startup"].pack_forget()

def show_channel_selection():
    channel_selection_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

# Matplotlib Plot Setup
fig, ax = plt.subplots(facecolor='#2b2b2b')
ax.set_facecolor('#abab9a')
ax.grid(True, color='#888888', linestyle='--', linewidth=0.5)

canvas = FigureCanvasTkAgg(fig, master=root)
frame_holder["graph"] = canvas.get_tk_widget()

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
            line_style = settings.line_style.get_line_style()
            font_dict = {"fontsize": 12, "fontweight": "bold"}
            for channel in settings.selected_channels:
                ax.plot(data_array[:, channel], label=settings.channel_names[channel], linestyle=line_style, linewidth=3)
                ax.set_title('Selected Channels', color='white', fontdict=font_dict)
                ax.set_xlabel('Sample', color='white', fontdict=font_dict)
                ax.set_ylabel('Value', color='white', fontdict=font_dict)
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
    font_dict = {"fontsize": 12, "fontweight": "bold"}
    ax.set_title('Selected Channels', color='white', fontdict=font_dict)
    ax.set_xlabel('Sample', color='white', fontdict=font_dict)
    ax.set_ylabel('Value', color='white', fontdict=font_dict)
    ax.grid(settings.grid_on.get(), color='#888888', linestyle='--', linewidth=0.5)
    canvas.draw()

    terminal_text.config(state='normal')
    terminal_text.delete(1.0, tk.END)
    terminal_text.config(state='disabled')

ani = animation.FuncAnimation(fig, update_data, interval=1, cache_frame_data=False)

if __name__ == "__main__":
    start_application()
    root.mainloop()
