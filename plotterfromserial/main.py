import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from serial_connection import SerialConnection
from time_manager import TimeDisplay
from channel_activities import ChannelActivities
from average_feature import AverageFeature

class ImportFromSerial:
    def __init__(self, root):
        self.root = root
        self.root.title("Red Screen Data Plotter")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1c1c1c')

        self.serial_conn = SerialConnection()
        self.channel_activities = ChannelActivities()
        self.data_list = []
        self.kalman_filter_active = False

        # GUI components creation
        self.setup_gui()

        # Refresh ports and start reading serial data after GUI is loaded
        self.serial_conn.refresh_ports(self.port_combobox)
        self.serial_conn.read_serial_data(self.terminal, self.data_list, self.channel_activities, self.root)

        # Schedule the first graph update
        self.root.after(1000, self.update_graph)

    def setup_gui(self):
        # Create the plotting area
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='#2f2f2f')
        self.ax = self.fig.add_subplot(111, facecolor='#3f3f3f')

        # Updated for 10 channels
        self.selected_channels = []
        self.channel_names = [f"Channel {i+1}" for i in range(10)]  # 10 channel names
        self.channel_vars = [tk.IntVar() for _ in range(len(self.channel_names))]  # Variables to track channel selection
        self.channel_entries = []  # Widgets for channel checkboxes

        # Create main frames
        main_frame = tk.Frame(self.root, bg='#1c1c1c')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top bar: Logo, Time, and XY Limit Inputs
        top_bar = tk.Frame(main_frame, bg='#333', height=50)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        logo = tk.Label(top_bar, text="LiveDataStream", bg='#333', fg='pink', font=("Arial", 16))
        logo.pack(side=tk.LEFT, padx=10)

        self.time_display = TimeDisplay(top_bar, bg='#333', fg='pink', font=("Arial", 12))
        self.time_display.time_label.pack(side=tk.RIGHT, padx=10)

        # XY Control Frame
        xy_control_frame = tk.Frame(top_bar, bg='#333')
        xy_control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

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

        # Grid
        self.ax.grid(True)

        # Left side bar: Controls
        left_frame = tk.Frame(main_frame, bg='#333', width=150)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

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
        self.baudrate_combobox.current(9)  # Default to 115200
        self.baudrate_combobox.pack(fill=tk.X, pady=(0, 5))

        # Connect Button
        connect_button = tk.Button(left_frame, text="Connect", bg='#456', fg='pink', width=8,
                                   command=lambda: self.serial_conn.connect_to_port(
                                       self.port_combobox.get(),
                                       self.baudrate_combobox.get(),
                                       self.connection_status,
                                       self.connection_indicator,
                                       self.indicator_circle,
                                       self.root))
        connect_button.pack(fill=tk.X, pady=(5, 5))

        # Disconnect Button
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

        # Terminal Area
        terminal_label = tk.Label(left_frame, text="Terminal:", bg='#333', fg='pink', font=("Arial", 14))
        terminal_label.pack(anchor='w', pady=(10, 5))

        self.terminal = ScrolledText(left_frame, wrap=tk.WORD, width=25, height=15, bg='#2A2B45', fg='white', font=("Arial", 10), bd=0, padx=5, pady=5)
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Right side bar: Channel selections, average input, and buttons
        right_frame = tk.Frame(main_frame, bg='#333', width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Channel selection controls
        self.setup_channel_controls(right_frame)

        # Average and Kalman Filter controls
        average_label = tk.Label(right_frame, text="Average last N Channels:", bg='#333', fg='pink', font=("Arial", 12))
        average_label.pack(anchor='w', pady=(10, 5))

        self.average_entry = tk.Entry(right_frame, width=5)
        self.average_entry.pack(anchor='w', padx=5, pady=(0, 5))

        calculate_average_button = tk.Button(right_frame, text="Calculate Average", bg='#555', fg='pink', command=self.calculate_average)
        calculate_average_button.pack(anchor='w', pady=(5, 10), fill=tk.X)

        kalman_filter_button = tk.Button(right_frame, text="Toggle Kalman Filter", bg='#555', fg='pink', command=self.toggle_kalman_filter)
        kalman_filter_button.pack(anchor='w', pady=(5, 10), fill=tk.X)

        clear_button = tk.Button(right_frame, text="Clear Graph", bg='#555', fg='pink', command=self.clear_graph, height=2)
        clear_button.pack(anchor='w', pady=(5, 10), fill=tk.X)

        # Plot area settings
        graph_frame = tk.Frame(main_frame, bg='#1c1c1c')
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize AverageFeature
        self.average_feature = AverageFeature(
            self.channel_activities,
            self.ax,
            self.x_start_entry,
            self.x_end_entry,
            self.y_start_entry,
            self.y_end_entry,
            self.canvas
        )

    def toggle_kalman_filter(self):
        """Toggle the Kalman filter on and off."""
        self.kalman_filter_active = not self.kalman_filter_active
        self.update_graph()

    def setup_channel_controls(self, parent_frame):
        """Setup the channel selection controls in the given frame."""
        channel_label = tk.Label(parent_frame, text="Select Channels:", bg='#333', fg='pink', font=("Arial", 14))
        channel_label.pack(anchor='w', pady=(10, 5))

        for idx, channel_name in enumerate(self.channel_names):
            checkbox = tk.Checkbutton(parent_frame, text=channel_name, variable=self.channel_vars[idx], bg='#333', fg='pink', font=("Arial", 12))
            checkbox.pack(anchor='w', padx=5, pady=2)
            self.channel_entries.append(checkbox)

    def update_graph(self):
        """Update the graph with the latest data."""
        if self.data_list:
            self.ax.clear()  # Clear the plot

            # Plot selected channels
            self.selected_channels = [i for i, var in enumerate(self.channel_vars) if var.get()]
            if not self.selected_channels:
                self.selected_channels = [0]  # Default to first channel if none selected

            for channel in self.selected_channels:
                channel_data = [row[channel] for row in self.data_list if len(row) > channel]
                if self.kalman_filter_active:
                    # Apply Kalman filter
                    filtered_data = [self.average_feature.kalman_filter.filter(value) for value in channel_data]
                    self.ax.plot(filtered_data, label=f"Filtered Channel {channel + 1}", linestyle='--')
                else:
                    self.ax.plot(channel_data, label=f"Channel {channel + 1}")

            # If average is active, plot the average
            if self.average_feature.average_active:
                try:
                    last_n_channels = int(self.average_entry.get())
                    if last_n_channels > 0:
                        average_data = self.channel_activities.calculate_average_of_channels_from_file(last_n_channels)
                        if average_data:
                            self.ax.plot(average_data, label=f"Average of last {last_n_channels} channels", linestyle='--')
                except ValueError:
                    print("Invalid number for averaging.")

            self.ax.legend()

            # Set X and Y axis limits based on user input
            try:
                x_start = int(self.x_start_entry.get())
                x_end = int(self.x_end_entry.get())
                self.ax.set_xlim([x_start, x_end])
            except ValueError:
                pass

            try:
                y_start = float(self.y_start_entry.get())
                y_end = float(self.y_end_entry.get())
                self.ax.set_ylim([y_start, y_end])
            except ValueError:
                pass

            self.ax.grid(True)
            self.canvas.draw()

        # Schedule the next update
        self.root.after(1, self.update_graph)  # Update every second

    def clear_graph(self):
        """Clear the graph and reset data."""
        self.data_list.clear()
        self.terminal.delete('1.0', tk.END)  # Clear terminal
        self.ax.clear()
        self.ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
        self.average_feature.average_active = False
        self.canvas.draw()

    def calculate_average(self):
        """Calculate the average of the last N channels."""
        try:
            num_channels = int(self.average_entry.get())
            if num_channels > 0:
                selected_channels = self.selected_channels
                if not selected_channels:
                    tk.messagebox.showerror("Error", "No channels selected for averaging.")
                    return
                self.average_feature.calculate_and_plot_average(
                    self.average_entry, selected_channels, self.channel_vars
                )
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a valid number for averaging.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImportFromSerial(root)
    root.mainloop()