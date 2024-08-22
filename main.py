import tkinter as tk
import subprocess
import os
import sys

def open_red_screen(root):
    root.destroy()  # Close the selection screen
    subprocess.run([sys.executable, os.path.join("plotterfromfile", "main.py")])  # Open the red screen

def open_black_screen(root):
    root.destroy()  # Close the selection screen
    subprocess.run([sys.executable, os.path.join("plotterfromserial", "main.py")])  # Open the black screen

def create_interface():
    root = tk.Tk()
    root.title("Live Data Plotter")
    root.geometry("1200x800")
    root.configure(bg='#2b2b2b')

    tk.Label(root, text="Welcome", font=("Arial", 18, "bold"), fg='white', bg='#2b2b2b').pack(pady=20)

    tk.Button(root, text="Open Red Screen", command=lambda: open_red_screen(root), bg='red', fg='white').pack(pady=10)
    tk.Button(root, text="Open Black Screen", command=lambda: open_black_screen(root), bg='black', fg='white').pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_interface()
