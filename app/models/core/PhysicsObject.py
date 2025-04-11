import pyxel
from pyxel import *

from models.core.Entity import Entity
from models.core.ColliderObject import ColliderObject

class PhysicsObject(Entity):
    """Classe que representa um objeto físico 2D, usado para simular movimento e colisões.
    A propria classe ja tem 2 colisores, um para o chão e outro para o objeto em si.

    Atributos:
        x (int): Posição X do objeto.
        y (int): Posição Y do objeto.
        width (int): Largura do objeto.
        height (int): Altura do objeto.
        acceleration_y (float): Aceleração gravitacional aplicada ao objeto.
        velocity_x (float): Velocidade horizontal do objeto.
        velocity_y (float): Velocidade vertical do objeto.
        on_ground (bool): Indica se o objeto está no chão.
        falling (bool): Indica se o objeto está caindo.
        ascending (bool): Indica se o objeto está subindo.

    Métodos:
        update_physics_colliders(): Atualiza os colisores do objeto.
        update_physics(delta_time: float): Atualiza a física do objeto, aplicando gravidade e movimento.
    """

    GRAVITY = 400
    MAX_VELOCITY_X = 100.0
    MAX_VELOCITY_Y = 250.0

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height) # Tamanho do objeto de fisica

        # Dinâmica
        self.acceleration_y = self.GRAVITY
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # Estados
        self.on_ground = False
        self.falling = False
        self.ascending = False

        # colisores
        self.ground_collider = ColliderObject(self.x, self.y + self.height, self.width, 2)
        self.entity_collider = ColliderObject(self.x, self.y, self.width, self.height)

        self.last_ground: ColliderObject = None
        self.last_wall: ColliderObject = None

    def set_position(self, x: int, y: int):
        # Reescrita da função para atualizar a posição da entidade
        self.x = x
        self.y = y
        self.update_center()

        self.ground_collider.update_collider(self.x, self.y + self.height)
        self.entity_collider.update_collider(self.x, self.y)

    def update_physics(self, delta_time):
        # Aplica gravidade se não estiver no chão
        if not self.on_ground:
            # Atualiza a velocidade Y com a aceleração gravitacional
            self.velocity_y = min( self.velocity_y + self.acceleration_y * delta_time, self.MAX_VELOCITY_Y )

            # Se a velocidade Y for positiva, o objeto está caindo
            self.falling = self.velocity_y > 0
            self.ascending = self.velocity_y < 0
        else:
            # Se o objeto estiver no chão, reseta a velocidade Y
            self.velocity_y = 0
            self.falling = self.ascending = False

        self.set_position(self.x + self.velocity_x * delta_time, self.y + self.velocity_y * delta_time)

    def draw(self):
        self.entity_collider.draw()
        self.ground_collider.draw()