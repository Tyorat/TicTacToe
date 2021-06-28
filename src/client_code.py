import os
import json
import socket
import subprocess
import sys
import datetime
import time
from PyQt5.QtWidgets import QMessageBox, QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PyQt5 import QtWidgets, QtCore, QtGui, Qt, QtSql
from game_client_ui import Ui_MainWindow
from registration_client_ui import Ui_Dialog as Reg_Ui
from sighin_client_ui import Ui_Dialog as Log_Ui

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_BASE_PATH = os.path.join(SCRIPT_PATH, "ted.data")


class ClientSockWith:
    def __init__(self, host, port):
        self.__server = ClientSocket()

    def __enter__(self):
        return self.__server

    def __exit__(self, some_type, value, traceback):
        print("close server")
        self.__server.client_sock.close()


class ClientSocket:
    def __init__(self):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect(('0', 8080))

    def login(self, username, password):
        req = {"command": "login", "username": username, "password": password}
        self.client_sock.sendall(bytes(json.dumps(req), "utf-8"))
        data = self.client_sock.recv(1024)
        return json.loads(data)

    def registration(self, username, password, email):
        req = {"command": "register", "username": username, "password": password, "email": email}
        self.client_sock.sendall(bytes(json.dumps(req), "utf-8"))
        data = self.client_sock.recv(1024)
        return json.loads(data)


class MessageWindow(QDialog):
    def __init__(self, message, title="Error"):
        super().__init__()
        self.setWindowTitle(title)
        QBtn = QDialogButtonBox.Ok
        # self.setIcon(QMessageBox.Critical)
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(message)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class RegistrationWindow(QtWidgets.QDialog, Reg_Ui):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.conf_button.clicked.connect(self.sighup)
        self.cancel_button.clicked.connect(self.close)

    def sighup(self):
        if self.username_line.text() and self.password_line and self.email_line:
            with ClientSockWith(1, 1) as client_socket:
                response = client_socket.registration(
                    self.username_line.text(),
                    self.password_line.text(),
                    self.email_line.text())
                if response["registration"]:
                    msg = MessageWindow("Registration success", title="Congratulation")
                    msg.exec()
                    self.close()
                else:
                    err_w = MessageWindow("User with username already exists")
                    err_w.exec()
        else:
            MessageWindow("Be sure to enter your password, username and email.").exec()


class LoginWindow(QtWidgets.QDialog, Log_Ui):
    def __init__(self, main_window, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.main_window = main_window
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.login_button.clicked.connect(self.login)
        self.create_account_button.clicked.connect(self.start_registration)

    @staticmethod
    def start_registration(self):
        reg_window = RegistrationWindow()
        reg_window.show()
        reg_window.exec()

    def login(self):
        if self.username_line.text() and self.password_line:
            with ClientSockWith(1, 1) as client_socket:
                response = client_socket.login(self.username_line.text(), self.password_line.text())
                if response["authorization"]:
                    self.main_window.taken = response["taken"]
                    print("success")
                    self.close()
                else:
                    err_w = MessageWindow("Invalid username or password")
                    err_w.exec()
        else:
            MessageWindow("Be sure to enter your password and username.").exec()


class GameClient(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.taken = None
        self.login()
        self.setupUi(self)
        self.mode = "pvp"
        self.symbol = None
        self.setup_game()
        self.comboBox.currentIndexChanged.connect(self.set_game_mode)

    def login(self):
        print("LOGIN")
        window = LoginWindow(self)
        window.show()
        window.exec_()

    def set_game_mode(self):
        # self.comboBox.setItemText(0, _translate("MainWindow", "PvP"))
        # self.comboBox.setItemText(1, _translate("MainWindow", "Easy AI"))
        # self.comboBox.setItemText(2, _translate("MainWindow", "Medium AI"))
        # self.comboBox.setItemText(3, _translate("MainWindow", "Hard Ai"))
        if self.comboBox.currentText() == "Easy AI":
            self.mode = "easy"
            self.you.setPixmap(QtGui.QPixmap("../data/easy_ai.png"))
        elif self.comboBox.currentText() == "Medium AI":
            self.mode = "medium"
            self.you.setPixmap(QtGui.QPixmap("../data/med_ai.png"))
        elif self.comboBox.currentText() == "Hard AI":
            self.mode = "hard"
            self.you.setPixmap(QtGui.QPixmap("../data/hard_ai.png"))
        else:
            self.mode = "pvp"
            self.you.setPixmap(QtGui.QPixmap("../data/question_mark.png"))

    def setup_game(self):
        self.you.setPixmap(QtGui.QPixmap("../data/question_mark.png"))


if __name__ == "__main__":
    # clSoc = ClientSocket()
    app = QtWidgets.QApplication(sys.argv)
    wind = GameClient()
    # wind = LoginWindow()
    wind.show()
    sys.exit(app.exec_())
