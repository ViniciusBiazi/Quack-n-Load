import pyxel
from pyxel import *

from utils.GameState import GameState

from network.Server import Server
from network.Client import Client

class HostMenu:
    def __init__(self, game_state: GameState, server: Server, client: Client):
        self.game_state = game_state
        self.server = server
        self.client = client

        self.selected_option = 0
        self.options = ["Start Host", "Back"]
        self.title = "Host Game"

    def update(self):
        if btnp(KEY_UP):
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif btnp(KEY_DOWN):
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif btnp(KEY_RETURN):
            match self.selected_option:
                case 0:
                    self.server.start_server()
                    self.client.connect(self.server.host, self.server.tcp_port)
                    
                    self.game_state.is_host = True
                    self.game_state.set_game_state("lobby")
                case 1:
                    self.game_state.set_game_state("main_menu")

    def draw(self):
        pyxel.text(50, 40, self.title, 7)

        for i, option in enumerate(self.options):
            color = 10 if i == self.selected_option else 7
            pyxel.text(50, 70 + i * 10, option, color)
