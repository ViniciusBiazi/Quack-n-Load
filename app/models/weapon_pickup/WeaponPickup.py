import pyxel
from pyxel import *

from models.core.PhysicsObject import PhysicsObject

class WeaponPickup(PhysicsObject):
    """ Classe para representar uma arma no chão. Se move com a gravidade e pode ser coletada pelo jogador. """
    WEAPON_DATA = {
        0: {"sprite": (64, 0), "width": 8, "height": 8}, # pistola
        1: {"sprite": (64, 8), "width": 16, "height": 8}, # shotgun
        2: {"sprite": (64, 32), "width": 32, "height": 8}, # rifle
        3: {"sprite": (72, 0), "width": 24, "height": 8}, # assault rifle
    }

    def __init__(self, id, x, y, weapon_type, ammo, reserve_ammo, remove_timer):
        """ Inicializa a arma no chão com base no tipo especificado. """
        super().__init__(x, y, self.WEAPON_DATA[weapon_type]["width"], self.WEAPON_DATA[weapon_type]["height"])
        self.set_center_position(x, y)
        self.id = id

        self.weapon_type = weapon_type
        self.weapon_sprite = self.WEAPON_DATA[weapon_type]["sprite"]

        self.ammo = ammo
        self.reserve_ammo = reserve_ammo

        self.pickable = False

        self.remove_timer = remove_timer

    def draw(self):
        """ Desenha o objeto na tela. """
        blt(self.x, self.y, 0, *self.weapon_sprite, self.width, self.height, 6)  # Desenha a arma na tela

        if self.pickable:
            text(self.x, self.y - 15, "Press E", 0)