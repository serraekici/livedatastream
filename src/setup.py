from cx_Freeze import setup, Executable

# Uygulamanızın temel ayarları
setup(
    name = "MyApp",
    version = "1.0",
    description = "My Application",
    executables = [Executable("main.py", base="Win32GUI", icon="myicon.ico")]
)
