import subprocess
import threading
import webview
import os
import yaml
import sys


if __name__ == "__main__":
    from utils import *
    config = read_config()

    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", os.path.join(os.path.dirname(__file__), "GUI.py"), "streamlit"],
    )
