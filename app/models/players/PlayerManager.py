import pyxel
from pyxel import *

from models.players.Player import Player
from models.players.RemotePlayer import RemotePlayer
from models.players.DeadPlayer import DeadPlayer
from models.players.PlayerGui import PlayerGui

from models.core.PhysicsManager import PhysicsManager
from models.weapon_pickup.WeaponPickupManager import WeaponPickupManager
from models.projectiles.ProjectileManager import ProjectileManager

class PlayerManager:
    def __init__(self, physics_manager: PhysicsManager, weapon_pickup_manager: WeaponPickupManager, projectile_manager: ProjectileManager):
        """ Inicializa o PlayerManager. """
        self.player: Player = None
        self.player_gui: PlayerGui = None

        self.remote_players: dict[int, RemotePlayer] = {}
        self.dead_players: dict[int, DeadPlayer] = {}

        self.physics_manager = physics_manager
        self.weapon_pickup_manager = weapon_pickup_manager
        self.projectile_manager = projectile_manager

    def update_player_manager(self, delta_time: float):
        """ Atualiza todos os jogadores e jogadores mortos. """
        if self.player:
            self.player.update_player(delta_time)

        # TODO ARRUMAR A COLISAO DO PROJETIL
        for projectile in self.projectile_manager.projectiles:
            for remote_player in self.remote_players.values():
                if projectile.collider.check_collision_rect(remote_player.entity_collider):
                    # Se o projétil colidir com um jogador remoto, remova o projétil
                    print(f"Projétil colidiu com o jogador remoto {remote_player.id}")
                    self.projectile_manager.projectiles.remove(projectile)

        for dead_player in self.dead_players:
            dead_player.update_dead_player(delta_time)

            if dead_player.on_ground and dead_player in self.physics_manager.physics_objects:
                # Se o jogador morto estiver no chão, remova-o da lista de objetos físicos
                self.physics_manager.remove_physics_object(dead_player)

            if dead_player.remove_timer <= 0:
                # Remove o jogador morto da lista de objetos físicos
                self.physics_manager.remove_physics_object(dead_player)
                self.dead_players.remove(dead_player)

    def add_player(self, x, y, player_id):
        """ Adiciona um novo jogador expecificamente o jogador local. """
        self.player = Player(x, y, player_id=player_id, weapon_pickup_manager=self.weapon_pickup_manager, projectile_manager=self.projectile_manager)
        self.player_gui = PlayerGui(player=self.player)

        # Adiciona o jogador à lista de objetos físicos
        self.physics_manager.add_physics_object(self.player)

    def add_remote_player(self, x, y, player_id):
        """ Adiciona um novo jogador remoto. """
        self.remote_players[player_id] = RemotePlayer(x, y, player_id=player_id)

    def update_remote_player(self, player_id, x, y, sprite, weapon=None):
        """ Atualiza o estado do jogador remoto. """
        self.remote_players[player_id].update_remote_player(x, y, sprite, weapon)

    def kill_player(self):
        """ Adiciona o jogador local à lista de jogadores mortos. """
        if self.player:
            dead_player = DeadPlayer(self.player.x, self.player.y, player_id=self.player.id, direction=not self.player.direction)
            self.dead_players[self.player.id] = dead_player

            # Remove o jogador da lista de objetos físicos
            self.physics_manager.remove_physics_object(self.player)
            self.physics_manager.add_physics_object(dead_player)

            # Remove o jogador local
            self.player = None
            self.player_gui = None

    def kill_remote_player(self, player_id):
        """ Adiciona o jogador remoto à lista de jogadores mortos. """

        remote_player = self.remote_players[player_id]

        dead_player = DeadPlayer(remote_player.x, remote_player.y, player_skin=remote_player.player_skin, direction=not remote_player.direction)
        self.dead_players.append(dead_player)

        # Remove o jogador remoto da lista de objetos físicos
        self.physics_manager.add_physics_object(dead_player)

        # Remove o jogador remoto
        del self.remote_players[player_id]
        return

    def get_player_data(self):
        """ Retorna os dados do jogador local. """
        player_data = f"{self.player.id};{self.player.x};{self.player.y};{self.player.draw_sprite}"

        if self.player.weapon:
            player_data += f";{self.player.weapon.x};{self.player.weapon.y};{self.player.weapon.draw_sprite};{self.player.weapon.weapon_rotation}"

        return player_data
    
    def draw(self):
        """ Desenha todos os jogadores e jogadores mortos na tela. """
        if self.player:
            self.player.draw()
            self.player_gui.draw()

        for remote_player in self.remote_players.values():
            remote_player.draw()

        for dead_player in self.dead_players.values():
            dead_player.draw()