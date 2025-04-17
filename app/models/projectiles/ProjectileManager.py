import pyxel
from pyxel import *

from utils.GameState import GameState

from models.projectiles.Projectile import Projectile

class ProjectileManager:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.projectiles: dict[int, Projectile] = {} # Dicionário para armazenar projéteis
        self.remote_projectiles: dict[int, Projectile] = {} # Dicionário para armazenar projéteis remotos
        self.to_remove: list[int] = [] # Lista para armazenar projéteis a serem removidos

    def update_projectile_manager(self, delta_time):
        """ Atualiza a posição dos projéteis e verifica colisões com os jogadores """
        self.remove_projectiles() # Remove os projeteis da lista de projeteis para remover

        for id, projectile in self.projectiles.items():
            projectile.update_projectile(delta_time)

            if projectile.x < 0 or projectile.x > pyxel.width or projectile.y < 0 or projectile.y > pyxel.height:
                # Se o projétil sair da tela, remova-o
                self.to_remove.append(id)
        
        for id, projectile in self.remote_projectiles.items():
            projectile.update_projectile(delta_time=delta_time)

    def try_add_projectile(self, x, y, angle, speed, damage, projectile_type=0): 
        self.game_state.game_to_client_queue.put(f"ADD_PROJECTILE:{self.game_state.player_id};{x};{y};{angle};{speed};{damage};{projectile_type}") # Envia a mensagem para o cliente
            
    def add_projectile(self, id, x, y, angle, speed, damage, projectile_type=0):
        new_projectile = Projectile(id, x, y, angle, speed, damage, projectile_type)
        self.projectiles[id] = new_projectile

    def add_remote_projectile(self,id, x, y, angle, speed, damage, projectile_type=0):
        new_projectile = Projectile(id, x, y, angle, speed, damage, projectile_type)
        self.remote_projectiles[id] = new_projectile

    def remove_projectile(self, projectile_id):
        if projectile_id in self.remote_projectiles.keys():
            self.remote_projectiles.pop(projectile_id, None)

    def remove_projectiles(self):
        for id in self.to_remove:
            self.projectiles.pop(id, None) # Remove o projétil do dicionário
            self.game_state.game_to_client_queue.put(f"REMOVE_PROJECTILE:{self.game_state.player_id};{id}") # Envia a mensagem para o cliente
        self.to_remove.clear() # Limpa a lista de projéteis a serem removidos

    def draw(self):
        for projectile in self.projectiles.values():
            projectile.draw()

        for projectile in self.remote_projectiles.values():
            projectile.draw()