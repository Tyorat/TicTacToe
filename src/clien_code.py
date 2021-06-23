import os
import json
import subprocess
import sys
import datetime
import time
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets, QtCore, QtGui, Qt, QtSql
from game_client_ui import Ui_MainWindow

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_BASE_PATH = os.path.join(SCRIPT_PATH, "ted.data")


class GameClient(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mode = "pvp"
        self.symbol = None
        self.setup_game()
        self.comboBox.currentIndexChanged.connect(self.set_game_mode)

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
    app = QtWidgets.QApplication(sys.argv)
    wind = GameClient()
    wind.show()
    sys.exit(app.exec_())
