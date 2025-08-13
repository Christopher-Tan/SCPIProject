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
        [sys.executable, "-m", "streamlit", "run", os.path.join(os.path.dirname(__file__), "GUI.py"), f"--server.headless={is_raspberry_pi()}", "streamlit"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    
    def process_output(break_condition=lambda line: False):
        for line in process.stdout:
            print(f"[Streamlit] {line.strip()}")
            out = break_condition(line)
            if out:
                return out
    
    url = process_output(lambda line: line.split("Local URL: ")[1] if "Local URL: " in line else None)
    
    threading.Thread(target=process_output).start()

    if is_raspberry_pi():
        subprocess.Popen(["chromium-browser", "--kiosk", url])
    
    process.wait()