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
    QPushButton, QMessageBox, QVBoxLayout, QWidget, QCheckBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

# === CONFIGURACIÓN ===
APP_NAME = "GRUPO DIAE"
LOGO_PATH = "logo.png"
QSS_PATH = "style.qss"
KEYS_FOLDER = "keys"
SESSION_FILE = "session.json"
DONT_ASK_FLAG = "dont_ask_again.flag"
MASTER_KEY = b'deg4OnaTyL0h4DyvCqq9qAD9ZOMsoDD3jhsEhRRi8sk='
CHROME_PORTABLE_PATH = os.path.join("chrome_portable", "GoogleChromePortable", "GoogleChromePortable.exe")


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - Perplexity PRO")
        self.setFixedSize(450, 600)

        if os.path.exists(QSS_PATH):
            with open(QSS_PATH, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())

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
        logo.setObjectName("logo")  # <- aquí

        self.welcome_label = QLabel("Bienvenido a GRUPO DIAE")
        self.welcome_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setWordWrap(True)
        layout.addWidget(self.welcome_label)
        self.welcome_label.setObjectName("welcome_label")

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

        self.help_label = QLabel("¿Necesitas ayuda? Llámanos al 966 387 995")
        self.help_label.setAlignment(Qt.AlignCenter)
        self.help_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(self.help_label)

        # Auto-login si ya hay sesión
        self.try_auto_login()

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

    def save_session(self, user_id, user_pin):
        try:
            data = json.dumps({"id": user_id, "pin": user_pin})
            encrypted = Fernet(MASTER_KEY).encrypt(data.encode())
            with open(SESSION_FILE, "wb") as f:
                f.write(encrypted)
        except Exception as e:
            print(f"Error al guardar sesión: {e}")

    def load_session(self):
        try:
            if not os.path.exists(SESSION_FILE):
                return None
            with open(SESSION_FILE, "rb") as f:
                encrypted = f.read()
            decrypted = Fernet(MASTER_KEY).decrypt(encrypted)
            return json.loads(decrypted.decode())
        except:
            return None

    def try_auto_login(self):
        session = self.load_session()
        if session:
            self.id_input.setText(session.get("id", ""))
            self.pin_input.setText(session.get("pin", ""))
            self.handle_login(auto=True)

    def ask_save_credentials(self, user_id, user_pin):
        if os.path.exists(DONT_ASK_FLAG):
            return

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Guardar acceso")
        msg.setText("¿Deseas guardar tu ID y PIN para iniciar sesión automáticamente?")
        checkbox = QCheckBox("No volver a preguntar")
        msg.setCheckBox(checkbox)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        choice = msg.exec_()

        if checkbox.isChecked():
            with open(DONT_ASK_FLAG, "w") as f:
                f.write("1")

        if choice == QMessageBox.Yes:
            self.save_session(user_id, user_pin)

    def handle_login(self, auto=False):
        user_id = self.id_input.text().strip().lower()
        user_pin = self.pin_input.text().strip().upper()
        key_path = os.path.join(KEYS_FOLDER, f"{user_id}.key")

        if not os.path.exists(key_path):
            if not auto:
                QMessageBox.critical(self, "Acceso denegado", "Licencia no encontrada.")
            return

        key_info = self.decrypt_key_file(key_path)
        if not key_info:
            if not auto:
                QMessageBox.critical(self, "Error", "La licencia es inválida o corrupta.")
            return

        device_hash = self.get_device_hash()
        if key_info.get("device_hash") != device_hash:
            if not auto:
                QMessageBox.critical(self, "Dispositivo no autorizado", "Esta licencia no corresponde a este equipo.")
            return

        if key_info.get("pin") != user_pin:
            if not auto:
                QMessageBox.critical(self, "Código incorrecto", "El PIN ingresado no coincide.")
            return

        expiry_date = datetime.datetime.strptime(key_info.get("expiry_date"), "%Y-%m-%d")
        if expiry_date < datetime.datetime.now():
            if not auto:
                QMessageBox.critical(self, "Licencia expirada", f"Esta licencia expiró el {expiry_date.date()}.")
            return

        nombre = key_info.get('nombre', user_id)
        subs = key_info.get("subscripcion", "desconocida").upper()

        self.welcome_label.setText(f"Bienvenido a GRUPO DIAE docente\n{nombre}")
        if not auto:
            QMessageBox.information(self, "✅ Acceso válido", f"Bienvenido {nombre}\nLicencia válida hasta: {expiry_date}")
            self.ask_save_credentials(user_id, user_pin)

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


def start_app():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start_app()
