import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def generate_data(num_channels, num_points):
    return np.random.randn(num_channels, num_points)

def update_data(num_channels, num_points):
    return generate_data(num_channels, num_points)

def create_graphs(data, start_channel, channels_per_graph=1, layout='horizontal'):
    num_channels, num_points = data.shape
    
    if layout == 'horizontal':
        fig, axs = plt.subplots(1, channels_per_graph, figsize=(15, 5))
    else:  # vertical
        fig, axs = plt.subplots(channels_per_graph, 1, figsize=(5, 15))

    if channels_per_graph == 1:
        axs = [axs]  # Tek bir eksen varsa, listeye dönüştür
    else:
        axs = list(axs)  # Çoklu eksen varsa, listeye dönüştür
    
    for i in range(channels_per_graph):
        channel_index = start_channel + i * 2
        if channel_index + 1 < num_channels:
            axs[i].plot(data[channel_index], label=f'Channel {channel_index}')
            axs[i].plot(data[channel_index + 1], label=f'Channel {channel_index + 1}')
            axs[i].set_facecolor("white")
            axs[i].legend()
        else:
            axs[i].set_visible(False)
    
    fig.tight_layout()  # Grafikleri düzgün hizalamak için
    return fig, axs

def update_graphs(val):
    global canvas, fig, axs, data, num_channels, channels_per_graph, zoom_limits
    start_channel = int(val) * channels_per_graph * 2

    # Verileri güncelle
    for i in range(channels_per_graph):
        channel_index = start_channel + i * 2
        ax = axs[i]
        ax.clear()
        if channel_index + 1 < num_channels:
            ax.plot(data[channel_index], label=f'Channel {channel_index}')
            ax.plot(data[channel_index + 1], label=f'Channel {channel_index + 1}')
            ax.set_facecolor("white")
            ax.legend()
            if ax in zoom_limits:
                ax.set_xlim(zoom_limits[ax]['xlim'])
                ax.set_ylim(zoom_limits[ax]['ylim'])
        else:
            ax.set_visible(False)  # Kullanılmayan eksenleri gizle
    
    fig.tight_layout()  # Grafikleri düzgün hizalamak için
    canvas.draw()

def update_data_continuously():
    global data
    # Veri boyutlarını artırarak eski verilerle birleştiriyoruz
    new_data = update_data(num_channels, num_points)
    data = np.concatenate((data, new_data), axis=1)  # Eski verilerle yeni verileri birleştir
    num_points_total = data.shape[1]  # Toplam veri noktası sayısı
    num_pages = (num_points_total - 1) // (channels_per_graph * 2) + 1  # Sayfa sayısını yeniden hesapla
    pagination_slider.num_pages = num_pages  # Sayfa sayısını güncelle
    update_graphs(pagination_slider.current_page)
    global after_id
    after_id = root.after(1000, update_data_continuously)

def set_graphs_per_screen(value, layout='horizontal'):
    global channels_per_graph, fig, axs, canvas

    channels_per_graph = int(value)
    
    # Eski figür ve eksenleri temizle
    canvas.get_tk_widget().pack_forget()  # Mevcut widget'ı kaldır
    fig.clf()  # Figürün içeriğini temizle

    # Yeni figür ve eksenleri oluştur
    fig, axs = create_graphs(data, 0, channels_per_graph, layout=layout)

    # Canvas'ı yeniden oluştur
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Zoom özelliklerini etkinleştir
    enable_zoom(canvas)

def update_data_type_label(data_type):
    data_type_label.config(text=data_type)
    update_graphs(pagination_slider.current_page)

def enable_zoom(canvas):
    def zoom(event):
        ax = event.inaxes
        if not ax:
            return
        xdata, ydata = event.xdata, event.ydata
        if event.button == 'up':
            scale_factor = 1.1
        elif event.button == 'down':
            scale_factor = 0.9
        else:
            scale_factor = 1

        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()

        new_xlim = [xdata - (xdata - cur_xlim[0]) * scale_factor,
                    xdata + (cur_xlim[1] - xdata) * scale_factor]
        new_ylim = [ydata - (ydata - cur_ylim[0]) * scale_factor,
                    ydata + (cur_ylim[1] - ydata) * scale_factor]

        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)

        zoom_limits[ax] = {'xlim': new_xlim, 'ylim': new_ylim}
        canvas.draw_idle()

    canvas.mpl_connect('scroll_event', zoom)

class PaginationSlider(tk.Frame):
    def __init__(self, parent, num_pages, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.num_pages = num_pages
        self.current_page = 0

        self.prev_button = tk.Button(self, text='<', command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.page_dots = []
        self.dot_frame = tk.Frame(self)
        self.dot_frame.pack(side=tk.LEFT)

        for i in range(num_pages):
            dot = tk.Label(self.dot_frame, text='●' if i == self.current_page else '○', font=('Arial', 20))
            dot.pack(side=tk.LEFT)
            self.page_dots.append(dot)

        self.next_button = tk.Button(self, text='>', command=self.next_page)
        self.next_button.pack(side=tk.LEFT)

        self.update_dots()

    def update_dots(self):
        for i, dot in enumerate(self.page_dots):
            dot.config(text='●' if i == self.current_page else '○')

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_dots()
            update_graphs(self.current_page)

    def next_page(self):
        if self.current_page < self.num_pages - 1:
            self.current_page += 1
            self.update_dots()
            update_graphs(self.current_page)

# Initialize data
num_channels = 120
num_points = 50
channels_per_graph = 1
data = generate_data(num_channels, num_points)

# Create the main window
root = tk.Tk()
root.title("Live Data Stream")

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Veri tipinin barı
category_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Data Type", menu=category_menu)

# Seçenekleri
category_menu.add_command(label="Brain Voltage", command=lambda: update_data_type_label("Brain Voltage"))
category_menu.add_command(label="Electrolyte", command=lambda: update_data_type_label("Electrolyte"))
category_menu.add_command(label="ex3", command=lambda: update_data_type_label("ex3"))

# Create a "Settings" menu
settings_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)

# Add options to the "Settings" menu for number of graphs per screen
settings_menu.add_command(label="1 Graph Horizontal", command=lambda: set_graphs_per_screen(1, 'horizontal'))
settings_menu.add_command(label="2 Graphs Horizontal", command=lambda: set_graphs_per_screen(2, 'horizontal'))
settings_menu.add_command(label="3 Graphs Horizontal", command=lambda: set_graphs_per_screen(3, 'horizontal'))
settings_menu.add_command(label="4 Graphs Horizontal", command=lambda: set_graphs_per_screen(4, 'horizontal'))
settings_menu.add_command(label="1 Graph Vertical", command=lambda: set_graphs_per_screen(1, 'vertical'))
settings_menu.add_command(label="2 Graphs Vertical", command=lambda: set_graphs_per_screen(2, 'vertical'))
settings_menu.add_command(label="3 Graphs Vertical", command=lambda: set_graphs_per_screen(3, 'vertical'))
settings_menu.add_command(label="4 Graphs Vertical", command=lambda: set_graphs_per_screen(4, 'vertical'))

# Create a frame for the controls
control_frame = tk.Frame(root)
control_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Create a frame for the canvas
canvas_frame = tk.Frame(root)
canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Create the initial figure and canvas
fig, axs = create_graphs(data, 0, channels_per_graph)
canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Zoom özelliklerini etkinleştir
zoom_limits = {}
enable_zoom(canvas)

# Create a label for the data type
data_type_label = tk.Label(canvas_frame, text="Data Type", font=("Arial", 20))
data_type_label.pack(side=tk.LEFT, padx=10, pady=10)

# Create the pagination slider
num_pages = (num_channels - 1) // (channels_per_graph * 2) + 1
pagination_slider = PaginationSlider(control_frame, num_pages)
pagination_slider.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# Initialize `after_id` to store the id of the `after` call
after_id = root.after(1000, update_data_continuously)

# Start the Tkinter main loop
root.mainloop()
