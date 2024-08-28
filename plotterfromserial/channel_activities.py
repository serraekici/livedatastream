import numpy as np
import pandas as pd
import csv
import math

class ChannelActivities:
    def __init__(self):
        self.channel_data = {}

    def add_channel_data_to_file(self, data):
        with open('channel_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        print(f"Data saved: {data}")

    def calculate_average_of_channels_from_file(self, last_n_channels):
        df = pd.read_csv('channel_data.csv', header=None)
        df = df.iloc[:, -last_n_channels:]
        return df.mean(axis=1)

    def plot_selected_channel(self, channel):
        try:
            data = pd.read_csv('channel_data.csv', header=None)
            channel_data = data.iloc[:, channel].values[-100:]  # Son 100 veriyi göster
    
            if len(channel_data) == 0:
                return
    
            if len(channel_data) > 5:
                channel_data = np.convolve(channel_data, np.ones(5)/5, mode='valid')
    
            self.ax.plot(channel_data, label=f"Kanal {channel + 1}")
    
            self.ax.legend()
    
            try:
                x_start = int(self.x_start_entry.get())
                x_end = int(self.x_end_entry.get())
                self.ax.set_xlim([x_start, x_end])
            except ValueError:
                pass
            
            try:
                y_start = int(self.y_start_entry.get())
                y_end = int(self.y_end_entry.get())
                self.ax.set_ylim([y_start, y_end])
            except ValueError:
                pass
            
        except Exception as e:
            print(f"Veri çiziminde hata: {e}")
    

    def update_channel_data(self, channel, data):
        if channel not in self.channel_data:
            self.channel_data[channel] = []
        self.channel_data[channel].append(data)
        if len(self.channel_data[channel]) > 100:  
            self.channel_data[channel].pop(0)

    def simulate_heartbeat_waveform(self, data):
        return [math.sin(x/10.0) for x in range(len(data))]
