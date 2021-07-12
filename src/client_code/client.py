import sys
from PyQt5 import QtWidgets
from gui_client import GameClient

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    wind = GameClient(sys.argv[1], int(sys.argv[2]))
    if wind.token:
        wind.show()
        sys.exit(app.exec())
