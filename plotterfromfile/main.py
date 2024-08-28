import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from average_feature import AverageFeature
from time_manager import TimeDisplay
from channel_activities import ChannelActivities


class ImportFromFile:
    print("Application starting...")
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Plotter")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1c1c1c')

        self.channel_activities = ChannelActivities()
        self.data_list = []
        self.channel_entries = []  # channel_entries list

        # Graph area initialization
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='#2f2f2f')
        self.ax = self.fig.add_subplot(111, facecolor='#3f3f3f')

        # Updated to handle 10 channels
        self.selected_channels = []
        self.channel_names = [f"Channel {i+1}" for i in range(10)]
        self.channel_vars = [tk.IntVar() for _ in range(len(self.channel_names))]

        # Create the main layout frames
        main_frame = tk.Frame(self.root, bg='#1c1c1c')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top bar for LiveDataStream logo, Time, and X-Y Limit inputs
        top_bar = tk.Frame(main_frame, bg='#333', height=50)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        logo = tk.Label(top_bar, text="CSV Data Plotter", bg='#333', fg='pink', font=("Arial", 16))
        logo.pack(side=tk.LEFT, padx=10)

        self.time_display = TimeDisplay(top_bar, bg='#333', fg='pink', font=("Arial", 12))
        self.time_display.time_label.pack(side=tk.RIGHT, padx=10)

        # X-Y Control Frame in the top bar
        xy_control_frame = tk.Frame(top_bar, bg='#333')
        xy_control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        x_start_label = tk.Label(xy_control_frame, text="X Start:", bg='#333', fg='pink', font=("Arial", 12))
        x_start_label.pack(side=tk.LEFT, padx=5)

        self.x_start_entry = tk.Entry(xy_control_frame, width=5)
        self.x_start_entry.pack(side=tk.LEFT)

        x_end_label = tk.Label(xy_control_frame, text="X End:", bg='#333', fg='pink', font=("Arial", 12))
        x_end_label.pack(side=tk.LEFT, padx=5)

        self.x_end_entry = tk.Entry(xy_control_frame, width=5)
        self.x_end_entry.pack(side=tk.LEFT)

        y_start_label = tk.Label(xy_control_frame, text="Y Start:", bg='#333', fg='pink', font=("Arial", 12))
        y_start_label.pack(side=tk.LEFT, padx=5)

        self.y_start_entry = tk.Entry(xy_control_frame, width=5)
        self.y_start_entry.pack(side=tk.LEFT)

        y_end_label = tk.Label(xy_control_frame, text="Y End:", bg='#333', fg='pink', font=("Arial", 12))
        y_end_label.pack(side=tk.LEFT, padx=5)

        self.y_end_entry = tk.Entry(xy_control_frame, width=5)
        self.y_end_entry.pack(side=tk.LEFT)

        # Left sidebar for controls
        left_frame = tk.Frame(main_frame, bg='#333', width=150)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        load_csv_button = tk.Button(left_frame, text="Load CSV", bg='#555', fg='pink', command=self.load_csv)
        load_csv_button.pack(anchor='w', pady=(10, 5))

        terminal_label = tk.Label(left_frame, text="Terminal:", bg='#333', fg='pink', font=("Arial", 14))
        terminal_label.pack(anchor='w', pady=(10, 5))

        self.terminal = ScrolledText(left_frame, wrap=tk.WORD, width=25, height=15, bg='#2A2B45', fg='white', font=("Arial", 10), bd=0, padx=5, pady=5)
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Graph display area
        graph_frame = tk.Frame(main_frame, bg='#1c1c1c')
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Right sidebar for channel selection and terminal
        right_frame = tk.Frame(main_frame, bg='#333', width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Setup Channel Controls in the right sidebar using ChannelActivities
        self.setup_channel_controls(right_frame)

        # Clear Graph Button at the bottom of the right frame
        clear_button = tk.Button(right_frame, text="Clear Graph", bg='#555', fg='pink', command=self.clear_graph, height=2)
        clear_button.pack(side=tk.BOTTOM, pady=10)

        # Average Feature initialization
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

    def setup_channel_controls(self, parent_frame):
        """Setup the channel selection controls in the given frame."""
        channel_label = tk.Label(parent_frame, text="Select Channels:", bg='#333', fg='pink', font=("Arial", 14))
        channel_label.pack(anchor='w', pady=(10, 5))

        for idx, channel_name in enumerate(self.channel_names):
            checkbox = tk.Checkbutton(parent_frame, text=channel_name, variable=self.channel_vars[idx], bg='#333', fg='pink', font=("Arial", 12), command=self.update_selected_channels)
            checkbox.pack(anchor='w', padx=5, pady=2)
            self.channel_entries.append(checkbox)

        # Seçilen kanalları göstermek için bir etiket
        self.selected_channels_label = tk.Label(parent_frame, text="", bg='#333', fg='pink', font=("Arial", 12))
        self.selected_channels_label.pack(anchor='w', pady=(10, 5))

    def update_selected_channels(self):
        """Seçilen kanalları güncelle ve UI'da göster."""
        selected_channels_names = [self.channel_names[i] for i, var in enumerate(self.channel_vars) if var.get()]
        self.selected_channels_label.config(text=f"Selected: {', '.join(selected_channels_names)}")
        self.update_graph()

    def load_csv(self):
        """CSV dosyasını yükleyip grafiğe veriyi aktar ve terminalde göster."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            # CSV dosyasını pandas ile okuyup, her sütunu bir kanal olarak işlemek
            self.data_list = pd.read_csv(file_path, header=None).values.tolist()

            # Terminalde dosyadaki verileri göster
            with open(file_path, 'r') as file:
                csv_content = file.read()
                self.terminal.delete(1.0, tk.END)  # Terminali temizle
                self.terminal.insert(tk.END, csv_content)  # CSV içeriğini terminale yaz

            self.update_graph()

    def update_graph(self):
        """Seçilen kanalların grafiğini güncelle."""
        if self.data_list:
            self.ax.clear()

            # Seçilen kanalları tespit et
            self.selected_channels = [i for i, var in enumerate(self.channel_vars) if var.get()]
    
            if self.selected_channels:
                for channel in self.selected_channels:
                    self.plot_selected_channel(channel)
            else:
                # Eğer hiçbir kanal seçilmemişse, varsayılan olarak ilk kanalı çiz
                self.plot_selected_channel(0)
    
            self.canvas.draw()

    def plot_selected_channel(self, channel):
        """Seçilen kanalın verilerini dosyadan okuyup çiz."""
        try:
            # Kanala ait verileri CSV dosyasından okunan veri listesinden alıyoruz
            channel_data = [row[channel] for row in self.data_list]
            # Seçilen kanalın verilerini grafiğe ekle
            self.ax.plot(channel_data, label=f"Channel {channel + 1}")

            # Grafikteki tüm çizgiler için bir gösterge (legend) ekliyoruz
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
       
if __name__ == "__main__":
    print("Initializing main application...")  # Uygulamanın başlangıç kısmını kontrol edelim
    root = tk.Tk()
    app = ImportFromFile(root)
    print("Starting main loop...")  # Main loop'un başladığını kontrol edelim
    root.mainloop()
    print("Application has exited.")  # Uygulamanın kapandığını kontrol edelim
