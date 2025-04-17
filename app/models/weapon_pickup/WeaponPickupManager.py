import pyxel
from pyxel import *

from utils.GameState import GameState

from models.players.weapons.Weapon import Weapon
from models.weapon_pickup.WeaponPickup import WeaponPickup
from models.core.PhysicsManager import PhysicsManager

class WeaponPickupManager:
    """ Gerencia os pickups de armas no jogo.
        Responsavel por adicionar, atualizar e desenhar pickups de armas no mundo.
    """

    def __init__(self, physics_manager: PhysicsManager, game_state: GameState):
        self.weapon_pickups: dict[int, WeaponPickup] = {} # Dicionário para armazenar pickups de armas
        self.game_state = game_state
        self.physics_manager = physics_manager
    
    def add_weapon_pickup(self, id, x, y, weapon_type, ammo, reserve_ammo, remove_timer):
        weapon_pickup = WeaponPickup(id, x, y, weapon_type, ammo, reserve_ammo, remove_timer)

        self.weapon_pickups[id] = weapon_pickup
        self.physics_manager.add_physics_object(weapon_pickup)

    def remove_weapon_pickup(self, weapon_pickup_id):
        """ Remove um pickup de arma da lista de pickups. """
        weapon_pickup = self.weapon_pickups.pop(weapon_pickup_id, None)
        if weapon_pickup:
            self.physics_manager.remove_physics_object(weapon_pickup)

    def try_pickup_weapon(self, weapon_pickup_id):
        self.game_state.game_to_client_queue.put(f"TRY_PICKUP_WEAPON:{self.game_state.player_id};{weapon_pickup_id}")

    def drop_weapon(self, weapon: Weapon):
        self.game_state.game_to_client_queue.put(f"DROP_WEAPON:{weapon.center_x};{weapon.center_y};{weapon.weapon_type};{weapon.ammo};{weapon.reserve_ammo};{5}")

    def update_weapon_pickup_manager(self):
        # Atualiza todos os pickups de armas
        for pickup in self.weapon_pickups.values():
            if pickup.on_ground and pickup in self.physics_manager.physics_objects:
                # Se o pickup estiver no chão, remova-o da lista de objetos físicos
                self.physics_manager.remove_physics_object(pickup)

    def draw(self):
        for pickup in self.weapon_pickups.values():
            pickup.draw()