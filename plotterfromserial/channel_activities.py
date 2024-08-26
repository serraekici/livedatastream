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
        """Calculate the average of the first 'last_n_channels' channels from the file."""
        if last_n_channels < 1 or last_n_channels > 10:
            raise ValueError("Invalid number of channels for average calculation. Please enter a value between 1 and 10.")

        # Read the data from the CSV file
        try:
            data = pd.read_csv('channel_data.csv', header=None)
            # Select only the first `last_n_channels` columns
            data = data.iloc[:, :last_n_channels]

            # Calculate the average across the columns
            avg = data.mean(axis=1)
            print(f"Average data calculated: {avg.values}")  # Debugging
            return avg.values
        except pd.errors.EmptyDataError:
            raise ValueError("No channel data available for averaging.")
