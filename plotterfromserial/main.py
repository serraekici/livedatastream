import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
from serial_connection import SerialConnection
from time_manager import TimeDisplay

class ImportFromSerial:

    def __init__(self, root):
        self.root = root
        self.root.title("Red Screen Data Plotter")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1c1c1c')

        self.serial_conn = SerialConnection()
        self.data_list = []

        # UI Elements and Main Frames
        appbar = tk.Frame(root, relief=tk.RAISED, bd=2, bg='#333', highlightbackground='#555', highlightthickness=1)
        appbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        logo = tk.Label(appbar, text="LiveDataStream", bg='#333', fg='white', font=("Arial", 16))
        logo.pack(side=tk.LEFT, padx=10)

        self.time_display = TimeDisplay(self.root, bg='#1c1c1c', fg='pink', font=("Arial", 12))
        
        # Create the indicator_circle and connection_indicator (a canvas element, for example)
        connection_indicator = tk.Canvas(self.root, width=20, height=20, bg='#1c1c1c', highlightthickness=0)
        connection_indicator.pack(side=tk.TOP, pady=1)
        indicator_circle = connection_indicator.create_oval(5, 5, 15, 15, fill='red')

        # Create a Label for connection status
        connection_status = tk.Label(self.root, text="Disconnected", fg='red', bg='#1c1c1c', font=("Arial", 12))
        connection_status.pack(side=tk.TOP, pady=10)

        # X-Y Control Frame
        xy_control_frame = tk.Frame(root, bg='#333')
        xy_control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        x_start_label = tk.Label(xy_control_frame, text="X Start:", bg='#333', fg='white', font=("Arial", 12))
        x_start_label.pack(side=tk.LEFT, padx=5)
        self.x_start_entry = tk.Entry(xy_control_frame, width=5)
        self.x_start_entry.pack(side=tk.LEFT, padx=5)

        x_end_label = tk.Label(xy_control_frame, text="X End:", bg='#333', fg='white', font=("Arial", 12))
        x_end_label.pack(side=tk.LEFT, padx=5)
        self.x_end_entry = tk.Entry(xy_control_frame, width=5)
        self.x_end_entry.pack(side=tk.LEFT, padx=5)

        y_start_label = tk.Label(xy_control_frame, text="Y Start:", bg='#333', fg='white', font=("Arial", 12))
        y_start_label.pack(side=tk.LEFT, padx=5)
        self.y_start_entry = tk.Entry(xy_control_frame, width=5)
        self.y_start_entry.pack(side=tk.LEFT, padx=5)

        y_end_label = tk.Label(xy_control_frame, text="Y End:", bg='#333', fg='white', font=("Arial", 12))
        y_end_label.pack(side=tk.LEFT, padx=5)
        self.y_end_entry = tk.Entry(xy_control_frame, width=5)
        self.y_end_entry.pack(side=tk.LEFT, padx=5)
        
        # Seri port bağlantısını kur
        self.serial_conn.connect_to_port(connection_indicator, indicator_circle, connection_status, self.root)

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ani = animation.FuncAnimation(self.fig, self.update_data, interval=1000, cache_frame_data=False)

        self.root.mainloop()

    def update_data(self, frame):
        data = self.serial_conn.read_data()
        if data:
            values = data.split(',')
            if all(v.replace('.', '', 1).isdigit() for v in values):
                self.data_list.append([float(v) for v in values])

            if self.data_list:
                data_array = np.array(self.data_list, dtype=float)
                self.ax.clear()
                self.ax.plot(data_array)  # Simply plot the data without any specific channel logic

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

                # Redraw the canvas
                self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImportFromSerial(root)
