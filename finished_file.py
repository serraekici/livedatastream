import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def generate_data(num_channels, num_points):
    return np.random.randn(num_channels, num_points)

def update_data(num_channels,):
    new_data = generate_data(num_channels, num_points)
    return new_data

def create_graphs(data, start_channel, channels_per_graph=1):
    num_channels, num_points = data.shape
    fig, axs = plt.subplots(1, channels_per_graph, figsize=(15, 5))
    
    if channels_per_graph == 1:
        axs = [axs]

    for i in range(channels_per_graph):
        channel_index = start_channel + i * 2
        if channel_index + 1 < num_channels:
            axs[i].plot(data[channel_index])
            axs[i].plot(data[channel_index + 1])
            axs[i].set_facecolor("white")  
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
            axs[i].set_facecolor("white") 
            axs[i].legend()
        else:
            axs[i].set_visible(False)
    
    canvas.draw()

def update_data_continuously():
    global data
    data = update_data(num_channels)
    update_graphs(slider.get())
    root.after(1000, update_data_continuously)

def set_graphs_per_screen(value):
    global channels_per_graph, fig, axs, canvas
    channels_per_graph = int(value)
    fig, axs = create_graphs(data, 0, channels_per_graph)
    canvas.figure = fig
    canvas.draw()
    update_graphs(slider.get())

# Initialize data
num_channels = 20
num_points = 50
channels_per_graph = 1

data = generate_data(num_channels, num_points)
fig, axs = create_graphs(data, 0, channels_per_graph)

# Create the main window
root = tk.Tk()
root.title("Live Data Stream")

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create a "Settings" menu
settings_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)

# Add options to the "Settings" menu for number of graphs per screen
settings_menu.add_command(label="1 Graph", command=lambda: set_graphs_per_screen(1))
settings_menu.add_command(label="2 Graphs", command=lambda: set_graphs_per_screen(2))
settings_menu.add_command(label="3 Graphs", command=lambda: set_graphs_per_screen(3))
settings_menu.add_command(label="4 Graphs", command=lambda: set_graphs_per_screen(4))

# Create a frame for the controls
control_frame = tk.Frame(root)
control_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Create a frame for the canvas
canvas_frame = tk.Frame(root)
canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Create and pack the canvas
canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Create a style for the slider
style = ttk.Style()
style.configure("TScale", sliderthickness=15)

# Create and pack the slider
slider = ttk.Scale(control_frame, from_=0, to=(num_channels // (channels_per_graph * 2)) - 1, orient=tk.HORIZONTAL, command=update_graphs, style="TScale")
slider.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# Start the continuous data update
root.after(1000, update_data_continuously)

# Start the Tkinter main loop
root.mainloop()
