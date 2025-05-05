import pyxel
from pyxel import *

from utils.GameState import GameState
from network.NetworkInfo import ClientPlayerInfo

class Lobby:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.title = "Lobby"

    def update(self):
        while not self.game_state.client_to_game_queue.empty():
            data = self.game_state.client_to_game_queue.get()

            if data.startswith("ADD_PLAYER:"):
                _, info = data.split(":")
                client_id, nickname, kills, deaths, wins = info.split(";")

                client_id = int(client_id)

                self.game_state.players[client_id] = ClientPlayerInfo(client_id, nickname)
                self.game_state.players[client_id].kills = int(kills)
                self.game_state.players[client_id].deaths = int(deaths)
                self.game_state.players[client_id].wins = int(wins)
            
            elif data.startswith("REMOVE_PLAYER:"):
                _, client_id = data.split(":")
                client_id = int(client_id)

                self.game_state.players.pop(client_id, None)

            elif data.startswith("DISCONNECTED"):
                self.game_state.reset()
                self.game_state.set_game_state("main_menu")
                return

            elif data.startswith("START_GAME"):
                self.game_state.set_game_state("game")
                return

            elif data.startswith("UPDATE_PING:"):
                _, info = data.split(":")
                client_id, ping = info.split(";")

                client_id = int(client_id)
                ping = int(ping)

                if client_id in self.game_state.players.keys():
                    self.game_state.players[client_id].ping = ping


        if btnp(KEY_ESCAPE):
            if self.game_state.is_host:
                self.game_state.game_to_server_queue.put("STOP_SERVER")

            else:
                self.game_state.game_to_client_queue.put("DISCONNECT")
            
            self.game_state.reset()
            self.game_state.set_game_state("main_menu")

        if self.game_state.is_host and btnp(KEY_RETURN):
            self.game_state.game_to_server_queue.put("START_GAME")

    def draw(self):
        cls(0)
        text(20, 20, self.title, 7)

        text(20, 45, f"Server Address: {self.game_state.host}:{self.game_state.tcp_port}", 10)
        text(20, 65, "| ID | Nickname        | Kills | Deaths | Wins | Ping |", 7)

        player_list = sorted(self.game_state.players.values(), key=lambda x: x.wins, reverse=True) # ordena por wins

        for i, player in enumerate(player_list):
            label = f"| {player.id:2} | {player.nickname:15} | {player.kills:5} | {player.deaths:6} | {player.wins:4} | {player.ping:4} |"

            if id == self.game_state.player_id:
                label = label + " [You]"

            text(20, 75 + i * 10, label, 11)

        if self.game_state.is_host:
            text(80, pyxel.height - 20, "ENTER: Start Game", 9)
        
        text(20, pyxel.height - 20, "ESQ: Quit", 8)

