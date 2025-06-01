import time
import sys

# === CONFIGURACIÓN (DESACTIVADA) ===
CHECK_INTERVAL = 5  # segundos

# === FUNCIÓN PRINCIPAL (INACTIVA) ===
def monitor():
    while True:
        # Esta versión está desactivada: no verifica carpetas ni emite advertencias.
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("[MONITOR] Detenido.")

