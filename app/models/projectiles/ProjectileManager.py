import pyxel
from pyxel import *

from models.projectiles.Projectile import Projectile

class ProjectileManager:
    def __init__(self):
        self.projectiles: list[Projectile] = []

        self.remote_projectiles: list[Projectile] = []

    def update_projectile_manager(self, delta_time):
        """ Atualiza a posição dos projéteis e verifica colisões com os jogadores """
        for projectile in self.projectiles:
            projectile.update_projectile(delta_time)

            if projectile.x < 0 or projectile.x > pyxel.width or projectile.y < 0 or projectile.y > pyxel.height:
                self.projectiles.remove(projectile)

        for projectile in self.remote_projectiles:
            projectile.update_projectile(delta_time)

            if projectile.x < 0 or projectile.x > pyxel.width or projectile.y < 0 or projectile.y > pyxel.height:
                self.remote_projectiles.remove(projectile)
            
            
    def add_projectile(self, x, y, angle, speed, damage, projectile_type=0):
        new_projectile = Projectile(x, y, angle, speed, damage, projectile_type)
        self.projectiles.append(new_projectile)

    def add_remote_projectile(self, x, y, angle, speed, damage, projectile_type=0):
        new_projectile = Projectile(x, y, angle, speed, damage, projectile_type)
        self.remote_projectiles.append(new_projectile)

    def draw(self):
        for projectile in self.projectiles + self.remote_projectiles:
            projectile.draw()