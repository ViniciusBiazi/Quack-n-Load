import pyxel
from pyxel import *
from random import randint

from models.weapon_pickup.WeaponPickup import WeaponPickup
from models.world.World import World
from models.core.PhysicsManager import PhysicsManager

class WeaponPickupManager:
    """ Gerencia os pickups de armas no jogo.
        Responsavel por adicionar, atualizar e desenhar pickups de armas no mundo.
    """
    MAX_WEAPON_PICKUPS = 5
    WEAPON_PICKUP_GEN_TIME = 5

    WEAPON_DATA = {
        0: {"ammo": 17, "reserve_ammo": 17 * 2}, # pistola
        1: {"ammo": 5, "reserve_ammo": 5 * 3}, # shotgun
        2: {"ammo": 5, "reserve_ammo": 5 * 2}, # rifle
        3: {"ammo": 30, "reserve_ammo": 30 * 2}, # assault rifle
    }

    def __init__(self, world: World, physics_manager: PhysicsManager):
        self.max_weapon_pickups= self.MAX_WEAPON_PICKUPS
        self.gen_weapon_pickups_timer = self.WEAPON_PICKUP_GEN_TIME

        self.weapon_pickups: list[WeaponPickup] = []
        self.spawn_points = world.weapon_spawn_points

        self.physics_manager = physics_manager

    def add_weapon_pickup(self, x, y, weapon_type, ammo, reserve_ammo, remove_timer=15):
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
        
        # Gera pickups de armas
        self.gen_weapon_pickups_timer -= delta_time
        if self.gen_weapon_pickups_timer <= 0:
            self.generate_weapon_pickup()
            self.gen_weapon_pickups_timer = self.WEAPON_PICKUP_GEN_TIME

    def generate_weapon_pickup(self):
        """ Adiciona um pickup de arma ao mundo. """
        if len(self.weapon_pickups) < self.max_weapon_pickups:
            weapon_type = randint(0, 3) # gera um tipo de arma aleatório
            weapon_spawn_point = self.spawn_points.pop(0) # pega o primeiro ponto de spawn da lista

            self.spawn_points.append(weapon_spawn_point) # adiciona o ponto de spawn no final da lista

            self.add_weapon_pickup(
                *weapon_spawn_point,
                weapon_type,
                self.WEAPON_DATA[weapon_type]["ammo"],
                self.WEAPON_DATA[weapon_type]["reserve_ammo"]
            )

    def draw(self):
        for pickup in self.weapon_pickups:
            pickup.draw()