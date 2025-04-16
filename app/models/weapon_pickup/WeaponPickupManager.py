import pyxel
from pyxel import *

from utils.GameState import GameState

from models.weapon_pickup.WeaponPickup import WeaponPickup
from models.world.World import World
from models.core.PhysicsManager import PhysicsManager

class WeaponPickupManager:
    """ Gerencia os pickups de armas no jogo.
        Responsavel por adicionar, atualizar e desenhar pickups de armas no mundo.
    """

    def __init__(self, physics_manager: PhysicsManager, game_state: GameState):
        self.weapon_pickups: list[WeaponPickup] = []
        self.game_state = game_state
        self.physics_manager = physics_manager

    def add_weapon_pickup(self, x, y, weapon_type, ammo, reserve_ammo, remove_timer):
        weapon_pickup = WeaponPickup(x, y, weapon_type, ammo, reserve_ammo, remove_timer)

        self.weapon_pickups.append(weapon_pickup)
        self.physics_manager.add_physics_object(weapon_pickup)

    def remove_weapon_pickup(self, weapon_pickup: WeaponPickup):
        """ Remove um pickup de arma da lista de pickups. """
        if weapon_pickup in self.weapon_pickups:
            self.weapon_pickups.remove(weapon_pickup)
            self.physics_manager.remove_physics_object(weapon_pickup)

    def update_weapon_pickup_manager(self, delta_time: float):
        # Atualiza todos os pickups de armas
        for pickup in self.weapon_pickups:
            pickup.update_weapon_pickup(delta_time)

            if pickup.on_ground and pickup in self.physics_manager.physics_objects:
                # Se o pickup estiver no chão, remova-o da lista de objetos físicos
                self.physics_manager.remove_physics_object(pickup)

            if pickup.remove_timer <= 0:
                # Remove o pickup da lista de objetos físicos
                self.physics_manager.remove_physics_object(pickup)
                self.weapon_pickups.remove(pickup)

    def draw(self):
        for pickup in self.weapon_pickups:
            pickup.draw()