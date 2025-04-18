import pyxel
from pyxel import *

from utils.GameState import GameState

from models.players.weapons.Weapon import Weapon
from models.weapon_pickup.WeaponPickup import WeaponPickup
from models.core.PhysicsManager import PhysicsManager

class WeaponPickupManager:
    def __init__(self, physics_manager: PhysicsManager, game_state: GameState):
        self.weapon_pickups: dict[int, WeaponPickup] = {} # Dicionário para armazenar pickups de armas
        self.game_state = game_state
        self.physics_manager = physics_manager
    
    def update_weapon_pickup_manager(self):
        # Atualiza todos os pickups de armas
        for pickup in self.weapon_pickups.values():
            if pickup.on_ground:
                # Se o pickup estiver no chão, remova-o da lista de objetos físicos
                self.physics_manager.remove_physics_object(pickup)

    def add_weapon_pickup(self, id: int, x: float, y: float, weapon_type: int, ammo: int, reserve_ammo: int, remove_timer: int):
        weapon_pickup = WeaponPickup(id, x, y, weapon_type, ammo, reserve_ammo, remove_timer)

        self.weapon_pickups[id] = weapon_pickup
        self.physics_manager.add_physics_object(weapon_pickup)

    def remove_weapon_pickup(self, weapon_pickup_id: int):
        weapon_pickup = self.weapon_pickups.pop(weapon_pickup_id, None)
        if weapon_pickup:
            self.physics_manager.remove_physics_object(weapon_pickup)

    def pickup_weapon(self, weapon_pickup_id: int):
        self.game_state.game_to_client_queue.put(f"PICKUP_WEAPON:{self.game_state.player_id};{weapon_pickup_id}")

    def drop_weapon(self, weapon: Weapon):
        self.game_state.game_to_client_queue.put(f"DROP_WEAPON:{weapon.center_x};{weapon.center_y};{weapon.weapon_type};{weapon.ammo};{weapon.reserve_ammo};{10}")

    def draw(self):
        for pickup in self.weapon_pickups.values():
            pickup.draw()