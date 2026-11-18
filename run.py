
import os
import sys
import subprocess
import time
import shutil
import socket

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def port_running(port):
    with socket.socket() as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0

def start_codespaces():
    # Install graphical dependencies if missing
    packages = ["Xvfb", "x11vnc", "websockify"]

    if any(not shutil.which(p) for p in packages):
        subprocess.check_call(["sudo", "apt-get", "update"])
        subprocess.check_call([
            "sudo", "apt-get", "install", "-y",
            "xvfb", "x11vnc", "novnc",
            "websockify", "python3-tk"
        ])

    os.environ["DISPLAY"] = ":90"

    if not os.path.exists("/tmp/.X11-unix/X90"):
        subprocess.Popen([
            "Xvfb", ":90", "-screen", "0",
            "1440x900x24"
        ])
        time.sleep(3)

    # Create password on first run
    password_file = os.path.expanduser("~/.vnc/passwd")

    if not os.path.exists(password_file):
        subprocess.check_call(["x11vnc", "-storepasswd"])

    if not port_running(5907):
        subprocess.Popen([
            "x11vnc", "-display", ":90",
            "-localhost", "-usepw",
            "-forever", "-shared",
            "-rfbport", "5907"
        ])
        time.sleep(2)

    if not port_running(6080):
        subprocess.Popen([
            "websockify",
            "--web=/usr/share/novnc",
            "6080", "localhost:5907"
        ])

    print("Open port 6080 and select vnc.html")

# Install Python libraries if missing
try:
    import requests
    import sklearn
except ImportError:
    subprocess.check_call([
        sys.executable, "-m", "pip",
        "install", "requests", "scikit-learn"
    ])

# Optional Ollama server
if shutil.which("ollama") and not port_running(11434):
    subprocess.Popen(["ollama", "serve"])
    time.sleep(3)

# Detect Codespaces
if os.environ.get("CODESPACES") == "true":
    start_codespaces()

# Launch graphical application
subprocess.call([sys.executable, "shopsmart.py"])

