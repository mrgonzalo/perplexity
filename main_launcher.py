import subprocess
import time
import os
import sys

# Ejecutar monitor.py como proceso independiente oculto
def run_monitor():
    try:
        subprocess.Popen(
            [sys.executable, "monitor.py"],
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        print("[INFO] Monitor iniciado.")
    except Exception as e:
        print(f"[ERROR] Al iniciar monitor: {e}")

# Ejecutar app.py (interfaz principal)
def run_app():
    try:
        subprocess.Popen(
            [sys.executable, "app.py"],
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        print("[INFO] App iniciada.")
    except Exception as e:
        print(f"[ERROR] Al iniciar app: {e}")

from updater import check_for_update
from monitor import start_monitor
from app import start_app

if __name__ == "__main__":
    check_for_update()
    start_monitor()
    start_app()

    check_for_update()
    time.sleep(1.5)  # Pequeña espera para que el monitor arranque primero
    run_app()
