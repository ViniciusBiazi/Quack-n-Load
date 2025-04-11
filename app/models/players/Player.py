import pyxel
from pyxel import *

from models.core.PhysicsObject import PhysicsObject
from models.weapon_pickup.WeaponPickupManager import WeaponPickupManager

from models.players.weapons.Pistol import Pistol
from models.players.weapons.Shotgun import Shotgun
from models.players.weapons.Rifle import Rifle
from models.players.weapons.AssaultRifle import AssaultRifle


class Player(PhysicsObject):
    """
    Classe que representa o player, herda de PhysicsObject, incluindo controle de movimento.
    """

    WALK_SPEED = 100  # Velocidade de caminhada
    JUMP_STRENGTH = -215  # Força do pulo
    JUMP_BUFFER = 0.2 # Buffer de pulo
    COYOTE_TIME = 0.1 # Tempo de coyote
    ANIMATION_TIMER = 0.2  # Velocidade da animação
    MAX_HEALTH = 100  # Vida máxima do player

    def __init__(self, x, y, width=13, height=16, player_id=0, weapon_pickup_manager: WeaponPickupManager = None, projectile_manager=None):
        super().__init__(x, y, width, height)  # Tamanho do objeto de fisica
        self.id = player_id

        self.health = 100  # Vida do player
        self.max_health = self.MAX_HEALTH  # Vida máxima do player

        self.player_skin = player_id

        self.sprite_right = (-width, height, 6)
        self.sprite_left = (width, height, 6)
        self.direction = True
        self.sprite_flip = self.sprite_right

        self.animations = {
            "idle": [(self.player_skin * 16 + 2, 0),
                     (self.player_skin * 16 + 2, 16),
                     (self.player_skin * 16 + 2, 0),
                     (self.player_skin * 16 + 2, 16)],
            "walking": [(self.player_skin * 16 + 2, 32),
                        (self.player_skin * 16 + 2, 48),
                        (self.player_skin * 16 + 2, 64),
                        (self.player_skin * 16 + 2, 80)],
            "ascending": [(self.player_skin * 16 + 2, 96)],
            "falling": [(self.player_skin * 16 + 2, 112)],
        }

        self.current_animation_key = "idle"
        self.current_animation = self.animations[self.current_animation_key]

        self.sprite = 0  # Frame atual da animação
        self.animation_timer = self.ANIMATION_TIMER  # Timer da animação

        self.walking = False 
        
        self.walk_speed = self.WALK_SPEED  # Velocidade de caminhada
        self.jump_strength = self.JUMP_STRENGTH  # Força do pulo

        self.jump_buffer = 0 # Buffer de pulo
        self.coyote_time = 0 # Tempo de coyote

        # Arma
        self.weapon = None  # Arma atual do jogador
        self.weapon_pickup_manager = weapon_pickup_manager
        self.projectile_manager = projectile_manager

    def update_player(self, delta_time):
        """ Atualiza o estado do player, incluindo controle e física. """
        # Lida com a entrada do jogador
        self.handle_input(delta_time)

        # Atualiza a animação
        self.update_animation(delta_time)

        if self.weapon:
            self.handle_weapon(delta_time)

    def handle_input(self, delta_time):
        """ Lida com as entradas do jogador (teclas pressionadas). """
        self.velocity_x = 0  # Reseta a velocidade horizontal
        self.walking = False  # Reseta o estado de andar

        if self.on_ground:  # Se o jogador está no chão
            self.coyote_time = self.COYOTE_TIME  # Reseta o tempo de coyote
        else:
            self.coyote_time = max(0, self.coyote_time - delta_time)

        if btn(KEY_A):  # Mover para a esquerda
            self.velocity_x = -self.walk_speed
            self.direction = False
            self.walking = True

        if btn(KEY_D):  # Mover para a direita
            self.velocity_x = self.walk_speed
            self.direction = True
            self.walking = True

        if btnp(KEY_SPACE) or btnp(KEY_W):  # Pular
            self.jump_buffer = self.JUMP_BUFFER  # Ativa o buffer de pulo
            self.sprite = 0  # Reseta o sprite da animação
        else:
            self.jump_buffer = max(0, self.jump_buffer - delta_time)  # Diminui o buffer de pulo

        if (self.on_ground or self.coyote_time > 0) and self.jump_buffer > 0:
            self.velocity_y = self.jump_strength
            self.on_ground = False  # Reseta o estado de estar no chão
            self.jump_buffer = 0  # Reseta o buffer de pulo
            self.coyote_time = 0  # Reseta o tempo de coyote

        if btnp(KEY_E):
            self.pickup_weapon()

        if btnp(KEY_Q):
            self.drop_weapon()

    def handle_weapon(self, delta_time):
        self.weapon.update(self.center_x, self.center_y + 2, delta_time)

        if btnp(KEY_R) and not self.weapon.is_reloading and self.weapon.ammo < self.weapon.max_ammo and self.weapon.reserve_ammo > 0 and self.weapon.can_fire:
            self.weapon.start_reload()
        
        if self.weapon.auto_fire:
            if btn(MOUSE_BUTTON_LEFT) and self.weapon.can_fire and self.weapon.fire_timer <= 0:
                if self.weapon.ammo > 0:
                    self.weapon.shoot()
        else:
            if btnp(MOUSE_BUTTON_LEFT) and self.weapon.can_fire and self.weapon.fire_timer <= 0:
                if self.weapon.ammo > 0:
                    self.weapon.shoot() 

    def update_animation(self, delta_time):
        """ Atualiza a animação do jogador. """
        if self.falling:
            self.current_animation_key = "falling"
            self.sprite = 0
        elif self.ascending:
            self.current_animation_key = "ascending"
            self.sprite = 0
        elif self.walking:
            self.current_animation_key = "walking"
        else:
            self.current_animation_key = "idle"

        # Atualiza a animação
        self.current_animation = self.animations[self.current_animation_key]

        # Atualiza o sprite flip
        if self.direction:
            self.sprite_flip = self.sprite_right
        else:
            self.sprite_flip = self.sprite_left

        # Atualiza o frame da animação
        self.animation_timer -= delta_time
        if self.animation_timer <= 0:
            self.animation_timer = self.ANIMATION_TIMER
            self.sprite = (self.sprite + 1) % len(self.current_animation)

    def draw(self):
        blt(self.x, self.y, 0, *self.current_animation[self.sprite], *self.sprite_flip)
        
        if self.weapon:
            self.weapon.draw()

    def pickup_weapon(self):
        """ Pega uma arma do WeaponPickupManager. """
        for weapon_pickup in self.weapon_pickup_manager.weapon_pickups:
            if self.entity_collider.check_collision_rect(weapon_pickup.entity_collider):
                # Remove a arma do WeaponPickupManager
                self.weapon_pickup_manager.remove_weapon_pickup(weapon_pickup)

                if weapon_pickup.weapon_type == 0:
                    weapon = Pistol(self.center_x, self.center_y, self.projectile_manager)
                elif weapon_pickup.weapon_type == 1:
                    weapon = Shotgun(self.center_x, self.center_y, self.projectile_manager)
                elif weapon_pickup.weapon_type == 2:
                    weapon = Rifle(self.center_x, self.center_y, self.projectile_manager)
                elif weapon_pickup.weapon_type == 3:
                    weapon = AssaultRifle(self.center_x, self.center_y, self.projectile_manager)

                weapon.ammo = weapon_pickup.ammo
                weapon.reserve_ammo = weapon_pickup.reserve_ammo

                self.drop_weapon()
                self.weapon = weapon

    def drop_weapon(self):
        """ Deixa a arma no chão. """
        if self.weapon:
            self.weapon_pickup_manager.add_weapon_pickup(self.center_x, self.center_y, self.weapon.weapon_type, self.weapon.ammo, self.weapon.reserve_ammo, 5)
            self.weapon = None