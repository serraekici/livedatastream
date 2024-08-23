import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
from serial_connection import SerialConnection
from time_manager import TimeDisplay
from channel_activities import ChannelActivities

class ImportFromSerial:

    def __init__(self, root):
        self.root = root
        self.root.title("Red Screen Data Plotter")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1c1c1c')

        self.serial_conn = SerialConnection()
        self.channel_activities = ChannelActivities(self)
        self.data_list = []
        
        # Updated to handle 10 channels
        self.selected_channels = []
        self.channel_names = [f"Channel {i+1}" for i in range(10)]  # 10 channel names
        self.channel_vars = [tk.IntVar() for _ in range(len(self.channel_names))]  # Variables to track selected channels
        self.channel_entries = []  # Will hold entry widgets for channel names

        # Create the main layout frames
        main_frame = tk.Frame(self.root, bg='#1c1c1c')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top bar for LiveDataStream logo and Time
        top_bar = tk.Frame(main_frame, bg='#333', height=50)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        logo = tk.Label(top_bar, text="LiveDataStream", bg='#333', fg='pink', font=("Arial", 16))
        logo.pack(side=tk.LEFT, padx=10)

        self.time_display = TimeDisplay(top_bar, bg='#333', fg='pink', font=("Arial", 12))
        self.time_display.time_label.pack(side=tk.RIGHT, padx=10)

        # Left sidebar for controls
        left_frame = tk.Frame(main_frame, bg='#333', width=150)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Right sidebar for channel selection and graph control
        right_frame = tk.Frame(main_frame, bg='#333', width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Graph area
        graph_frame = tk.Frame(main_frame, bg='#1c1c1c')
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Port Selection Elements
        port_label = tk.Label(left_frame, text="Select Port", bg='#333', fg='pink', font=("Arial", 14))
        port_label.pack(anchor='w', pady=(10, 5))

        self.port_combobox = ttk.Combobox(left_frame, state="readonly", width=10)
        self.port_combobox.pack(fill=tk.X, pady=(0, 5))

        refresh_button = tk.Button(left_frame, text="Refresh", command=lambda: self.serial_conn.refresh_ports(self.port_combobox), bg='#555', fg='pink', width=8)
        refresh_button.pack(fill=tk.X, pady=(0, 10))

        baudrate_label = tk.Label(left_frame, text="Baud Rate", bg='#333', fg='pink', font=("Arial", 14))
        baudrate_label.pack(anchor='w', pady=(10, 5))

        self.baudrate_combobox = ttk.Combobox(left_frame, values=[1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400], state="readonly", width=10)
        self.baudrate_combobox.current(9)
        self.baudrate_combobox.pack(fill=tk.X, pady=(0, 5))
        
        connect_button = tk.Button(left_frame, text="Connect", bg='#456', fg='pink', width=8, 
                                   command=lambda: self.serial_conn.connect_to_port(
                                       self.port_combobox.get(),
                                       self.baudrate_combobox.get(),
                                       self.connection_status,
                                       self.connection_indicator,
                                       self.indicator_circle,
                                       self.root))
        connect_button.pack(fill=tk.X, pady=(5, 5))

        disconnect_button = tk.Button(left_frame, text="Disconnect", bg='#456', fg='pink', width=8,
                                      command=lambda: self.serial_conn.disconnect_from_port(
                                          self.connection_status,
                                          self.connection_indicator,
                                          self.indicator_circle,
                                          self.root))
        disconnect_button.pack(fill=tk.X, pady=(5, 5))

        # Connection Status Indicator
        self.connection_status = tk.Label(left_frame, text="Disconnected", bg='#333', fg='red', font=("Arial", 12))
        self.connection_status.pack(pady=(5, 5))

        self.connection_indicator = tk.Canvas(left_frame, width=20, height=20, bg='#333', highlightthickness=0)
        self.indicator_circle = self.connection_indicator.create_oval(2, 2, 18, 18, fill='red')
        self.connection_indicator.pack(pady=(5, 10))

        # Channel Selection on the right sidebar
        tk.Label(right_frame, text="Select Channels:", bg='#333', fg='pink', font=("Arial", 14)).pack(anchor='w', pady=(10, 5))

        for idx, name in enumerate(self.channel_names):
            channel_check = tk.Checkbutton(right_frame, text=name, variable=self.channel_vars[idx], bg='#333', fg='pink', 
                                           selectcolor='blue', command=self.channel_activities.update_selected_channels)
            channel_check.pack(anchor='w', padx=10)
            entry = tk.Entry(right_frame, width=15)
            entry.insert(0, name)
            entry.bind('<Return>', lambda event, idx=idx: self.channel_activities.update_channel_name(idx, event))
            entry.pack(anchor='w', padx=20, pady=2)
            self.channel_entries.append(entry)

        # X-Y Control Frame in the right sidebar
        xy_control_frame = tk.Frame(right_frame, bg='#333')
        xy_control_frame.pack(fill=tk.X, pady=(10, 10))

        x_start_label = tk.Label(xy_control_frame, text="X Start:", bg='#333', fg='pink', font=("Arial", 12))
        x_start_label.pack(side=tk.LEFT, padx=5)
        self.x_start_entry = tk.Entry(xy_control_frame, width=5)
        self.x_start_entry.pack(side=tk.LEFT, padx=5)

        x_end_label = tk.Label(xy_control_frame, text="X End:", bg='#333', fg='pink', font=("Arial", 12))
        x_end_label.pack(side=tk.LEFT, padx=5)
        self.x_end_entry = tk.Entry(xy_control_frame, width=5)
        self.x_end_entry.pack(side=tk.LEFT, padx=5)

        y_start_label = tk.Label(xy_control_frame, text="Y Start:", bg='#333', fg='pink', font=("Arial", 12))
        y_start_label.pack(side=tk.LEFT, padx=5)
        self.y_start_entry = tk.Entry(xy_control_frame, width=5)
        self.y_start_entry.pack(side=tk.LEFT, padx=5)

        y_end_label = tk.Label(xy_control_frame, text="Y End:", bg='#333', fg='pink', font=("Arial", 12))
        y_end_label.pack(side=tk.LEFT, padx=5)
        self.y_end_entry = tk.Entry(xy_control_frame, width=5)
        self.y_end_entry.pack(side=tk.LEFT, padx=5)

        # Clear Graph Button
        clear_button = tk.Button(right_frame, text="Clear Graph", bg='#555', fg='pink', width=15,height=5, command=self.clear_graph)
        clear_button.pack(anchor='w', pady=(10, 1))

        # Initialize serial port
        self.serial_conn.refresh_ports(self.port_combobox)

        # Create the graph in the graph frame
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='#2f2f2f')  # Set the figure background color to gray
        self.ax = self.fig.add_subplot(111, facecolor='#3f3f3f')  # Set the axes background color to a slightly darker gray
        self.ax.grid(True, color='gray', linestyle='--', linewidth=0.5)  # Adding a dark gray grid
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Start the animation for updating data
        self.ani = animation.FuncAnimation(self.fig, self.update_data, interval=1, cache_frame_data=False)

        self.root.mainloop()

    def update_data(self, frame=None):
        data = self.serial_conn.read_data()
        if data:
            values = data.split(',')
            if all(v.replace('.', '', 1).isdigit() for v in values):
                self.data_list.append([float(v) for v in values])

            if self.data_list:
                data_array = np.array(self.data_list, dtype=float)
                self.ax.clear()
                
                # Add grid to the graph
                self.ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
                
                # Plot only selected channels
                for channel in self.selected_channels:
                    self.ax.plot(data_array[:, channel], label=self.channel_names[channel])

                self.ax.legend()
                # Set X and Y axis limits based on user input
                try:
                    x_start = int(self.x_start_entry.get())
                    x_end = int(self.x_end_entry.get())
                    self.ax.set_xlim([x_start, x_end])
                except ValueError:
                    pass  # Ignore if the input is not a valid integer

                try:
                    y_start = int(self.y_start_entry.get())
                    y_end = int(self.y_end_entry.get())
                    self.ax.set_ylim([y_start, y_end])
                except ValueError:
                    pass  # Ignore if the input is not a valid integer

                self.canvas.draw()

    def clear_graph(self):
        """Clear the graph and reset the data list."""
        self.data_list.clear()
        self.ax.clear()
        self.ax.grid(True, color='gray', linestyle='--', linewidth=1)  # Re-add the grid after clearing
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImportFromSerial(root)
