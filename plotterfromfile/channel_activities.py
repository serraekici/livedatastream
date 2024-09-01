import numpy as np
import pandas as pd  # Make sure pandas is imported here
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

            # Check if there are enough channels in the data
            if data.shape[1] < last_n_channels:
                raise ValueError(f"Data only contains {data.shape[1]} channels, but {last_n_channels} were requested.")

            # Select only the first `last_n_channels` columns
            data = data.iloc[:, :last_n_channels]

            # Calculate the average across the columns
            avg = data.mean(axis=1)
            print(f"Average data calculated: {avg.values}")  # Debugging
            return avg.values
        except pd.errors.EmptyDataError:
            raise ValueError("No channel data available for averaging.")
        except FileNotFoundError:
            raise ValueError("The file 'channel_data.csv' was not found.")
        except Exception as e:
            raise ValueError(f"An error occurred while calculating the average: {str(e)}")

    def load_channel_data_from_file(self):
        """Load channel data from the CSV file into memory."""
        try:
            file_path = 'channel_data.csv'
            with open(file_path, 'r') as file:
                print(f"File '{file_path}' exists and is ready to be read.")

            data = pd.read_csv(file_path, header=None)
            print(f"CSV'den okunan ham veri:\n{data}")  # CSV dosyasının doğru okunduğunu kontrol edelim
    
            self.channel_data = data.to_dict(orient='list')
            print(f"Channel data loaded: {self.channel_data}")  # channel_data'nın içeriğini terminalde gösterelim
        except pd.errors.EmptyDataError:
            raise ValueError("No channel data available.")
        except FileNotFoundError:
            raise ValueError("The file 'channel_data.csv' was not found.")
        except Exception as e:
            raise ValueError(f"An error occurred while loading channel data: {str(e)}")


    def get_channel_data(self, channel_index):
        """Retrieve data for a specific channel."""
        try:
            # Kanala ait verileri channel_data sözlüğünden çekiyoruz
            if channel_index in self.channel_data:
                print(f"Channel {channel_index + 1} successfully retrieved.")
                return self.channel_data[channel_index]
            else:
                print(f"Channel {channel_index + 1} not found in channel_data.")
                raise ValueError(f"Channel {channel_index + 1} data is not available.")
        except KeyError:
            raise ValueError(f"Channel {channel_index + 1} data is not available.")
        except Exception as e:
            raise ValueError(f"An error occurred while retrieving channel data: {str(e)}")

    def apply_kalman_filter(self, data):
        """Apply Kalman filter to the provided data."""
        n_iter = len(data)
        sz = (n_iter,)  # size of array
        Q = 1e-5  # process variance

        # Allocate space for arrays
        xhat = np.zeros(sz)  # a posteriori estimate of x
        P = np.zeros(sz)  # a posteriori error estimate
        xhatminus = np.zeros(sz)  # a priori estimate of x
        Pminus = np.zeros(sz)  # a priori error estimate
        K = np.zeros(sz)  # gain or blending factor

        R = 0.1 ** 2  # estimate of measurement variance

        # Initial guesses
        xhat[0] = data[0]
        P[0] = 1.0

        for k in range(1, n_iter):
            # Time update
            xhatminus[k] = xhat[k-1]
            Pminus[k] = P[k-1] + Q

            # Measurement update
            K[k] = Pminus[k] / (Pminus[k] + R)
            xhat[k] = xhatminus[k] + K[k] * (data[k] - xhatminus[k])
            P[k] = (1 - K[k]) * Pminus[k]

        return xhat
