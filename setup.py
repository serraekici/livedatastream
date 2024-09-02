from cx_Freeze import setup, Executable
import sys
import os

# Python'un yüklü olduğu dizini kontrol etmek için
python_path = os.path.dirname(os.__file__)
print(python_path)

# Uygulamanızın temel ayarları
build_exe_options = {
    "packages": ["os"],
    "includes": ["tkinter"],
    "include_files": [],  # Gerekli ekstra dosyalar burada eklenebilir
    "excludes": []
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Konsol penceresini gizlemek için

setup(
    name="Data Stream",
    version="1.0",
    description="Live-Constant Data Stream Application",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="myicon.ico")]
)
