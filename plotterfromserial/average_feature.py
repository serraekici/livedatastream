import numpy as np

class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def filter(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

        return self.posteri_estimate

class AverageFeature:
    def __init__(self, channel_activities, ax, x_start_entry, x_end_entry, y_start_entry, y_end_entry, canvas):
        self.channel_activities = channel_activities
        self.ax = ax
        self.x_start_entry = x_start_entry
        self.x_end_entry = x_end_entry
        self.y_start_entry = y_start_entry
        self.y_end_entry = y_end_entry
        self.canvas = canvas
        self.average_active = False
        self.kalman_filter = KalmanFilter(1e-5, 1e-1, 1e-1)  # Kalman filtresi varsayılan parametrelerle başlatıldı

    def calculate_and_plot_average(self, average_entry, selected_channels, channel_vars):
        try:
            # ChannelActivities'ten gelen verileri alıyoruz
            data_list = self.channel_activities.channel_data  # Verilerin saklandığı yer

            if not data_list or len(data_list) == 0:
                raise ValueError("Aritmetik ortalama için kullanılacak veri bulunamadı.")

            last_n_channels = int(average_entry.get())
            if last_n_channels <= 0 or last_n_channels > len(selected_channels):
                raise ValueError("Aritmetik ortalama için geçersiz kanal sayısı.")

            # Seçilen kanalların verilerini çıkar
            selected_data = []
            for i, channel in enumerate(selected_channels):
                if channel_vars[i].get() == 1:
                    selected_data.append([row[channel] for row in data_list])

            if not selected_data:
                raise ValueError("Hiçbir kanal seçilmedi.")

            # N kanalın ortalamasını hesapla
            selected_data = np.array(selected_data)
            if selected_data.shape[0] < last_n_channels:
                raise ValueError("Seçilen kanalların sayısı, ortalama hesaplama için yeterli değil.")

            average_data = np.mean(selected_data[:last_n_channels], axis=0)

            # Aritmetik ortalamaya Kalman filtresi uygula
            filtered_average_data = [self.kalman_filter.filter(value) for value in average_data]

            # Grafiği temizle
            self.ax.clear()

            # Filtrelenmiş ortalama veriyi grafiğe ekle
            self.ax.plot(filtered_average_data, label="Filtrelenmiş Ortalama", linestyle='--')

            # İlk seçilen kanalı referans olarak grafiğe ekle
            if selected_channels:
                first_selected_channel = selected_channels[0]
                channel_data = [row[first_selected_channel] for row in data_list]
                self.ax.plot(channel_data, label=f"Channel {first_selected_channel + 1}")

            # Girişlere göre X ve Y limitlerini ayarla
            try:
                x_start = float(self.x_start_entry.get())
                x_end = float(self.x_end_entry.get())
                self.ax.set_xlim([x_start, x_end])
            except ValueError:
                pass

            try:
                y_start = float(self.y_start_entry.get())
                y_end = float(self.y_end_entry.get())
                self.ax.set_ylim([y_start, y_end])
            except ValueError:
                pass

            # Kanvası yeniden çiz
            self.canvas.draw()

            # Lejantı güncelle
            self.ax.legend()

        except ValueError as e:
            print(f"Aritmetik ortalama hesaplanırken hata: {e}")
        except Exception as ex:
            print(f"Beklenmeyen bir hata oluştu: {ex}")
