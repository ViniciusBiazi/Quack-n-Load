import pyxel
from pyxel import *

from utils.GameState import GameState

from multiprocessing import Process, Queue
from network.Client import start_client_process
from network.ClientInfo import PlayerInfo

class JoinMenu:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.title = "Join Game"
        self.fields = ["IP:", "Port:"]
        self.inputs = ["0.0.0.0", "6969"]
        self.selected_field = 0
        self.typing = True
        self.char_limit = 21

        self.status_message = ""

    def update(self):
        if btnp(KEY_ESCAPE):
            self.game_state.set_game_state("main_menu")
            return

        if self.typing:
            if btnp(KEY_BACKSPACE):
                if self.inputs[self.selected_field]:
                    self.inputs[self.selected_field] = self.inputs[self.selected_field][:-1]

            elif btnp(KEY_RETURN):
                if self.selected_field < len(self.fields):
                    self.selected_field += 1

                if self.selected_field == len(self.fields):
                    self.game_state.client_to_game_queue = Queue()
                    self.game_state.game_to_client_queue = Queue()
                    self.game_state.client_process = Process(target=start_client_process, args=(self.inputs[0], int(self.inputs[1]), self.game_state.client_to_game_queue, self.game_state.game_to_client_queue))
                    self.game_state.client_process.start()

                    data = self.game_state.client_to_game_queue.get()
                        
                    if data == "CONNECTED":
                        self.game_state.host = self.inputs[0]
                        self.game_state.tcp_port = int(self.inputs[1])

                        data = self.game_state.client_to_game_queue.get()

                        if data.startswith("PLAYER_ID:"):
                            _, client_id = data.split(":")
                            client_id = int(client_id)

                            self.game_state.player_id = client_id
                            self.game_state.players[client_id] = PlayerInfo(client_id)

                            self.game_state.set_game_state("lobby")

                        elif data == "SERVER_FULL":
                            self.status_message = "Server is full. Try again later."
                            self.game_state.reset()
                    
                    elif data.startswith("CONNECTION_ERROR:"):
                        _, error_message = data.split(":")
                        self.status_message = f"Client connection error: {error_message}"
                        self.game_state.reset()

            else:
                for i in range(32, 127):
                    if btnp(i):
                        char = chr(i)
                        if len(self.inputs[self.selected_field]) < self.char_limit:
                            self.inputs[self.selected_field] += char

        if btnp(KEY_UP):
            self.selected_field = (self.selected_field - 1) % (len(self.fields) + 1)
        elif btnp(KEY_DOWN):
            self.selected_field = (self.selected_field + 1) % (len(self.fields) + 1)

    def draw(self):
        cls(0)
        text(40, 20, self.title, 7)

        for i, field in enumerate(self.fields):
            y = 50 + i * 15
            color = 10 if i == self.selected_field else 7
            text(40, y, field, color)
            rect(80, y - 2, 100, 10, 1)
            text(82, y, self.inputs[i], 7)

        # Botão [ Connect ]
        y_connect = 50 + len(self.fields) * 15
        connect_color = 10 if self.selected_field == len(self.fields) else 7
        text(40, y_connect, "[ Connect ]", connect_color)

        # Mensagem de status
        if self.status_message:
            text(40, y_connect + 20, self.status_message, 8)
