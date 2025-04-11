import pyxel
from pyxel import *

from utils.GameState import GameState

class MainMenu:
    def __init__(self, game_state: GameState):
        self.selected_option = 0
        self.options = ["Host", "Join", "Options", "Exit"]
        self.title = "Quack'n'Load"
        self.game_state = game_state

    def update(self):
        if btnp(KEY_UP):
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif btnp(KEY_DOWN):
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif btnp(KEY_RETURN):
            match self.selected_option:
                case 0:
                    print("Host selected")
                    self.game_state.set_game_state("host_menu")
                case 1:
                    print("Join selected")
                    self.game_state.set_game_state("join_menu")
                case 2:
                    print("Options selected")
                    # Menu de opções (a implementar)
                case 3:
                    quit()

    def draw(self):
        pyxel.text(50, 50, self.title, 7)

        for i, option in enumerate(self.options):
            color = 10 if i == self.selected_option else 7
            pyxel.text(50, 70 + i * 10, option, color)
