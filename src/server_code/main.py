"""
Game Tic-Tac-Toe
"""
import asyncio
import sys
from server import GameForWith, show_ip
if __name__ == "__main__":
    show_ip()
    with GameForWith("0", sys.argv[1]) as game_serv:
        asyncio.run(game_serv.run_server())
