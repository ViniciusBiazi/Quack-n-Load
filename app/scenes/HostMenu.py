import pyxel
from pyxel import *
from multiprocessing import Process, Queue
from queue import Empty

from utils.GameState import GameState
from network.NetworkInfo import ClientPlayerInfo
from network.Server import start_server_process
from network.Client import start_client_process

class HostMenu:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.title = "Host Game"
        self.field = "Nick:"
        self.input = ""

        self.char_limit_nickname = 15 # 15 chars

        self.status_message = ""

    def update(self):
        if btnp(KEY_BACKSPACE, 60, 10):
            self.input = self.input[:-1]

        elif btnp(KEY_RETURN):
                try:
                    self.game_state.server_to_game_queue = Queue()
                    self.game_state.game_to_server_queue = Queue()
                    self.game_state.server_process = Process(target=start_server_process, args=(self.game_state.server_to_game_queue, self.game_state.game_to_server_queue))
                    self.game_state.server_process.start()
                
                    # espera a resposta do servidor
                    data = self.game_state.server_to_game_queue.get(timeout=5)

                    if data.startswith("SERVER_STARTED:"):
                        _, info = data.split(":")
                        host, tcp_port = info.split(";")

                        tcp_port = int(tcp_port)

                        self.game_state.host = host
                        self.game_state.tcp_port = tcp_port

                        self.game_state.client_to_game_queue = Queue()
                        self.game_state.game_to_client_queue = Queue()
                        self.game_state.client_process = Process(target=start_client_process, args=(host, tcp_port, self.game_state.client_to_game_queue, self.game_state.game_to_client_queue, self.input))
                        self.game_state.client_process.start()

                        data = self.game_state.client_to_game_queue.get(timeout=5)
                        
                        if data == "CONNECTED":
                            data = self.game_state.client_to_game_queue.get(timeout=5)

                            if data.startswith("PLAYER_ID:"):
                                _, info = data.split(":")
                                client_id, nickname = info.split(";")

                                client_id = int(client_id)

                                self.game_state.player_id = client_id
                                self.game_state.players[client_id] = ClientPlayerInfo(client_id, nickname)

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

                except Empty:
                    self.status_message = "Server Error: Timeout"
                    self.game_state.reset()

                except Exception as e:
                    self.status_message = f"Connection error: {type(e).__name__}"
                    self.game_state.reset()

        if btnp(KEY_ESCAPE):
            self.reset_host_menu()
            self.game_state.reset()
            self.game_state.set_game_state("main_menu")

        else:
            for i in range(97, 123):
                if btnp(i, 60, 10):
                    char = chr(i)

                    if btn(KEY_SHIFT):
                        char = char.upper()

                    if len(self.input) < self.char_limit_nickname:
                        self.input += char

    def reset_host_menu(self):
        self.input = ""
        self.status_message = ""

    def draw(self):
        cls(0)
        text(20, 20, self.title, 7)

        text(20, 50, self.field, 10) # tag do campo
        rect(50, 50 - 2, 63, 9, 1) # borda do campo
        text(52, 50, self.input, 7) # texto do campo

        text(20, pyxel.height - 20, "ENTER: Host Game", 9)
        text(110, pyxel.height - 20, "ESQ: Back", 8)

        # Mensagem de status
        if self.status_message:
            text(20, 50 + 20, self.status_message, 8)