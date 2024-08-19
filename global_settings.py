import numpy as np

class GlobalSettings:
    def __init__(self):
        self.serial_conn = None
        self.time_manager = None
        self.selected_channels = list(range(10))
        self.num_channels = 10
        self.channel_names = [f'Channel {i+1}' for i in range(self.num_channels)]
        self.data_list = []
        self.grid_on = None
        self.ax = None  # Matplotlib ekseni burada saklanacak
        self.canvas = None  # Matplotlib tuvali burada saklanacak

    def update_data(self, frame=None):
        data = self.serial_conn.read_data()
        if data:
            values = data.split(',')
            if all(v.replace('.', '', 1).isdigit() for v in values) and len(values) == self.num_channels:
                self.data_list.append([float(v) for v in values])

            if self.data_list:
                data_array = np.array(self.data_list, dtype=float)
                self.ax.clear()
                line_style = self.get_line_style()
                for channel in self.selected_channels:
                    self.ax.plot(data_array[:, channel], label=self.channel_names[channel], linestyle=line_style, linewidth=3)
                self.ax.set_title('Selected Channels', color='white')
                self.ax.set_xlabel('Sample', color='white')
                self.ax.set_ylabel('Value', color='white')
                self.ax.legend(loc='upper right', facecolor='#3f3f3f')
                self.ax.grid(self.grid_on.get(), color='#888888', linestyle='--', linewidth=0.5)

                try:
                    self.ax.set_xlim([int(self.x_start_entry.get()), int(self.x_end_entry.get())])
                except ValueError:
                    pass

                try:
                    self.ax.set_ylim([int(self.y_start_entry.get()), int(self.y_end_entry.get())])
                except ValueError:
                    pass

                self.canvas.draw()

    def get_line_style(self):
        styles = {
            'Solid': '-',
            'Dashed': '--',
            'Dotted': ':',
            'Dashdot': '-.'
        }
        return styles.get(self.line_style_combobox.get(), '-')
