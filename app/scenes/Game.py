import pyxel
from pyxel import *
import time

from utils.GameState import GameState

from models.players.PlayerManager import PlayerManager
from models.world.World import World
from models.core.PhysicsManager import PhysicsManager
from models.projectiles.ProjectileManager import ProjectileManager
from models.weapon_pickup.WeaponPickupManager import WeaponPickupManager

class Game:
    WIDTH= 384
    HEIGHT = 256

    def __init__(self, game_state: GameState):
        load("assets/assets.pyxres")
        self.game_state = game_state

        self.world = World(self.WIDTH, self.HEIGHT)

        self.physics_manager = PhysicsManager(self.world)

        self.projectile_manager = ProjectileManager(self.game_state)

        self.weapon_pickup_manager = WeaponPickupManager(self.physics_manager, self.game_state)

        self.player_manager = PlayerManager(self.physics_manager, self.weapon_pickup_manager, self.projectile_manager)

    def update(self, delta_time):
        while not self.game_state.client_to_game_queue.empty():
            data = self.game_state.client_to_game_queue.get()

            if data.startswith("ADD_GAME_PLAYER:"):
                _, info = data.split(":")
                client_id, x, y = info.split(";")

                client_id = int(client_id)
                x = float(x)
                y = float(y)

                if client_id in self.game_state.players.keys():
                    if client_id == self.game_state.player_id:
                        self.player_manager.add_player(x, y, client_id)
                    else:
                        self.player_manager.add_remote_player(x, y, client_id)

            elif data.startswith("UPDATE_PLAYER:"):
                _, info = data.split(":")
                parts = info.split(";")

                client_id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                sprite = tuple(map(int, parts[3].strip("()").split(",")))

                weapon = None
                if len(parts) > 4:
                    weapon_x = float(parts[4])
                    weapon_y = float(parts[5])
                    weapon_sprite = tuple(map(int, parts[6].strip("()").split(",")))
                    weapon_rotation = float(parts[7])
                    weapon = (weapon_x, weapon_y, weapon_sprite, weapon_rotation)

                self.player_manager.update_remote_player(client_id, x, y, sprite, weapon)
            
            elif data.startswith("ADD_WEAPON_PICKUP:"):
                _, info = data.split(":")
                x, y, weapon_type, ammo, reserve_ammo, remove_timer = info.split(";")

                x = float(x)
                y = float(y)
                weapon_type = int(weapon_type)
                ammo = int(ammo)
                reserve_ammo = int(reserve_ammo)
                remove_timer = int(remove_timer)

                self.weapon_pickup_manager.add_weapon_pickup(x, y, weapon_type, ammo, reserve_ammo, remove_timer)

            elif data.startswith("ADD_PROJECTILE:"):
                _, info = data.split(":")
                _ , x, y, angle, speed, damage, projectile_type = info.split(";")

                x = float(x)
                y = float(y)
                angle = float(angle)
                speed = float(speed)
                damage = int(damage)
                projectile_type = int(projectile_type)

                self.projectile_manager.add_remote_projectile(x, y, angle, speed, damage, projectile_type)

        self.physics_manager.update_physics_manager(delta_time)

        # autaliza os jogadores
        self.player_manager.update_player_manager(delta_time)

        # Atualiza os pickups de armas
        self.weapon_pickup_manager.update_weapon_pickup_manager(delta_time)

        # Atualiza os projéteis
        self.projectile_manager.update_projectile_manager(delta_time)

        if self.player_manager.player:
            self.game_state.game_to_client_queue.put(f"UPDATE_PLAYER:{self.player_manager.get_player_data()}")

    def draw(self):
        self.world.draw()

        self.player_manager.draw()

        self.weapon_pickup_manager.draw()

        self.projectile_manager.draw()
