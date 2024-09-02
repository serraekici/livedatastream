import pandas as pd
import csv

class ChannelActivities:
    def __init__(self):
        self.channel_data = []

    def add_channel_data_to_file(self, data):
        """Save incoming data to a CSV file."""
        with open('channel_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        print(f"Data saved: {data}")

    def update_channel_data(self, new_data):
        """Update internal channel data for real-time processing."""
        self.channel_data.append(new_data)
        print(f"Channel data updated: {new_data}")

    def calculate_average_of_channels_from_file(self, last_n_channels):
        """Calculate the average of the last N channels from the file."""
        try:
            data = pd.read_csv('channel_data.csv', header=None)
            return data.iloc[:, :last_n_channels].mean(axis=1).tolist()
        except Exception as e:
            print(f"Error calculating average: {e}")
            return []