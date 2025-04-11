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
        self.remote_players: list[RemotePlayer] = []
        self.dead_players: list[DeadPlayer] = []
        self.player_gui: PlayerGui = None

        self.physics_manager = physics_manager
        self.weapon_pickup_manager = weapon_pickup_manager
        self.projectile_manager = projectile_manager

    def update_player_manager(self, delta_time: float):
        """ Atualiza todos os jogadores e jogadores mortos. """
        if self.player:
            self.player.update_player(delta_time)

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
        remote_player = RemotePlayer(x, y, player_id=player_id)
        self.remote_players.append(remote_player)

    def update_remote_player(self, player_id, x, y, sprite):
        """ Atualiza o estado do jogador remoto. """
        for remote_player in self.remote_players:
            if remote_player.id == player_id:
                remote_player.update_remote_player(x, y, sprite)
                return

    def kill_player(self):
        """ Adiciona o jogador local à lista de jogadores mortos. """
        if self.player:
            dead_player = DeadPlayer(self.player.x, self.player.y, player_skin=self.player.player_skin, direction=not self.player.direction)
            self.dead_players.append(dead_player)

            # Remove o jogador da lista de objetos físicos
            self.physics_manager.remove_physics_object(self.player)
            self.physics_manager.add_physics_object(dead_player)

            # Remove o jogador local
            self.player = None
            self.player_gui = None

    def kill_remote_player(self, player_id):
        """ Adiciona o jogador remoto à lista de jogadores mortos. """
        for remote_player in self.remote_players:
            if remote_player.id == player_id:
                dead_player = DeadPlayer(remote_player.x, remote_player.y, player_skin=remote_player.player_skin, direction=not remote_player.direction)
                self.dead_players.append(dead_player)

                # Remove o jogador remoto da lista de objetos físicos
                self.physics_manager.add_physics_object(dead_player)

                # Remove o jogador remoto
                self.remote_players.remove(remote_player)
                return

    def draw(self):
        """ Desenha todos os jogadores e jogadores mortos na tela. """
        if self.player:
            self.player.draw()
            self.player_gui.draw()

        for remote_player in self.remote_players:
            remote_player.draw()

        for dead_player in self.dead_players:
            dead_player.draw()