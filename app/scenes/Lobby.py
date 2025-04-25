import pyxel
from pyxel import *

from utils.GameState import GameState
from network.NetworkInfo import ClientPlayerInfo

class Lobby:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def update(self):
        while not self.game_state.client_to_game_queue.empty():
            data = self.game_state.client_to_game_queue.get()
            
            if data.startswith("UPDATE_LOBBY_DATA:"):
                _, info = data.split(":")
                parts = info.split(",")

                for part in parts:
                    client_id, nickname, kills, deaths, wins, ping = part.split(";")
                    client_id = int(client_id)
                    kills = int(kills)
                    deaths = int(deaths)
                    wins = int(wins)
                    ping = int(ping)

                    if client_id in self.game_state.players.keys():
                        self.game_state.players[client_id].nickname = nickname
                        self.game_state.players[client_id].kills = kills
                        self.game_state.players[client_id].deaths = deaths
                        self.game_state.players[client_id].wins = wins
                        self.game_state.players[client_id].ping = ping

            elif data.startswith("ADD_PLAYER:"):
                _, info = data.split(":")
                client_id, nickname = info.split(";")

                client_id = int(client_id)

                self.game_state.players[client_id] = ClientPlayerInfo(client_id, nickname)
            
            elif data.startswith("REMOVE_PLAYER:"):
                _, client_id = data.split(":")
                client_id = int(client_id)

                if client_id in self.game_state.players.keys():
                    del self.game_state.players[client_id]

            elif data.startswith("DISCONNECTED"):
                self.game_state.reset()
                self.game_state.set_game_state("main_menu")
                return

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

        pyxel.text(10, 45, "| ID | Nickname        | Kills | Deaths | Wins | Ping |", 7)

        player_list = []

        for id, player in self.game_state.players.items():
            player_list.append((id, player.nickname, player.kills, player.deaths, player.wins, player.ping))

        # Ordena por ID para manter consistência
        player_list = sorted(player_list, key=lambda x: x[0])

        for i, (id, nickname, kills, deaths, wins, ping) in enumerate(player_list):
            label = f"| {id:2} | {nickname:15} | {kills:5} | {deaths:6} | {wins:4} | {ping:4} |"

            if id == self.game_state.player_id:
                label = label + " [You]"

            pyxel.text(10, 60 + i * 10, label, 11)

        pyxel.text(10, pyxel.height - 20, "ESQ: Quit", 8)
        if self.game_state.is_host:
            pyxel.text(80, pyxel.height - 20, "ENTER: Start Game", 9)