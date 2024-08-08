import numpy as np
import serial
import threading

class DataUpdater:
    def __init__(self, update_callback, app):
        self.update_callback = update_callback
        self.app = app  # Save the app instance
        self.serial_port = serial.Serial('COM8', 115200, timeout=1)
        self.stop_event = threading.Event()

    def update_data(self):
        if self.serial_port.in_waiting:
            line = self.serial_port.readline().decode('utf-8').strip()
            try:
                values = list(map(int, line.split(',')))
                if len(values) == self.app.num_channels:
                    new_data = np.array(values).reshape(self.app.num_channels, 1)
                    if self.app.data.shape[1] >= 10:  # Keep the latest 10 data points
                        self.app.data = np.hstack((self.app.data[:, -9:], new_data))
                    else:
                        self.app.data = np.hstack((self.app.data, new_data))
                    self.update_callback(self.app.data)
            except ValueError:
                pass

    def update_data_continuously(self):
        while not self.stop_event.is_set():
            self.update_data()
            self.stop_event.wait(1)

    def start(self):
        self.thread = threading.Thread(target=self.update_data_continuously)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        self.serial_port.close()
