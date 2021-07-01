import asyncio
from game_logic import Game, WrongMove
import json
from database_connector import Authorization


class GameForWith:
    def __init__(self, host, port):
        self.__server = GameServer(host, port)

    def __enter__(self):
        return self.__server

    def __exit__(self, some_type, value, traceback):
        print("close server")
        self.__server.server.close()
        self.__server.user_db.db.connection.close()


class GameServer:
    def __init__(self, host, port):
        self.server = None
        self.host = host
        self.port = port
        self.user_db = Authorization()
        self.users = {}
        self.users_wait_match = []

    async def run_server(self):
        self.server = await asyncio.start_server(self.serv_client, self.host, self.port)
        await self.server.serve_forever()
        print('server is running, please, press ctrl+c to stop')

    async def serv_client(self, reader, writer):
        request = await self.read_request(reader)
        if request is None:
            print('Client unexpectedly disconnected')
        else:
            try:
                response = await self.handle_request(request, writer)
            except WrongMove:
                response = [{"writer": writer, "message": {"result": False, "message": "Wrong move"}}]
            await self.write_response(response)

    @staticmethod
    async def read_request(reader, delimiter=b'}'):
        request = bytearray()
        while True:
            chunk = await reader.read(4)
            if not chunk:
                break
            request += chunk
            if delimiter in request:
                try:
                    return json.loads(str(request, "utf-8"))
                except:
                    print(request)

        return None

    async def handle_request(self, request, writer):
        """
        command:
        register (username, password, email)
        login (username, password)
        start (username, type, level, taken)
        turn (username, ceil, taken)
        surr (username, taken)
        :param writer:
        :param request:
        :return:
        """
        command = request["command"]
        response = [{"writer": writer, "message": None}]
        if command == "register":
            response[0]["message"] = self.user_db.signup_user(request["username"], request["password"],
                                                              request["email"])
        elif command == "login":
            db_mes = self.user_db.login_user(request["username"], request["password"])
            if db_mes["authorization"]:
                self.users[request["username"]] = {"taken": db_mes["taken"], "game": None}
            response[0]["message"] = db_mes
        elif command == "start":
            response = self.handle_find_game(request, writer)
        elif command == "turn":
            response = self.handle_turn_command(request, writer)
        return response

    def handle_find_game(self, request, writer):
        username = request["username"]
        response = []
        if username in self.users and self.users[username]["taken"] == request["taken"]:
            self.users[username]["game"] = "wait"
            self.users_wait_match.append(username)
            self.users[username]["writer"] = writer
            print("user wait for opponent")
        if len(self.users_wait_match) >= 2:
            writer = self.start_match()
            response = [{"writer": writer, "message": {"result": True, "turn_opponent": None}}]
        return response

    def start_match(self):
        player_one = self.users_wait_match.pop()
        player_two = self.users_wait_match.pop()
        game = Game(player_one, player_two)
        self.users[player_one]["game"] = game
        self.users[player_two]["game"] = game
        game.choose_random_player()
        return self.users[game.turn]["writer"]

    def handle_turn_command(self, request, writer):
        ceil = request["ceil"]
        username = request["username"]
        game = self.users[username]["game"]
        self.users[username]["writer"] = writer
        game_mes = game.check_turn(ceil, username)
        game_mes.update({"result": True, "turn_opponent": ceil})
        response = [{"writer": self.users[game.turn]["writer"], "message": game_mes}]
        if game_mes["endgame"]:
            game_mes["turn_opponent"] = None
            response.append({"writer": writer, "message": game_mes})
        return response

    @staticmethod
    async def write_response(response):
        for client in response:
            client["writer"].write(json.dumps(client["message"]).encode("utf-8"))
            await client["writer"].drain()
            client["writer"].close()
