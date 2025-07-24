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
        [sys.executable, "-m", "streamlit", "run", os.path.join(os.path.dirname(__file__), "GUI.py"), f"--server.headless={config['client']['windowMode']}", "streamlit"],
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

    import io
    def is_raspberry_pi():
        try:
            return "raspberry pi" in io.open('/sys/firmware/devicetree/base/model', 'r').read().lower()
        except:
            return False

    if config["client"]['windowMode']:
        if is_raspberry_pi():
            subprocess.Popen(["chromium-browser", "--kiosk", url])
        else:
            webview.create_window("Coupling measurements", url, width=800, height=600, text_select=True)
            webview.start(debug=config["client"]['developerMode'])
            process.terminate() # close the Streamlit process when the window is closed