"""
Game Tic-Tac-Toe
"""
import random
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

SWITCH_TURN = {"x": "o", "o": "x"}


class WrongMove(Exception): pass


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

    def check_turn(self, index, who):
        if self.__field[index - 1] != index:
            raise WrongMove("The cell is already occupied")
        elif who not in "xo":
            raise WrongMove("Wrong symbol")
        elif who != self.__turn:
            raise WrongMove("Not your turn")
        self.__field[index - 1] = who
        self.check_end_game()
        self.__turn = SWITCH_TURN[self.__turn]

    def choose_random_player(self):
        self.__turn = random.choice("xo")

    def show_field(self):
        print("************")
        print("|" + "|".join(map(str, self.__field[:3])) + "|")
        print("|" + "|".join(map(str, self.__field[3:6])) + "|")
        print("|" + "|".join(map(str, self.__field[6:])) + "|")
        print("************")


if __name__ == "__main__":
    game = Game()
    # for num in range(1, 10):
    #     game.check_turn(num, "x")
    while True:
        game.check_turn(int(input()), input())
    # print(game.check_end_game())
