import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
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

        # Graph area initialization (Moved up)
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='#2f2f2f')  # Set the figure background color to gray
        self.ax = self.fig.add_subplot(111, facecolor='#3f3f3f')  # Set the axes background color to a slightly darker gray

        # Updated to handle 10 channels
        self.selected_channels = []
        self.channel_names = [f"Channel {i+1}" for i in range(10)]  # 10 channel names
        self.channel_vars = [tk.IntVar() for _ in range(len(self.channel_names))]  # Variables to track selected channels
        self.channel_entries = []  # Will hold entry widgets for channel names

        # Create the main layout frames
        main_frame = tk.Frame(self.root, bg='#1c1c1c')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top bar for LiveDataStream logo, Time, and X-Y Limit inputs
        top_bar = tk.Frame(main_frame, bg='#333', height=50)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        logo = tk.Label(top_bar, text="LiveDataStream", bg='#333', fg='pink', font=("Arial", 16))
        logo.pack(side=tk.LEFT, padx=10)

        self.time_display = TimeDisplay(top_bar, bg='#333', fg='pink', font=("Arial", 12))
        self.time_display.time_label.pack(side=tk.RIGHT, padx=10)

        # X-Y Control Frame in the top bar
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

        # Left sidebar for controls
        left_frame = tk.Frame(main_frame, bg='#333', width=150)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Graph area (graph_frame) setup (Using previously defined self.fig and self.ax)
        graph_frame = tk.Frame(main_frame, bg='#1c1c1c')
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Right sidebar for channel selection and terminal
        right_frame = tk.Frame(main_frame, bg='#333', width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

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

        # Terminal Area (moved below connection info)
        terminal_label = tk.Label(left_frame, text="Terminal:", bg='#333', fg='pink', font=("Arial", 14))
        terminal_label.pack(anchor='w', pady=(10, 5))

        self.terminal = ScrolledText(left_frame, wrap=tk.WORD, width=25, height=15, bg='#2A2B45', fg='white', font=("Arial", 10), bd=0, padx=5, pady=5)
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Setup Channel Controls in the right sidebar using ChannelActivities
        self.setup_channel_controls(right_frame)

        # Clear Graph Button at the bottom of the right frame
        clear_button = tk.Button(right_frame, text="Clear Graph", bg='#555', fg='pink', command=self.clear_graph, height=2)
        clear_button.pack(side=tk.BOTTOM, pady=10)

        # Average Feature sınıfını başlatma
        self.average_feature = AverageFeature(
            self.channel_activities,
            self.ax,
            self.x_start_entry,
            self.x_end_entry,
            self.y_start_entry,
            self.y_end_entry,
            self.canvas
        )

        # Average Calculation Controls
        average_label = tk.Label(right_frame, text="Average of N Channels:", bg='#333', fg='pink', font=("Arial", 12))
        average_label.pack(anchor='w', pady=(10, 5))
        self.average_entry = tk.Entry(right_frame, width=10)
        self.average_entry.pack(anchor='w', pady=(5, 5))

        calculate_button = tk.Button(right_frame, text="Calculate and Plot", bg='#456', fg='pink',
                                     command=lambda: self.average_feature.calculate_and_plot_average(
                                         self.average_entry,
                                         self.selected_channels,
                                         self.channel_vars
                                     ))
        calculate_button.pack(anchor='w', pady=(5, 10))

        # Initialize serial port
        self.serial_conn.refresh_ports(self.port_combobox)

        # Start reading the serial data in real-time
        self.serial_conn.read_serial_data(self.terminal, self.data_list, self.update_graph, self.root)

        self.root.mainloop()

    def setup_channel_controls(self, parent_frame):
        """Setup the channel selection controls in the given frame."""
        channel_label = tk.Label(parent_frame, text="Select Channels:", bg='#333', fg='pink', font=("Arial", 14))
        channel_label.pack(anchor='w', pady=(10, 5))

        for idx, channel_name in enumerate(self.channel_names):
            checkbox = tk.Checkbutton(parent_frame, text=channel_name, variable=self.channel_vars[idx], bg='#333', fg='pink', font=("Arial", 12))
            checkbox.pack(anchor='w', padx=5, pady=2)
            self.channel_entries.append(checkbox)

    def update_graph(self):
        """Seçilen kanalların grafiğini güncelle."""
        if self.data_list:
            # Yeni gelen veriyi dosyaya ekle
            self.channel_activities.add_channel_data_to_file(self.data_list[-1])
            self.data_list.clear()  # Veriyi dosyaya kaydettikten sonra listeyi temizle

            self.ax.clear()  # Grafiği temizle

            # Eğer ortalama özelliği aktif değilse seçilen tüm kanalları çiz
            if not self.average_feature.average_active:
                self.selected_channels = [i for i, var in enumerate(self.channel_vars) if var.get()]
                if self.selected_channels:
                    for channel in self.selected_channels:
                        self.plot_selected_channel(channel)
                else:
                    # Eğer hiç kanal seçilmemişse, varsayılan olarak ilk kanalı çiz
                    self.plot_selected_channel(0)
            else:
                # Ortalama özelliği aktifse ortalamayı ve seçili kanalı çiz
                self.average_feature.calculate_and_plot_average(
                    self.average_entry,
                    self.selected_channels,
                    self.channel_vars
                )

            self.canvas.draw()

    def plot_selected_channel(self, channel):
        """Seçilen kanalın verilerini dosyadan okuyup çiz."""
        try:
            data = pd.read_csv('channel_data.csv', header=None)
            channel_data = data.iloc[:, channel].values
    
            # Seçilen kanalın verilerini grafiğe ekle
            self.ax.plot(channel_data, label=f"Kanal {channel + 1}")
    
            self.ax.legend()
    
            # Kullanıcı girişine göre X ve Y eksen limitlerini ayarla
            try:
                x_start = int(self.x_start_entry.get())
                x_end = int(self.x_end_entry.get())
                self.ax.set_xlim([x_start, x_end])
            except ValueError:
                pass  # Eğer giriş geçerli bir sayı değilse, yok say
            
            try:
                y_start = int(self.y_start_entry.get())
                y_end = int(self.y_end_entry.get())
                self.ax.set_ylim([y_start, y_end])
            except ValueError:
                pass  # Eğer giriş geçerli bir sayı değilse, yok say
            
        except Exception as e:
            print(f"Veri çiziminde hata: {e}")
    
    
    def clear_graph(self):
        """Grafiği temizle ve veri listesini sıfırla."""
        self.data_list.clear()
        self.ax.clear()
        self.ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
        self.average_feature.average_active = False
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImportFromSerial(root)
