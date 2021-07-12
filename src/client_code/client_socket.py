import json
import socket


class ClientSockWith:
    def __init__(self, host, port):
        self.__server = ClientSocket(host, port)

    def __enter__(self):
        return self.__server

    def __exit__(self, some_type, value, traceback):
        self.__server.client_sock.close()


class ClientSocket:
    def __init__(self, host, port):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_sock.connect((host, port))
        except socket.error:
            # MessageWindow("No connection with game server.").exec()
            print("No connection with game server.")
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

    def find_match(self, username, token, type_match):
        req = {"command": "start", "username": username, "token": token, "type": type_match}
        self.client_sock.sendall(bytes(json.dumps(req), "utf-8"))
        data = self.client_sock.recv(1024)
        return json.loads(data)

    def request_turn(self, username, token, ceil):
        req = {"command": "turn", "username": username, "token": token, "ceil": ceil}
        self.client_sock.sendall(bytes(json.dumps(req), "utf-8"))
        data = self.client_sock.recv(1024)
        return json.loads(data)
