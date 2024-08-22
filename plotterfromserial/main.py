# main.py
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from time_manager import TimeDisplay  # time_manager.py dosyasından TimeDisplay sınıfını import ediyoruz
from serial_connection import SerialConnection  # SerialConnection sınıfını import ediyoruz

class ImportFromSerial:

    def __init__(self, root):
        self.root = root
        self.root.title("Red Screen Data Plotter")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1c1c1c')

        self.serial_conn = SerialConnection()
        self.time_display = TimeDisplay(self.root, bg='#1c1c1c', fg='white', font=("Arial", 12))

        # Seri port bağlantısını kur
        self.serial_conn.connect_to_port(None, None, None, self.root)

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.data = []

        self.ani = animation.FuncAnimation(self.fig, self.update_graph, interval=1000, cache_frame_data=False)

        self.root.mainloop()

    def update_graph(self, frame):
        data = self.serial_conn.read_data()
        print('TEST')
        print('TEST2')
        if data:
            print(f"Gelen veri: {data}")  # Gelen veriyi terminale yazdırın
    
            try:
                # Eğer veri birden fazla sayı içeriyorsa, virgüllerle ayrıldığını varsayıyoruz.
                data_points = data.split(',')
                for point in data_points:
                    try:
                        value = float(point.strip())
                        self.data.append(value)
                    except ValueError:
                        print(f"Veri işlenemedi: {point}")
                
                # Grafiği temizleyip yeni verilerle güncelliyoruz
                self.ax.clear()
                self.ax.plot(self.data, label="Serial Data")
                self.ax.set_title("Live Data Plot")
                self.ax.legend()
                self.canvas.draw()
            except Exception as e:
                print(f"Grafik çiziminde hata: {e}")
        else:
            print("Gelen veri boş veya None")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImportFromSerial(root)
