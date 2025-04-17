from pyxel import *
import time

from utils.GameState import GameState

from scenes.MainMenu import MainMenu
from scenes.JoinMenu import JoinMenu
from scenes.HostMenu import HostMenu
from scenes.Lobby import Lobby
from scenes.Game import Game

class App:
    def __init__(self):
        init(384, 256, title="Quack'n'Load", fps=120)

        self.game_state = GameState()

        # Instâncias fixas
        self.main_menu = MainMenu(self.game_state)
        self.host_menu = HostMenu(self.game_state)
        self.join_menu = JoinMenu(self.game_state)
        self.lobby = Lobby(self.game_state)
        self.game = Game(self.game_state)

        self.last_time = time.monotonic()
        self.current_time = time.monotonic()

        run(self.update, self.draw)

    def update(self):
        self.current_time = time.monotonic()
        delta_time = self.current_time - self.last_time
        self.last_time = self.current_time

        if self.game_state.current_state == "main_menu":
            self.main_menu.update()
        elif self.game_state.current_state == "join_menu":
            self.join_menu.update()
        elif self.game_state.current_state == "host_menu":
            self.host_menu.update()
        elif self.game_state.current_state == "lobby":
            self.lobby.update()
        elif self.game_state.current_state == "game":
            self.game.update(delta_time=delta_time)

    def draw(self):
        cls(0)

        if self.game_state.current_state == "main_menu":
            self.main_menu.draw()
        elif self.game_state.current_state == "join_menu":
            self.join_menu.draw()
        elif self.game_state.current_state == "host_menu":
            self.host_menu.draw()
        elif self.game_state.current_state == "lobby":
            self.lobby.draw()
        elif self.game_state.current_state == "game":
            self.game.draw()

if __name__ == "__main__":
    App()
