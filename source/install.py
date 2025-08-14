requirements = [
    "streamlit==1.48.1",
    "streamlit_extras==0.7.6",
    "streamlit_navigation_bar==3.3.0",
    "streamlit_autorefresh==1.0.1",
    "schemdraw==0.21",
    "pyvisa==1.15.0",
    "pyyaml==6.0.2",
    "lgpio",
    "reportlab==4.4.3",
    "pyvisa-py==0.8.0",
    "numpy==2.2.6",
    "PyQt5==5.15.11",
    "pyperclip==1.9.0",
    "beautifulsoup4==4.13.4"
]

import subprocess
import sys
import os


def install_package(package_name, args=""):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + ([args] if args else []) + [package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Successfully installed {package_name}")
    except Exception as e:
        print(f"Failed to install {package_name}: {e}")
        
if __name__ == "__main__":
    print("Installing required packages... It is likely fine if some packages fail to install.")
    for package in requirements:
        install_package(package)
    install_package(os.path.join(os.path.dirname(__file__), "libraries", "pymeasure"), "-e")