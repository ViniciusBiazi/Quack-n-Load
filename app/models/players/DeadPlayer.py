import pyxel
from pyxel import *

from models.core.PhysicsObject import PhysicsObject

class DeadPlayer(PhysicsObject):
    def __init__(self, x, y, width=16, height=8, player_id=0, direction=True):
        super().__init__(x, y, width, height)
        self.player_id = player_id
        self.player_skin = player_id

        self.sprite_right = (-width, height, 6)
        self.sprite_left = (width, height, 6)
        self.sprite_flip = self.sprite_right if direction else self.sprite_left

        self.sprite = (self.player_skin * 16, 136)

        self.direction = direction  # True para direita, False para esquerda
        self.remove_timer = 5

    def update_dead_player(self, delta_time):
        if self.remove_timer > 0:
            self.remove_timer -= delta_time

    def draw(self):
        blt(self.x, self.y, 0, *self.sprite, *self.sprite_flip)