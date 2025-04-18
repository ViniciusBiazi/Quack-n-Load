import pyxel
from pyxel import *

from models.core.Entity import Entity
from models.core.ColliderObject import ColliderObject

class RemotePlayer(Entity):
    def __init__(self, x, y, width=13, height=16, player_id=1):
        super().__init__(x, y, width, height)
        self.id = player_id
        self.health = 100
        self.sprite = ()

        self.player_skin = player_id
        self.direction = True

        self.entity_collider = ColliderObject(x, y, width, height)

        self.weapon: RemoteWeapon = None

    def update_remote_player(self, x, y, sprite, weapon=None):
        self.set_position(x, y)
        self.entity_collider.update_collider(x, y)

        self.sprite = sprite

        if weapon:
            self.weapon = RemoteWeapon()
            self.weapon.x = weapon[0]
            self.weapon.y = weapon[1]
            self.weapon.sprite = weapon[2]
            self.weapon.rotation = weapon[3]
        else:
            self.weapon = None

    def draw(self):
        if self.sprite:
            blt(self.x, self.y, 0, *self.sprite)
        if self.weapon:
            blt(self.weapon.x, self.weapon.y, 0, *self.weapon.sprite, self.weapon.rotation)

class RemoteWeapon():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.sprite = ()
        self.rotation = 0