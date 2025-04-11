import pyxel
from pyxel import *
from time import time

from utils.GameState import GameState

from scenes.MainMenu import MainMenu

from scenes.JoinMenu import JoinMenu
from scenes.HostMenu import HostMenu

from scenes.Lobby import Lobby

from network.Server import Server
from network.Client import Client

from scenes.Game import Game

class App:
    def __init__(self):
        init(384, 256, title="Quack'n'Load", fps=999)

        self.game_state = GameState()

        # Inicializa o servidor e o cliente
        self.server = Server()
        self.client = Client(self.game_state)

        # Instâncias fixas
        self.main_menu = MainMenu(self.game_state)

        self.host_menu = HostMenu(self.game_state, self.server, self.client)
        self.join_menu = JoinMenu(self.game_state, self.client)

        # Instância fixa do jogo
        self.game = Game()

        # Instância dinâmica do Lobby
        self.lobby = Lobby(self.game_state, self.client, self.server)

        self.last_time = time()
        self.current_time = time()

        self.fps_timer = 0
        self.frame_count = 0
        self.fps = 0

        run(self.update, self.draw)

    def update(self):
        self.current_time = time()
        delta_time = self.current_time - self.last_time
        self.last_time = self.current_time

        # Atualiza o FPS
        self.fps_timer += delta_time
        self.frame_count += 1

        if self.fps_timer >= 1:
            self.fps = self.frame_count
            self.fps_timer = 0
            self.frame_count = 0


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
