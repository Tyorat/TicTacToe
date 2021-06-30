import os
import hashlib
import secrets
import string
import sqlite3

PASSWORD = 2
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


class Authorization:
    def __init__(self):
        self.db = UserStorage()

    def login_user(self, username, password):
        user = self.db.get_user(username)
        if user and user[PASSWORD] == hashlib.sha256(
                password.encode("utf-8")).hexdigest():
            return {"authorization": True, "taken": "".join(
                [secrets.choice(string.ascii_letters + string.digits) for _ in range(16)])}
        else:
            return {"authorization": False}

    def signup_user(self, username, password, email):
        user = self.db.get_user(username)
        if user:
            return {"registration": False}
        else:
            self.db.put_user(username, hashlib.sha256(
                password.encode("utf-8")).hexdigest(), email)
            return {"registration": True}


class UserStorage:
    def __init__(self):
        self.connection = sqlite3.connect(os.path.join(SCRIPT_PATH, "..", "..", "data", "users.db"))
        cur = self.connection.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username CHAR(255) NOT NULL, "
                    "password CHAR(64) NOT NULL, email CHAR(255) );")
        self.connection.commit()

    def get_user(self, username):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=(?);", (username,))
        return cur.fetchone()

    def put_user(self, username, password, email):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?);", (username, password, email))
        self.connection.commit()
