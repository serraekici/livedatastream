import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

class UIManager:
    def __init__(self, root, ax, canvas, settings):
        self.root = root
        self.ax = ax
        self.canvas = canvas
        self.settings = settings
        self.port_combobox = None
        self.baud_combobox = None
        self.connect_button = None
        self.disconnect_button = None
        self.clear_button = None
        self.terminal_output = None
        self.channel_checkbuttons = []
        self.setup_ui_elements()
        self.last_update_time = time.time()
        self.start_graph_updates()

    def setup_ui_elements(self):
        # Frame for serial port controls
        control_frame = tk.Frame(self.root, bg='#1c1c1c')
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
    
        # Port selection dropdown
        port_label = tk.Label(control_frame, text="Select Port", bg='#1c1c1c', fg='white')
        port_label.pack(anchor=tk.W)
    
        self.port_combobox = ttk.Combobox(control_frame)
        self.port_combobox.pack(anchor=tk.W, pady=5)
    
        # Button to refresh port list
        refresh_button = tk.Button(control_frame, text="Refresh COM Port List", command=self.refresh_ports)
        refresh_button.pack(anchor=tk.W, pady=5)
    
        # Baud rate selection dropdown
        baud_label = tk.Label(control_frame, text="Baud Rate", bg='#1c1c1c', fg='white')
        baud_label.pack(anchor=tk.W)
    
        self.baud_combobox = ttk.Combobox(control_frame, values=["9600", "19200", "38400", "57600", "115200"])
        self.baud_combobox.current(4)  # Default to 115200 baud
        self.baud_combobox.pack(anchor=tk.W, pady=5)
    
        # Connect and Disconnect buttons
        self.connect_button = tk.Button(control_frame, text="Connect", bg='#456', fg='white', command=self.connect_to_port)
        self.connect_button.pack(anchor=tk.W, pady=5)
    
        self.disconnect_button = tk.Button(control_frame, text="Disconnect", bg='#456', fg='white', command=self.disconnect_from_port)
        self.disconnect_button.pack(anchor=tk.W, pady=5)
    
        # Clear Graph button
        self.clear_button = tk.Button(control_frame, text="Clear Graph", bg='#456', fg='white', command=self.clear_graph)
        self.clear_button.pack(anchor=tk.W, pady=5)
    
        # Terminal Output
        terminal_label = tk.Label(control_frame, text="Terminal Output:", bg='#1c1c1c', fg='white')
        terminal_label.pack(anchor=tk.W, pady=10)
    
        self.terminal_output = tk.Text(control_frame, height=15, width=40, bg='black', fg='white')
        self.terminal_output.pack(anchor=tk.W)
    
        # Refresh ports on startup
        self.refresh_ports()


    def refresh_ports(self):
        ports = self.settings.serial_conn.list_serial_ports()
        self.port_combobox['values'] = ports
        if ports:
            self.port_combobox.current(0)
        print(f"Available ports: {ports}")

    def connect_to_port(self):
        selected_port = self.port_combobox.get()
        baudrate = self.baud_combobox.get()
        if selected_port:
            self.settings.serial_conn.connect_to_port(selected_port, baudrate, None, None, None, self.root)
            self.terminal_output.insert(tk.END, f"Connected to {selected_port}\n")

    def disconnect_from_port(self):
        self.settings.serial_conn.disconnect_from_port()
        self.terminal_output.insert(tk.END, "Disconnected from the current port\n")

    def clear_graph(self):
        self.ax.clear()
        self.canvas.draw()
        self.terminal_output.insert(tk.END, "Graph cleared\n")

    def toggle_grid(self):
        self.ax.grid(self.settings.grid_on.get(), color='#888888', linestyle='--', linewidth=0.5)
        self.canvas.draw()

    def update_selected_channels(self):
        selected_channels = [i for i, var in enumerate(self.channel_checkbuttons) if var.get()]
        self.settings.selected_channels = selected_channels
        self.update_graph()

    def start_graph_updates(self):
        self.update_graph()

    def update_graph(self):
        current_time = time.time()
        if current_time - self.last_update_time > 0.5:  # 500ms debounce time
            data = self.settings.serial_conn.read_data()
            if data:
                self.terminal_output.insert(tk.END, f"Received data: {data}\n")
                self.terminal_output.see(tk.END)  # Auto-scroll to the latest data
                self.settings.update_data(None)
            
            self.last_update_time = current_time
        self.root.after(100, self.update_graph)  # Schedule the next update
