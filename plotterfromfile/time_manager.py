import tkinter as tk
import time

class TimeDisplay:
    def __init__(self, parent, **kwargs):
        self.time_label = tk.Label(parent, **kwargs)
        self.update_time()

    def update_time(self):
        current_time = time.strftime('%D %H:%M:%S')
        self.time_label.config(text=current_time)
        self.time_label.after(1000, self.update_time)
