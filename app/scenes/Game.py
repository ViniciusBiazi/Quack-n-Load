import pyxel
from pyxel import *
from time import time

from models.players.PlayerManager import PlayerManager
from models.world.World import World
from models.core.PhysicsManager import PhysicsManager
from models.projectiles.ProjectileManager import ProjectileManager
from models.weapon_pickup.WeaponPickupManager import WeaponPickupManager

class Game:
    WIDTH= 384
    HEIGHT = 256

    def __init__(self):
        load("assets/assets.pyxres")

        self.world = World(self.WIDTH, self.HEIGHT)

        self.physics_manager = PhysicsManager(self.world)

        self.projectile_manager = ProjectileManager()

        self.weapon_pickup_manager = WeaponPickupManager(self.world, self.physics_manager)

        self.player_manager = PlayerManager(self.physics_manager, self.weapon_pickup_manager, self.projectile_manager)

    def update(self, delta_time):
        # Atualiza a física
        self.physics_manager.update_physics_manager(delta_time)

        # autaliza os jogadores
        self.player_manager.update_player_manager(delta_time)

        # Atualiza os pickups de armas
        self.weapon_pickup_manager.update_weapon_pickup_manager(delta_time)

        # Atualiza os projéteis
        self.projectile_manager.update_projectile_manager(delta_time)

    def draw(self):
        self.world.draw()

        self.player_manager.draw()

        self.weapon_pickup_manager.draw()

        self.projectile_manager.draw()
