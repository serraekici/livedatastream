import tkinter as tk
class ChannelActivities:
    def __init__(self, settings):
        self.settings = settings

    def update_selected_channels(self):
        """Update selected channels when checkboxes are toggled."""
        self.settings.selected_channels = [i for i, var in enumerate(self.settings.channel_vars) if var.get() == 1]
        self.settings.update_graph()

    def update_channel_name(self, idx, event):
        """Update the channel name based on user input."""
        self.settings.channel_names[idx] = self.settings.channel_entries[idx].get()
        self.settings.update_graph()

    def setup_channel_controls(self, right_frame):
        """Setup channel controls in the right sidebar."""
        for idx, name in enumerate(self.settings.channel_names):
            channel_check = tk.Checkbutton(right_frame, text=name, variable=self.settings.channel_vars[idx], bg='#333', fg='pink',
                                           selectcolor='blue', command=self.update_selected_channels)
            channel_check.pack(anchor='w', padx=10)
            entry = tk.Entry(right_frame, width=15)
            entry.insert(0, name)
            entry.bind('<Return>', lambda event, idx=idx: self.update_channel_name(idx, event))
            entry.pack(anchor='w', padx=20, pady=2)
            self.settings.channel_entries.append(entry)

