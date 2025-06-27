import subprocess
import threading
import time
import webview

def start_streamlit():
    subprocess.Popen(["streamlit", "run", "GUI.py", "--server.headless=true"])

if __name__ == "__main__":
    threading.Thread(target=start_streamlit, daemon=True).start()

    time.sleep(2)

    webview.create_window("Coupling measurements", "http://localhost:8501", width=800, height=600)
    webview.start()