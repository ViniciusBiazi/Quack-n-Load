import pyxel
from pyxel import *
from queue import Empty

from utils.GameState import GameState

from multiprocessing import Process, Queue
from network.Client import start_client_process
from network.NetworkInfo import ClientPlayerInfo

class JoinMenu:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.title = "Join Game"
        self.fields = ["Nick:", "IP:", "Port:"]
        self.inputs = ["", "0.0.0.0", "6969"]

        self.char_limit_ip = 15 # 255.255.255.255
        self.char_limit_port = 5 # 65535
        self.char_limit_nickname = 15 # 15 chars

        self.selected_field = 0

        self.status_message = ""

    def update(self):
        if btnp(KEY_UP, 60, 20):
            self.selected_field = (self.selected_field - 1) % (len(self.fields))

        elif btnp(KEY_DOWN, 60, 20):
            self.selected_field = (self.selected_field + 1) % (len(self.fields))
        
        elif btnp(KEY_ESCAPE):
            self.reset_join_menu()
            self.game_state.reset()
            self.game_state.set_game_state("main_menu")

        elif btnp(KEY_BACKSPACE, 60, 10):
            self.inputs[self.selected_field] = self.inputs[self.selected_field][:-1]

        elif btnp(KEY_RETURN):
            try:
                self.game_state.client_to_game_queue = Queue()
                self.game_state.game_to_client_queue = Queue()
                self.game_state.client_process = Process(target=start_client_process, args=(self.inputs[1], int(self.inputs[2]), self.game_state.client_to_game_queue, self.game_state.game_to_client_queue, self.inputs[0]))
                self.game_state.client_process.start()

                data = self.game_state.client_to_game_queue.get(timeout=5)
                    
                if data == "CONNECTED":
                    self.game_state.host = self.inputs[1]
                    self.game_state.tcp_port = int(self.inputs[2])

                    data = self.game_state.client_to_game_queue.get(timeout=5)

                    if data.startswith("PLAYER_ID:"):
                        _, info = data.split(":")
                        client_id, nickname = info.split(";")

                        client_id = int(client_id)

                        self.game_state.player_id = client_id
                        self.game_state.players[client_id] = ClientPlayerInfo(client_id, nickname)

                        self.game_state.set_game_state("lobby")

                    elif data == "SERVER_FULL":
                        self.status_message = "Server is full. Try again later."
                        self.game_state.reset()
                    
                    elif data == "SERVER_IN_GAME":
                        self.status_message = "Server is already in game. Try again later."
                        self.game_state.reset()
                
                elif data.startswith("CONNECTION_ERROR:"):
                    _, error_message = data.split(":")
                    self.status_message = f"Client connection error: {error_message}"
                    self.game_state.reset()

            except Empty:
                self.status_message = "Client Error: Timeout"
                self.game_state.reset()
            
            except Exception as e:
                self.status_message = f"Connection error: {type(e).__name__}"
                self.game_state.reset()

        else:
            if self.selected_field == 0:
                for i in range(97, 123):
                    if btnp(i, 60, 10):
                        char = chr(i)

                        if btn(KEY_SHIFT):
                            char = char.upper()

                        if len(self.inputs[self.selected_field]) < self.char_limit_nickname:
                            self.inputs[self.selected_field] += char

            elif self.selected_field == 1:
                for i in range(46, 58):
                    if btnp(i, 60, 10):
                        if len(self.inputs[self.selected_field]) < self.char_limit_ip:
                            self.inputs[self.selected_field] += chr(i)

            elif self.selected_field == 2:
                for i in range(48, 58):
                    if btnp(i, 60, 10):
                        if len(self.inputs[self.selected_field]) < self.char_limit_port:
                            self.inputs[self.selected_field] += chr(i)

    def reset_join_menu(self):
        self.inputs = ["", "0.0.0.0", "6969"]
        self.selected_field = 0
        self.status_message = ""

    def draw(self):
        cls(0)
        text(20, 20, self.title, 7)

        for i, field in enumerate(self.fields):
            y = 50 + i * 15
            color = 10 if i == self.selected_field else 7
            text(20, y, field, color)
            rect(50, y - 2, 63, 9, 1)
            text(52, y, self.inputs[i], 7)

        text(20, pyxel.height - 20, "ENTER: Join Game", 9)
        text(110, pyxel.height - 20, "ESQ: Back", 8)

        # Mensagem de status
        if self.status_message:
            text(20, y + 20, self.status_message, 8)
