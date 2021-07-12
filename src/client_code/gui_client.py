import os
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PyQt5 import QtWidgets, QtCore, QtGui
from game_client_ui import Ui_MainWindow
from registration_client_ui import Ui_Dialog as Reg_Ui
from sighin_client_ui import Ui_Dialog as Log_Ui
from end_game_ui import Ui_Dialog as End_Ui
from client_socket import ClientSockWith
from threads_workers import FindMatchWorker, MakeTurnWorker

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


class EndGameWindow(QDialog, End_Ui):
    def __init__(self, icon, title, main_window, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.label_result.resize(icon.size())
        self.label_result.setPixmap(icon)
        self.main_window = main_window
        self.exit_button.clicked.connect(self.exit_game)
        self.new_game_button.clicked.connect(self.new_game)

    def exit_game(self):
        self.main_window.close()
        self.close()

    def new_game(self):
        print("START NEW GAME")
        # self.main_window.clear_field()
        self.close()
        print("Close NEW GAME MENU")


class LoginWindow(QtWidgets.QDialog, Log_Ui):
    def __init__(self, main_window, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.main_window = main_window
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.login_button.clicked.connect(self.login)
        self.create_account_button.clicked.connect(self.start_registration)

    def start_registration(self):
        reg_window = RegistrationWindow(self.main_window.server_host, self.main_window.server_port)
        reg_window.show()
        reg_window.exec()

    def login(self):
        if self.username_line.text() and self.password_line:
            with ClientSockWith(self.main_window.server_host, self.main_window.server_port) as client_socket:
                response = client_socket.login(self.username_line.text(), self.password_line.text())
                if response["authorization"]:
                    self.main_window.token = response["token"]
                    self.main_window.username = self.username_line.text()
                    print("success")
                    self.close()
                else:
                    err_w = MessageWindow("Invalid username or password", parent=self)
                    err_w.exec()
        else:
            MessageWindow("Be sure to enter your password and username.", parent=self).exec()


class MessageWindow(QDialog):
    def __init__(self, message, title="Error", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        q_button = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(q_button)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(message)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class RegistrationWindow(QtWidgets.QDialog, Reg_Ui):
    def __init__(self, host, port, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.host = host
        self.port = port
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.conf_button.clicked.connect(self.sighup)
        self.cancel_button.clicked.connect(self.close)

    def sighup(self):
        if self.username_line.text() and self.password_line and self.email_line:
            with ClientSockWith(self.host, self.port) as client_socket:
                response = client_socket.registration(
                    self.username_line.text(),
                    self.password_line.text(),
                    self.email_line.text())
                if response["registration"]:
                    msg = MessageWindow("Registration success", title="Congratulation", parent=self)
                    msg.exec()
                    self.close()
                else:
                    err_w = MessageWindow("User with username already exists", parent=self)
                    err_w.exec()
        else:
            MessageWindow("Be sure to enter your password, username and email.", parent=self).exec()


class GameClient(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, host, port, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.token = None
        self.server_host = host
        self.server_port = port
        self.username = None
        self.setupUi(self)
        self.login()
        self.mode = "pvp"
        self.end_game = None
        self.setup_game()
        self.comboBox.currentIndexChanged.connect(self.set_game_mode)
        self.connect_button.clicked.connect(self.launcher_find_match)
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
        self.bind_button()
        self.switch_block_field()
        self.__threads = []
        self.index = None
        self.setFixedSize(850, 700)

    def login(self):
        window = LoginWindow(self)
        window.show()
        window.exec_()

    def setup_game(self):
        self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "question_mark.png")))

    def switch_block_field(self):
        for button in self.field:
            button.setEnabled(not button.isEnabled())

    def bind_button(self):
        for index, button in enumerate(self.field, 1):
            button.clicked.connect(lambda state, x=index: self.launch_make_turn(x))

    def set_game_mode(self):
        if self.comboBox.currentText() == "Easy AI":
            self.mode = "easy"
            self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "easy_ai.png")))
            msg = MessageWindow("Coming soon", title="Information", parent=self)
            msg.exec()
        elif self.comboBox.currentText() == "Medium AI":
            self.mode = "medium"
            self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "med_ai.png")))
            msg = MessageWindow("Coming soon", title="Information", parent=self)
            msg.exec()
        elif self.comboBox.currentText() == "Hard AI":
            self.mode = "hard"
            self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "hard_ai.png")))
            msg = MessageWindow("Coming soon", title="Information", parent=self)
            msg.exec()
        else:
            self.mode = "pvp"
            self.you.setPixmap(QtGui.QPixmap(os.path.join(SCRIPT_PATH, "..", "..", "data", "question_mark.png")))

    def launcher_find_match(self):
        self.connect_button.setEnabled(False)
        worker = FindMatchWorker(self.server_host, self.server_port, self.username, self.token, "pvp")
        thread = QtCore.QThread()
        thread.setObjectName('thread_find_match')
        self.__threads.append((thread, worker))
        worker.moveToThread(thread)
        worker.sig_done.connect(self.on_worker_find_match_done)
        thread.started.connect(worker.work)
        thread.start()

    @QtCore.pyqtSlot(dict)
    def on_worker_find_match_done(self, response):
        if response["result"]:
            msg = MessageWindow("Your turn!", title="Game start", parent=self)
            msg.exec()
            self.switch_block_field()
            if response["turn_opponent"]:
                self.field[response["turn_opponent"] - 1].setIcon(self.circle_icon)
                self.field[response["turn_opponent"] - 1].setIconSize(
                    self.field[response["turn_opponent"] - 1].size())

    def launch_make_turn(self, index):
        self.field[index - 1].setIcon(self.cross_icon)
        self.field[index - 1].setIconSize(self.field[index - 1].size())
        self.switch_block_field()
        self.index = index
        worker = MakeTurnWorker(self.server_host, self.server_port, self.username, self.token, index)
        thread = QtCore.QThread()
        thread.setObjectName('thread_make_turn')
        self.__threads.append((thread, worker))
        worker.moveToThread(thread)
        worker.sig_done.connect(self.on_worker_make_turn_done)
        thread.started.connect(worker.work)
        thread.start()

    @QtCore.pyqtSlot(dict)
    def on_worker_make_turn_done(self, response):
        if response["result"]:
            if response["turn_opponent"]:
                self.field[response["turn_opponent"] - 1].setIcon(self.circle_icon)
                self.field[response["turn_opponent"] - 1].setIconSize(
                    self.field[response["turn_opponent"] - 1].size())
            if response["endgame"]:
                self.end_game_window(response)
        self.switch_block_field()

    @QtCore.pyqtSlot()
    def abort_workers(self):
        for thread, worker in self.__threads:  # note nice unpacking by Python, avoids indexing
            thread.quit()  # this will quit **as soon as thread event loop unblocks**
            thread.wait()  # <- so you need to wait for it to *actually* quit

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
        self.end_game = EndGameWindow(icon, title, self, parent=self)
        self.end_game.show()
        self.end_game.exec_()
        self.clear_field()

    def clear_field(self):
        for button in self.field:
            button.setIcon(QtGui.QIcon())
        if self.end_game:
            self.switch_block_field()
            self.end_game = None
            self.launcher_find_match()

    def logout(self):
        self.clear_field()
        self.token = None
        self.username = None
        self.hide()
        self.login()
