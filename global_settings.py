class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class GlobalSettings(metaclass=SingletonMeta):
    def __init__(self):
        self.serial_conn = None  # SerialConnection instance will be set later
        self.time_manager = None  # TimeManager instance will be set later
        self.selected_channels = list(range(10))  # Tüm kanallar başlangıçta seçili
        self.num_channels = 10
        self.channel_names = [f'Channel {i+1}' for i in range(self.num_channels)]
        self.data_list = []
        self.grid_on = None
