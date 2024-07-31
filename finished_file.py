import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor


class DataGenerator:
    @staticmethod
    def generate_data(num_channels, num_points):
        return np.random.randn(num_channels, num_points)


class GraphManager:
    def __init__(self, canvas_frame):
        self.canvas_frame = canvas_frame
        self.fig = None
        self.axs = []
        self.zoom_limits = {}

    def create_graphs(self, data, start_channel, channels_per_graph, layout, compare=False, compare_channels=[]):
        num_channels, num_points = data.shape
        if layout == 'horizontal':
            fig, axs = plt.subplots(1, channels_per_graph, figsize=(15, 5))
        else:
            fig, axs = plt.subplots(channels_per_graph, 1, figsize=(5, 15))

        axs = [axs] if channels_per_graph == 1 else list(axs)

        for i in range(channels_per_graph):
            ax = axs[i]
            if compare:
                self.plot_compare_data(ax, data, compare_channels, i, num_channels)
            else:
                channel_index = start_channel + i
                if channel_index < num_channels:
                    ax.plot(data[channel_index], label=f'Channel {channel_index}', marker='o')
                    ax.set_facecolor("white")
                    ax.legend()
                    ax.grid(True)
                else:
                    ax.set_visible(False)

        fig.tight_layout()
        return fig, axs

    def plot_compare_data(self, ax, data, compare_channels, i, num_channels):
        if len(compare_channels) > i * 2:
            channel_index1 = compare_channels[i * 2]
            if channel_index1 < num_channels:
                ax.plot(data[channel_index1], label=f'Channel {channel_index1}', marker='o')
            if len(compare_channels) > i * 2 + 1:
                channel_index2 = compare_channels[i * 2 + 1]
                if channel_index2 < num_channels:
                    ax.plot(data[channel_index2], label=f'Channel {channel_index2}', marker='o')
            ax.set_facecolor("white")
            ax.legend()
            ax.grid(True)
        else:
            ax.set_visible(False)

    def enable_zoom(self, canvas):
        def zoom(event):
            ax = event.inaxes
            if not ax:
                return
            xdata, ydata = event.xdata, event.ydata
            scale_factor = 1.1 if event.button == 'up' else 0.9

            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            new_xlim = [xdata - (xdata - cur_xlim[0]) * scale_factor,
                        xdata + (cur_xlim[1] - xdata) * scale_factor]
            new_ylim = [ydata - (ydata - cur_ylim[0]) * scale_factor,
                        ydata + (cur_ylim[1] - ydata) * scale_factor]

            ax.set_xlim(new_xlim)
            ax.set_ylim(new_ylim)

            self.zoom_limits[ax] = {'xlim': new_xlim, 'ylim': new_ylim}
            canvas.draw_idle()

        canvas.mpl_connect('scroll_event', zoom)

    def add_cursor(self, ax):
        cursor = Cursor(ax, useblit=True, color='red', linewidth=1)
        return cursor


class LiveDataApp:
    def __init__(self, root):
        self.root = root
        self.num_channels = 120
        self.num_points = 1
        self.channels_per_graph = 1
        self.compare_mode = False
        self.compare_channels = []
        self.data = DataGenerator.generate_data(self.num_channels, self.num_points)

        self.init_ui()
        self.update_data_continuously()

    def update_data(self):
        new_data = DataGenerator.generate_data(self.num_channels, self.num_points)
        self.data = np.concatenate((self.data, new_data), axis=1)

    def update_graphs(self, val):
        start_channel = int(val) * self.channels_per_graph * 2 if self.compare_mode else int(val) * self.channels_per_graph

        for i in range(self.channels_per_graph):
            ax = self.graph_manager.axs[i]
            ax.clear()
            if self.compare_mode:
                self.graph_manager.plot_compare_data(ax, self.data, self.compare_channels, i, self.num_channels)
            else:
                channel_index = start_channel + i
                if channel_index < self.num_channels:
                    ax.plot(self.data[channel_index], label=f'Channel {channel_index}', marker='o')
                    ax.set_facecolor("white")
                    ax.legend()
                    ax.grid(True)
            if ax in self.graph_manager.zoom_limits:
                ax.set_xlim(self.graph_manager.zoom_limits[ax]['xlim'])
                ax.set_ylim(self.graph_manager.zoom_limits[ax]['ylim'])

        self.graph_manager.fig.tight_layout()
        self.graph_manager.canvas.draw()

    def update_data_continuously(self):
        self.update_data()
        num_points_total = self.data.shape[1]
        num_pages = (num_points_total - 1) // (self.channels_per_graph * 2) + 1
        self.pagination_slider.num_pages = num_pages
        self.pagination_slider.update_dots()
        self.update_graphs(self.pagination_slider.current_page)
        self.after_id = self.root.after(2000, self.update_data_continuously)

    def set_graphs_per_screen(self, value, layout='horizontal', compare=False, compare_channels=[]):
        self.channels_per_graph = int(value)
        self.compare_mode = compare

        self.graph_manager.canvas.get_tk_widget().pack_forget()
        self.graph_manager.fig.clf()

        self.graph_manager.fig, self.graph_manager.axs = self.graph_manager.create_graphs(
            self.data, 0, self.channels_per_graph, layout=layout, compare=self.compare_mode, compare_channels=compare_channels)

        self.graph_manager.canvas = FigureCanvasTkAgg(self.graph_manager.fig, master=self.graph_manager.canvas_frame)
        self.graph_manager.canvas.draw()
        self.graph_manager.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.graph_manager.enable_zoom(self.graph_manager.canvas)

    def update_data_type_label(self, data_type):
        self.data_type_label.config(text=data_type)
        self.update_graphs(self.pagination_slider.current_page)

    def open_compare_dialog(self):
        self.compare_channels = []
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Channels for Comparison")

        tk.Label(dialog, text="Enter two channels to compare (e.g., 0,1):").pack(pady=10)

        entry = tk.Entry(dialog)
        entry.pack(pady=5)

        def submit():
            try:
                channels = list(map(int, entry.get().split(',')))
                if len(channels) == 2 and len(set(channels)) == 2:
                    self.compare_channels = channels
                    dialog.destroy()
                    self.set_graphs_per_screen(self.channels_per_graph, layout='horizontal', compare=True, compare_channels=self.compare_channels)
                else:
                    tk.messagebox.showerror("Input Error", "Please enter exactly two unique channels.")
            except ValueError:
                tk.messagebox.showerror("Input Error", "Please enter valid integers separated by commas.")

        tk.Button(dialog, text="Submit", command=submit).pack(pady=10)

    def disable_compare_mode(self):
        self.compare_channels = []
        self.set_graphs_per_screen(self.channels_per_graph, layout='horizontal', compare=False, compare_channels=self.compare_channels)

    def init_ui(self):
        self.root.title("Live Data Stream")

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.category_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Data Type", menu=self.category_menu)

        self.category_menu.add_command(label="Brain Voltage", command=lambda: self.update_data_type_label("Brain Voltage"))
        self.category_menu.add_command(label="Electrolyte", command=lambda: self.update_data_type_label("Electrolyte"))
        self.category_menu.add_command(label="ex3", command=lambda: self.update_data_type_label("ex3"))

        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)

        for i in range(1, 5):
            self.settings_menu.add_command(label=f"{i} Graph{'s' if i > 1 else ''} Horizontal", 
                                            command=lambda i=i: self.set_graphs_per_screen(i, 'horizontal', self.compare_mode, self.compare_channels))
            self.settings_menu.add_command(label=f"{i} Graph{'s' if i > 1 else ''} Vertical", 
                                            command=lambda i=i: self.set_graphs_per_screen(i, 'vertical', self.compare_mode, self.compare_channels))

        self.compare_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Compare", menu=self.compare_menu)

        self.compare_menu.add_command(label="Enable Compare Mode", command=self.open_compare_dialog)
        self.compare_menu.add_command(label="Disable Compare Mode", command=self.disable_compare_mode)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.graph_manager = GraphManager(self.root)
        self.graph_manager.canvas_frame = tk.Frame(self.root)
        self.graph_manager.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.graph_manager.fig, self.graph_manager.axs = self.graph_manager.create_graphs(
            self.data, 0, self.channels_per_graph, layout='horizontal', compare=self.compare_mode, compare_channels=self.compare_channels)

        self.graph_manager.canvas = FigureCanvasTkAgg(self.graph_manager.fig, master=self.graph_manager.canvas_frame)
        self.graph_manager.canvas.draw()
        self.graph_manager.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.graph_manager.enable_zoom(self.graph_manager.canvas)

        self.data_type_label = tk.Label(self.graph_manager.canvas_frame, text="Data Type", font=("Arial", 20))
        self.data_type_label.pack(side=tk.LEFT, padx=10, pady=10)

        num_pages = (self.data.shape[1] - 1) // (self.channels_per_graph * 2) + 1
        self.pagination_slider = PaginationSlider(self.control_frame, num_pages)
        self.pagination_slider.pack(side=tk.BOTTOM, fill=tk.X)


class PaginationSlider(tk.Frame):
    def __init__(self, parent, num_pages, layout='horizontal', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.num_pages = num_pages
        self.current_page = 0
        self.layout = layout

        self.prev_button = tk.Button(self, text='<', command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.page_dots = []
        self.dot_frame = tk.Frame(self)
        self.dot_frame.pack(side=tk.LEFT)

        for i in range(num_pages):
            dot = tk.Label(self.dot_frame, text='●' if i == self.current_page else '○', font=('Arial', 20))
            dot.pack(side=tk.TOP if layout == 'vertical' else tk.LEFT)
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
            app.update_graphs(self.current_page)

    def next_page(self):
        if self.current_page < self.num_pages - 1:
            self.current_page += 1
            self.update_dots()
            app.update_graphs(self.current_page)


if __name__ == "__main__":
    root = tk.Tk()
    app = LiveDataApp(root)
    root.mainloop()
