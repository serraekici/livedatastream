import pandas as pd
import tkinter as tk

class AverageFeature:
    def __init__(self, channel_activities, ax, x_start_entry, x_end_entry, y_start_entry, y_end_entry, canvas):
        self.channel_activities = channel_activities
        self.ax = ax
        self.x_start_entry = x_start_entry
        self.x_end_entry = x_end_entry
        self.y_start_entry = y_start_entry
        self.y_end_entry = y_end_entry
        self.canvas = canvas
        self.average_active = False

    def calculate_and_plot_average(self, average_entry, selected_channels, channel_vars):
        """Calculate the average of the first N channels and plot it with a selected channel."""
        try:
            last_n_channels = int(average_entry.get())
            if last_n_channels <= 1 or last_n_channels > 10:
                raise ValueError("The number of channels must be between 2 and 10.")

            selected_channel_index = [i for i, var in enumerate(channel_vars) if var.get()]
            if len(selected_channel_index) != 1:
                raise ValueError("Please select exactly one channel to compare with the average.")

            selected_channel = selected_channel_index[0]
            average_data = self.channel_activities.calculate_average_of_channels_from_file(last_n_channels)
            self.average_active = True
            self.plot_channel_with_average(selected_channel, average_data, last_n_channels)

        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))

    def plot_channel_with_average(self, channel, average_data, last_n_channels):
        """Plot the selected channel's data and the calculated average together."""
        try:
            # Read the selected channel's data from the file
            data = pd.read_csv('channel_data.csv', header=None)
            channel_data = data.iloc[:, channel].values

            self.ax.clear()

            # Plot the selected channel
            self.ax.plot(channel_data, label=f"Channel {channel + 1}")

            if average_data is not None:
                # Plot the average data
                self.ax.plot(average_data, label=f"Average of last {last_n_channels} channels.", linestyle='--')

            self.ax.legend()

            # Set X and Y axis limits based on user input
            try:
                x_start = int(self.x_start_entry.get())
                x_end = int(self.x_end_entry.get())
                self.ax.set_xlim([x_start, x_end])
            except ValueError:
                pass  # Ignore if the input is not a valid integer

            try:
                y_start = int(self.y_start_entry.get())
                y_end = int(self.y_end_entry.get())
                self.ax.set_ylim([y_start, y_end])
            except ValueError:
                pass  # Ignore if the input is not a valid integer

            self.canvas.draw()
        except Exception as e:
            print(f"Veri çiziminde hata: {e}")