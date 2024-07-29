import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def generate_data(num_channels, num_points):
    return np.random.randn(num_channels, num_points)

def update_data(num_channels, num_points):
    new_data = generate_data(num_channels, num_points)
    return new_data

def create_graphs(data, start_channel, channels_per_graph=1):
    num_channels, num_points = data.shape
    fig, axs = plt.subplots(1, channels_per_graph, figsize=(15, 5))
    
    if channels_per_graph == 1:
        axs = [axs]  # Tek bir alt grafik olduğunda axs bir liste gibi kullanılabilir.

    for i in range(channels_per_graph):
        channel_index = start_channel + i * 2  
        if channel_index + 1 < num_channels:
            axs[i].plot(data[channel_index])
            axs[i].plot(data[channel_index + 1])
            axs[i].legend()
        else:
            axs[i].set_visible(False)
    
    return fig, axs


def update_graphs(val):
    global canvas, fig, axs, data
    start_channel = int(val) * channels_per_graph * 2  

    for i in range(channels_per_graph):
        channel_index = start_channel + i * 2
        axs[i].cla()  
        if channel_index + 1 < num_channels:
            axs[i].plot(data[channel_index])
            axs[i].plot(data[channel_index + 1])
            axs[i].legend()
        else:
            axs[i].set_visible(False)
    
    canvas.draw()


def update_data_continuously():
    global data
    data = update_data(num_channels, num_points)
    update_graphs(slider.get())
    root.after(1000, update_data_continuously)
    
num_channels = 20
num_points = 5
channels_per_graph = 1


data = generate_data(num_channels, num_points)
fig, axs = create_graphs(data, 0, channels_per_graph)

root = tk.Tk()
root.title("Live Data Stream")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

slider = tk.Scale(root, from_=0, to=(num_channels // (channels_per_graph * 2)) - 1, orient=tk.HORIZONTAL, command=update_graphs)
slider.pack(side=tk.BOTTOM, fill=tk.X)

root.after(1000, update_data_continuously)

root.mainloop()
