import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
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

        # GUI bileşenlerinin oluşturulması
        self.setup_gui()

        # Portları yenileme ve veri okuma işlemleri GUI yüklendikten sonra
        self.serial_conn.refresh_ports(self.port_combobox)
        self.serial_conn.read_serial_data(self.terminal, self.data_list, self.update_graph, self.root)

    def setup_gui(self):
        # Grafik alanı oluşturma
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='#2f2f2f')
        self.ax = self.fig.add_subplot(111, facecolor='#3f3f3f')

        # 10 kanal için güncellendi
        self.selected_channels = []
        self.channel_names = [f"Channel {i+1}" for i in range(10)]  # 10 kanal adı
        self.channel_vars = [tk.IntVar() for _ in range(len(self.channel_names))]  # Kanal seçimlerini takip etmek için değişkenler
        self.channel_entries = []  # Kanal adı giriş widget'ları için

        # Ana çerçevelerin oluşturulması
        main_frame = tk.Frame(self.root, bg='#1c1c1c')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Üst çubuk: Logo, Zaman ve XY Limiti Girdileri
        top_bar = tk.Frame(main_frame, bg='#333', height=50)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        logo = tk.Label(top_bar, text="LiveDataStream", bg='#333', fg='pink', font=("Arial", 16))
        logo.pack(side=tk.LEFT, padx=10)

        self.time_display = TimeDisplay(top_bar, bg='#333', fg='pink', font=("Arial", 12))
        self.time_display.time_label.pack(side=tk.RIGHT, padx=10)

        # XY Kontrol Çerçevesi
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

        # Sol yan çubuk: Kontroller
        left_frame = tk.Frame(main_frame, bg='#333', width=150)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Port Seçim Elemanları
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

        # Bağlanma Butonu
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

        # Bağlantı Durum Göstergesi
        self.connection_status = tk.Label(left_frame, text="Disconnected", bg='#333', fg='red', font=("Arial", 12))
        self.connection_status.pack(pady=(5, 5))

        self.connection_indicator = tk.Canvas(left_frame, width=20, height=20, bg='#333', highlightthickness=0)
        self.indicator_circle = self.connection_indicator.create_oval(2, 2, 18, 18, fill='red')
        self.connection_indicator.pack(pady=(5, 10))

        # Terminal Alanı
        terminal_label = tk.Label(left_frame, text="Terminal:", bg='#333', fg='pink', font=("Arial", 14))
        terminal_label.pack(anchor='w', pady=(10, 5))

        self.terminal = ScrolledText(left_frame, wrap=tk.WORD, width=25, height=15, bg='#2A2B45', fg='white', font=("Arial", 10), bd=0, padx=5, pady=5)
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Sağ yan çubuk: Kanal seçimleri, ortalama girişi ve butonlar
        right_frame = tk.Frame(main_frame, bg='#333', width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Kanal seçim kontrolleri
        self.setup_channel_controls(right_frame)

        # Ortalama ve Kalman Filtresi kontrolleri
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

        # Grafik alanı (graph_frame) ayarları
        graph_frame = tk.Frame(main_frame, bg='#1c1c1c')
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Ortalama hesaplama işlevinin başlatılması
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
        """Grafiği en son verilerle güncelle."""
        if self.data_list:
            self.ax.clear()  # Grafiği temizle

            # Seçilen kanalların verilerini çiz
            self.selected_channels = [i for i, var in enumerate(self.channel_vars) if var.get()]
            if not self.selected_channels:
                self.selected_channels = [0]  # Hiçbiri seçilmediyse varsayılan olarak ilk kanal

            for channel in self.selected_channels:
                channel_data = [row[channel] for row in self.data_list]
                if self.kalman_filter_active:
                    # Kalman filtresi uygula
                    filtered_data = [self.average_feature.kalman_filter.filter(value) for value in channel_data]
                    self.ax.plot(filtered_data, label=f"Filtered Channel {channel + 1}", linestyle='--')
                else:
                    self.ax.plot(channel_data, label=f"Channel {channel + 1}")

            # Eğer ortalama aktifse, ortalama verisini yeniden çiz
            if self.average_feature.average_active:
                # Ortalama verisini yeniden çiz
                last_n_channels = int(self.average_entry.get())
                average_data = self.channel_activities.calculate_average_of_channels_from_file(last_n_channels)
                if average_data:  # Make sure there is data to plot
                    selected_channel = self.selected_channels[0]
                    self.ax.plot(average_data, label=f"Average of last {last_n_channels} channels", linestyle='--')

            self.ax.legend()

            # Kullanıcı girişi baz alınarak X ve Y eksen limitlerini ayarla
            try:
                x_start = int(self.x_start_entry.get())
                x_end = int(self.x_end_entry.get())
                self.ax.set_xlim([x_start, x_end])
            except ValueError:
                pass
            
            try:
                y_start = int(self.y_start_entry.get())
                y_end = int(self.y_end_entry.get())
                self.ax.set_ylim([y_start, y_end])
            except ValueError:
                pass
            
            self.ax.grid(True)  # Grafiği güncelledikten sonra grid'in her zaman görünür olmasını sağla
            self.canvas.draw()  # Güncellenmiş grafikle kanvası yeniden çiz

            # Schedule the next update after a short delay
            self.root.after(1000, self.update_graph)  # Update every second (1000ms)


    def clear_graph(self):
        """Grafiği temizle ve veri listesini sıfırla."""
        self.data_list.clear()
        self.terminal.delete('1.0', tk.END)  # Terminal alanını temizle
        self.ax.clear()
        self.ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
        self.average_feature.average_active = False
        self.canvas.draw()

    def generate_heartbeat_data(self, length):
        """Kalp atışı benzeri bir sinyal simüle eder."""
        time = np.linspace(0, 10, length)
        signal = 0.5 * (np.sin(2 * np.pi * 1.0 * time) + np.sin(2 * np.pi * 2.0 * time) + np.sin(2 * np.pi * 3.0 * time))
        signal += 0.1 * np.random.normal(size=time.shape)  # Gürültü ekleyerek daha gerçekçi hale getirme
        return signal

    def calculate_average(self):
        try:
            num_channels = int(self.average_entry.get())
            if num_channels > 0:
                selected_channel = self.selected_channels[0] if self.selected_channels else 0
                self.average_feature.calculate_and_plot_average(
                    self.average_entry, [selected_channel], self.channel_vars
                )
        except ValueError:
            print("Lütfen geçerli bir sayı girin")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImportFromSerial(root)
    root.mainloop()
