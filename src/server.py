import asyncio
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
        self.users_in_match = []
        # self.game_list = []

    async def run_server(self):
        self.server = await asyncio.start_server(self.serv_client, self.host, self.port)
        await self.server.serve_forever()
        print('server is running, please, press ctrl+c to stop')

    async def serv_client(self, reader, writer):
        request = await self.read_request(reader)
        if request is None:
            print('Client unexpectedly disconnected')
        else:
            response = await self.handle_request(request)
            await self.write_response(writer, response)

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

    async def handle_request(self, request):
        """
        command:
        register (username, password, email)
        login (username, password)
        start (username, type, level, taken)
        turn (username, symbol, ceil, taken)
        surr (username, taken)
        :param request:
        :return:
        """
        command = request["command"]
        response = None
        if command == "register":
            response = self.user_db.signup_user(request["username"], request["password"], request["email"])
        elif command == "login":
            response = self.user_db.login_user(request["username"], request["password"])
            if response["authorization"]:
                self.users[request["username"]] = {"taken": response["taken"], "game": None}
        elif command == "start":
            username = request["username"]
            if username in self.users and self.users[username]["taken"] == request["taken"]:
                self.users[username]["game"] = "wait"

        return response

    async def write_response(self, writer, response):
        writer.write(json.dumps(response).encode("utf-8"))
        await writer.drain()
        writer.close()
        print(f'Client has been served')
        # await writer.wait_closed()
