"""
Game Tic-Tac-Toe
"""
import asyncio
from server import GameForWith
if __name__ == "__main__":
    # server_address = ('localhost', 8686)
    # connect_database = DataBase()
    with GameForWith("0", 8080) as game_serv:
        asyncio.run(game_serv.run_server())
    #     print(game_serv.user_db.signup_user("Tim", b"vy767676", "robert_polson@gmail.com"))
    #     print(game_serv.user_db.login_user("Tim", b"vy767676"))
    # game_serv.wait_user()
    pass
