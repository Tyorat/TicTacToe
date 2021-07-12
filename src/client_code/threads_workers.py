from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from client_socket import ClientSockWith


class FindMatchWorker(QObject):
    # signal when match is find
    sig_done = pyqtSignal(dict)

    def __init__(self, host: str, port: int, username: str, token: str, game_mode: str):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.token = token
        self.game_mode = game_mode

    @pyqtSlot()
    def work(self):
        with ClientSockWith(self.host, self.port) as client_socket:
            response = client_socket.find_match(self.username, self.token, self.game_mode)
            self.sig_done.emit(response)


class MakeTurnWorker(QObject):
    # signal when match is find
    sig_done = pyqtSignal(dict)

    def __init__(self, host: str, port: int, username: str, token: str, index: int):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.token = token
        self.index = index

    @pyqtSlot()
    def work(self):
        with ClientSockWith(self.host, self.port) as client_socket:
            req = client_socket.request_turn(
                username=self.username,
                token=self.token,
                ceil=self.index)
            self.sig_done.emit(req)
