import pyxel
from pyxel import *

from utils.GameState import GameState
from network.ClientInfo import PlayerInfo

class Lobby:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def update(self):
        while not self.game_state.client_to_game_queue.empty():
            data = self.game_state.client_to_game_queue.get()
            # print (f"Received data in lobby: {data}")
            
            if data.startswith("UPDATE_PING:"):
                _, info = data.split(":")
                client_id, ping = info.split(";")

                client_id = int(client_id)
                ping = int(ping)

                if client_id in self.game_state.players.keys():
                    self.game_state.players[client_id].ping = ping

            elif data.startswith("ADD_PLAYER:"):
                _, client_id = data.split(":")
                client_id = int(client_id)
                self.game_state.players[client_id] = PlayerInfo(client_id)
            
            elif data.startswith("REMOVE_PLAYER:"):
                _, client_id = data.split(":")
                client_id = int(client_id)

                if client_id in self.game_state.players.keys():
                    del self.game_state.players[client_id]

            elif data.startswith("DISCONNECTED"):
                self.game_state.reset()
                self.game_state.set_game_state("main_menu")

            elif data.startswith("START_GAME"):
                self.game_state.set_game_state("game")
                return

        if btnp(KEY_Q):
            self.game_state.set_game_state("main_menu")

            if self.game_state.is_host:
                self.game_state.game_to_server_queue.put("STOP_SERVER")

            else:
                self.game_state.game_to_client_queue.put("DISCONNECT")

        if self.game_state.is_host and btnp(KEY_RETURN):
            self.game_state.game_to_server_queue.put("START_GAME")

    def draw(self):
        pyxel.cls(0)
        pyxel.text(10, 10, "Lobby", 7)

        # Mostra o endereço do servidor
        pyxel.text(10, 25, f"Server Address: {self.game_state.host}:{self.game_state.tcp_port}", 7)

        pyxel.text(10, 45, "Players:", 7)

        player_list = []

        for id, player in self.game_state.players.items():
            player_list.append((id, player.nickname, player.ping))

        # Ordena por ID para manter consistência
        player_list = sorted(player_list, key=lambda x: x[0])

        for i, (id, nickname, ping) in enumerate(player_list):
            label = f"{id}: {nickname} ({ping}ms)"

            if id == self.game_state.player_id:
                label = label + " [You]"

            pyxel.text(15, 60 + i * 10, label, 11)

        pyxel.text(10, pyxel.height - 20, "Q: Quit", 8)
        if self.game_state.is_host:
            pyxel.text(80, pyxel.height - 20, "ENTER: Start Game", 9)
