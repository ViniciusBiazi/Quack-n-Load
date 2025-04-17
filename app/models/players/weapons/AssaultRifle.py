import pyxel
from pyxel import *

from models.players.weapons.Weapon import Weapon
from models.projectiles.ProjectileManager import ProjectileManager

class AssaultRifle(Weapon):
    def __init__(self, x, y, projectile_manager: ProjectileManager):
        super().__init__(x, y, width=24, height=8, weapon_type=3, max_ammo=30, reserve_ammo=60, rpm=600, reload_time=2.3, weapon_sprite=(72, 0), projectile_manager=projectile_manager)

        # parametros do projetil
        self.auto_fire = True
        self.projectile_speed = 500
        self.projectile_damage = 10

    def update(self, x, y, delta_time):
        # Atualiza a pistola com a lógica da classe base Gun
        super().update(x, y, delta_time)

    def draw(self):
        # Desenha a pistola na tela usando o método da classe base
        super().draw()

    def shoot(self):
        if self.is_reloading:
            return
        
        self.ammo -= 1
        play(0, 9)
        self.fire_timer = self.fire_rate
        self.can_fire = False
        
        self.projectile_manager.try_add_projectile(self.weapon_muzzle_x, self.weapon_muzzle_y, angle=self.angle, speed=self.projectile_speed, damage=self.projectile_damage)

    def start_reload(self):
        self.is_reloading = True
        self.can_fire = False
        play(1, [10, 11])
        self.reload_timer = self.reload_time

    def reloading(self, delta_time):
        if self.reload_timer > 0:
            self.reload_timer -= delta_time
        else:
            ammount = min(self.max_ammo - self.ammo, self.reserve_ammo)
            self.ammo += ammount
            self.reserve_ammo -= ammount
            self.is_reloading = False
            self.can_fire = True