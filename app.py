import os
import sys
import platform
import hashlib
import json
import datetime
import subprocess
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit,
    QPushButton, QMessageBox, QVBoxLayout, QWidget
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

# === CONFIGURACIÓN ===
APP_NAME = "GRUPO DIAE"
LOGO_PATH = "logo.png"
QSS_PATH = "style.qss"
KEYS_FOLDER = "keys"
MASTER_KEY = b'deg4OnaTyL0h4DyvCqq9qAD9ZOMsoDD3jhsEhRRi8sk='
CHROME_PORTABLE_PATH = os.path.join("chrome_portable", "GoogleChromePortable", "GoogleChromePortable.exe")


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - Perplexity PRO")
        self.setFixedSize(450, 600)

        if os.path.exists(QSS_PATH):
            self.setStyleSheet(open(QSS_PATH, 'r').read())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        central_widget.setLayout(layout)

        logo = QLabel()
        if os.path.exists(LOGO_PATH):
            pixmap = QPixmap(LOGO_PATH).scaledToHeight(100, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Bienvenido a GRUPO DIAE")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID del docente")
        self.id_input.setObjectName("inputField")
        layout.addWidget(self.id_input)

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Código PIN")
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setObjectName("inputField")
        layout.addWidget(self.pin_input)

        self.login_btn = QPushButton("VERIFICAR ACCESO")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

    def get_device_hash(self):
        info = platform.uname()
        base = info.node + info.system + info.machine
        return hashlib.sha256(base.encode()).hexdigest()

    def decrypt_key_file(self, filepath):
        try:
            with open(filepath, "rb") as f:
                encrypted = f.read()
            decrypted = Fernet(MASTER_KEY).decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception as e:
            print(f"Error al descifrar la licencia: {e}")
            return None

    def handle_login(self):
        user_id = self.id_input.text().strip().lower()
        user_pin = self.pin_input.text().strip().upper()
        key_path = os.path.join(KEYS_FOLDER, f"{user_id}.key")

        if not os.path.exists(key_path):
            QMessageBox.critical(self, "Acceso denegado", "Licencia no encontrada.")
            return

        key_info = self.decrypt_key_file(key_path)
        if not key_info:
            QMessageBox.critical(self, "Error", "La licencia es inválida o corrupta.")
            return

        device_hash = self.get_device_hash()
        if key_info.get("device_hash") != device_hash:
            QMessageBox.critical(self, "Dispositivo no autorizado", "Esta licencia no corresponde a este equipo.")
            return

        if key_info.get("pin") != user_pin:
            QMessageBox.critical(self, "Código incorrecto", "El PIN ingresado no coincide.")
            return

        expiry_date = datetime.datetime.strptime(key_info.get("expiry_date"), "%Y-%m-%d")
        if expiry_date < datetime.datetime.now():
            QMessageBox.critical(self, "Licencia expirada", f"Esta licencia expiró el {expiry_date.date()}.")
            return

        subs = key_info.get("subscripcion", "desconocida").upper()
        QMessageBox.information(self, "✅ Acceso válido", f"Bienvenido {key_info.get('nombre', user_id)}\nSubscripción: {subs}")
        self.launch_app()

    def launch_app(self):
        if not os.path.exists(CHROME_PORTABLE_PATH):
            QMessageBox.critical(self, "Error", "Navegador Chrome Portable no encontrado.")
            return
        subprocess.Popen([
            CHROME_PORTABLE_PATH,
            "--user-data-dir=chrome_portable/GoogleChromePortable/Data/profile",
            "--app=https://www.perplexity.ai/"
        ])
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
