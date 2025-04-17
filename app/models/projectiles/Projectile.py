import pyxel
from pyxel import *

from models.core.Entity import Entity
from models.core.ColliderObject import ColliderObject

# Classe para projéteis
class Projectile(Entity):
    def __init__(self, id, x, y, angle, speed, damage, projectile_type=0):
        super().__init__(x, y, 3, 3)
        self.id = id

        self.set_center_position(x, y) # Define a posição inicial do projétil

        self.angle = angle
        self.speed = speed
        self.damage = damage

        self.projectile_sprites = {
            0: (80, 8, 3, 3, 6),  # Tipo 0: Projétil padrão
            1: (83, 8, 3, 3, 6), # Tipo 1: Projétil shotgun
        }

        self.sprite = self.projectile_sprites[projectile_type]

        self.velocity_x = self.speed * cos(self.angle)
        self.velocity_y = self.speed * sin(self.angle)

        self.collider = ColliderObject(self.x, self.y, 3, 3)

    def update_projectile(self, delta_time):
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.collider.update_collider(self.x, self.y)

    def draw(self):
        """ Desenha o projétil na tela """
        blt(self.x, self.y, 0, *self.sprite)