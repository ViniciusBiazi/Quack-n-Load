import pyxel
from pyxel import *

from models.core.Entity import Entity

class Crosshair(Entity):
    def __init__(self, x=0, y=0, width=15, height=15, crosshair_type=0):
        """ Inicializa a mira com a posição e o sprite padrão. """
        super().__init__(x, y, width, height)
        
        self.crosshair_sprites = {
            0: (96, 0),  # Tipo 0: Mira padrão
            1: (96, 16), # Tipo 1: Mira shotgun
        }

        self.crosshair_sprite = self.crosshair_sprites[crosshair_type]

    def update_crosshair(self):
        # Atualiza a posição da mira com base na posição do mouse
        self.set_center_position(pyxel.mouse_x, pyxel.mouse_y)

    def draw(self):
        # Desenha a mira na tela
        blt(self.x, self.y, 0, *self.crosshair_sprite, self.width, self.height, 6)