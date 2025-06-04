import time
import sys
import subprocess
import os

# === CONFIGURACIÓN (DESACTIVADA) ===
CHECK_INTERVAL = 5  # segundos

# === FUNCIÓN DE MONITOREO (INACTIVA) ===
def monitor():
    while True:
        # Esta versión está desactivada: no verifica carpetas ni emite advertencias.
        time.sleep(CHECK_INTERVAL)

# === FUNCIÓN PARA INICIAR COMO SUBPROCESO OCULTO DESDE LAUNCHER ===
def start_monitor():
    try:
        subprocess.Popen(
            [sys.executable, os.path.abspath(__file__)],
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        print("[INFO] Monitor iniciado como proceso oculto.")
    except Exception as e:
        print(f"[ERROR] Al iniciar monitor: {e}")

if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("[MONITOR] Detenido.")
