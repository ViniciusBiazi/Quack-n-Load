from network.NetworkInfo import PlayerInfo
from multiprocessing import Process, Queue

class GameState:
    def __init__(self):
        self.states = ["main_menu", "join_menu", "host_menu", "lobby", "game"]
        self.current_state = "main_menu"

        self.player_id: int = None
        self.players: dict[int, PlayerInfo] = {}

        self.host = None
        self.tcp_port = None

        self.is_host = False

        self.server_process: Process = None
        self.server_to_game_queue: Queue = None
        self.game_to_server_queue: Queue = None

        self.client_process: Process = None
        self.client_to_game_queue: Queue = None
        self.game_to_client_queue: Queue = None

    def set_game_state(self, state):
        if state not in self.states:
            raise ValueError(f"Invalid game state: {state}")
        
        self.current_state = state
        print(f"[GameState] Current state: {self.current_state}")

    def reset(self):
        self.player_id = None
        self.players = {}

        self.host = None
        self.tcp_port = None

        self.is_host = False

        if self.server_process:
            self.server_process.terminate()
            self.server_process = None

        if self.client_process:
            self.client_process.terminate()
            self.client_process = None

        self.server_to_game_queue = None
        self.game_to_server_queue = None
        self.client_to_game_queue = None
        self.game_to_client_queue = None
