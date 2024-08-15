import time

class TimeManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TimeManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'current_time'):
            self.current_time = ""

    def update_time(self):
        self.current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        return self.current_time
