import os
import json
import socket
# import subprocess
import sys
# import datetime
# import time
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PyQt5 import QtWidgets, QtCore, QtGui
from game_client_ui import Ui_MainWindow
from registration_client_ui import Ui_Dialog as Reg_Ui
from sighin_client_ui import Ui_Dialog as Log_Ui
from end_game_ui import Ui_Dialog as End_Ui

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


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
        try:
            self.client_sock.connect(('0', 8080))
        except socket.error:
            MessageWindow("No connection with game server.").exec()
            raise

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

    def find_match(self, username, taken, type_match):
        req = {"command": "start", "username": username, "taken": taken, "type": type_match}
        self.client_sock.sendall(bytes(json.dumps(req), "utf-8"))
        data = self.client_sock.recv(1024)
        return json.loads(data)

    def request_turn(self, username, taken, ceil):
        req = {"command": "turn", "username": username, "taken": taken, "ceil": ceil}
        self.client_sock.sendall(bytes(json.dumps(req), "utf-8"))
        data = self.client_sock.recv(1024)
        return json.loads(data)


class EndGameWindow(QDialog, End_Ui):
    def __init__(self, icon, title, main_window):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(title)
        # icon.sclaed(500, 200)
        self.label_result.resize(icon.size())
        self.label_result.setPixmap(icon)
        self.main_window = main_window
        self.exit_button.clicked.connect(self.exit_game)
        self.new_game_button.clicked.connect(main_window.clear_field)

    def exit_game(self):
        self.main_window.close()
        self.close()

    def new_game(self):
        self.main_window.clear_field(self)


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
    def start_registration():
        reg_window = RegistrationWindow()
        reg_window.show()
        reg_window.exec()

    def login(self):
        if self.username_line.text() and self.password_line:
            with ClientSockWith(1, 1) as client_socket:
                response = client_socket.login(self.username_line.text(), self.password_line.text())
                if response["authorization"]:
                    self.main_window.taken = response["taken"]
                    self.main_window.username = self.username_line.text()
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
        self.username = None
        self.setupUi(self)
        self.login()
        self.mode = "pvp"
        self.end_game = None
        self.symbol = None
        self.setup_game()
        self.comboBox.currentIndexChanged.connect(self.set_game_mode)
        self.connect_button.clicked.connect(self.find_match)
        self.cross_icon = QtGui.QIcon(os.path.join(SCRIPT_PATH, "..", "..", "data", "cross.png"))
        self.circle_icon = QtGui.QIcon(os.path.join(SCRIPT_PATH, "..", "..", "data", "circle.png"))
        self.field = [
            self.cel_1,
            self.cel_2,
            self.cel_3,
            self.cel_4,
            self.cel_5,
            self.cel_6,
            self.cel_7,
            self.cel_8,
            self.cel_9]
        self.switch_block_field()

    def clear_field(self):
        list(map(lambda x: x.setIcon(QtGui.QIcon()), self.field))
        if self.end_game:
            self.end_game.close()
            self.end_game = None

    def switch_block_field(self):
        # list(map(lambda x: x.setEnabled(not x.isEnabled()), self.field))
        pass
        # self.cel_1.isEnabled()

    def make_turn(self, button, index):
        self.switch_block_field()
        with ClientSockWith(1, 1) as client_socket:
            req = client_socket.request_turn(username=self.username, taken=self.taken, ceil=index)
            print(f"req{req}")
            previous_icon = button.icon()
            button.setIcon(self.cross_icon)
            button.setIconSize(button.size())
            self.update()
            if req["result"]:
                if req["turn_opponent"]:
                    self.field[req["turn_opponent"] - 1].setIcon(self.circle_icon)
                    self.field[req["turn_opponent"] - 1].setIconSize(
                        self.field[req["turn_opponent"] - 1].size())
                if req["endgame"]:
                    self.end_game_window(req)
            else:
                button.setIcon(previous_icon)
            self.switch_block_field()

    def end_game_window(self, req):
        message = req["message"]
        if message == "draw":
            title = 'Draw!'
            icon = QtGui.QPixmap(os.path.join("..", "..", "data", "draw.png"))
        elif message[4:] == self.username:
            title = "Congratulation"
            icon = QtGui.QPixmap(os.path.join("..", "..", "data", "win.jpg"))
        else:
            title = "Defeat"
            icon = QtGui.QPixmap(os.path.join("..", "..", "data", "lose.png"))
        self.end_game = EndGameWindow(icon, title, self)
        self.end_game.show()
        self.end_game.exec_()

    def bind_button(self):
        # for index, button in enumerate(self.field, 1):
        #     print(index, button)
        #     button.clicked.connect(lambda: self.make_turn(button, index))
        self.field[0].clicked.connect(lambda: self.make_turn(self.field[0], 1))
        self.field[1].clicked.connect(lambda: self.make_turn(self.field[1], 2))
        self.field[2].clicked.connect(lambda: self.make_turn(self.field[2], 3))
        self.field[3].clicked.connect(lambda: self.make_turn(self.field[3], 4))
        self.field[4].clicked.connect(lambda: self.make_turn(self.field[4], 5))
        self.field[5].clicked.connect(lambda: self.make_turn(self.field[5], 6))
        self.field[6].clicked.connect(lambda: self.make_turn(self.field[6], 7))
        self.field[7].clicked.connect(lambda: self.make_turn(self.field[7], 8))
        self.field[8].clicked.connect(lambda: self.make_turn(self.field[8], 9))

    def find_match(self):
        with ClientSockWith(1, 1) as client_socket:
            response = client_socket.find_match(self.username, self.taken, "pvp")
            print(f"response {response}")
            if response["result"]:
                self.switch_block_field()
                self.bind_button()
                if response["turn_opponent"]:
                    self.field[response["turn_opponent"] - 1].setIcon(self.circle_icon)
                    self.field[response["turn_opponent"] - 1].setIconSize(
                        self.field[response["turn_opponent"] - 1].size())
                    # self.field[response["turn_opponent"] - 1]

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
            self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "easy_ai.png")))
            msg = MessageWindow("Coming soon", title="Information")
            msg.exec()
        elif self.comboBox.currentText() == "Medium AI":
            self.mode = "medium"
            self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "med_ai.png")))
            msg = MessageWindow("Coming soon", title="Information")
            msg.exec()
        elif self.comboBox.currentText() == "Hard AI":
            self.mode = "hard"
            self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "hard_ai.png")))
            msg = MessageWindow("Coming soon", title="Information")
            msg.exec()
        else:
            self.mode = "pvp"
            self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "question_mark.png")))

    def setup_game(self):
        self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "question_mark.png")))


if __name__ == "__main__":
    # clSoc = ClientSocket()
    app = QtWidgets.QApplication(sys.argv)
    wind = GameClient()
    # wind = LoginWindow()
    if wind.taken:
        wind.show()
        sys.exit(app.exec_())
