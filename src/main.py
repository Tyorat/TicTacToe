"""
Game Tic-Tac-Toe
"""
import asyncio
import hashlib
import json
import secrets
import socket
import string
import sqlite3
import sys

WIN_COMBO = ((1, 2, 3),
             (4, 5, 6),
             (7, 8, 9),
             (1, 4, 7),
             (2, 5, 8),
             (3, 6, 9),
             (1, 5, 9),
             (7, 5, 3)
             )

SWITCH_TURN = {"x": "o", "o": "x"}


class WrongMove(Exception): pass


# move to separate file, rename to Authentication, extract db operations into UserStore class
class DataBase:
    def __init__(self):
        self.connection = sqlite3.connect("../data/users.db")
        cur = self.connection.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username CHAR(255) NOT NULL, "
                    "password CHAR(64) NOT NULL, email CHAR(255) );")
        self.connection.commit()

    def login_user(self, username, password):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=(?);", (username,))
        if cur.fetchone()[2] == hashlib.sha256(
                password).hexdigest():
            # use secure crypto
            return {"authorization": True, "taken": "".join(
                [secrets.choice(string.ascii_letters + string.digits) for x in range(16)])}
        else:
            return {"authorization": False}

    def signup_user(self, username, password, email):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=(?);", (username,))
        if cur.fetchall():
            return {"registration": False}
        else:
            cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?);", (username, hashlib.sha256(
                password).hexdigest(), email))
            self.connection.commit()
            return {"registration": True}


class GameForWith:
    def __init__(self, address, max_connection):
        self.__server = GameServer(address, max_connection)

    def __enter__(self):
        return self.__server

    def __exit__(self, some_type, value, traceback):
        print("close server")
        self.__server.server_socket.close()
        self.__server.user_db.connection.close()


class GameServer:
    def __init__(self, address, max_connection):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_socket.setblocking(False)
        self.server_socket.bind(address)
        self.server_socket.listen(max_connection)
        self.user_db = DataBase()
        self.users = {}
        # self.game_list = []
        print('server is running, please, press ctrl+c to stop')

    async def wait_user(self):
        while True:
            connection, address = self.server_socket.accept()
            print("new connection from {address}".format(address=address))
            data = connection.recv(1024)
            if not data:
                break
            print(data)
            connection.send(bytes('Hello from server!', encoding='UTF-8'))

    async def accept_user(self):
        client_sock, client_addr = self.server_socket.accept()
        return client_sock

    async def serv_client(self):
        pass


# move to separate file
class Game:
    def __init__(self):
        self.__field = list(range(1, 10))
        self.__turn = None
        self.choose_random_player()

    turn = property()

    @turn.getter
    def turn(self):
        return self.__turn

    def check_end_game(self):
        self.show_field()
        for combo in WIN_COMBO:
            if self.__field[combo[0] - 1] == self.__field[combo[1] - 1] == self.__field[combo[2] - 1]:
                return f"win {self.__field[combo[0] - 1]}"
        if not any(list(map(lambda x: str(x).isdigit(), self.__field))):
            return "draw"
        else:
            return "wait opponent"

    def check_turn(self, index, who):
        if self.__field[index - 1] != index:
            raise WrongMove("The cell is already occupied")
        elif who not in "xo":
            raise WrongMove("Wrong symbol")
        elif who != self.__turn:
            raise WrongMove("Not your turn")
        self.__field[index - 1] = who
        res = self.check_end_game()
        self.__turn = SWITCH_TURN[self.__turn]
        return res

    def choose_random_player(self):
        self.__turn = secrets.choice("xo")

    def show_field(self):
        print("************")
        print("|" + "|".join(map(str, self.__field[:3])) + "|")
        print("|" + "|".join(map(str, self.__field[3:6])) + "|")
        print("|" + "|".join(map(str, self.__field[6:])) + "|")
        print("************")


if __name__ == "__main__":
    # server_address = ('localhost', 8686)
    # connect_database = DataBase()
    with GameForWith(("0", 8080), 10) as game_serv:
        print(game_serv.user_db.signup_user("Tim", b"vy767676", "robert_polson@gmail.com"))
        print(game_serv.user_db.login_user("Tim", b"vy767676"))
        # game_serv.wait_user()
