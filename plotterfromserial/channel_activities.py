import numpy as np
import pandas as pd
import csv

class ChannelActivities:
    def __init__(self):
        self.channel_data = {}

    def add_channel_data_to_file(self, data):
        """Save incoming data to a CSV file."""
        with open('channel_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        print(f"Data saved: {data}")

    def calculate_average_of_channels_from_file(self, last_n_channels):
        """Calculate the average of the last n channels from the saved file."""
        df = pd.read_csv('channel_data.csv', header=None)
        df = df.iloc[:, -last_n_channels:]
        return df.mean(axis=1)

    def plot_selected_channels(self, selected_channels, ax, canvas):
        """Plot multiple selected channels on the same graph."""
        if not selected_channels:
            return
        
        for channel in selected_channels:
            if channel in self.channel_data:
                data = self.channel_data[channel]
                ax.plot(data, label=f'Channel {channel}')
        
        ax.legend(loc='upper right')
        canvas.draw()

    def update_channel_data(self, channel, data):
        """Update the channel data with new incoming data."""
        if channel not in self.channel_data:
            self.channel_data[channel] = []
        self.channel_data[channel].append(data)
        if len(self.channel_data[channel]) > 100:  # Assuming a limit of 100 data points per channel
            self.channel_data[channel].pop(0)
