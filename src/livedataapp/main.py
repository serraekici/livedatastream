import tkinter as tk
import numpy as np
from model.data_updater import DataUpdater, DataGenerator
from view.view import InterfaceApplications

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

        self.data_updater = DataUpdater(self)
        self.interface = InterfaceApplications(root, self)
        # Initialize with a single graph
        self.interface.app.graph_manager.set_graphs_per_screen(1, layout='horizontal')

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

