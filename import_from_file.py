import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

class ImportFromFile:
    def __init__(self, root, ax, canvas, settings):
        self.root = root
        self.ax = ax
        self.canvas = canvas
        self.settings = settings
        self.data_list = []
        self.num_channels = 10
        self.channel_names = [f'Channel {i+1}' for i in range(self.num_channels)]

    def load_data_from_file(self):
        file_path = filedialog.askopenfilename(title="Select Data File", filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")])
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                else:
                    df = pd.read_csv(file_path)
                self.process_data(df)
                self.plot_static_data()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while loading the data file: {e}")

    def process_data(self, df):
        self.data_list.clear()
        for _, row in df.iterrows():
            values = row.tolist()
            if all(isinstance(v, (int, float)) for v in values) and len(values) == self.num_channels:
                self.data_list.append(values)

    def plot_static_data(self):
        self.ax.clear()
        data_array = np.array(self.data_list, dtype=float)
        for channel in range(self.num_channels):
            self.ax.plot(data_array[:, channel], label=self.channel_names[channel], linewidth=3)
        self.ax.set_title('Loaded Data from File', color='white', font=("Arial", 12, "bold"))
        self.ax.set_xlabel('Sample', color='white', font=("Arial", 12, "bold"))
        self.ax.set_ylabel('Value', color='white', font=("Arial", 12, "bold"))
        self.ax.legend(loc='upper right', facecolor='#3f3f3f')
        self.ax.grid(True, color='#888888', linestyle='--', linewidth=0.5)
        self.canvas.draw()
        self.settings.ax = self.ax
        self.settings.canvas = self.canvas
