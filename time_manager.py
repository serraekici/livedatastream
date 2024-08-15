import time

class TimeManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TimeManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        pass

    def get_current_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S')

    def update_time(self, time_label, root):
        current_time = self.get_current_time()
        time_label.config(text=current_time)
        root.after(1000, lambda: self.update_time(time_label, root))
