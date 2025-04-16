import pyxel
from pyxel import *
from multiprocessing import Process, Queue
from queue import Empty

from utils.GameState import GameState
from network.ClientInfo import PlayerInfo
from network.Server import start_server_process
from network.Client import start_client_process

class HostMenu:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.selected_option = 0
        self.options = ["Start Host", "Back"]
        self.title = "Host Game"
        self.status_message = None

    def update(self):
        if btnp(KEY_UP):
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif btnp(KEY_DOWN):
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif btnp(KEY_RETURN):
            match self.selected_option:
                case 0:
                    self.game_state.server_to_game_queue = Queue()
                    self.game_state.game_to_server_queue = Queue()
                    self.game_state.server_process = Process(target=start_server_process, args=(self.game_state.server_to_game_queue, self.game_state.game_to_server_queue))
                    self.game_state.server_process.start()
                    
                    # espera a resposta do servidor
                    data = self.game_state.server_to_game_queue.get()

                    if data.startswith("SERVER_STARTED:"):
                        _, info = data.split(":")
                        host, tcp_port = info.split(";")

                        tcp_port = int(tcp_port)

                        self.game_state.host = host
                        self.game_state.tcp_port = tcp_port

                        self.game_state.client_to_game_queue = Queue()
                        self.game_state.game_to_client_queue = Queue()
                        self.game_state.client_process = Process(target=start_client_process, args=(host, tcp_port, self.game_state.client_to_game_queue, self.game_state.game_to_client_queue))
                        self.game_state.client_process.start()

                        data = self.game_state.client_to_game_queue.get()
                        
                        if data == "CONNECTED":
                            data = self.game_state.client_to_game_queue.get()

                            if data.startswith("PLAYER_ID:"):
                                _, client_id = data.split(":")
                                client_id = int(client_id)

                                self.game_state.player_id = client_id
                                self.game_state.players[client_id] = PlayerInfo(client_id)

                                self.game_state.is_host = True
                                self.game_state.set_game_state("lobby")
                        
                        elif data.startswith("CONNECTION_ERROR:"):
                            _, error_message = data.split(":")
                            self.status_message = f"Client connection error: {error_message}"
                            self.game_state.reset()
                    
                    elif data.startswith("SERVER_START_ERROR:"):
                        _, error_message = data.split(":")
                        self.status_message = f"Server start error: {error_message}"
                        self.game_state.reset()

                case 1:
                    self.status_message = None
                    self.game_state.reset()
                    self.game_state.set_game_state("main_menu")

    def draw(self):
        pyxel.text(50, 40, self.title, 7)

        for i, option in enumerate(self.options):
            color = 10 if i == self.selected_option else 7
            pyxel.text(50, 70 + i * 10, option, color)

        if self.status_message:
            pyxel.text(50, 100, self.status_message, 8)