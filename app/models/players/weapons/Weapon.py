import pyxel
from pyxel import *

from models.core.Entity import Entity
from models.players.weapons.Crosshair import Crosshair
from models.projectiles.ProjectileManager import ProjectileManager

class Weapon(Entity):
    def __init__(self, x, y, width, height, weapon_type, weapon_sprite, max_ammo, reserve_ammo, rpm, reload_time, projectile_manager: ProjectileManager, crosshair_type=0):
        super().__init__(x, y, width, height)

        self.angle = 0
        
        # Sistema de munição
        self.max_ammo = max_ammo
        self.ammo = max_ammo
        self.reserve_ammo = reserve_ammo
        
        # Sistema de disparo
        self.fire_rate = 60 / rpm  # Converte RPM para disparos por segundo
        self.fire_timer = 0
        self.can_fire = True

        # Recarga
        self.reload_time = reload_time
        self.reload_timer = 0
        self.is_reloading = False

        self.weapon_type = weapon_type
        self.weapon_sprite = weapon_sprite

        self.weapon_sprite_left = (width, height, 6)
        self.weapon_sprite_right = (-width, height, 6)

        self.weapon_flip = self.weapon_sprite_left
        self.weapon_rotation = 0

        self.crosshair = Crosshair(x, y, crosshair_type=crosshair_type)
        self.projectile_manager = projectile_manager

        self.weapon_muzzle_x = 0
        self.weapon_muzzle_y = 0

        self.auto_fire = False

        self.draw_sprite = (*self.weapon_sprite, *self.weapon_flip)

    def update(self, x, y, delta_time):
        self.set_center_position(x, y)

        self.crosshair.update_crosshair()
        
        self.angle = atan2(self.crosshair.center_y - self.center_y, self.crosshair.center_x - self.center_x)

        self.weapon_muzzle_x = self.center_x + cos(self.angle) * (self.width // 2)
        self.weapon_muzzle_y = self.center_y + sin(self.angle) * (self.width // 2)

        # Atualiza a rotação da arma
        if self.crosshair.center_x < self.center_x:
            self.weapon_flip = self.weapon_sprite_left
            self.weapon_rotation = self.angle + 180
        else:
            self.weapon_flip = self.weapon_sprite_right
            self.weapon_rotation = -self.angle

        # Atualiza o timer de disparo
        if self.fire_timer > 0:
            self.fire_timer -= delta_time
        else:
            self.can_fire = True

        # Atualiza o timer de recarga
        if self.is_reloading:
            self.reloading(delta_time)

    def draw(self):
        """Renderiza a arma e interface."""
        self.crosshair.draw()
        self.draw_sprite = (*self.weapon_sprite, *self.weapon_flip)
        blt(self.x, self.y, 0, *self.draw_sprite, self.weapon_rotation)

    def shoot(self):
        """Método para disparar a arma. Deve ser implementado nas subclasses."""
        pass
    def start_reload(self):
        """Método para iniciar a recarga. Deve ser implementado nas subclasses."""
        pass
    def reloading(self):
        """Método para lógica de recarga. Deve ser implementado nas subclasses."""
        pass