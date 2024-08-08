import tkinter as tk
from tkinter import simpledialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

    def enable_zoom(self):
        def zoom(scale_factor, axis='both'):
            for ax in self.axs:
                try:
                    if len(ax.get_lines()) > 0:
                        xdata, ydata = (sum(ax.get_xlim()) / 2, sum(ax.get_ylim()) / 2)

                        cur_xlim = ax.get_xlim()
                        cur_ylim = ax.get_ylim()

                        if axis in ['x', 'both']:
                            new_xlim = [xdata - (xdata - cur_xlim[0]) * scale_factor,
                                        xdata + (cur_xlim[1] - xdata) * scale_factor]
                            new_xlim = [max(0, min(new_xlim)), min(len(ax.get_lines()[0].get_xdata()) - 1, max(new_xlim))]

                        if axis in ['y', 'both']:
                            new_ylim = [ydata - (ydata - cur_ylim[0]) * scale_factor,
                                        ydata + (cur_ylim[1] - ydata) * scale_factor]
                            new_ylim = [max(min(ax.get_lines()[0].get_ydata()), min(new_ylim)),
                                        min(max(ax.get_lines()[0].get_ydata()), max(new_ylim))]

                        ax.set_xlim(new_xlim)
                        ax.set_ylim(new_ylim)

                        self.zoom_limits[ax] = {'xlim': new_xlim, 'ylim': new_ylim}
                        self.canvas.draw_idle()
                except Exception as e:
                    print(f"Error during zoom operation: {e}")

        self.zoom_in = lambda: zoom(0.9)
        self.zoom_out = lambda: zoom(1.1)

    def zoom_in_menu(self):
        self.zoom_in()

    def zoom_out_menu(self):
        self.zoom_out()

    def zoom_in_x(self):
        self.zoom(0.9, axis='x')

    def zoom_out_x(self):
        self.zoom(1.1, axis='x')

    def zoom_in_y(self):
        self.zoom(0.9, axis='y')

    def zoom_out_y(self):
        self.zoom(1.1, axis='y')

    def zoom(self, scale_factor, axis='both'):
        ax = self.fig.gca()
        if not ax:
            return

        if axis == 'x' or axis == 'both':
            xdata, _ = (sum(ax.get_xlim()) / 2, sum(ax.get_ylim()) / 2)
            cur_xlim = ax.get_xlim()
            new_xlim = [xdata - (xdata - cur_xlim[0]) * scale_factor,
                        xdata + (cur_xlim[1] - xdata) * scale_factor]
            ax.set_xlim(new_xlim)

        if axis == 'y' or axis == 'both':
            _, ydata = (sum(ax.get_xlim()) / 2, sum(ax.get_ylim()) / 2)
            cur_ylim = ax.get_ylim()
            new_ylim = [ydata - (ydata - cur_ylim[0]) * scale_factor,
                        ydata + (cur_ylim[1] - ydata) * scale_factor]
            ax.set_ylim(new_ylim)

        self.zoom_limits[ax] = {'xlim': ax.get_xlim(), 'ylim': ax.get_ylim()}
        self.canvas.draw_idle()

    def update_graphs(self, val):
        start_channel = int(val) * self.app.channels_per_graph * 2 if self.app.compare_mode else int(val) * self.app.channels_per_graph

        for i in range(self.app.channels_per_graph):
            ax = self.axs[i]
            ax.clear()  # Clear old data
            if self.app.compare_mode:
                self.plot_compare_data(ax, self.app.data, self.app.compare_channels, i, self.app.num_channels)
            else:
                channel_index = start_channel + i
                if channel_index < self.app.num_channels:
                    ax.plot(self.app.data[channel_index], label=f'Channel {channel_index}', marker='o')
                    ax.set_facecolor("white")
                    ax.legend()
                    ax.grid(True)
            # Reapply zoom limits
            if ax in self.zoom_limits:
                ax.set_xlim(self.zoom_limits[ax]['xlim'])
                ax.set_ylim(self.zoom_limits[ax]['ylim'])

        self.fig.tight_layout()
        self.canvas.draw()

    def set_graphs_per_screen(self, value, layout='horizontal', compare=False, compare_channels=[]):
        self.app.channels_per_graph = int(value)
        self.app.compare_mode = compare
    
        if self.canvas is not None:
            self.canvas.get_tk_widget().pack_forget()
            self.fig.clf()
    
        self.fig, self.axs = self.create_graphs(
            self.app.data, 0, self.app.channels_per_graph, layout=layout, compare=self.app.compare_mode, compare_channels=compare_channels)
    
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
        self.enable_zoom()
        
        # Check if pagination_slider is initialized before using it
        if self.app.pagination_slider:
            self.app.pagination_slider.update_pages()
        else:
            print("PaginationSlider is not initialized.")



    def update_data_type_label(self, data_type):
        self.app.data_type_label.config(text=data_type)
        self.update_graphs(self.app.pagination_slider.current_page)


class PaginationSlider(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.current_page = 0
        self.num_pages = 1

        self.prev_button = tk.Button(self, text="←", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.slider = tk.Scale(self, from_=0, to=self.num_pages-1, orient=tk.HORIZONTAL, showvalue=False)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.next_button = tk.Button(self, text="→", command=self.next_page)
        self.next_button.pack(side=tk.LEFT)

        self.dots_frame = tk.Frame(self)
        self.dots_frame.pack()

        self.slider.bind("<ButtonRelease-1>", self.page_changed)
        self.slider.bind("<B1-Motion>", self.page_changing)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.slider.set(self.current_page)
            self.page_changed(None)

    def next_page(self):
        if self.current_page < self.num_pages - 1:
            self.current_page += 1
            self.slider.set(self.current_page)
            self.page_changed(None)

    def page_changed(self, event):
        self.app.graph_manager.update_graphs(self.current_page)

    def page_changing(self, event):
        self.current_page = int(self.slider.get())
        self.update_dots()

    def update_dots(self):
        for widget in self.dots_frame.winfo_children():
            widget.destroy()

        for i in range(self.num_pages):
            dot = tk.Label(self.dots_frame, text="•", font=("Arial", 12))
            dot.pack(side=tk.LEFT, padx=2)
            if i == self.current_page:
                dot.config(fg="blue")

    def update_pages(self):
        self.num_pages = (self.app.num_channels // self.app.channels_per_graph) + 1
        self.slider.config(to=self.num_pages - 1)
        self.update_dots()


    def update_dots(self):
        for widget in self.dots_frame.winfo_children():
            widget.destroy()
        
        for i in range(self.num_pages):
            dot = tk.Label(self.dots_frame, text="•", font=("Arial", 12), padx=5)
            if i == self.current_page:
                dot.config(fg="blue")
            else:
                dot.config(fg="gray")
            dot.pack(side=tk.LEFT)

class InterfaceApplications:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        
        # Create the widgets first
        self.create_widgets()

        # Initialize PaginationSlider first
        self.app.pagination_slider = PaginationSlider(self.root, self.app)
        self.app.pagination_slider.pack(side=tk.TOP, fill=tk.X)

        # Initialize GraphManager
        self.app.graph_manager = GraphManager(self.canvas_frame, self.app)
        # Set up the initial state for GraphManager
        self.app.graph_manager.set_graphs_per_screen(1, layout='horizontal')

    def create_widgets(self):
        self.root.title("Data Stream Application")

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Settings Menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        
        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View Menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Graph Layout", command=self.show_layout_buttons)
        self.view_menu.add_command(label="Graphs per Screen", command=self.choose_graphs_per_screen)
        self.view_menu.add_command(label="Compare Channels", command=self.compare_channels)
    
        # Zoom Menu
        self.zoom_menu = tk.Menu(self.settings_menu, tearoff=0)
        self.settings_menu.add_cascade(label="Zoom", menu=self.zoom_menu)
        # Adding Zoom commands
        self.zoom_menu.add_command(label="Zoom In X", command=self.zoom_in_x)
        self.zoom_menu.add_command(label="Zoom Out X", command=self.zoom_out_x)
        self.zoom_menu.add_command(label="Zoom In Y", command=self.zoom_in_y)
        self.zoom_menu.add_command(label="Zoom Out Y", command=self.zoom_out_y)
        
        # Canvas Frame
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Data Type Label
        self.data_type_label = tk.Label(self.root, text="Data Type", font=("Arial", 14))
        self.data_type_label.pack(side=tk.TOP)

    def show_layout_buttons(self):
        layout_window = tk.Toplevel(self.root)
        layout_window.title("Select Layout")
        
        horizontal_button = tk.Button(layout_window, text="Horizontal", command=lambda: self.set_graph_layout('horizontal'))
        horizontal_button.pack(padx=20, pady=10)

        vertical_button = tk.Button(layout_window, text="Vertical", command=lambda: self.set_graph_layout('vertical'))
        vertical_button.pack(padx=20, pady=10)

    def set_graph_layout(self, layout):
        self.app.graph_manager.set_graphs_per_screen(self.app.channels_per_graph, layout=layout)

    def choose_graphs_per_screen(self):
        value = simpledialog.askinteger("Graphs per Screen", "Enter number of graphs per screen:")
        if value is not None:
            self.app.graph_manager.set_graphs_per_screen(value, layout='horizontal')

    def compare_channels(self):
        channels = simpledialog.askstring("Compare Channels", "Enter channels to compare (comma-separated):")
        if channels:
            compare_channels = list(map(int, channels.split(',')))
            self.app.graph_manager.set_graphs_per_screen(self.app.channels_per_graph, layout='horizontal', compare=True, compare_channels=compare_channels)

    def zoom_in_x(self):
        self.app.graph_manager.zoom_in_x()

    def zoom_out_x(self):
        self.app.graph_manager.zoom_out_x()

    def zoom_in_y(self):
        self.app.graph_manager.zoom_in_y()

    def zoom_out_y(self):
        self.app.graph_manager.zoom_out_y()

