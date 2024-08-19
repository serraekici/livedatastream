import tkinter as tk

class ShowStartupScreenSingleton:
    _instance = None

    def __new__(cls, root, start_from_file, start_from_serial):
        if cls._instance is None:
            cls._instance = super(ShowStartupScreenSingleton, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, root, start_from_file, start_from_serial):
        if self._initialized:
            return
        self.root = root
        self.start_from_file = start_from_file
        self.start_from_serial = start_from_serial
        self._initialized = True

    def show_startup_screen(self):
        self.startup_screen = tk.Frame(self.root, bg='#2b2b2b')
        self.startup_screen.pack(expand=True, fill=tk.BOTH)

        welcome_label = tk.Label(self.startup_screen, text="Welcome", font=("Arial", 24), fg='white', bg='#2b2b2b')
        welcome_label.pack(pady=(40, 20))

        subtext_label = tk.Label(self.startup_screen, text="How Can We Help You?", font=("Arial", 12), fg='#bbbbbb', bg='#2b2b2b')
        subtext_label.pack(pady=(0, 40))

        options_frame = tk.Frame(self.startup_screen, bg='#2b2b2b')
        options_frame.pack(pady=20)

        file_frame = tk.Frame(options_frame, bg='#333', bd=2, relief=tk.RAISED)
        file_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.BOTH, expand=True)

        serial_frame = tk.Frame(options_frame, bg='#333', bd=2, relief=tk.RAISED)
        serial_frame.pack(side=tk.RIGHT, padx=20, pady=10, fill=tk.BOTH, expand=True)

        file_label = tk.Label(file_frame, text="📂", font=("Arial", 64), bg='#333', fg='#5e97f6')
        file_label.pack(pady=(10, 10))

        file_text = tk.Label(file_frame, text="Dosyadan Aktarım", font=("Arial", 14), fg='white', bg='#333')
        file_text.pack()

        serial_label = tk.Label(serial_frame, text="🔌", font=("Arial", 64), bg='#333', fg='#9c27b0')
        serial_label.pack(pady=(10, 10))

        serial_text = tk.Label(serial_frame, text="Seri Cihazdan Aktarım", font=("Arial", 14), fg='white', bg='#333')
        serial_text.pack()

        file_frame.bind("<Button-1>", lambda e: self.start_from_file())
        serial_frame.bind("<Button-1>", lambda e: self.start_from_serial())
