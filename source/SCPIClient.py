import subprocess
import threading
import time
import webview
import os

if __name__ == "__main__":
    process = subprocess.Popen(
        ["streamlit", "run", os.path.join(os.path.dirname(__file__), "GUI.py"), "--server.headless=true", "streamlit"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    
    def process_output(break_condition=lambda line: False):
        for line in process.stdout:
            print(f"[Streamlit] {line.strip()}")
            out = break_condition()
            if out:
                return out
    
    url = process_output(lambda line: line.split("Local URL: ")[1] if "Local URL: " in line else None)
    
    threading.Thread(target=process_output).start()

    webview.create_window("Coupling measurements", url, width=800, height=600)
    webview.start()