import pyxel
from pyxel import *

from utils.GameState import GameState

from models.projectiles.Projectile import Projectile

class ProjectileManager:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.projectiles: dict[int, Projectile] = {} # Dicionário para armazenar projéteis
        self.remote_projectiles: dict[int, Projectile] = {} # Dicionário para armazenar projéteis remotos

    def update_projectile_manager(self, delta_time):
        """ Atualiza a posição dos projéteis e verifica colisões com os jogadores """
        for id, projectile in list(self.projectiles.items()) + list(self.remote_projectiles.items()):
            projectile.update_projectile(delta_time)

            if projectile.x < 0 or projectile.x > pyxel.width or projectile.y < 0 or projectile.y > pyxel.height:
                self.projectiles.pop(id, None)
                self.remote_projectiles.pop(id, None)

    def try_add_projectile(self, x, y, angle, speed, damage, projectile_type=0):
        self.game_state.game_to_client_queue.put(f"ADD_PROJECTILE:{self.game_state.player_id};{x};{y};{angle};{speed};{damage};{projectile_type}")  

    def add_projectile(self, player_id, id, x, y, angle, speed, damage, projectile_type=0):
        new_projectile = Projectile(id, x, y, angle, speed, damage, projectile_type)
        if player_id == self.game_state.player_id:
            self.projectiles[id] = new_projectile
        else:
            self.remote_projectiles[id] = new_projectile

    def remove_projectile(self, id):
        """ Remove um projétil do dicionário de projéteis """
        self.projectiles.pop(id, None)
        self.remote_projectiles.pop(id, None)

    def draw(self):
        for projectile in list(self.projectiles.values()) + list(self.remote_projectiles.values()):
            projectile.draw()

    def reset_projectile_manager(self):
        """ Reseta o gerenciador de projéteis """
        self.projectiles.clear()
        self.remote_projectiles.clear()