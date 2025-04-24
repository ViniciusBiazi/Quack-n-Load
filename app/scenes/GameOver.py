import pyxel
from pyxel import *

from utils.GameState import GameState

class GameOver:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.return_to_lobby_timer = 2

    def update(self, delta_time):
        if self.return_to_lobby_timer > 0:
            self.return_to_lobby_timer -= delta_time
        else:
            self.game_state.set_game_state("lobby")
            self.game_state.winner = None
            return


    def draw(self):
        pyxel.text(50, 40, "Game Over", 7)
        pyxel.text(50, 60, f"Winner: {self.game_state.players[self.game_state.winner].nickname}", 7)