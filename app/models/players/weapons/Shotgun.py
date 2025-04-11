import pyxel
from pyxel import *


from models.players.weapons.Weapon import Weapon
from models.projectiles.ProjectileManager import ProjectileManager

# Classe Pistol herda Gun e define seu sprite específico
class Shotgun(Weapon):

    def __init__(self, x, y, projectile_manager: ProjectileManager):
        
        super().__init__(x, y, width=16, height=8, weapon_type=1, max_ammo=5, reserve_ammo=4*3, rpm=85, reload_time=3, weapon_sprite=(64, 8), projectile_manager=projectile_manager, crosshair_type=1)

        # Inicializa os parametros específicos da Shotgun
        self.reload_time_per_shell = self.reload_time / self.max_ammo
        self.reload_timer_per_shell = self.reload_time_per_shell

        # parametros do projetil
        self.projectile_speed = 400
        self.projectile_damage = 1

    def update(self, x, y, delta_time):
        # Atualiza a pistola com a lógica da classe base Gun
        super().update(x, y, delta_time)

    def draw(self):
        # Desenha a pistola na tela usando o método da classe base
        super().draw()

    def shoot(self):
        self.is_reloading = False     
        self.ammo -= 1
        play(0, 1)
        self.fire_timer = self.fire_rate

        # Cria os projéteis da shotgun
        for i in range(3):
            angle_offset = (i - 1) * 5
            self.projectile_manager.add_projectile(self.weapon_muzzle_x, self.weapon_muzzle_y, angle=self.angle + angle_offset, speed=self.projectile_speed, damage=self.projectile_damage, projectile_type=1)

    def start_reload(self):
        self.is_reloading = True
        self.reload_timer_per_shell = self.reload_time_per_shell

    def reloading(self, delta_time):
        if self.reload_timer_per_shell > 0:
            self.reload_timer_per_shell -= delta_time
        else:
            self.reload_timer_per_shell = self.reload_time_per_shell

            if self.ammo == 0:
                play(1, [8, 4])
                self.reload_timer_per_shell += 0.4
                self.fire_timer = self.fire_rate + 0.1
            else:
                play(1, 8)

            self.ammo += 1
            self.reserve_ammo -= 1

            if self.ammo >= self.max_ammo or self.reserve_ammo <= 0:
                self.is_reloading = False

