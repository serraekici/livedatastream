
import tkinter as tk
import datetime

class TimeDisplay:
    def __init__(self, root, **kwargs):
        self.time_label = tk.Label(root, **kwargs)
        self.time_label.pack(anchor='ne', padx=4, pady=1)
        self.update_time()

    def update_time(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=f"Current Time: {current_time}")
        self.time_label.after(1000, self.update_time)
