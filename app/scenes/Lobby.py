import pyxel
from pyxel import *

from utils.GameState import GameState

from network.Server import Server
from network.Client import Client

class Lobby:
    def __init__(self, game_state: GameState, client: Client, server: Server = None):
        self.game_state = game_state
        self.client = client
        self.server = server

    def update(self):
        if btnp(KEY_Q):
            if self.game_state.is_host:
                self.server.stop_server()

            self.game_state.set_game_state("main_menu")

        if self.game_state.is_host and btnp(KEY_RETURN):
            print("[Lobby] Starting game...")

    def draw(self):
        pyxel.cls(0)
        pyxel.text(10, 10, "Lobby", 7)

        # Mostra o endereço do servidor
        pyxel.text(10, 25, f"Server Address: {self.client.host}:{self.client.tcp_port}", 7)

        pyxel.text(10, 45, "Players:", 7)

        player_list = []

        for id, player in self.client.players.items():
            player_list.append((id, player.nickname, player.ping))

        # Ordena por ID para manter consistência
        player_list = sorted(player_list, key=lambda x: x[0])

        for i, (id, nickname, ping) in enumerate(player_list):
            label = f"{id}: {nickname} ({ping}ms)"

            if id == self.client.client_id:
                label = label + " [You]"

            pyxel.text(15, 60 + i * 10, label, 11)

        pyxel.text(10, pyxel.height - 20, "Q: Quit", 8)
        if self.game_state.is_host:
            pyxel.text(80, pyxel.height - 20, "ENTER: Start Game", 9)
