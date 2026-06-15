import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
PORT = 8501
SHUTDOWN_FLAG = APP_DIR / "shutdown.flag"


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) == 0


def stop_process_tree(proc):
    """Stop Streamlit and its child processes on Windows/macOS/Linux."""
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main():
    os.chdir(APP_DIR)
    if SHUTDOWN_FLAG.exists():
        SHUTDOWN_FLAG.unlink()

    if is_port_open(PORT):
        print(f"AI Learning Coach may already be running at http://localhost:{PORT}")
        print("If this is an old instance, close it before starting again.")
        webbrowser.open(f"http://localhost:{PORT}")
        return

    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(PORT),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]
    proc = subprocess.Popen(cmd, cwd=str(APP_DIR))

    opened = False
    for _ in range(80):
        if is_port_open(PORT):
            if not opened:
                webbrowser.open(f"http://localhost:{PORT}")
                opened = True
            break
        if proc.poll() is not None:
            print("Streamlit failed to start. Please run install_requirements.bat first.")
            return
        time.sleep(0.25)

    print("AI Learning Coach is running.")
    print("To stop it safely, click the in-app '关闭程序' button or close this window.")

    try:
        while proc.poll() is None:
            if SHUTDOWN_FLAG.exists():
                print("Shutdown request received. Stopping Streamlit...")
                try:
                    SHUTDOWN_FLAG.unlink()
                except Exception:
                    pass
                stop_process_tree(proc)
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_process_tree(proc)


if __name__ == "__main__":
    main()
