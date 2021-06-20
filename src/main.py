"""
Game Tic-Tac-Toe
"""
import socket
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


class Game:
    def __init__(self):
        self.__field = list(range(1, 10))

    def check_end_game(self):
        for combo in WIN_COMBO:
            if self.__field[combo[0] - 1] == self.__field[combo[1] - 1] == self.__field[combo[2] - 1]:
                return f"win {self.__field[combo[0] - 1]}"
            else:
                print(self.__field)

    def check_turn(self, index, who):
        if self.__field[index - 1] == index and who in "xo" and any(map(lambda x: str(x).isdigit(), self.__field)):
            self.__field[index - 1] = who
            self.check_end_game()
        else:
            raise Exception("invalid turn")


if __name__ == "__main__":
    game = Game()
    game.check_turn(1, "x")
    game.check_turn(2, "o")
    game.check_turn(3, "x")
    game.check_turn(5, "o")
    game.check_turn(8, "o")
    print(game.check_end_game())
