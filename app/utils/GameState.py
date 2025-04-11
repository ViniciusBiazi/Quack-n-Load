class GameState:
    def __init__(self):
        self.states = ["main_menu", "join_menu", "host_menu", "lobby", "game"]
        self.current_state = "main_menu"
        self.is_host = False

    def set_game_state(self, state):
        if state not in self.states:
            raise ValueError(f"Invalid game state: {state}")
        
        self.current_state = state
        print(f"[GameState] Current state: {self.current_state}")
