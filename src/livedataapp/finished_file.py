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
    def __init__(self, canvas_frame, app):
        self.canvas_frame = canvas_frame
        self.app = app
        self.fig = None
        self.axs = []
        self.zoom_limits = {}
        self.canvas = None

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
        print(f"Created {len(axs)} subplots.")
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

    def update_graphs(self, val):
        if self.fig is None:
            print("Error: Figure is not initialized.")
            return

        start_channel = int(val) * self.app.channels_per_graph * 2 if self.app.compare_mode else int(val) * self.app.channels_per_graph

        for i in range(self.app.channels_per_graph):
            try:
                ax = self.axs[i]
                ax.clear()
                if self.app.compare_mode:
                    self.plot_compare_data(ax, self.app.data, self.app.compare_channels, i, self.app.num_channels)
                else:
                    channel_index = start_channel + i
                    if channel_index < self.app.num_channels:
                        ax.plot(self.app.data[channel_index], label=f'Channel {channel_index}', marker='o')
                        ax.set_facecolor("white")
                        ax.legend()
                        ax.grid(True)
                if ax in self.zoom_limits:
                    ax.set_xlim(self.zoom_limits[ax]['xlim'])
                    ax.set_ylim(self.zoom_limits[ax]['ylim'])
            except IndexError as e:
                print(f"IndexError: {e} - i: {i}, len(self.axs): {len(self.axs)}")

        if self.fig:
            self.fig.tight_layout()
            self.canvas.draw()
        else:
            print("Error: Figure object is None.")

    def set_graphs_per_screen(self, value, layout='horizontal', compare=False, compare_channels=[]):
        self.app.channels_per_graph = int(value)
        self.app.compare_mode = compare

        if self.canvas is not None:
            self.canvas.get_tk_widget().pack_forget()
            self.fig.clf()

        self.fig, self.axs = self.create_graphs(
            self.app.data, 0, self.app.channels_per_graph, layout=layout, compare=self.app.compare_mode, compare_channels=compare_channels)

        if self.fig is None:
            print("Error: Figure was not created.")
            return

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.enable_zoom(self.canvas)

class DataUpdater:
    def __init__(self, app):
        self.app = app

    def update_data(self):
        new_data = DataGenerator.generate_data(self.app.num_channels, self.app.num_points)
        self.app.data = np.concatenate((self.app.data, new_data), axis=1)

    def update_data_continuously(self):
        self.update_data()
        start_channel = (self.app.pagination_slider.current_page - 1) * self.app.channels_per_graph
        self.app.graph_manager.update_graphs(start_channel)
        self.app.after_id = self.app.root.after(2000, self.update_data_continuously)


class InterfaceApplications:
    def __init__(self, root):
        self.root = root
        self.num_channels = 50
        self.num_points = 1
        self.channels_per_graph = 1
        self.compare_mode = False
        self.compare_channels = []
        self.data = DataGenerator.generate_data(self.num_channels, self.num_points)
        

        self.init_ui()
        self.data_updater = DataUpdater(self)
        self.data_updater.update_data_continuously()

    def destroy(self):
        self.root.destroy()

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
                    self.graph_manager.set_graphs_per_screen(self.channels_per_graph, layout='horizontal', compare=True, compare_channels=self.compare_channels)
                else:
                    tk.messagebox.showerror("Input Error", "Please enter exactly two unique channels.")
            except ValueError:
                tk.messagebox.showerror("Input Error", "Please enter valid integers separated by commas.")

        tk.Button(dialog, text="Submit", command=submit).pack(pady=10)

    def disable_compare_mode(self):
        self.compare_channels = []
        self.graph_manager.set_graphs_per_screen(self.channels_per_graph, layout='horizontal', compare=False, compare_channels=self.compare_channels)

    def init_ui(self):
        self.root.title("Live Data Stream")

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.category_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Data Type", menu=self.category_menu)

        self.category_menu.add_command(label="Brain Voltage", command=lambda: self.graph_manager.update_data_type_label("Brain Voltage"))
        self.category_menu.add_command(label="Electrolyte", command=lambda: self.graph_manager.update_data_type_label("Electrolyte"))
        self.category_menu.add_command(label="ex3", command=lambda: self.graph_manager.update_data_type_label("ex3"))

        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)

        for i in range(1, 5):
            self.settings_menu.add_command(label=f"{i} Graph{'s' if i > 1 else ''} Horizontal", 
                                            command=lambda i=i: self.graph_manager.set_graphs_per_screen(i, 'horizontal', self.compare_mode, self.compare_channels))
            self.settings_menu.add_command(label=f"{i} Graph{'s' if i > 1 else ''} Vertical", 
                                            command=lambda i=i: self.graph_manager.set_graphs_per_screen(i, 'vertical', self.compare_mode, self.compare_channels))

        self.compare_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Compare", menu=self.compare_menu)

        self.compare_menu.add_command(label="Compare Channels", command=self.open_compare_dialog)
        self.compare_menu.add_command(label="Disable Compare", command=self.disable_compare_mode)

        self.data_type_label = tk.Label(self.root, text="Brain Voltage", font=("Arial", 16))
        self.data_type_label.pack(pady=10)

        # Pagination controls with arrows
        self.pagination_frame = tk.Frame(self.root)
        self.pagination_frame.pack(pady=10, side=tk.TOP)

        self.prev_button = tk.Button(self.pagination_frame, text="◄", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.pagination_frame, text="►", command=self.next_page)
        self.next_button.pack(side=tk.LEFT)

        self.page_label = tk.Label(self.pagination_frame, text="Page 1")
        self.page_label.pack(side=tk.LEFT)

        num_channels = self.data.shape[0]
        num_pages = (num_channels - 1) // self.channels_per_graph + 1
        self.pagination_slider = PaginationSlider(self, num_pages)
        self.pagination_slider.pack(pady=10)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.graph_manager = GraphManager(self.canvas_frame, self)
        self.graph_manager.set_graphs_per_screen(self.channels_per_graph, layout='horizontal', compare=self.compare_mode, compare_channels=self.compare_channels)

    def next_page(self):
        num_channels, num_points = self.data.shape
        num_graphs = self.channels_per_graph
        num_pages = (num_channels - 1) // num_graphs + 1
        if self.pagination_slider.current_page < num_pages:
            self.pagination_slider.current_page += 1
            self.update_page_label()

    def prev_page(self):
        if self.pagination_slider.current_page > 1:
            self.pagination_slider.current_page -= 1
            self.update_page_label()

    def update_page_label(self):
        self.page_label.config(text=f"Page {self.pagination_slider.current_page}")
        start_channel = (self.pagination_slider.current_page - 1) * self.channels_per_graph
        self.graph_manager.update_graphs(start_channel)

class PaginationSlider(tk.Frame):
    def __init__(self, parent, num_pages=1):
        super().__init__(parent.root)
        self.parent = parent
        self.num_pages = num_pages
        self.current_page = 1
        self.dots = []
        self.create_widgets()

    def create_widgets(self):
        for i in range(self.num_pages):
            dot = tk.Label(self, text="•", font=("Arial", 24))
            dot.pack(side=tk.LEFT, padx=2)
            self.dots.append(dot)
        self.update_dots(self.num_pages)

    def update_dots(self, num_pages):
        for dot in self.dots:
            dot.destroy()
        self.dots = []

        self.num_pages = num_pages
        for i in range(self.num_pages):
            dot = tk.Label(self, text="•", font=("Arial", 24))
            dot.pack(side=tk.LEFT, padx=2)
            self.dots.append(dot)
        self.highlight_current_page()

    def highlight_current_page(self):
        for i, dot in enumerate(self.dots):
            if i == self.current_page - 1:
                dot.config(fg="blue")
            else:
                dot.config(fg="black")

    def set_current_page(self, page):
        self.current_page = page
        self.highlight_current_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceApplications(root)
    root.protocol("WM_DELETE_WINDOW", app.destroy)
    root.mainloop()