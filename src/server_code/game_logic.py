import secrets

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
    def __init__(self, player_one, player_two):
        self.__field = list(range(1, 10))
        self.switch_turn = {player_one: player_two, player_two: player_one}
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
                return{"endgame": True, "message": f"win {self.__field[combo[0] - 1]}"}
        if not any(list(map(lambda x: str(x).isdigit(), self.__field))):
            return {"endgame": True, "message": "draw"}
        else:
            return {"endgame": False, "message": "wait for opponent"}

    def check_turn(self, index, who):
        if self.__field[index - 1] != index:
            raise WrongMove("The cell is already occupied")
        elif who not in self.switch_turn.keys():
            raise WrongMove("Wrong player")
        elif who != self.__turn:
            raise WrongMove("Not your turn")
        self.__field[index - 1] = who
        res = self.check_end_game()
        self.__turn = self.switch_turn[self.__turn]
        return res

    def choose_random_player(self):
        print(self.switch_turn.keys())
        self.__turn = secrets.choice(list(self.switch_turn.keys()))

    def show_field(self):
        print("************")
        print("|" + "|".join(map(str, self.__field[:3])) + "|")
        print("|" + "|".join(map(str, self.__field[3:6])) + "|")
        print("|" + "|".join(map(str, self.__field[6:])) + "|")
        print("************")
