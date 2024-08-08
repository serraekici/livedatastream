import tkinter as tk

import numpy as np
from finished_file import DataGenerator
from view.view import InterfaceApplications
from model.data_updater import DataUpdater

class App:
    def __init__(self, root):
        self.root = root
        self.num_channels = 10
        self.channels_per_graph = 1  # Start with 1 graph
        self.compare_mode = False
        self.compare_channels = []
        self.data = DataGenerator.generate_data(self.num_channels, 10)
        self.graph_manager = None
        self.pagination_slider = None
        self.data_type_label = None

        self.interface = InterfaceApplications(root, self)
        self.graph_manager = self.interface.app.graph_manager
        
        # Initialize DataUpdater with the app instance
        self.data_updater = DataUpdater(self.update_data, self)

        # Initialize with a single graph
        self.graph_manager.set_graphs_per_screen(1, layout='horizontal')

    def update_data(self, new_data):
        self.data = new_data
        if self.graph_manager:
            self.graph_manager.update_graphs(self.pagination_slider.current_page)

    def start(self):
        self.data_updater.start()
        self.root.mainloop()

    def stop(self):
        self.data_updater.stop()
        self.root.destroy()  # Ensure the application window is properly closed

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    app.start()

