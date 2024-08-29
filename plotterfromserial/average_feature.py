import numpy as np
import tkinter as tk

import pandas as pd

class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def filter(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

        return self.posteri_estimate

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
        self.kalman_filter = KalmanFilter(1e-5, 1e-1, 1e-1)  # Initialize Kalman filter with default parameters

    def calculate_and_plot_average(self, average_entry, selected_channels, channel_vars):
        """Calculate the average of the first N channels, apply Kalman filter, and plot it with a selected channel."""
        try:
            data_list = self.channel_activities.data_list  # Access the data_list

            if not data_list or len(data_list) == 0:
                raise ValueError("No data available for averaging.")

            last_n_channels = int(average_entry.get())
            if last_n_channels <= 1 or last_n_channels > len(data_list[0]):
                raise ValueError(f"The number of channels must be between 2 and {len(data_list[0])}.")

            selected_channel_index = [i for i, var in enumerate(channel_vars) if var.get()]
            if len(selected_channel_index) != 1:
                raise ValueError("Please select exactly one channel to compare with the average.")

            selected_channel = selected_channel_index[0]

            # Collect the data from the last_n_channels channels
            selected_data = [np.array([row[channel] for row in data_list]) for channel in range(last_n_channels)]
            average_data = np.mean(selected_data, axis=0)

            # Apply Kalman filter to the averaged data
            filtered_data = np.array([self.kalman_filter.filter(value) for value in average_data])

            self.average_active = True
            self.plot_channel_with_average(selected_channel, filtered_data, last_n_channels)

        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))

    def plot_channel_with_average(self, channel, average_data, last_n_channels):
        """Plot the selected channel's data and the calculated average together."""
        try:
            # Get the selected channel's data directly from the file
            data = pd.read_csv('channel_data.csv', header=None)
            channel_data = data.iloc[:, channel].values

            self.ax.clear()

            # Plot the selected channel
            self.ax.plot(channel_data, label=f"Channel {channel + 1}")

            if average_data is not None:
                # Plot the filtered average data
                self.ax.plot(average_data, label=f"Filtered Average of last {last_n_channels} channels", linestyle='--')

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
            print(f"Error plotting data: {e}")
